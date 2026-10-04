# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Exercise the tutorial's offline conversion/config/Collector contracts, without services."""
import argparse
import ast
from copy import deepcopy
import importlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
from unittest.mock import patch
import zipfile

root = Path(__file__).resolve().parent
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--source-root', type=Path, required=True)
a = p.parse_args()
source = a.source_root.resolve()
sys.path.insert(0, str(source))
from omegaconf import OmegaConf
from nemo_gym.global_config import GlobalConfigDictParser, GlobalConfigDictParserConfig
from nemo_gym.rollout_collection import (
    RolloutCollectionConfig, RolloutCollectionHelper, _native_episode_request_body, _episode_record,
)
from nemo_gym.single_agent_turn_types import SingleAgentTurnRequest
from nemo_gym.reward_profile import RewardProfiler

checks = []
os.environ.update({
    'GYM_HOST': '192.0.2.10', 'POLICY_BASE_URL': 'http://invalid.example/v1',
    'POLICY_MODEL_NAME': 'tutorial-model', 'POLICY_API_KEY': 'tutorial-placeholder',
    'OPENSANDBOX_DOMAIN': 'invalid.example', 'OPENSANDBOX_API_KEY': 'tutorial-placeholder',
    'PYTHONPATH': str(source),
})
steps = json.loads((root / 'benchmark-lab.json').read_text())
for step in steps:
    subprocess.run(['bash', '-n'], input=step['command'], text=True, check=True)
for name in ['prepare-tutorial-tasks.py', 'command_lesson.py']:
    ast.parse((root / name).read_text())
