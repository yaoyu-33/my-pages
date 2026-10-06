# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Embed pre-rendered PR interaction diagrams and their accessible reading guides."""
import base64
import hashlib
import html
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET


def enhance(template: str, root: Path) -> tuple[str, dict]:
    rendered = (root / "interaction-guide.html").read_text()
    metadata = json.loads((root / "interaction-source.json").read_text())
    assets = {}
    for kind in ("architecture", "sequence"):
        for suffix, mime in (("svg", "image/svg+xml"), ("mmd", "text/plain")):
            path = root / f"interaction-{kind}.{suffix}"
            raw = path.read_bytes()
            assets[path.name] = hashlib.sha256(raw).hexdigest()
            text = raw.decode()
            if suffix == "svg":
                document = ET.fromstring(text)
                assert document.tag == "{http://www.w3.org/2000/svg}svg"
                assert not re.search(r"<(?:script|foreignObject)\b|(?:href|src)=[\"']https?://", text)
                text = text.replace('role="graphics-document document"', f'role="img" aria-labelledby="interaction-{kind}-caption"', 1)
                text = re.sub(r"^<\?xml[^>]*>\s*", "", text)
            else:
                text = html.escape(text)
            rendered = rendered.replace(f"@@{kind.upper()}_{suffix.upper()}@@", text)
            url = f"data:{mime};base64," + base64.b64encode(raw).decode()
            rendered = rendered.replace(f"@@{kind.upper()}_{suffix.upper()}_URL@@", url)
    sections = re.split(r"<!-- INTERACTION: (\w+) -->", rendered)
    for kind, markup in zip(sections[1::2], sections[2::2]):
        marker = f"@@INTERACTION_{kind.upper()}@@"
        assert template.count(marker) == 1, marker
        template = template.replace(marker, markup.strip())
    template = template.replace("</head>", "<style>" + (root / "interaction-guide.css").read_text() + "</style></head>", 1)
    template = template.replace("</body>", "<script>" + (root / "interaction-guide.js").read_text() + "</script></body>", 1)
    return template, {"source": metadata, "assets_sha256": assets}
