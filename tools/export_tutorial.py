# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Export a standalone language edition from privacy-reviewed public inputs."""
import argparse
import hashlib
import json
from pathlib import Path
from check_public_content import inspect_text

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('source_directory', type=Path)
p.add_argument('--language', choices=['zh-CN', 'en'], default='zh-CN')
a = p.parse_args()
source = (a.source_directory/'index.html').read_bytes()
manifest = json.loads((a.source_directory/'source-manifest.json').read_text())
sha = lambda value: hashlib.sha256(value).hexdigest()
assert sha(source) == manifest['html_sha256']
html = source.decode()
assert not inspect_text(html, 'tutorial'), 'Private source detected: prepare and review public inputs before exporting.'
assert 'id="publication-note"' in html
assert f'<html lang="{a.language}">' in html
count = html.count('href="/"')
assert count == 3
english = a.language == 'en'
home = '../../' if english else '../'
public = html.replace('href="/"', f'href="{home}"')
assert public.replace(f'href="{home}"', 'href="/"').encode() == source
links = [('zh-CN', '中文', '../' if english else './'), ('en', 'English', './' if english else './en/')]
nav = '<nav class="language-switch" aria-label="Language">' + ''.join(
    f'<a data-language="{lang}" lang="{lang}" hreflang="{lang}" href="{href}"'
    + (' aria-current="page"' if lang == a.language else '') + f'>{label}</a>'
    for lang, label, href in links) + '</nav>'
style = '<style>.language-switch{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 24px;font-size:14px}.language-switch a{padding:5px 14px;border:1px solid var(--line);border-radius:20px;text-decoration:none}.language-switch a[aria-current=page]{background:var(--green);color:white}@media print{.language-switch{display:none}}</style>'
script = '''<script>(function(){const links=[...document.querySelectorAll('[data-language]')];const bases=links.map(a=>a.getAttribute('href'));function sync(){links.forEach((a,i)=>a.setAttribute('href',bases[i]+location.hash));}addEventListener('hashchange',sync);sync();})();</script>'''
assert public.count('<main>') == 1 and public.count('</body>') == 1
public = public.replace('<main>', '<main>\n'+nav, 1).replace('</head>', style+'</head>', 1).replace('</body>', script+'</body>', 1)
destination = ROOT/'gym-design-tutorial'/('en' if english else '')
destination.mkdir(parents=True, exist_ok=True)
(destination/'index.html').write_text(public)
provenance = {
    'language': a.language,
    'interactions': manifest['interactions'],
    'source_sha': manifest['source_sha'],
    'public_source_html_sha256': sha(source),
    'public_html_sha256': sha(public.encode()),
    'files_sha256': manifest['files_sha256'],
    'public_evidence_sha256': manifest['evidence_sha256'],
    'http_evidence_sha256': manifest['http_evidence_sha256'],
    'app_reading_steps': manifest['app_reading_steps'],
    'command_steps': manifest['command_steps'],
    'study_cases': manifest['study_cases'],
    'learning_questions': manifest['learning_questions'],
    'async_mini_script_sha256': manifest['async_mini_script_sha256'],
    'command_bundle_sha256': manifest['command_bundle_sha256'],
    'navigation_replacements': {'href="/"': count, 'home_target': home},
    'content_changes': 'Built from reviewed public inputs; export adjusts three homepage links and adds a language switch that preserves the current section.',
    'history_scope': 'Current branch content only; older public commits are not rewritten.',
}
(destination/'provenance.json').write_text(json.dumps(provenance, indent=2)+'\n')
print(json.dumps({k:v for k,v in provenance.items() if k != 'files_sha256'}))
