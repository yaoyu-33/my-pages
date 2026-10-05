# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Reject known private-location patterns in public assets and embedded downloads."""
import argparse
import base64
import io
import ipaddress
import json
from pathlib import Path
import re
import zipfile

PATTERNS = {
    'private_domain': r'gitlab-master\.nvidia\.com|linear\.app/nvidia|[\w.-]+\.cluster\.local',
    'machine_path': r'/(?:home|lustre|Users|mnt)/[^\s<>"\x27`]+',
    'cluster_label': r'\b(?:HSG|EOS|Lyris)\b',
    'signed_link': r'[?&](?:signature|access_token|auth_token)=',
}


def inspect_text(text: str, name: str) -> list[str]:
    findings = [name+':'+label for label, pattern in PATTERNS.items() if re.search(pattern, text)]
    for value in re.findall(r'(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])', text):
        try:
            ip = ipaddress.ip_address(value)
        except ValueError:
            continue
        if any(ip in ipaddress.ip_network(cidr) for cidr in ['10.0.0.0/8','172.16.0.0/12','192.168.0.0/16']):
            findings.append(name+':private_ip')
    for n, encoded in enumerate(re.findall(r'data:application/zip;base64,([A-Za-z0-9+/=]+)', text)):
        with zipfile.ZipFile(io.BytesIO(base64.b64decode(encoded))) as archive:
            for item in archive.namelist():
                findings.extend(inspect_text(archive.read(item).decode(),f'{name}:zip{n}/{item}'))
    return findings


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root', type=Path)
    args = p.parse_args()
    paths = [args.root/'README.md', args.root/'index.html']
    for folder in ['tutorial-source', 'tutorial-source-en']:
        paths += list((args.root/folder).glob('*'))
    paths += list((args.root/'gym-design-tutorial').rglob('*'))
    failures = []
    count = 0
    for path in paths:
        if not path.is_file() or path.suffix not in {'.md','.html','.json','.yaml','.py','.txt','.css','.js'}:
            continue
        failures.extend(inspect_text(path.read_text(),str(path.relative_to(args.root))))
        count += 1
    if failures:
        raise SystemExit(json.dumps(failures))
    print(json.dumps({'result':'PASS','files_checked':count,'embedded_zip_checked':True,
        'scope':'Current tree and embedded downloads; manual review is also required; Git history excluded.'}))


if __name__ == '__main__':
    main()
