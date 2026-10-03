# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Validate the tutorial examples offline against the pinned Gym source."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-root', type=Path, default=Path('/private/tmp/gym-tutorial-source'))
parser.add_argument('--evidence-root', type=Path, default=Path('/private/tmp/gym-native-hermes-evidence'))
args = parser.parse_args()
sys.path.insert(0, str(args.source_root))
os.chdir(args.source_root)
from omegaconf import OmegaConf
from nemo_gym.global_config import GlobalConfigDictParser, GlobalConfigDictParserConfig
from nemo_gym.single_agent_turn_types import SingleAgentTurnRequest, SingleAgentTurnResponse
from environment_servers.single_agent_turn.app import SingleAgentTurnEnvironmentServerConfig

os.environ.update({
    'POLICY_BASE_URL': 'http://invalid.example/v1', 'POLICY_API_KEY': 'tutorial-placeholder',
    'POLICY_MODEL_NAME': 'tutorial-model', 'OPENSANDBOX_DOMAIN': 'invalid.example',
    'OPENSANDBOX_API_KEY': 'tutorial-placeholder',
})
initial = OmegaConf.create({'config_paths': [str(root / 'native-hermes.yaml'), str(root / 'model-provider.yaml')]})
resolved = GlobalConfigDictParser().parse(GlobalConfigDictParserConfig(
    initial_global_config_dict=initial, skip_load_from_cli=True, skip_load_from_dotenv=True, offline=True,
))
cfg = OmegaConf.to_container(resolved, resolve=True)
environments = {k: list(v['environment_servers']) for k, v in cfg.items() if isinstance(v, dict) and 'environment_servers' in v}
assert environments == {'single_agent_turn': ['single_agent_turn']}
env_cfg = cfg['single_agent_turn']['environment_servers']['single_agent_turn']
SingleAgentTurnEnvironmentServerConfig.model_validate({"name": "single_agent_turn", **env_cfg})
assert env_cfg['agent_server']['name'] == 'hermes_agent'
assert env_cfg['resources_server']['name'] == 'swebench_pro_resources_server'
assert cfg['hermes_agent']['responses_api_agents']['hermes_agent']['model'] == 'tutorial-model'
assert cfg['hermes_agent']['responses_api_agents']['hermes_agent']['enabled_toolsets'] == ['terminal']
row = json.loads((args.evidence_root / 'request.json').read_text())
with tempfile.TemporaryDirectory(prefix='gym-typed-example-') as tmp:
    input_file, output_file = Path(tmp) / 'input.jsonl', Path(tmp) / 'native-request.json'
    input_file.write_text(json.dumps(row) + '\n')
    cmd = [sys.executable, str(root / 'prepare-native-request.py'), str(input_file), str(output_file),
           '--taskset', 'swebench_pro:tutorial-check', '--rollout-id', 'tutorial-check', '--attempt', '1']
    subprocess.run(cmd, check=True, capture_output=True, env={**os.environ, 'PYTHONPATH': str(args.source_root)})
    req = SingleAgentTurnRequest.model_validate_json(output_file.read_text())
    assert req.task.task_id.task_id == row['instance_id']
    assert req.episode_id.capture_key == 'tutorial-check-a1'
    assert req.task.task_input.responses_create_params.input
    expected = {k: v for k, v in row.items() if k not in {'responses_create_params', 'agent_ref', 'task_source', 'skills_ref'} and not k.startswith('_ng_')}
    assert req.task.task_input.task_data == expected
    assert not any(k.startswith('_ng_') for k in req.task.task_input.task_data)
    saved = json.loads((args.evidence_root / 'episode.json').read_text())
    good = SingleAgentTurnResponse.model_validate({'episode_id': req.episode_id, 'task_id': req.task.task_id, 'result': saved})
    bad = SingleAgentTurnResponse.model_validate({'episode_id': req.episode_id, 'task_id': req.task.task_id, 'failure': {'failure_reason': 'example only', 'terminal': True}})
    assert good.result.reward == 1 and bad.result is None
report = {
    'result': 'PASS', 'source_sha': '3ef478df1ee163134d32a3f291f0a9e5981d0e52',
    'checks': ['offline full config composition', 'one native Environment implementation and correct references',
               'native Environment config schema', 'copyable request script executed on saved real row',
               'typed request and attempt-qualified identity', 'all verifier fields preserved, routing removed',
               'typed success/failure response schemas'],
    'model_calls_made': 0, 'service_processes_started': 0,
    'scope': 'Static examples only; placeholder endpoints; no network/model execution or complete HTTP episode.',
}
(root / 'example-validation.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
