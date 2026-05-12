# Civica — Project Instructions for Claude

## What this project is
Civica is a single-page web app that scores towns and cities on fiscal health, schools, taxes, safety, and infrastructure to help homebuyers make better decisions. Currently live at bluepenguin1234.github.io/civica covering 36 Essex County (MA) towns and cities.

## File rules — read this first

**There are two copies of the active file and both must always be kept in sync:**
- `C:\Users\Brian\Desktop\Civica\civica-v5.html` — GitHub repo source (authoritative)
- `C:\Users\Brian\Desktop\civica-v5.html` — local desktop preview copy

**Always edit both files.** Never edit just one. Copy commands fail silently on this system — use the Edit tool directly on each file.

**Version history — never touch these:**
- `civica.html` = v1, locked forever, do not edit
- `civica-v2.html` through `civica-v4.html` = old versions, ignore

**If a new version is ever needed**, create `civica-v6.html` — never overwrite v5.

## Git workflow
1. Make changes on the `dev` branch
2. Commit to dev
3. `git checkout main && git merge dev && git push origin main`
4. `git checkout dev && git push origin dev`
- Live site: bluepenguin1234.github.io/civica
- Never force-push to main

## Data file
- Towns CSV lives at: `C:\Users\Brian\Desktop\files\towns.csv`
- Whenever town data changes in the HTML, update the CSV to match
- CSV has 1 header row + 36 data rows (one per town)

## TOWNS array — how it works
- All town data lives in a JavaScript `const TOWNS = [...]` array in civica-v5.html
- Each town is one long object on a single line with ~50 fields
- Insertion point for new towns: after the last existing town entry, before `];`
- The Edit tool sometimes fails with "file modified since read" — if this happens, use a Python script to do the replacement atomically (read + write in one operation). `py script.py` works; `python3` does not.

## Town count branding
When adding new towns, update all three of these in both HTML files:
1. Hero badge: `Now live · Massachusetts · X towns and cities`
2. Stats counter: `<span class="sn-num">X</span>`
3. Map subtitle: `Civica scores X towns and cities across...`

## Data sources
- Pension: MA PERAC — Essex Regional Retirement System covers most Essex County towns (~53.8% funded)
- Bond ratings: EMMA/MSRB
- School rankings: DESE district profiles / SchoolDigger
- Crime: FBI UCR / MA EOPSS
- Demographics: Census ACS 2023
- Municipal electric savings: confirmed MLDs in Essex County — Danvers, Ipswich, Georgetown, Middleton, Merrimac, Groveland, Rowley, Marblehead (MMLD), Peabody (PMLP)

## Logo spec (use on every page)
30×30 blue SVG icon + logotype: `civi` in dark + `ca` in blue (#0071e3). Never change this.

## Ad structure
Three ad units render on every town profile:
1. Featured Agent — `AD_AGENT` object (currently placeholder: Sarah Mitchell)
2. Featured Listings — `AD_LISTINGS_MAP` (only Beverly has real data; others use defaults)
3. Vendor Strip — `AD_VENDORS` array (4 slots: moving, inspection, mortgage, insurance)
Mortgage calculator on every profile is unsold/unsponsored.

## Key contacts / config
- Email shown in UI: hello@civica.com
- GitHub repo: bluepenguin1234/civica
- User email: rxbw5d7www@privaterelay.appleid.com
