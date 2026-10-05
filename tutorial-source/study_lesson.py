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
        cards.append(f'''<article class="study-card" id="study-{case['id']}"><div class="kicker">案例 {case['evidence_key']} · {esc(case['stage'])}</div><h3>{esc(case['title'])}</h3><p class="study-symptom">{esc(case['symptom'])}</p><dl><dt>记录里观察到什么</dt><dd>{esc(case['evidence'])}</dd><dt>下次具体查什么</dt><dd>{esc(case['action'])}</dd><dt>要分清的几种情况</dt><dd>{esc(case['pitfall'])}</dd></dl><p class="sources"><a data-src="{case['source']}">同类机制的源码入口</a></p></article>''')
    return (root / 'run-log-lessons.html').read_text().replace('@@STUDY_CARDS@@', '\n'.join(cards)).replace(
        '@@STUDY_JUMPS@@', ''.join(f'<a href="#study-{c["id"]}">{c["evidence_key"]} · {esc(c["stage"])}</a>' for c in cases)).replace(
        '@@STUDY_TEMPLATE@@', esc((root / 'run-log-template.txt').read_text()))
