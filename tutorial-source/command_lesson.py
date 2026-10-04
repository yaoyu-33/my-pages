# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Render the chapter-six command guide and its self-contained download."""
import base64
import hashlib
import html
import io
import json
import zipfile
from pathlib import Path


def render(root: Path, source: Path) -> str:
    esc = html.escape
    steps = json.loads((root / 'benchmark-lab.json').read_text())
    files = {name: (root / name).read_text() for name in (
        'native-hermes.yaml', 'model-provider.yaml', 'lab.yaml', 'prepare-tutorial-tasks.py')}
    files['README.md'] = '# Gym native benchmark lab\n\nTeaching source: 3ef478df1ee163134d32a3f291f0a9e5981d0e52.\n\nConfiguration, conversion and Collector planning checked offline. No new model rollout.\nExtract tutorial-lab/ under a full pinned Gym checkout. Run shell snippets in Bash.\n\n' + '\n\n'.join(
        f"## {i}. {s['title']}\n\n{s['label']}\n\n{s['text']}\n\n```bash\n{s['command']}\n```\n\n{s['expect']}" for i, s in enumerate(steps, 1))
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, body in files.items():
            entry = zipfile.ZipInfo('tutorial-lab/' + name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            archive.writestr(entry, body)
    bundle = stream.getvalue()
    (root / 'gym-benchmark-lab.zip').write_bytes(bundle)
    result = (root / 'benchmark-lab.html').read_text()
    cards = []
    for i, s in enumerate(steps, 1):
        path, start, end = s['source']
        lines = (source / path).read_text().splitlines()
        assert 1 <= start <= end <= len(lines)
        numbered = '\n'.join(f'{n:>4}  {lines[n-1]}'.rstrip() for n in range(start, end+1))
        cards.append(f'''<article class="command-step" id="command-{s['id']}">
<div class="command-title"><span class="command-number">{i:02}</span><div><div class="kicker">{esc(s['label'])}</div><h4>{esc(s['title'])}</h4></div></div>
<p>{esc(s['text'])}</p><div class="splitline"><span class="small">COMMAND · Bash</span><button class="copy" data-copy="command-code-{i}">复制</button></div>
<pre><code class="lab-shell" id="command-code-{i}">{esc(s['command'])}</code></pre>
<div class="command-expect"><b>看到什么才算这一步完成？</b><p>{esc(s['expect'])}</p></div>
<details><summary>一起看源码：{esc(path)} · L{start}–{end}</summary><p>{esc(s['code_note'])}</p>
<pre><code class="lab-source" data-file="{esc(path)}" data-start="{start}" data-end="{end}">{esc(numbered)}</code></pre>
<p class="sources"><a data-src="{esc(path)}" data-line="{start}">打开固定版本的完整文件</a></p></details></article>''')
    configs = ''.join(f'<details><summary>{name} · {label}</summary><div class="splitline"><span class="small">解压后路径：tutorial-lab/{name}</span><button class="copy" data-copy="lab-file-{i}">复制</button></div><pre><code id="lab-file-{i}">{esc(files[name])}</code></pre></details>' for i, (name, label) in enumerate([
        ('native-hermes.yaml', '连接 Environment / Resources / Hermes'),
        ('model-provider.yaml', '连接模型和 OpenSandbox'),
        ('lab.yaml', '可达地址、Head、单题并发'),
        ('prepare-tutorial-tasks.py', '把 prepared rows 变成原生 tasks'),
    ]))
    return result.replace('@@COMMAND_STEPS@@', '\n'.join(cards)).replace('@@COMMAND_CONFIGS@@', configs).replace('@@COMMAND_JUMPS@@', ''.join(
        f'<a href="#command-{s["id"]}">{i} · {esc(s["title"].split("，")[0])}</a>' for i, s in enumerate(steps, 1))).replace('@@COMMAND_BUNDLE@@', base64.b64encode(bundle).decode()).replace('@@COMMAND_BUNDLE_SHA@@', hashlib.sha256(bundle).hexdigest())
