import sys, csv, io
sys.stdout.reconfigure(encoding='utf-8')

HTML = 'civica-v5.html'
CSV  = 'data/towns.csv'

# ── Fix transit in towns.csv (stored as "none" → canonical "None") ──────────
rows = []
fieldnames = []
with open(CSV, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = list(reader.fieldnames)
    for row in reader:
        if row['town_name'] == 'Provincetown' and row['transit_access'] == 'none':
            row['transit_access'] = 'None'
        rows.append(row)
with open(CSV, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)
print('Fixed transit_access in towns.csv')

# ── Replace glance + standout in HTML ───────────────────────────────────────
with open(HTML, encoding='utf-8') as f:
    html = f.read()

# Find the Provincetown object and locate its glance/standout fields
idx = html.find('"Provincetown"', html.find('const TOWNS'))
chunk = html[idx:idx+2000]

# Locate old glance and standout substrings
import re
glance_m   = re.search(r'glance:"[^"]*(?:"[^,}]*)*"', chunk)
standout_m = re.search(r'standout:"[^"]*(?:"[^,}]*)*"', chunk)

if glance_m and standout_m:
    old_glance   = glance_m.group(0)
    old_standout = standout_m.group(0)

    new_glance = (
        'glance:"Provincetown is a 3,700-person community at the very tip of Cape Cod — '
        'one of New England\'s most culturally distinct towns, with an arts scene, a strong '
        'LGBTQ+ identity, and a summer economy that swells the population to roughly 60,000. '
        'The defining trade-offs for permanent buyers: 42.1% of properties carry current flood '
        'risk (rising to 46.1% by 2050), a school district ranked #326 of 396 statewide, and '
        'no MBTA transit. On the fiscal side: AA+ bond rating, 7.1% free cash reserves, and '
        'one of the lowest residential tax rates on Cape Cod at $5.60 per $1,000."'
    )
    new_standout = (
        'standout:"Provincetown: extreme flood exposure (42.1% of properties at current risk, '
        'rising to 46.1% by 2050); AA+ bond; school district #326 of 396 statewide; '
        'residential tax rate $5.60 per $1,000 — among the lowest on Cape Cod."'
    )

    html = html.replace(old_glance,   new_glance,   1)
    html = html.replace(old_standout, new_standout, 1)

    with open(HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    print('Updated glance and standout for Provincetown.')
else:
    print('ERROR: could not locate glance/standout fields.')
    if glance_m:   print('  glance found:', glance_m.group(0)[:80])
    if standout_m: print('  standout found:', standout_m.group(0)[:80])
    print('Chunk:', chunk[:600])
