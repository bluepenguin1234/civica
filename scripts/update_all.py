"""
Master update pipeline — applies all new data, recomputes scores,
updates towns.csv and civica-v5.html in one pass.
"""

import csv, re, math
from pathlib import Path

ROOT     = Path(__file__).parent.parent
CSV_FILE = ROOT / "data" / "towns.csv"
HTML_FILE= ROOT / "civica-v5.html"
BULK     = ROOT / "data" / "bulk"
DATA     = ROOT / "data"

# ─── Load bulk data ───────────────────────────────────────────────────────────
def load_csv_index(path, key_col, transform=None):
    idx = {}
    if not path.exists():
        print(f"  MISSING: {path.name}")
        return idx
    for r in csv.DictReader(open(path, encoding="utf-8")):
        k = (transform(r[key_col]) if transform else r[key_col]).strip()
        idx[k] = r
    return idx

census  = load_csv_index(BULK / "census_acs_ma_towns.csv", "town_name", str.lower)
schools = load_csv_index(BULK / "ma_schools_combined.csv", "district_name", str.lower)
print(f"Loaded: {len(census)} Census towns, {len(schools)} school districts")

# Town → district name mapping for regional schools
DISTRICT_MAP = {
    "Boxford":              "masconomet",
    "Topsfield":            "masconomet",
    "Middleton":            "masconomet",
    "Hamilton":             "hamilton-wenham",
    "Wenham":               "hamilton-wenham",
    "Manchester-by-the-Sea":"manchester essex",
    "Essex":                "manchester essex",
    "Merrimac":             "pentucket",
    "Groveland":            "pentucket",
    "West Newbury":         "pentucket",
    "Georgetown":           "pentucket",
    "Rowley":               "triton",
    "Salisbury":            "triton",
    "Newbury":              "triton",
    "Nahant":               "lynn",
}

def get_school(town):
    district = DISTRICT_MAP.get(town, town).lower()
    # Try exact match first
    if district in schools:
        return schools[district]
    # Fuzzy: first match containing key word
    for k, v in schools.items():
        if district.split()[0] in k:
            return v
    return None

# ─── Agent data ───────────────────────────────────────────────────────────────
# Bond ratings confirmed by MA DLS fiscal agent
BOND_UPDATES = {
    "Lynn":         "A",
    "Boxford":      "AAA",
    "Hamilton":     "AAA",
    "Merrimac":     "AA+",
    "North Andover":"AAA",
    "Swampscott":   "AA+",
    "Burlington":   "AAA",
}

# Pension funded ratios (PERAC data)
ESSEX_REGIONAL_PENSION = 53.79  # covers 18 Essex County towns
PENSION_UPDATES = {
    "Lawrence":              65.0,
    "Haverhill":             69.4,
    "Uxbridge":              51.9,
    "Ipswich":               ESSEX_REGIONAL_PENSION,
    "Lynnfield":             ESSEX_REGIONAL_PENSION,
    "Rockport":              ESSEX_REGIONAL_PENSION,
    "Manchester-by-the-Sea": ESSEX_REGIONAL_PENSION,
    "Boxford":               ESSEX_REGIONAL_PENSION,
    "Hamilton":              ESSEX_REGIONAL_PENSION,
    "Georgetown":            ESSEX_REGIONAL_PENSION,
    "Middleton":             ESSEX_REGIONAL_PENSION,
    "Salisbury":             ESSEX_REGIONAL_PENSION,
    "Topsfield":             ESSEX_REGIONAL_PENSION,
    "Merrimac":              ESSEX_REGIONAL_PENSION,
    "Groveland":             ESSEX_REGIONAL_PENSION,
    "Newbury":               ESSEX_REGIONAL_PENSION,
    "West Newbury":          ESSEX_REGIONAL_PENSION,
    "Rowley":                ESSEX_REGIONAL_PENSION,
    "Nahant":                ESSEX_REGIONAL_PENSION,
    "Wenham":                ESSEX_REGIONAL_PENSION,
    "Essex":                 ESSEX_REGIONAL_PENSION,
}

# GFOA consecutive years confirmed
GFOA_UPDATES = {
    "Chelsea":   26,
    "Amesbury":  7,  # free cash also below
}

# Free cash updates
FREE_CASH_UPDATES = {
    "Amesbury": 7.77,
}

