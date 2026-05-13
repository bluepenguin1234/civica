"""
Extract the 11 HTML-only towns and append them to towns.csv.
Run once to make towns.csv the single source of truth for all 47 towns.
"""

import re, csv, json
from pathlib import Path

ROOT     = Path(__file__).parent.parent
HTML     = ROOT / "civica-v5.html"
CSV_FILE = ROOT / "data" / "towns.csv"

# HTML field  →  CSV column
FIELD_MAP = {
    "name":       "town_name",
    "state":      "state",
    "county":     "county",
    "zip":        "zip_codes",
    "pop":        "population",
    "bond":       "bond_rating_sp",
    "free_cash":  "free_cash_pct_of_budget",
    "pension":    "pension_funded_ratio_pct",
    "debt_pc":    "debt_per_capita",
    "gfoa":       "gfoa_certificate_consecutive_years",
    "tax_non_res":"tax_base_non_residential_pct",
    "eff_rate":   "effective_tax_rate_pct",
    "med_tax":    "median_annual_tax_bill",
    "med_inc":    "median_household_income",
    "res_rate":   "residential_rate_per_1000",
    "d_rank":     "district_state_rank",
    "d_total":    "district_state_rank_total",
    "d_10yr":     "district_rank_10yr_change",
    "math":       "test_scores_math_pct",
    "grad":       "graduation_rate_pct",
    "ap":         "ap_participation_pct",
    "transp":     "transparency",
    "elec_save":  "electric_savings_vs_state_avg",
    "water_viol": "water_violations_5yr",
    "transit":    "transit_access",
    "violent":    "violent_crime_per_100k",
    "prop_crime": "property_crime_per_100k",
    "crime5yr":   "crime_5yr_pct_change",
    "inc10yr":    "income_10yr_change_pct",
    "pop10yr":    "population_10yr_change_pct",
    "bach":       "bachelors_degree_pct",
    "unemp":      "unemployment_pct",
    "pov":        "poverty_pct",
    "flood":      "flood_risk_pct",
    "flood50":    "flood_2050_growth_pts",
    "fire":       "wildfire_risk",
    "score":      "civica_score",
    "ter":        "ter",
    "ter_r":      "ter_rating",
    "gaps":       "data_gaps_count",
    "conf":       "data_confidence",
    "standout":   "compiler_notes",
}

MA_ZHVI = 613049.0
ZHVI = {
    "Cambridge":995293,"Lynn":537825,"Lawrence":455876,"Somerville":892143,
    "Haverhill":497568,"Medford":784462,"Peabody":652390,"Methuen":561211,
    "Arlington":1005584,"Salem":572734,"Woburn":704405,"Chelsea":505101,
    "Beverly":696077,"Andover":911128,"Lexington":1469802,"North Andover":760639,
    "Saugus":650624,"Danvers":674241,"Gloucester":693415,"Wakefield":756484,
    "Belmont":1377983,"Burlington":824833,"Reading":844034,"Winchester":1449988,
    "Newburyport":845604,"Amesbury":570013,"Marblehead":959425,"Uxbridge":487277,
    "Swampscott":763080,"Lynnfield":1018229,"Ipswich":790546,"Middleton":819582,
    "Salisbury":589785,"Georgetown":708796,"Boxford":989433,"Hamilton":827397,
    "Newbury":844611,"Groveland":648353,"Topsfield":898745,"Merrimac":597359,
    "Rockport":834071,"Rowley":733628,"Manchester-by-the-Sea":1183983,
    "Wenham":938834,"West Newbury":861236,"Essex":827029,"Nahant":903532,
}
RATING_BANDS = [(82,"Great Value"),(65,"Good Value"),(50,"Fair Market"),(35,"Premium"),(0,"Luxury")]

def compute_value(score, name):
    zhvi = ZHVI.get(name)
    if not zhvi:
        return "", ""
    raw = score / (zhvi / MA_ZHVI)
    vs = round(raw, 1)
    for t, label in RATING_BANDS:
        if vs >= t:
            return str(vs), label
    return str(vs), "Luxury"

def parse_val(v):
    """Convert JS literal to Python string."""
    v = v.strip()
    if v == "null":
        return ""
    if v.startswith('"') or v.startswith("'"):
        return v[1:-1]
    return v

def extract_town_objects(html):
    start = html.index("const TOWNS = [") + len("const TOWNS = [")
    depth = 1; i = start
    while i < len(html) and depth > 0:
        if html[i] == "[": depth += 1
        elif html[i] == "]": depth -= 1
        i += 1
    block = html[start:i-1]
    objects = []
    depth = 0; obj_start = None
    for idx, ch in enumerate(block):
        if ch == "{":
            if depth == 0: obj_start = idx
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and obj_start is not None:
                objects.append(block[obj_start:idx+1])
                obj_start = None
    return objects

def parse_object(obj):
    """Extract key:value pairs from a JS object literal."""
    result = {}
    # Match key: then quoted string, number, or null
    pattern = re.compile(r'(\w+):((?:"[^"]*"|\'[^\']*\'|-?\d+(?:\.\d+)?|null))')
    for m in pattern.finditer(obj):
        result[m.group(1)] = parse_val(m.group(2))
    return result


# ── Load existing CSV ─────────────────────────────────────────────────────────
rows = list(csv.DictReader(open(CSV_FILE, encoding="utf-8")))
fieldnames = list(rows[0].keys())
csv_towns = {r["town_name"] for r in rows}

# ── Extract missing towns from HTML ───────────────────────────────────────────
html = HTML.read_text(encoding="utf-8")
objects = extract_town_objects(html)

added = []
for obj in objects:
    parsed = parse_object(obj)
    name = parsed.get("name", "")
    if not name or name in csv_towns:
        continue

    new_row = {k: "" for k in fieldnames}
    for html_key, csv_col in FIELD_MAP.items():
        if csv_col in fieldnames and html_key in parsed:
            new_row[csv_col] = parsed[html_key]

    # Normalize transparency to lowercase yes/no
    t = new_row.get("transparency", "").strip().lower()
    new_row["transparency"] = "yes" if t == "yes" else ("no" if t == "no" else t)

    new_row["last_updated"] = "2026-05-13"

    score_str = new_row.get("civica_score", "")
    if score_str:
        vs, rating = compute_value(int(score_str), name)
        new_row["value_score"] = vs
        new_row["value_rating"] = rating

    rows.append(new_row)
    added.append(name)
    csv_towns.add(name)

# ── Write updated CSV ─────────────────────────────────────────────────────────
with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)

print(f"Added {len(added)} towns: {', '.join(added)}")
print(f"towns.csv now has {len(rows)} rows")
