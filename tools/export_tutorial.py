# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Publish a tutorial built from privacy-reviewed public inputs."""
import argparse
import hashlib
import json
from pathlib import Path
from check_public_content import inspect_text

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('source_directory', type=Path)
a = p.parse_args()
source = (a.source_directory/'index.html').read_bytes()
manifest = json.loads((a.source_directory/'source-manifest.json').read_text())
sha = lambda value: hashlib.sha256(value).hexdigest()
assert sha(source) == manifest['html_sha256']
html = source.decode()
assert not inspect_text(html,'tutorial'), 'Private source detected: prepare and review public inputs before exporting.'
assert 'id="publication-note"' in html
count = html.count('href="/"')
assert count == 3
public = html.replace('href="/"','href="../"')
assert public.replace('href="../"','href="/"').encode() == source
(ROOT/'gym-design-tutorial/index.html').write_text(public)
provenance = {
    'source_sha':manifest['source_sha'],
    'public_source_html_sha256':sha(source),
    'public_html_sha256':sha(public.encode()),
    'files_sha256':manifest['files_sha256'],
    'public_evidence_sha256':manifest['evidence_sha256'],
    'http_evidence_sha256':manifest['http_evidence_sha256'],
    'app_reading_steps':manifest['app_reading_steps'],
    'command_steps':manifest['command_steps'],
    'study_cases':manifest['study_cases'],
    'learning_questions':manifest['learning_questions'],
    'async_mini_script_sha256':manifest['async_mini_script_sha256'],
    'command_bundle_sha256':manifest['command_bundle_sha256'],
    'navigation_replacements':{'href="/"':count},
    'content_changes':'Private artifact locations and internal reference URLs omitted from public inputs; see tutorial-source/public-redactions.json. Export only changes three homepage hrefs.',
    'history_scope':'Current branch content only; older public commits are not rewritten.',
}
(ROOT/'gym-design-tutorial/provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
print(json.dumps({k:v for k,v in provenance.items() if k!='files_sha256'}))