# District rank 10yr change (from MA DOE agent)
RANK_CHANGE_UPDATES = {
    "Marblehead":            7,
    "Salem":                -31,
    "Gloucester":            2,
    "Newburyport":          -25,
    "Swampscott":           81,
    "Burlington":           -85,
    "Rockport":             -1,
    "Manchester-by-the-Sea":-4,
    "Boxford":               5,
    "Hamilton":             -39,
    "Nahant":               -4,
    "Chelsea":              -28,
    "Saugus":                3,
    "North Andover":        12,
}

# Crime corrections/additions (crime agent)
VIOLENT_CRIME_UPDATES = {
    "Peabody":               147.7,  # was wrong (4.6)
    "Rockport":              21.5,
    "Manchester-by-the-Sea": 0.0,
    "Boxford":               6.1,
    "Hamilton":              72.8,
    "Georgetown":            41.6,
    "Newbury":               59.6,
    "West Newbury":          65.1,
    "Rowley":                40.8,
    "Nahant":                15.1,
    "Wenham":                70.0,
    "Essex":                 54.4,
}
PROPERTY_CRIME_UPDATES = {
    "Peabody":               61.8,   # was wrong (254.7)
    "Rockport":              7.9,
    "Manchester-by-the-Sea": 30.8,
    "Boxford":               2.5,
    "Hamilton":              21.2,
    "Georgetown":            25.6,
    "Newbury":               30.5,
    "West Newbury":          9.8,
    "Rowley":                17.9,
    "Nahant":                10.6,
    "Wenham":                17.0,
    "Essex":                 29.9,
    "Merrimac":              23.8,
}

# Flood data (crime agent)
FLOOD_RISK_UPDATES     = {"Gloucester": 20.0, "Chelsea": 14.0}
FLOOD_2050_UPDATES     = {"Chelsea": 5.0}

# Wildfire (all low for coastal Essex County)
WILDFIRE_UPDATES = {t: "Low" for t in [
    "Rockport","Manchester-by-the-Sea","Boxford","Hamilton","Georgetown",
    "Newbury","West Newbury","Rowley","Wenham","Essex"
]}

# ─── Load methodology ─────────────────────────────────────────────────────────
def load_methodology():
    def lc(p): return list(csv.DictReader(open(DATA / p, encoding="utf-8")))
    master  = lc("master_weights.csv")
    pillar  = lc("pillar_weights.csv")
    rubrics = lc("scoring_rubrics.csv")
    state   = lc("state_context.csv")
    pw = {r["pillar_id"]: float(r["weight"]) for r in master}
    sw = {}
    for r in pillar:
        sw.setdefault(r["pillar_id"], {})[r["submetric_id"]] = float(r["weight"])
    ri = {}
    for r in rubrics:
        ri.setdefault(r["submetric_id"], []).append(r)
    si = {}
    for r in state:
        si.setdefault(r["state"], {})[r["metric"]] = float(r["value"])
    return pw, sw, ri, si

def score_submetric(sm_id, raw, ri):
    if sm_id not in ri: return 50
    rules = ri[sm_id]
    default = float(rules[0]["default_if_missing"])
    if raw is None or raw == "": return default
    for rule in rules:
        if rule["rule_type"] == "range":
            try:
                v = float(raw); lo = float(rule["lower_bound"]); hi = float(rule["upper_bound"])
                if lo <= v < hi: return float(rule["score_0_100"])
            except: return default
        elif rule["rule_type"] == "lookup":
            if str(raw).strip().lower() == str(rule["match_value"]).strip().lower():
                return float(rule["score_0_100"])
    return default

