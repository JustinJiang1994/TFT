#!/usr/bin/env python3
"""Validate the self-contained release using the Python standard library."""
import json
import re
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.ids = set()
        self.links = []
        self.feed(path.read_text(encoding='utf-8'))
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            assert attrs['id'] not in self.ids, f"Duplicate ID: {attrs['id']}"
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if attrs.get(key):
                self.links.append(attrs[key])

pages = {name: Page(ROOT / name) for name in ('index.html', 'equipment.html', 'assistant.html', 'versions.html')}
for name, page in pages.items():
    for link in page.links:
        url = urlsplit(link)
        if url.scheme or url.netloc:
            continue
        target = unquote(url.path) or name
        assert (ROOT / target).is_file(), f'{name}: missing {target}'
        if url.fragment and target in pages:
            assert unquote(url.fragment) in pages[target].ids, f'{name}: missing anchor {link}'
    text = (ROOT / name).read_text(encoding='utf-8')
    assert 'file:///Users/' not in text, f'{name}: local absolute link'
    for payload in re.findall(r'<script[^>]*type=["\']application/json["\'][^>]*>(.*?)</script>', text, re.S):
        json.loads(payload)
assert len([i for i in pages['index.html'].ids if re.fullmatch(r'c\d+', i)]) == 21
files = list((ROOT / 'data').rglob('*.json'))
for path in files:
    json.loads(path.read_text(encoding='utf-8'))
assert (ROOT / 'skills/metatft-guide/SKILL.md').is_file()
with zipfile.ZipFile(ROOT / 'downloads/metatft-guide-skill.zip') as archive:
    assert archive.testzip() is None
    assert 'metatft-guide/SKILL.md' in archive.namelist()
for path in ROOT.rglob('*'):
    if path.is_file() and '.git' not in path.parts:
        assert path.stat().st_size < 100 * 1024 * 1024, f'File exceeds GitHub limit: {path}'
print(f'PASS: 4 pages, 21 compositions, {len(files)} JSON files, local links and Skill archive.')
