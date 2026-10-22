#!/usr/bin/env python3
"""Macarena: cautious LFL public-profile fetcher (stdlib only).
Run: python sync_lfl.py --player 132559 --out data.json
Does not bypass access restrictions or infer missing season records.
"""
import argparse, json, re, urllib.request, urllib.error
from html.parser import HTMLParser
from datetime import datetime, timezone
from pathlib import Path

class Text(HTMLParser):
    def __init__(self):
        super().__init__();self.parts=[];self.skip=0
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style'):self.skip+=1
        if tag in ('p','h1','h2','li','div','br'): self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in ('script','style') and self.skip:self.skip-=1
    def handle_data(self,data):
        if not self.skip:self.parts.append(data)

def parse_profile(html,player_id):
    p=Text();p.feed(html)
    t=' '.join(' '.join(p.parts).split())
    name=re.search(r'Пайтян Геворг Камоевич',t) if player_id==132559 else None
    if not name:
        headings=re.search(r'(?:Главная\s*>.*?)?([А-ЯЁ][а-яё-]+\s+[А-ЯЁ][а-яё-]+(?:\s+[А-ЯЁ][а-яё-]+)?)\s+Возраст',t)
        name=headings.group(1) if headings else None
    # Require explicit labels, never guess figures.
    values={}
    for key,label in [('matches','Матчи'),('goals','Голы'),('assists','Передачи'),('penalties','Наказания')]:
        found=re.search(r'(?<![А-Яа-яЁё])'+label+r'\s+(\d{1,6})(?!\d)',t)
        values[key]=int(found.group(1)) if found else None
    if not name or all(v is None for v in values.values()):
        raise ValueError('Player profile fields were not confidently found; no data overwritten')
    return {'player_id':player_id,'name':name,'totals':values,
            'seasons':[], 'season_status':'not_exposed_by_public_html',
            'source':f'https://page.lfl.ru/persons/{player_id}',
            'fetched_at':datetime.now(timezone.utc).isoformat(),
            'notes':'Totals are LFL-wide, not a sum for Macarena. No season stats inferred.'}

def fetch(player_id):
    url=f'https://page.lfl.ru/persons/{player_id}'
    request=urllib.request.Request(url,headers={'User-Agent':'MacarenaClubSite/0.1 (+public-profile fetch; contact site admin)', 'Accept':'text/html'})
    with urllib.request.urlopen(request,timeout=15) as response:
        if response.status!=200:raise RuntimeError(f'HTTP {response.status}')
        blob=response.read(2_000_000)
        charset=response.headers.get_content_charset() or 'utf-8'
    return parse_profile(blob.decode(charset,errors='replace'),player_id)

def main():
    a=argparse.ArgumentParser();a.add_argument('--player',type=int,default=132559);a.add_argument('--out',default='data.json');opts=a.parse_args()
    if opts.player<1:raise SystemExit('Invalid player ID')
    try:
        result=fetch(opts.player)
    except (urllib.error.URLError,ValueError,RuntimeError) as exc:
        print('SYNC FAILED:',str(exc),'— existing data not overwritten')
        return 1
    Path(opts.out).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print('OK: general profile stats saved; season stats not claimed:',opts.out)
    return 0
if __name__=='__main__':raise SystemExit(main())