checks.append('8 Bash blocks and helper Python syntax')
with tempfile.TemporaryDirectory(prefix='gym-command-lab-') as temporary:
    work = Path(temporary)
    os.chdir(work)
    with zipfile.ZipFile(root / 'gym-benchmark-lab.zip') as bundle:
        bundle.extractall(work)
    fixture = {
        'instance_id': 'tutorial-synthetic-0',
        'responses_create_params': {'input': [{'role': 'user', 'content': 'Synthetic offline fixture'}]},
        'base_commit': 'fixture', 'image_digest': 'sha256:fixture',
        'run_script': 'echo fixture', 'parser_script': '# fixture',
        'FAIL_TO_PASS': ['test_a'], 'PASS_TO_PASS': ['test_b'], 'gold_patch': 'fixture',
        'agent_ref': {'name': 'old-routing'}, '_ng_task_index': 99,
    }
    raw = work / 'input.jsonl'
    raw.write_text('\n'.join(json.dumps({**fixture, 'instance_id': f'tutorial-synthetic-{i}'}) for i in range(2))+'\n')
    cmd = [sys.executable, str(work/'tutorial-lab/prepare-tutorial-tasks.py'), str(raw), str(work/'run'), '--limit', '0']
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    assert subprocess.run(cmd, capture_output=True).returncode != 0, 'must refuse output overwrite'
    subprocess.run(cmd[:-3]+[str(work/'single'), '--limit', '1'], check=True, capture_output=True)
    assert len((work/'single/tasks.jsonl').read_text().splitlines()) == 1
    rows = [json.loads(line) for line in (work/'run/tasks.jsonl').read_text().splitlines()]
    assert len(rows) == 2 and 'episode_id' not in rows[0] and 'agent_ref' not in rows[0]
    for row in rows:
        assert row['task_input']['responses_create_params'] == fixture['responses_create_params']
        expected = {k:v for k,v in fixture.items() if k not in {'agent_ref','_ng_task_index','responses_create_params'}}
        expected['instance_id'] = row['task_id']['task_id']
        assert row['task_input']['task_data'] == expected
    checks.append('downloaded converter: 2 tasks, limit=1, verifier-field preservation and overwrite rejection')
    merged = GlobalConfigDictParser().parse(GlobalConfigDictParserConfig(
        initial_global_config_dict=OmegaConf.create({'config_paths': ['tutorial-lab/lab.yaml', str(work/'run/routing.yaml')]}),
        skip_load_from_cli=True, skip_load_from_dotenv=True, offline=True,
    ))
    cfg = OmegaConf.to_container(merged, resolve=True)
    envs = {k:list(v['environment_servers']) for k,v in cfg.items() if isinstance(v,dict) and 'environment_servers' in v}
    assert envs == {'single_agent_turn': ['single_agent_turn']}
    assert cfg['single_agent_turn']['environment_servers']['single_agent_turn']['max_concurrent_episodes'] == 1
    assert cfg['policy_model']['responses_api_models']['openai_model']['host'] == '192.0.2.10'
    assert cfg['head_server']['host'] == '127.0.0.1' and cfg['head_server']['port'] == 11000
    checks.append('offline full composition: exactly one native Environment; references, reachable host and local Head')
    collection = RolloutCollectionConfig.model_validate({**cfg,
        'input_jsonl_fpath': str(work/'run/tasks.jsonl'),
        'output_jsonl_fpath': str(work/'run/rollouts.jsonl'),
        'num_repeats': 2, 'num_samples_in_parallel': 1,
    })
    helper = RolloutCollectionHelper()
    expanded = helper._preprocess_rows_from_config(collection)
    assert len(expanded) == 4
    assert {r['_ng_environment_server'] for r in expanded} == {'single_agent_turn'}
    requests = [_native_episode_request_body(row) for row in expanded]
    for body in requests:
        SingleAgentTurnRequest.model_validate(body)
    assert len({(b['episode_id']['rollout_id'], b['episode_id']['attempt']) for b in requests}) == 4
    retry = _native_episode_request_body({**expanded[0], '_ng_attempt_index': 1})
    assert retry['episode_id']['rollout_id'] == requests[0]['episode_id']['rollout_id']
    assert retry['episode_id']['attempt'] == 1
    for bad in [fixture, {**rows[0], 'task_id': {**rows[0]['task_id'], 'taskset': 'unmapped'}}]:
        try:
            helper._preprocess_raw_rows([(0,json.dumps(bad),deepcopy(bad))], collection)
        except ValueError:
            pass
        else:
            raise AssertionError('flat or unmapped input should be rejected')
    checks.append('real Collector planning: 2 tasks × 2 repeats, typed requests, attempt identity, flat/unmapped rejection')
    results = []
    for row, body in zip(expanded, requests):
        record = _episode_record({**body, 'task_id': body['task']['task_id'],
            'result': {'reward': float(row['_ng_rollout_index']), 'evaluation_completed': True}})
        assert 'result' not in record and 'reward' in record
        record.update({k:v for k,v in row.items() if k.startswith('_ng_')})
        results.append(record)
    profiler = RewardProfiler()
    groups, agents, repeats = profiler.profile_from_data(expanded, results)
    assert len(groups) == 2
    assert all(g['mean/reward'] == 0.5 and g['num_rollouts'] == 2 for g in groups)
    for output in profiler.write_to_disk(groups, agents, repeats, work/'run/rollouts.jsonl'):
        assert output.exists()
    failure = _episode_record({'task_id': requests[0]['task']['task_id'], 'failure': {'failure_reason':'fixture', 'terminal':False}})
    assert failure['_ng_failure_class'] == 'environment_server_failed'
    checks.append('real result unwrapping/failure conversion and synthetic reward profiling: mean 0.5 on two tasks')
    cli = importlib.import_module('nemo_gym.cli.main')
    for words in [
        'env start --config tutorial-lab/lab.yaml',
        'env resolve --config tutorial-lab/lab.yaml --config run/routing.yaml',
        'env status',
        'eval run --no-serve --config tutorial-lab/lab.yaml --config run/routing.yaml --input run/tasks.jsonl --output run/rollouts.jsonl --limit 1 --num-repeats 1 --concurrency 1',
        'eval profile --inputs run/rollouts_materialized_inputs.jsonl --rollouts run/rollouts.jsonl',
    ]:
        with patch.object(sys, 'argv', ['gym', *shlex.split(words)]), patch.object(cli, 'dispatch') as dispatch:
            cli.main()
            assert dispatch.call_count == 1
            if words.startswith('eval run'):
                assert dispatch.call_args.args[0] == 'nemo_gym.cli.eval:collect_rollouts'
    checks.append('5 actual CLI parsers/dispatch targets; --no-serve selects collect_rollouts')
report = {'result': 'PASS', 'source_sha': '3ef478df1ee163134d32a3f291f0a9e5981d0e52',
    'checks': checks, 'model_calls': 0, 'services_started': 0,
    'scope': 'Synthetic offline contract checks; no upstream dataset preparation, real server startup, sandbox or model benchmark run.'}
(root/'command-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
