# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Check technical parity between built Chinese and English tutorial editions.

This checks stable identifiers, source references, evidence and executable
examples. Language quality and equivalence of prose need independent review.
"""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import zipfile


class Page(HTMLParser):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.ids = []
        self.sources = []
        self.controls = []
        self.lang = None
        self.feed(text)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == 'html':
            self.lang = values.get('lang')
        if values.get('id'):
            self.ids.append(values['id'])
        if values.get('data-src'):
            self.sources.append((values['data-src'], values.get('data-line')))
        # Mermaid edge coordinates depend on translated label widths; IDs and edges still match.
        stable = tuple(sorted((key, value) for key, value in attrs if key.startswith('data-') and key != 'data-points'))
        if stable:
            self.controls.append((tag, stable))


def read(root: Path, name: str):
    return json.loads((root/name).read_text())


def normalized_command(command: str) -> str:
    # Shell comments and illustrative placeholder descriptions are localized.
    lines = [line for line in command.splitlines() if not line.lstrip().startswith('#')]
    return re.sub(r'<[^>\n]+>', '<PLACEHOLDER>', '\n'.join(lines)).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path, help='Public repository root')
    args = parser.parse_args()
    zh, en = (args.root/name for name in ['tutorial-source', 'tutorial-source-en'])
    manifests = [read(p, 'source-manifest.json') for p in [zh, en]]
    for key in ['source_sha','files_sha256','evidence_sha256','http_evidence_sha256',
                'async_mini_script_sha256','app_reading_steps','command_steps','study_cases','learning_questions']:
        assert manifests[0][key] == manifests[1][key], key
    assert manifests[0]['interactions']['source'] == manifests[1]['interactions']['source']
    for folder, manifest in zip([zh, en], manifests):
        for name, expected in manifest['interactions']['assets_sha256'].items():
            assert hashlib.sha256((folder/name).read_bytes()).hexdigest() == expected, name
    for name in ['native-evidence.json','weather-http-evidence.json','async-mini-evidence.json',
                 'evidence.json','command-validation.json','example-validation.json',
                 'native-hermes.yaml','model-provider.yaml','lab.yaml','prepare-tutorial-tasks.py',
                 'prepare-native-request.py','async-mini-lab.py','weather-lab.py']:
        assert (zh/name).read_bytes() == (en/name).read_bytes(), name
    for filename, fields in [
        ('learning-guide.json', ['id','answer','anchor']),
        ('run-log-lessons.json', ['id','evidence_key','source']),
        ('benchmark-lab.json', ['id','source']),
    ]:
        left, right = read(zh, filename), read(en, filename)
        assert len(left) == len(right), filename
        for a, b in zip(left, right):
            assert a.keys() == b.keys(), (filename, 'fields')
            for key in fields:
                assert a[key] == b[key], (filename, a['id'], key)
            if 'options' in a:
                assert len(a['options']) == len(b['options'])
            if 'command' in a:
                assert normalized_command(a['command']) == normalized_command(b['command']), (a['id'], 'command')
    left, right = read(zh, 'app-walkthrough.json'), read(en, 'app-walkthrough.json')
    assert len(left) == len(right)
    for a, b in zip(left, right):
        assert a['id'] == b['id'] and len(a['steps']) == len(b['steps'])
        for x, y in zip(a['steps'], b['steps']):
            for key in ['file','start','end','focus']:
                assert x[key] == y[key], (a['id'], key)
    with zipfile.ZipFile(zh/'gym-benchmark-lab.zip') as a, zipfile.ZipFile(en/'gym-benchmark-lab.zip') as b:
        assert a.namelist() == b.namelist()
        for name in a.namelist():
            if name != 'tutorial-lab/README.md':
                assert a.read(name) == b.read(name), name
    pages = [Page((p/'index.html').read_text()) for p in [zh, en]]
    assert [p.lang for p in pages] == ['zh-CN', 'en']
    for field in ['ids', 'sources', 'controls']:
        assert getattr(pages[0],field) == getattr(pages[1],field), field
    assert len(set(pages[0].ids)) == len(pages[0].ids)
    for source, folder in [(zh,args.root/'gym-design-tutorial'), (en,args.root/'gym-design-tutorial/en')]:
        provenance = read(folder,'provenance.json')
        assert hashlib.sha256((folder/'index.html').read_bytes()).hexdigest() == provenance['public_html_sha256']
        assert hashlib.sha256((source/'index.html').read_bytes()).hexdigest() == provenance['public_source_html_sha256']
    print(json.dumps({'result':'PASS','source_links':len(pages[0].sources),'shared_ids':len(pages[0].ids),
                      'source_files':len(manifests[0]['files_sha256']),
                      'zip_scope':'Four code/config files identical; README localized',
                      'command_scope':'Executable text equal after removing full-line comments and normalizing illustrative placeholders',
                      'scope':'Technical parity; prose quality requires independent review.'}))


if __name__ == '__main__':
    main()
