# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Add original learner exercises without changing historical evidence."""
import html
import json
import re
from pathlib import Path


def enhance(template: str, root: Path) -> str:
    chunks = re.split(r'<!-- SLOT: (\w+) -->', (root / 'learning-guide.html').read_text())
    blocks = dict(zip(chunks[1::2], chunks[2::2]))
    questions = json.loads((root / 'learning-guide.json').read_text())
    def question(item: dict) -> str:
        options = ''.join(f'<button type="button" data-choice="{i}" aria-pressed="false">{html.escape(label)}</button>' for i, label in enumerate(item['options']))
        return f'<fieldset class="learn-question" id="question-{item["id"]}" data-question="{item["id"]}"><legend>{html.escape(item["prompt"])}</legend><div class="learn-options">{options}</div><div class="learn-feedback" hidden aria-live="polite"></div><details class="learn-answer"><summary>Want to check? Show the answer</summary><p><strong>Correct answer: {html.escape(item["options"][item["answer"]])}</strong></p><p>{html.escape(item["feedback"])}</p><a href="#{item["anchor"]}">Back to the example →</a></details><div class="learn-print-answer"><p><strong>Correct answer: {html.escape(item["options"][item["answer"]])}</strong></p><p>{html.escape(item["feedback"])}</p></div></fieldset>'
    blocks['config'] = blocks['config'].replace('@@CONFIG_QUESTION@@', question(questions[0]))
    blocks['reading'] = blocks['reading'].replace('@@PRACTICE_QUESTIONS@@', ''.join(question(q) for q in questions[1:]))
    blocks['async_lab'] = blocks['async_lab'].replace('@@ASYNC_MINI_SOURCE@@', html.escape((root/'async-mini-lab.py').read_text()))
    assert template.count('@@LEARNING_ROUTES@@') == 1, 'learning routes'
    template = template.replace('@@LEARNING_ROUTES@@', blocks['goals'], 1)
    template = template.replace('<div id="benchmark-lab"', blocks['config']+'<div id="benchmark-lab"', 1)
    for section, block in [('tiny','wire'),('async','async_lab'),('contracts','identity'),('reading','reading')]:
        tag = 'header' if section == 'intro' else 'section'
        pattern = rf'(<{tag}\b[^>]*id="{section}".*?)(</{tag}>)'
        template, count = re.subn(pattern, lambda m: m[1]+blocks[block]+m[2], template, count=1, flags=re.S)
        assert count == 1, section
    data = json.dumps(questions,ensure_ascii=False).replace('<','\\u003c')
    assets = '<style>'+(root/'learning-guide.css').read_text()+'</style>'
    assets += '<script type="application/json" id="learning-data">'+data+'</script>'
    assets += '<script>'+(root/'learning-guide.js').read_text()+'</script>'
    return template.replace('</body>', assets+'</body>')
