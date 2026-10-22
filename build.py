#!/usr/bin/env python3
"""Build a static, phone-friendly single-file club website from verified LFL snapshots."""
import json, re, csv, html, argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ALIASES={'Макарена-Д':'Макарена Запад','Макарена Ультра':'Макарена Запад','Макарена Запад':'Макарена Запад','Макарена':'Макарена'}
FIELDS=['player_id','season','tournament','source_team','matches','goals','assists','source_url']

def read_seasons(path):
    if not path.exists():return []
    with path.open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if reader.fieldnames!=FIELDS:raise ValueError('Season CSV must use columns: '+','.join(FIELDS))
        out=[];seen=set()
        for row in reader:
            if not row['season'] or not row['tournament']:raise ValueError('Missing season or tournament')
            if row['source_team'] not in ALIASES:raise ValueError('Unrecognized team: '+row['source_team'])
            if not row['source_url'].startswith(('https://lfl.ru/','https://page.lfl.ru/')):raise ValueError('Not an LFL source URL')
            for k in ('player_id','matches','goals','assists'):
                if not row[k].isdigit() or int(row[k])<0:raise ValueError('Invalid '+k)
            if int(row['goals'])>int(row['matches'])*30 or int(row['assists'])>int(row['matches'])*30:raise ValueError('Suspicious season row')
            key=(row['player_id'],row['season'],row['tournament'],row['source_team'])
            if key in seen:raise ValueError('Duplicate season record: '+str(key))
            seen.add(key)
            row['canonical_team']=ALIASES[row['source_team']];out.append(row)
        return out

def build():
    player=json.loads((ROOT/'data/player_132559.json').read_text(encoding='utf-8'))
    if player['player_id']!=132559 or any(not isinstance(player['totals'].get(k),int) for k in ['matches','goals','assists','penalties']):raise ValueError('Bad player snapshot')
    seasons=[s for s in read_seasons(ROOT/'data/seasons.csv') if s['player_id']=='132559']
    page=(ROOT/'template.html').read_text(encoding='utf-8')
    numbers=[('matches','Матчи'),('goals','Голы'),('assists','Передачи'),('penalties','Наказания')]
    new_tiles='<div class="stats-grid">'+''.join(f'<div class="stat-tile"><b>{player["totals"][k]}</b><span>{label}</span></div>' for k,label in numbers)+'</div>'
    page,n=re.subn(r'<div class="stats-grid">.*?</div></div>',lambda m:new_tiles,page,count=1,flags=re.S)
    if n!=1:raise ValueError('Stats area in original site changed')
    alltotal=player['totals']
    page=page.replace('120 матчей · 0 голов · 2 передачи · 12 наказаний (сводка ЛФЛ).',f'{alltotal["matches"]} матчей · {alltotal["goals"]} голов · {alltotal["assists"]} передач · {alltotal["penalties"]} наказаний (сводка ЛФЛ).')
    status=('Последняя серверная проверка: '+html.escape(player.get('fetched_at') or player.get('snapshot_verified_on') or 'неизвестно')+'. ') if player.get('fetched_at') else 'Данные взяты из последнего сохранённого снимка ЛФЛ. '
    notice='<div class="notice">'+status+'Общие числа могут включать другие клубы и не равны статистике «Макарены Запад». Сезонные показатели добавляются только после подтверждения в ЛФЛ.</div>'
    page,n=re.subn(r'<div class="notice">Эти числа относятся.*?</div>',lambda m:notice,page,count=1,flags=re.S)
    if n!=1:raise ValueError('Status notice changed')
    if seasons:
        sections=[];links=[]
        for idx,s in enumerate(seasons):
            target='lfl-season-'+str(idx)
            links.append(f'<a href="#{target}">{html.escape(s["season"])} — {html.escape(s["tournament"])}</a>')
            sections.append(f'<div class="season-unit" id="{target}"><strong>{html.escape(s["season"])} · {html.escape(s["canonical_team"])}</strong><p>{html.escape(s["tournament"])} · {s["matches"]} матчей · {s["goals"]} голов · {s["assists"]} передач</p><p>Название в архиве: {html.escape(s["source_team"])} · <a href="{html.escape(s["source_url"],quote=True)}" target="_blank" rel="noopener noreferrer">Источник ЛФЛ ↗</a></p></div>')
        add='<h3>Подтверждённые сезонные записи ЛФЛ</h3><div class="profile-seasons">'+''.join(links)+'</div>'+''.join(sections)
        page=page.replace('<p class="profile-source">Источник:',add+'<p class="profile-source">Источник:',1)
    else:
        page=page.replace('Название «Макарена-Д» в архиве относится к команде «Макарена Запад».', 'Названия «Макарена-Д» и «Макарена Ультра» в архиве относятся к команде «Макарена Запад».',1)
    page=page.replace('<h3>Статистика по сезонам</h3>','<h3>Статистика по сезонам</h3><div class="notice">Сезонные данные ещё не импортированы. Переключатель ниже показывает достижения, но не результаты матчей по сезонам.</div>',1)
    (ROOT/'index.html').write_text(page,encoding='utf-8')
    return len(seasons)
if __name__=='__main__':
    print('Built index.html; verified season records:',build())
