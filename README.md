# FC Macarena — website + cautious LFL sync

`index.html` opens **on iPhone even if JavaScript is disabled**. Club ID 2272 is Macarena; club ID 9037 is Macarena Zapad (older names Macarena-D and Macarena Ultra). Historic aliases are not separate clubs.

## Files
- `index.html`: ready-to-open static site (generated from `template.html`)
- `sync_lfl.py`: general-profile extractor from https://page.lfl.ru/persons/132559
- `update.py`: tries server fetch, preserves the last snapshot if unavailable, builds site
- `build.py`: builds index with verified data, strict season CSV validation
- `data/player_132559.json`: clearly labelled LFL general career snapshot
- `data/seasons.csv`: currently **header only**: seasonal data is not yet accessible through a confirmed endpoint
- `.github/workflows/update.yml`: optional GitHub Actions daily update when repository is uploaded to GitHub and workflow runs

## Run on computer or server
```
python3 build.py
python3 update.py
```
No Python packages needed. The automatic update cannot run inside a local HTML file on an iPhone. After uploading this folder to GitHub, Actions can try updating daily and commit results; availability, policy and page structure can prevent updates. Publishing the repo via a static hosting service is a separate step.

## Import verified historical seasons
Only add rows to `data/seasons.csv` copied **from LFL** with original LFL URLs; columns must be `player_id,season,tournament,source_team,matches,goals,assists,source_url`. No fabricated records or other leagues. Example *format only*, **not real data**:
```
# no example values: retain header until actual records are verified
```
Build fails if numeric values are invalid, a team alias is unknown, source isn't LFL, or a record is duplicated. Data shown in the original v5 season tabs may represent *awards*, not season appearance statistics.

## Remaining limitation
Public HTML for the new LFL profile yields general counters but not detailed seasonal competition tables. Old site blocks automated fetching in current testing; **season import remains manual until an authorized seasonal source/API is confirmed**. Do not bypass site restrictions. Email LFL to request a documented/authorized feed if necessary.