def score_town(td, pw, sw, ri, si):
    ctx = si.get(td.get("state","MA"), si["MA"])
    def sf(a, b):
        try: return float(a)/float(b)
        except: return None
    def fv(k): return td.get(k) or None

    h = {
        "tax_burden_pct":       (float(td["median_annual_tax_bill"])/float(td["median_household_income"])*100)
                                 if td.get("median_annual_tax_bill") and td.get("median_household_income") else None,
        "rank_percentile":      (1-float(td["district_state_rank"])/float(td["district_state_rank_total"]))*100
                                 if td.get("district_state_rank") and td.get("district_state_rank_total") else None,
        "debt_ratio":           sf(fv("debt_per_capita"), ctx["debt_per_capita_median"]),
        "violent_crime_ratio":  sf(fv("violent_crime_per_100k"), ctx["violent_crime_per_100k"]),
        "property_crime_ratio": sf(fv("property_crime_per_100k"), ctx["property_crime_per_100k"]),
        "income_ratio":         sf(fv("median_household_income"), ctx["median_household_income"]),
        "poverty_ratio":        sf(fv("poverty_pct"), ctx["poverty_rate_pct"]),
        "unemployment_ratio":   sf(fv("unemployment_pct"), ctx["unemployment_rate_pct"]),
    }
    SM = {
        "bond_rating":           fv("bond_rating_sp"),
        "free_cash_pct":         fv("free_cash_pct_of_budget"),
        "pension_funded":        fv("pension_funded_ratio_pct"),
        "debt_per_capita":       h["debt_ratio"],
        "gfoa_years":            fv("gfoa_certificate_consecutive_years"),
        "tax_base_diversification": fv("tax_base_non_residential_pct"),
        "effective_tax_rate":    fv("effective_tax_rate_pct"),
        "tax_burden_to_income":  h["tax_burden_pct"],
        "tax_base_health":       fv("tax_base_non_residential_pct"),
        "rank_percentile":       h["rank_percentile"],
        "rank_trajectory":       fv("district_rank_10yr_change"),
        "test_scores":           fv("test_scores_math_pct"),
        "graduation_rate":       fv("graduation_rate_pct"),
        "ap_participation":      fv("ap_participation_pct"),
        "transparency":          fv("transparency"),
        "electric_value":        fv("electric_savings_vs_state_avg"),
        "water_quality":         fv("water_violations_5yr"),
        "transit":               fv("transit_access"),
        "violent_crime":         h["violent_crime_ratio"],
        "property_crime":        h["property_crime_ratio"],
        "crime_trajectory":      fv("crime_5yr_pct_change"),
        "income_trend":          fv("income_10yr_change_pct"),
        "population_trend":      fv("population_10yr_change_pct"),
        "income_level":          h["income_ratio"],
        "education_attainment":  fv("bachelors_degree_pct"),
        "unemployment":          h["unemployment_ratio"],
        "poverty":               h["poverty_ratio"],
        "flood_risk":            fv("flood_risk_pct"),
        "flood_trajectory":      fv("flood_2050_growth_pts"),
        "wildfire":              fv("wildfire_risk"),
    }
    ss = {sm: score_submetric(sm, val, ri) for sm, val in SM.items()}
    ps = {}
    for pillar_id, weights in sw.items():
        ps[pillar_id] = sum(ss[k]*weights[k] for k in weights)
    civica = round(sum(ps[p]*pw[p] for p in pw))

    res_rate = td.get("residential_rate_per_1000")
    if res_rate:
        ter = round(civica / float(res_rate), 1)
    else:
        ter = None
    if ter is None:       ter_r = "N/A"
    elif ter >= 9.0:      ter_r = "Exceptional"
    elif ter >= 7.0:      ter_r = "Strong"
    elif ter >= 5.0:      ter_r = "Average"
    elif ter >= 3.0:      ter_r = "Below Average"
    else:                 ter_r = "Poor"

    # Count data gaps (fields used in scoring that are missing)
    scored_fields = ["bond_rating_sp","free_cash_pct_of_budget","pension_funded_ratio_pct",
                     "debt_per_capita","gfoa_certificate_consecutive_years",
                     "tax_base_non_residential_pct","effective_tax_rate_pct",
                     "median_annual_tax_bill","district_state_rank","district_rank_10yr_change",
                     "test_scores_math_pct","graduation_rate_pct","ap_participation_pct",
                     "transparency","electric_savings_vs_state_avg","water_violations_5yr",
                     "transit_access","violent_crime_per_100k","property_crime_per_100k",
                     "crime_5yr_pct_change","income_10yr_change_pct","population_10yr_change_pct",
                     "bachelors_degree_pct","unemployment_pct","poverty_pct",
                     "flood_risk_pct","flood_2050_growth_pts","wildfire_risk"]
    gaps = sum(1 for f in scored_fields if not td.get(f))
    conf = "high" if gaps <= 3 else ("medium" if gaps <= 8 else "low")

    return civica, ter, ter_r, gaps, conf

# ─── Main update loop ─────────────────────────────────────────────────────────
print("\nLoading methodology...")
pw, sw, ri, si = load_methodology()

print("Loading towns.csv...")
rows = list(csv.DictReader(open(CSV_FILE, encoding="utf-8")))
fieldnames = list(rows[0].keys())

def setf(row, field, value):
    """Set field only if value is not None and field is in CSV."""
    if value is not None and field in fieldnames:
        row[field] = str(value)

