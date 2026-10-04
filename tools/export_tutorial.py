# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Export the full workstation tutorial with navigation for the public project site."""

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source_directory', type=Path)
args = parser.parse_args()
source = (args.source_directory / 'index.html').read_bytes()
manifest = json.loads((args.source_directory / 'source-manifest.json').read_text())
sha = lambda data: hashlib.sha256(data).hexdigest()
assert sha(source) == manifest['html_sha256'], 'Source does not match its build manifest.'
html = source.decode()
replacements = {
    'href="/"': 'href="../"',
    'href="/architecture/"': 'href="http://10.111.115.167:8765/architecture/"',
    'href="/harness-handoff/"': 'href="http://10.111.115.167:8765/harness-handoff/"',
}
counts = {}
for before, after in replacements.items():
    counts[before] = html.count(before)
    assert counts[before] > 0, f'Expected navigation missing: {before}'
    html = html.replace(before, after)
# Verify that the only differences from the full source are the declared links.
roundtrip = html
for before, after in reversed(list(replacements.items())):
    roundtrip = roundtrip.replace(after, before)
assert roundtrip.encode() == source
output = ROOT / 'gym-design-tutorial' / 'index.html'
output.parent.mkdir(exist_ok=True)
output.write_text(html)
provenance = {
    'source_sha': manifest['source_sha'],
    'workstation_html_sha256': sha(source),
    'public_html_sha256': sha(html.encode()),
    'files_sha256': manifest['files_sha256'],
    'evidence_sha256': manifest['evidence_sha256'],
    'http_evidence_sha256': manifest['http_evidence_sha256'],
    'app_reading_steps': manifest['app_reading_steps'],
    'command_steps': manifest['command_steps'],
    'command_bundle_sha256': manifest['command_bundle_sha256'],
    'navigation_replacements': counts,
    'content_changes': 'None; only homepage and companion-page href targets changed.',
}
(ROOT / 'gym-design-tutorial' / 'provenance.json').write_text(
    json.dumps(provenance, ensure_ascii=False, indent=2) + '\n'
)
print(json.dumps({k: v for k, v in provenance.items() if k != 'files_sha256'}, ensure_ascii=False))
