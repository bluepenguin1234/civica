"""
Add Value Score to Civica
=========================
Value Score = Civica Score / (Town ZHVI / MA State ZHVI)

Measures quality per dollar relative to the state median.
Rating bands (calibrated to 47-town distribution):
  Great Value  >= 82
  Good Value   >= 65
  Fair Market  >= 50
  Premium      >= 35
  Luxury        < 35
"""

import re, csv, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
HTML_FILE = ROOT / "civica-v5.html"
CSV_FILE  = ROOT / "data" / "towns.csv"

MA_ZHVI_2024 = 613049.0

ZHVI_2024 = {
    "Cambridge":            995293,
    "Lynn":                 537825,
    "Lawrence":             455876,
    "Somerville":           892143,
    "Haverhill":            497568,
    "Medford":              784462,
    "Peabody":              652390,
    "Methuen":              561211,
    "Arlington":            1005584,
    "Salem":                572734,
    "Woburn":               704405,
    "Chelsea":              505101,
    "Beverly":              696077,
    "Andover":              911128,
    "Lexington":            1469802,
    "North Andover":        760639,
    "Saugus":               650624,
    "Danvers":              674241,
    "Gloucester":           693415,
    "Wakefield":            756484,
    "Belmont":              1377983,
    "Burlington":           824833,
    "Reading":              844034,
    "Winchester":           1449988,
    "Newburyport":          845604,
    "Amesbury":             570013,
    "Marblehead":           959425,
    "Uxbridge":             487277,
    "Swampscott":           763080,
    "Lynnfield":            1018229,
    "Ipswich":              790546,
    "Middleton":            819582,
    "Salisbury":            589785,
    "Georgetown":           708796,
    "Boxford":              989433,
    "Hamilton":             827397,
    "Newbury":              844611,
    "Groveland":            648353,
    "Topsfield":            898745,
    "Merrimac":             597359,
    "Rockport":             834071,
    "Rowley":               733628,
    "Manchester-by-the-Sea":1183983,
    "Wenham":               938834,
    "West Newbury":         861236,
    "Essex":                827029,
    "Nahant":               903532,
}

RATING_BANDS = [
    (82, "Great Value"),
    (65, "Good Value"),
    (50, "Fair Market"),
    (35, "Premium"),
    (0,  "Luxury"),
]

def compute_value(civica_score, town_name):
    zhvi = ZHVI_2024.get(town_name)
    if not zhvi:
        return None, None
    raw = civica_score / (zhvi / MA_ZHVI_2024)
    vs = round(raw, 1)
    for threshold, label in RATING_BANDS:
        if vs >= threshold:
            return vs, label
    return vs, "Luxury"

# ── Update towns.csv ──────────────────────────────────────────────────────────
print("Updating towns.csv...")
rows = list(csv.DictReader(open(CSV_FILE, encoding="utf-8")))
fieldnames = list(rows[0].keys())

if "value_score" not in fieldnames:
    idx = fieldnames.index("ter_rating") + 1
    fieldnames.insert(idx, "value_score")
    fieldnames.insert(idx + 1, "value_rating")

for row in rows:
    score_val = row.get("civica_score", "")
    if score_val:
        vs, rating = compute_value(int(score_val), row["town_name"])
        row["value_score"] = str(vs) if vs is not None else ""
        row["value_rating"] = rating or ""
    else:
        row["value_score"] = ""
        row["value_rating"] = ""

with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)
print(f"  towns.csv: {sum(1 for r in rows if r['value_score'])} towns updated")

# ── Update civica-v5.html using brace-balanced parsing ───────────────────────
print("Updating civica-v5.html...")
html = open(HTML_FILE, encoding="utf-8").read()

start_marker = "const TOWNS = ["
ts = html.index(start_marker) + len(start_marker)

# Find end of TOWNS array (matching bracket)
depth = 1
i = ts
while i < len(html) and depth > 0:
    if html[i] == '[': depth += 1
    elif html[i] == ']': depth -= 1
    i += 1
te = i - 1   # index of closing ]

towns_block = html[ts:te]

# Extract individual town objects by brace-counting
objects = []   # list of (start_in_block, end_in_block)
depth = 0
obj_start = None
for idx, ch in enumerate(towns_block):
    if ch == '{':
        if depth == 0:
            obj_start = idx
        depth += 1
    elif ch == '}':
        depth -= 1
        if depth == 0 and obj_start is not None:
            objects.append((obj_start, idx + 1))
            obj_start = None

print(f"  Found {len(objects)} town objects in TOWNS array")

patched_count = 0
delta = 0   # running offset from prior insertions

for obj_start, obj_end in objects:
    s = ts + obj_start + delta
    e = ts + obj_end + delta
    obj = html[s:e]

    # Get name
    nm = re.search(r'name:"([^"]+)"', obj)
    sc = re.search(r'score:(\d+)', obj)
    if not nm or not sc:
        continue
    name = nm.group(1)
    score = int(sc.group(1))

    vs, rating = compute_value(score, name)
    if vs is None:
        continue

    # Remove existing val_s / val_r if present
    obj_clean = re.sub(r',val_s:[^,}]+', '', obj)
    obj_clean = re.sub(r',val_r:"[^"]*"', '', obj_clean)

    # Insert before final }
    insertion = f',val_s:{vs},val_r:"{rating}"'
    obj_new = obj_clean[:-1] + insertion + '}'

    html = html[:s] + obj_new + html[e:]
    delta += len(obj_new) - len(obj)
    patched_count += 1

print(f"  Patched {patched_count} town objects")

with open(HTML_FILE, "w", encoding="utf-8") as f:
    f.write(html)

# Verify
val_count = len(re.findall(r'val_s:[\d.]+', html))
print(f"  val_s fields in HTML: {val_count}")

# ── Print summary table ───────────────────────────────────────────────────────
print()
print(f"{'Town':<26} {'Score':>6} {'ZHVI 2024':>11} {'Val Score':>10} {'Rating'}")
print("-" * 65)
preview = []
for row in rows:
    if row["value_score"]:
        preview.append((row["town_name"], int(row["civica_score"]),
                        ZHVI_2024.get(row["town_name"], 0),
                        float(row["value_score"]), row["value_rating"]))
preview.sort(key=lambda x: x[3], reverse=True)
for name, score, zhvi, vs, rating in preview:
    print(f"{name:<26} {score:>6} ${zhvi:>10,} {vs:>10.1f}  {rating}")
