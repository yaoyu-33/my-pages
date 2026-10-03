# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Build the standalone tutorial from the inspected source and compact evidence."""

import argparse
import hashlib
import html
import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--source-root', type=Path, default=Path('/private/tmp/gym-tutorial-source'))
args = parser.parse_args()
SOURCE = args.source_root
SHA = '3ef478df1ee163134d32a3f291f0a9e5981d0e52'
evidence = json.loads((ROOT / 'native-evidence.json').read_text())
summary = {
    'tutorial_source_sha': SHA,
    'review_date': '2026-10-02 America/Los_Angeles',
    'audit': evidence['audit'],
    'selection': evidence['selection'],
    'independent_checks': evidence['checks'],
    'image_digest': evidence['image_digest'],
    'base_commit': evidence['base_commit'],
    'tests': evidence['tests'],
    'scope': evidence['scope'],
    'source_files_sha256': evidence['source_files_sha256'],
    'artifact_hashes': evidence['artifact_hashes'],
    'cleanup_saved_receipt': evidence['cleanup_saved_receipt'],
}
hermes_lines = (SOURCE / 'responses_api_agents/hermes_agent/app.py').read_text().splitlines()
snippet = '\n'.join(hermes_lines[1079:1105])
source_manifest = {}
import re

template = (ROOT / 'index.template.html').read_text()
repo_front, repo_middle = (ROOT / 'repo-chapters.html').read_text().split('<!-- INSERT_AFTER_ASYNC -->')
template = template.replace('@@REPO_FRONT@@', repo_front).replace('@@REPO_MIDDLE@@', repo_middle)
parts = re.split(r'<!-- SLOT: (\w+) -->', (ROOT / 'diagrams.html').read_text())
for name, markup in zip(parts[1::2], parts[2::2]):
    template = template.replace('@@DIAGRAM_' + name.upper() + '@@', markup.strip())
template = template.replace('@@ILLUSTRATED_CSS@@', (ROOT / 'illustrated.css').read_text())
template = template.replace('@@ILLUSTRATED_JS@@', (ROOT / 'illustrated.js').read_text())
for path in sorted(set(re.findall(r'data-src="([^"]+)"', template))):
    p = SOURCE / path
    if not p.is_file():
        raise ValueError(f'Missing cited source: {path}')
    source_manifest[path] = hashlib.sha256(p.read_bytes()).hexdigest()
for path, line in re.findall(r'data-src="([^"]+)" data-line="(\d+)"', template):
    assert int(line) <= len((SOURCE / path).read_text().splitlines()), (path, line)
replacements = {
    'SHA': SHA,
    'BOARD': 'https://gitlab-master.nvidia.com/yuya/how-to-run/-/blob/main',
    'ACTIVATION_SNIPPET': html.escape(snippet),
    'WEATHER_TOOL': html.escape(textwrap.dedent('\n'.join((SOURCE / 'resources_servers/example_single_tool_call/app.py').read_text().splitlines()[60:62]))),
    'WEATHER_VERIFY': html.escape(textwrap.dedent('\n'.join((SOURCE / 'resources_servers/example_single_tool_call/app.py').read_text().splitlines()[42:47]))),
    'PATCH': html.escape(evidence['patch']),
    'TOOL_EXCERPT': html.escape(json.dumps(evidence['tools'][:4], ensure_ascii=False, indent=2)),
    'TESTS': html.escape(json.dumps(evidence['tests'], ensure_ascii=False, indent=2)),
    'NATIVE_YAML': html.escape((ROOT / 'native-hermes.yaml').read_text()),
    'REQUEST_SCRIPT': html.escape((ROOT / 'prepare-native-request.py').read_text()),
    'EVIDENCE_SUMMARY': html.escape(json.dumps({
        'run': evidence['audit'],
        'instance_id': evidence['audit']['instance_id'],
        'image_digest': evidence['image_digest'],
        'candidate_patch_sha256': evidence['audit']['patch_sha256'],
        'artifact_directory': evidence['source_path'],
        'checks_reperformed': evidence['checks'],
    }, ensure_ascii=False, indent=2)),
    'EVIDENCE_JSON': json.dumps(summary, ensure_ascii=False, indent=2).replace('<', '\\u003c'),
}
for key, value in replacements.items():
    template = template.replace('@@' + key + '@@', value)
assert not re.search(r'@@\w+@@', template)
(ROOT / 'index.html').write_text(template)
(ROOT / 'source-manifest.json').write_text(json.dumps({
    'source_sha': SHA, 'files_sha256': source_manifest,
    'html_sha256': hashlib.sha256(template.encode()).hexdigest(),
    'evidence_sha256': hashlib.sha256((ROOT / 'native-evidence.json').read_bytes()).hexdigest(),
}, indent=2) + '\n')
print(f'Built {len(template.encode()):,} bytes; {len(source_manifest)} pinned source files checked.')
