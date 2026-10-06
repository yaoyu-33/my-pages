# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Copy explicit tutorial inputs into the public tree, removing private locations.

Review new study text manually. Pattern checks are a backstop, not a guarantee
that arbitrary private logs are suitable for publication. Never copy raw logs.
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUTS = (
    'app-reading.css', 'app-reading.html', 'app-reading.js', 'app-walkthrough.json',
    'benchmark-lab.html', 'benchmark-lab.json', 'build.py', 'command-validation.json',
    'command_lesson.py', 'diagrams.html', 'evidence.json', 'example-validation.json',
    'illustrated.css', 'illustrated.js', 'index.template.html', 'lab.yaml',
    'model-provider.yaml', 'native-evidence.json', 'native-hermes.yaml',
    'prepare-native-request.py', 'prepare-tutorial-tasks.py', 'repo-chapters.html',
    'validate-command-lab.py', 'validate_examples.py', 'verify-weather-lab.py',
    'weather-http-evidence.json', 'weather-lab.py',
    'learning-guide.html', 'learning-guide.json', 'learning-guide.css', 'learning-guide.js',
    'learning_guide.py', 'async-mini-lab.py', 'async-mini-evidence.json',
    'interaction-architecture.mmd', 'interaction-architecture.svg', 'interaction-guide.css', 'interaction-guide.html', 'interaction-guide.js', 'interaction-mermaid.json', 'interaction-sequence.mmd', 'interaction-sequence.svg', 'interaction-source.json', 'interaction_guide.py',
    'run-log-lessons.html', 'run-log-lessons.json', 'run-log-template.txt', 'study_lesson.py',
)
PRIVATE_URL = re.compile(
    r'https?://(?:10\.[^/\s<>"\x27]+|192\.168\.[^/\s<>"\x27]+|'
    r'172\.(?:1[6-9]|2\d|3[01])\.[^/\s<>"\x27]+|'
    r'[^/\s<>"\x27]*(?:gitlab-master\.nvidia\.com|cluster\.local)|linear\.app/nvidia)'
    r'[^\s<>"\x27]*'
)
PRIVATE_PATH = re.compile(r'/(?:home|lustre|Users|mnt)/[^\s<>"\x27`]+')


def sanitize(text: str) -> tuple[str, dict[str, int]]:
    counts = {}
    text, counts['board_links'] = re.subn(r'href="@@BOARD@@[^\"]*"', 'href="#publication-note"', text)
    text, counts['companion_links'] = re.subn(r'href="/(?:architecture|harness-handoff)/"', 'href="#publication-note"', text)
    text, counts['private_urls'] = PRIVATE_URL.subn('#publication-note', text)
    text, counts['private_paths'] = PRIVATE_PATH.subn('[private artifact location omitted]', text)
    return text, {k:v for k,v in counts.items() if v}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('private_source', type=Path)
    args = parser.parse_args()
    reports = {}
    for name in INPUTS:
        text, counts = sanitize((args.private_source / name).read_text())
        if name.endswith('.json'):
            json.loads(text)
        (ROOT / 'tutorial-source' / name).write_text(text)
        if counts:
            reports[name] = counts
    (ROOT/'tutorial-source/public-redactions.json').write_text(json.dumps({
        'scope': 'Current published tree only; historical Git objects are not rewritten.',
        'policy': 'No private cluster/host addresses, private evidence URLs or machine artifact paths.',
        'redactions': reports,
        'retained': 'Task/test evidence, public source pins, original results and explicit limits; no raw logs added.',
    }, indent=2)+'\n')
    print(json.dumps({'inputs':len(INPUTS),'files_redacted':len(reports)}))


if __name__ == '__main__':
    main()