def setf_if_empty(row, field, value):
    """Set field only if currently empty and value not None."""
    if value is not None and field in fieldnames and not row.get(field):
        row[field] = str(value)

score_changes = []

for row in rows:
    town = row["town_name"]
    print(f"  {town}...", end=" ")

    # 1. Census ACS data (authoritative — update all towns)
    c = census.get(town.lower()) or census.get(town.lower() + " town")
    if c:
        setf(row, "bachelors_degree_pct",       c.get("bachelors_degree_pct"))
        setf(row, "poverty_pct",                c.get("poverty_pct"))
        setf(row, "unemployment_pct",           c.get("unemployment_pct"))
        setf(row, "income_10yr_change_pct",     c.get("income_10yr_change_pct"))
        setf(row, "population_10yr_change_pct", c.get("population_10yr_change_pct"))
        # Only update median income if currently missing
        setf_if_empty(row, "median_household_income", c.get("median_household_income"))

    # 2. DESE school data (update all towns)
    sc = get_school(town)
    if sc:
        setf(row, "test_scores_math_pct", sc.get("mcas_math_pct"))
        setf(row, "graduation_rate_pct",  sc.get("graduation_rate_pct"))
        setf(row, "ap_participation_pct", sc.get("ap_participation_pct"))

    # 3. Agent data — fill gaps only
    setf_if_empty(row, "bond_rating_sp",                  BOND_UPDATES.get(town))
    setf_if_empty(row, "pension_funded_ratio_pct",         PENSION_UPDATES.get(town))
    setf_if_empty(row, "gfoa_certificate_consecutive_years", GFOA_UPDATES.get(town))
    setf_if_empty(row, "free_cash_pct_of_budget",          FREE_CASH_UPDATES.get(town))
    setf_if_empty(row, "district_rank_10yr_change",        RANK_CHANGE_UPDATES.get(town))
    setf_if_empty(row, "flood_risk_pct",                   FLOOD_RISK_UPDATES.get(town))
    setf_if_empty(row, "flood_2050_growth_pts",            FLOOD_2050_UPDATES.get(town))
    setf_if_empty(row, "wildfire_risk",                    WILDFIRE_UPDATES.get(town))

    # 4. Crime — use corrections (override if wrong)
    if town in VIOLENT_CRIME_UPDATES:
        setf(row, "violent_crime_per_100k", VIOLENT_CRIME_UPDATES[town])
    if town in PROPERTY_CRIME_UPDATES:
        setf(row, "property_crime", PROPERTY_CRIME_UPDATES[town])
        setf(row, "property_crime_per_100k", PROPERTY_CRIME_UPDATES[town])

    # 5. Recompute score
    old_score = row.get("civica_score", "")
    civica, ter, ter_r, gaps, conf = score_town(row, pw, sw, ri, si)
    row["civica_score"]     = str(civica)
    row["ter"]              = str(ter) if ter else ""
    row["ter_rating"]       = ter_r
    row["data_gaps_count"]  = str(gaps)
    row["data_confidence"]  = conf
    row["last_updated"]     = "2026-05-13"

    # 6. Recompute value score
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
    zhvi = ZHVI.get(town)
    if zhvi and civica:
        raw = civica / (zhvi / MA_ZHVI)
        vs = round(raw, 1)
        rating = next(label for t, label in RATING_BANDS if vs >= t)
        row["value_score"]  = str(vs)
        row["value_rating"] = rating

    delta = int(civica) - int(old_score) if old_score.isdigit() else 0
    score_changes.append((town, old_score, civica, delta))
    print(f"{old_score} -> {civica} ({'+' if delta>=0 else ''}{delta})")

# ─── Save towns.csv ───────────────────────────────────────────────────────────
with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)
print(f"\nSaved towns.csv ({len(rows)} towns)")

# ─── Patch civica-v5.html ─────────────────────────────────────────────────────
print("Patching civica-v5.html...")
html = HTML_FILE.read_text(encoding="utf-8")

# Build town lookup by name
town_lookup = {r["town_name"]: r for r in rows}

start_marker = "const TOWNS = ["
ts = html.index(start_marker) + len(start_marker)
depth = 1; i = ts
while i < len(html) and depth > 0:
    if html[i] == "[": depth += 1
    elif html[i] == "]": depth -= 1
    i += 1
te = i - 1
block = html[ts:te]

objects = []
depth = 0; obj_start = None
for idx2, ch in enumerate(block):
    if ch == "{":
        if depth == 0: obj_start = idx2
        depth += 1
    elif ch == "}":
        depth -= 1
        if depth == 0 and obj_start is not None:
            objects.append((obj_start, idx2+1))
            obj_start = None

