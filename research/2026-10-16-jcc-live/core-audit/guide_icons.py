import re,json
from html import escape as E,unescape
from pathlib import Path
P=Path(__file__).resolve().parent
CSS='''
.hero-icon{width:22px;height:22px;object-fit:cover;vertical-align:-5px;margin-right:5px;border-radius:3px;display:inline-block;background:#e5ebe7}.equip-icon{width:16px;height:16px;object-fit:cover;vertical-align:-3px;margin-right:3px;border-radius:2px;display:inline-block;background:#e5ebe7}.equip-name{white-space:nowrap;display:inline-block}.hero h3{line-height:24px}.first-set{line-height:23px}.combo .items{line-height:24px}
'''
def decorate(html):
 cat=json.loads((P/'catalog.json').read_text())['data'];heroes={}
 for h in cat['hero']:
  if h.get('heroType')==0 and h.get('picture'):heroes.setdefault(h['name'],h['picture'])
 equips={x['name']:x['picture'] for x in cat['equip'] if x.get('picture')}
 def icon(url,cls,size):return '<img class="'+cls+'" src="'+E(url,quote=True)+'" width="'+str(size)+'" height="'+str(size)+'" alt="" decoding="async" referrerpolicy="no-referrer">'
 def hero(m):
  name=unescape(m.group(1));assert name in heroes,name
  return '<h3>'+icon(heroes[name],'hero-icon',22)+m.group(1)+' <span class="role">'
 html=re.sub(r'<h3>([^<]+) <span class="role">',hero,html)
 def item(m):
  name=unescape(m.group(1));assert name in equips,name
  return '<span class="equip-name">'+icon(equips[name],'equip-icon',16)+m.group(1)+'</span>'
 html=re.sub(r'<span class="equip-name">([^<]+)</span>',item,html)
 def combos(m):
  tokens=m.group(1).split(' ＋ ')
  return '<div class="items">'+' ＋ '.join('<span class="equip-name">'+icon(equips[unescape(n)],'equip-icon',16)+n+'</span>' for n in tokens)+'</div>'
 html=re.sub(r'<div class="items">([^<]+)</div>',combos,html)
 # The default row is already the first choice; remove its redundant tag to make room for icons.
 html=html.replace('<div class="first-set"><span class="tag">首选</span>','<div class="first-set">')
 html=re.sub(r'(<div class="first-set">)(.*?)(</div>)',lambda m:m[1]+m[2].replace(' ＋ ',' · ')+m[3],html,flags=re.S)
 return html.replace('</style>',CSS+'</style>',1)
