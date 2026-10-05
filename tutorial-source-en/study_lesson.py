# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Render anonymized lessons; private evidence mappings do not belong in this input."""
import html
import json
from pathlib import Path


def render(root: Path) -> str:
    cases = json.loads((root / 'run-log-lessons.json').read_text())
    esc = html.escape
    cards = []
    for case in cases:
        cards.append(f'''<article class="study-card" id="study-{case['id']}"><div class="kicker">Case {case['evidence_key']} · {esc(case['stage'])}</div><h3>{esc(case['title'])}</h3><p class="study-symptom">{esc(case['symptom'])}</p><dl><dt>What the records showed</dt><dd>{esc(case['evidence'])}</dd><dt>What to check next time</dt><dd>{esc(case['action'])}</dd><dt>Keep this distinction in mind</dt><dd>{esc(case['pitfall'])}</dd></dl><p class="sources"><a data-src="{case['source']}">Source code for the related mechanism</a></p></article>''')
    return (root / 'run-log-lessons.html').read_text().replace('@@STUDY_CARDS@@', '\n'.join(cards)).replace(
        '@@STUDY_JUMPS@@', ''.join(f'<a href="#study-{c["id"]}">{c["evidence_key"]} · {esc(c["stage"])}</a>' for c in cases)).replace(
        '@@STUDY_TEMPLATE@@', esc((root / 'run-log-template.txt').read_text()))