patched = 0; delta = 0
TRANSIT_MAP = {
    "commuter_rail_in_town": "Commuter Rail (in town)",
    "commuter_rail_nearby":  "Commuter Rail (nearby)",
    "bus_only":              "Bus only",
    "none":                  "None",
    "no":                    "None",
}

for obj_start, obj_end in objects:
    s = ts + obj_start + delta
    e = ts + obj_end  + delta
    obj = html[s:e]

    nm = re.search(r'name:"([^"]+)"', obj)
    if not nm: continue
    name = nm.group(1)
    row = town_lookup.get(name)
    if not row: continue

    def fv(k, default=None):
        v = row.get(k, "")
        return v if v else default

    def js_num(k, default="null"):
        v = fv(k)
        try: return str(float(v)) if v else default
        except: return default

    def js_str(k, default="null"):
        v = fv(k)
        return f'"{v}"' if v else default

    score  = fv("civica_score", "0")
    ter    = js_num("ter", "null")
    ter_r  = js_str("ter_rating", '"N/A"')
    gaps   = fv("data_gaps_count", "0")
    conf   = js_str("data_confidence", '"medium"')

    # Patch: score, ter, ter_r, gaps, conf
    # Also patch math, grad, ap, bach, pov, unemp from new data
    math  = js_num("test_scores_math_pct")
    grad  = js_num("graduation_rate_pct")
    ap    = js_num("ap_participation_pct")
    bach  = js_num("bachelors_degree_pct")
    pov   = js_num("poverty_pct")
    unemp = js_num("unemployment_pct")
    inc10 = js_num("income_10yr_change_pct")
    pop10 = js_num("population_10yr_change_pct")
    viol  = js_num("violent_crime_per_100k")
    prop  = js_num("property_crime_per_100k")
    flood = js_num("flood_risk_pct")
    fl50  = js_num("flood_2050_growth_pts")
    fire  = js_str("wildfire_risk")
    bond  = js_str("bond_rating_sp")
    free  = js_num("free_cash_pct_of_budget")
    pens  = js_num("pension_funded_ratio_pct")
    gfoa  = js_num("gfoa_certificate_consecutive_years")
    d10yr = js_num("district_rank_10yr_change")

    # Apply patches using regex substitution
    def patch(obj, pattern, replacement):
        m = re.search(pattern, obj)
        if m:
            return obj[:m.start()] + replacement + obj[m.end():]
        return obj

    obj = patch(obj, r'score:\d+',      f'score:{score}')
    obj = patch(obj, r'ter:[\d.]+',     f'ter:{ter}')
    obj = patch(obj, r'ter_r:"[^"]*"',  f'ter_r:{ter_r}')
    obj = patch(obj, r'gaps:\d+',       f'gaps:{gaps}')
    obj = patch(obj, r'conf:"[^"]*"',   f'conf:{conf}')
    obj = patch(obj, r'math:[\d.]+',    f'math:{math}')
    obj = patch(obj, r'grad:[\d.]+',    f'grad:{grad}')
    if fv("ap_participation_pct"):
        obj = patch(obj, r'ap:[\d.]+',  f'ap:{ap}')
    obj = patch(obj, r'bach:[\d.]+',    f'bach:{bach}')
    obj = patch(obj, r'pov:[\d.]+',     f'pov:{pov}')
    if fv("violent_crime_per_100k"):
        obj = patch(obj, r'violent:[\d.]+', f'violent:{viol}')
    if fv("property_crime_per_100k"):
        obj = patch(obj, r'prop_crime:[\d.]+', f'prop_crime:{prop}')

    html = html[:s] + obj + html[e:]
    delta += len(obj) - (obj_end - obj_start)
    patched += 1

HTML_FILE.write_text(html, encoding="utf-8")
print(f"  Patched {patched} town objects")

# ─── Summary ──────────────────────────────────────────────────────────────────
print("\nSCORE CHANGES:")
print(f"{'Town':<28} {'Old':>5} {'New':>5} {'Delta':>7}")
print("-"*45)
for town, old, new, d in sorted(score_changes, key=lambda x: abs(x[3]), reverse=True):
    marker = " <-- LARGE CHANGE" if abs(d) >= 5 else ""
    print(f"{town:<28} {str(old):>5} {new:>5} {('+' if d>=0 else '')+str(d):>7}{marker}")
