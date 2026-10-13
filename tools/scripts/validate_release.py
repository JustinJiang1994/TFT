#!/usr/bin/env python3
"""Validate the self-contained release using the Python standard library."""
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]

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

page_paths = list(ROOT.glob('*.html')) + [p for p in (ROOT / 'games').rglob('*.html') if '/raw/' not in str(p) and '/research/' not in str(p)] + list((ROOT/'tools/archive/research').glob('*.html'))
pages = {str(p.relative_to(ROOT)): Page(p) for p in page_paths}
for name, page in pages.items():
    for link in page.links:
        url = urlsplit(link)
        if url.scheme or url.netloc:
            continue
        target = str(((ROOT / name).parent / unquote(url.path)).resolve().relative_to(ROOT)) if url.path else name
        assert (ROOT / target).is_file(), f'{name}: missing {target}'
        if url.fragment and target in pages:
            assert unquote(url.fragment) in pages[target].ids, f'{name}: missing anchor {link}'
    text = (ROOT / name).read_text(encoding='utf-8')
    assert 'file:///Users/' not in text, f'{name}: local absolute link'
    for payload in re.findall(r'<script[^>]*type=["\']application/json["\'][^>]*>(.*?)</script>', text, re.S):
        json.loads(payload)
catalog = json.loads((ROOT / 'games/jcc/releases.json').read_text())
active = next(r for r in catalog['releases'] if r['id'] == catalog['active'])
knowledge = json.loads((ROOT / active['knowledge']).read_text())
assert {i for i in pages[active['path']].ids if i.startswith('comp-')} == {'comp-' + c['id'] for c in knowledge['comps']}
assert len([i for i in pages['games/tft/set18/18.4b/index.html'].ids if re.fullmatch(r'c\d+', i)]) == 21
files = list((ROOT / 'games').rglob('*.json')) + list((ROOT / 'tools/archive').rglob('*.json'))
for path in files:
    json.loads(path.read_text(encoding='utf-8'))
for path in ROOT.rglob('*'):
    if path.is_file() and '.git' not in path.parts:
        assert path.stat().st_size < 100 * 1024 * 1024, f'File exceeds GitHub limit: {path}'
print(f'PASS: {len(pages)} pages, {len(knowledge["comps"])} current compositions, historical 21 retained, {len(files)} JSON files, local links.')
