#!/usr/bin/env python3
"""Safely refresh from public new LFL page then rebuild site. Never claim seasons fetched."""
import json, os, tempfile
from pathlib import Path
from sync_lfl import fetch
from build import build, ROOT
if __name__=='__main__':
    target=ROOT/'data/player_132559.json'
    try:
        updated=fetch(132559)
        with tempfile.NamedTemporaryFile('w',encoding='utf8',dir=target.parent,delete=False) as f:
            json.dump(updated,f,ensure_ascii=False,indent=2);tmp=f.name
        os.replace(tmp,target)
        print('LFL general totals refreshed')
    except Exception as exc:
        print('LFL not available; retaining verified snapshot:',exc)
    build()
