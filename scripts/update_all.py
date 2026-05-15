"""
Master update pipeline — applies all new data, recomputes scores,
updates towns.csv and civica-v5.html in one pass.
"""

import csv, re, openpyxl
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

# Compute district ranks from bulk data (composite: math 50%, grad 30%, AP 20%)
_rank_scored = []
for _dname, _d in schools.items():
    try:
        _m = float(_d.get('mcas_math_pct') or 0)
        _g = float(_d.get('graduation_rate_pct') or 0)
        _a = float(_d.get('ap_participation_pct') or 0)
        if _m > 0 or _g > 0:
            _rank_scored.append((_dname, _m * 0.5 + _g * 0.3 + _a * 0.2))
    except: pass
_rank_scored.sort(key=lambda x: x[1], reverse=True)
RANK_TOTAL = len(_rank_scored)
DISTRICT_RANKS = {name: rank + 1 for rank, (name, _) in enumerate(_rank_scored)}
print(f"  Computed ranks for {RANK_TOTAL} school districts")

# ─── Load Excel bulk data ─────────────────────────────────────────────────────
def _find_col(headers, *keywords):
    """Find column index where all keywords appear in the header (case-insensitive)."""
    for i, h in enumerate(headers):
        hl = h.lower()
        if all(kw in hl for kw in keywords):
            return i
    return None

# Free Cash (CFC_PerBudg.xlsx) — all 351 MA municipalities, stored as decimal (0.048 = 4.8%)
print("Loading free cash Excel...")
free_cash_bulk = {}
fc_path = BULK / "CFC_PerBudg.xlsx"
if fc_path.exists():
    wb = openpyxl.load_workbook(fc_path, read_only=True, data_only=True)
    ws = wb.active
    rows_it = ws.iter_rows(values_only=True)
    hdrs = [str(h).strip() if h else "" for h in next(rows_it)]
    muni_i = _find_col(hdrs, "municipality")
    fy_i   = _find_col(hdrs, "fiscal year") or _find_col(hdrs, "fy")
    fc_i   = _find_col(hdrs, "%", "budget") or _find_col(hdrs, "% of")
    if None not in (muni_i, fy_i, fc_i):
        town_years = {}
        for r in rows_it:
            muni = str(r[muni_i]).strip() if r[muni_i] else ""
            if not muni or muni == "None": continue
            try:   fy = int(float(str(r[fy_i])))
            except: continue
            try:   pct = round(float(r[fc_i]) * 100, 2) if r[fc_i] else None
            except: pct = None
            if pct is not None:
                town_years.setdefault(muni.lower(), {})[fy] = pct
        for muni_l, yrs in town_years.items():
            free_cash_bulk[muni_l] = yrs[max(yrs)]
        print(f"  {len(free_cash_bulk)} municipalities loaded (best available year)")
    else:
        print(f"  Could not identify columns: muni={muni_i} fy={fy_i} fc={fc_i}")
        print(f"  Headers: {hdrs}")
    wb.close()
else:
    print(f"  MISSING: {fc_path.name}")

# Municipal Debt (municipaldebt2022.xlsx) — headers at row ~7, town name forward-filled
print("Loading municipal debt Excel...")
debt_per_capita_bulk = {}
debt_path = BULK / "municipaldebt2022.xlsx"
if debt_path.exists():
    wb = openpyxl.load_workbook(debt_path, read_only=True, data_only=True)
    ws = wb["Debt"] if "Debt" in wb.sheetnames else wb.active
    rows_it = ws.iter_rows(values_only=True)
    # Scan for header row (contains "Municipality")
    hdrs = None
    for _ in range(20):
        r = next(rows_it, None)
        if r and any(str(c).strip().lower() == "municipality" for c in r if c):
            hdrs = [str(c).strip() if c else "" for c in r]
            break
    if hdrs:
        muni_i = _find_col(hdrs, "municipality")
        fy_i   = _find_col(hdrs, "fy")
        debt_i = _find_col(hdrs, "total outstanding debt") or _find_col(hdrs, "outstanding debt")
        if None not in (muni_i, fy_i, debt_i):
            cur_muni = ""
            raw_debt = {}  # town_lower -> {fy: total_debt}
            for r in rows_it:
                if r[muni_i]:
                    cur_muni = str(r[muni_i]).strip()
                if not cur_muni: continue
                try:   fy = int(float(str(r[fy_i])))
                except: continue
                try:   debt_val = float(r[debt_i]) if r[debt_i] else None
                except: debt_val = None
                if debt_val:
                    raw_debt.setdefault(cur_muni.lower(), {})[fy] = debt_val
            # Use most recent year, divide by census population
            for muni_l, yrs in raw_debt.items():
                best_debt = yrs[max(yrs)]
                c = census.get(muni_l)
                if c:
                    try:
                        pop = float(c.get("population") or 0)
                        if pop > 0:
                            debt_per_capita_bulk[muni_l] = round(best_debt / pop, 0)
                    except: pass
            print(f"  {len(debt_per_capita_bulk)} municipalities with debt_per_capita")
        else:
            print(f"  Could not identify columns. Headers: {hdrs}")
    else:
        print("  Could not find header row in debt file")
    wb.close()
else:
    print(f"  MISSING: {debt_path.name}")

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
    "Acton":                "acton-boxborough",
    "Concord":              "concord-carlisle",
    "Kingston":             "silver lake",
    "Northborough":         "northborough-southborough",
    "North Attleborough":   "north attleborough",
    "Yarmouth":              "dennis-yarmouth",
    "Dennis":                "dennis-yarmouth",
    "Harwich":               "monomoy regional school district",
    "Chatham":               "monomoy regional school district",
    "Brewster":              "nauset",
    "Orleans":               "nauset",
    "Holden":               "wachusett",
    "Southborough":         "northborough-southborough",
    "Upton":                "mendon-upton",
    "Raynham":              "bridgewater-raynham",
    "Rehoboth":             "dighton-rehoboth",
    "Whitman":              "whitman-hanson",
    "Bridgewater":          "bridgewater-raynham",
    "Marion":               "old rochester",
    "Dover":                "dover-sherborn",
    "Sherborn":             "dover-sherborn",
    "Lincoln":              "lincoln-sudbury",
    "Carlisle":             "concord-carlisle",
    "Stow":                 "nashoba",
    "Groton":               "groton-dunstable",
    "Plainville":           "king philip",
    "Ayer":                 "ayer shirley school district",
    "Pepperell":            "north middlesex",
    "Bolton":               "nashoba",
    "Spencer":              "spencer-e brookfield",
    "Charlton":             "dudley-charlton reg",
    "Norfolk":              "king philip",
    "Townsend":             "north middlesex",
    "Lancaster":            "nashoba",
    "Sterling":             "wachusett",
    "Sturbridge":           "tantasqua",
    "Somerset":             "somerset berkley",
}

def get_school(town):
    district = DISTRICT_MAP.get(town, town).lower()
    if district in schools:
        return schools[district]
    for k, v in schools.items():
        if district.split()[0] in k:
            return v
    return None

def get_school_rank(town):
    """Return (rank, total) for a town's school district, or (None, None) if not found."""
    district = DISTRICT_MAP.get(town, town).lower()
    if district in DISTRICT_RANKS:
        return DISTRICT_RANKS[district], RANK_TOTAL
    for k in DISTRICT_RANKS:
        if district.split()[0] in k:
            return DISTRICT_RANKS[k], RANK_TOTAL
    return None, None

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
    # Batch 5 — confirmed S&P ratings (May 2026)
    "Sudbury":      "AAA",   # S&P Jan 2024
    "Westwood":     "AAA",   # S&P Oct 2025
    "Holliston":    "AAA",   # S&P Nov 2021 upgrade
    "Bedford":      "AAA",   # S&P May 2023, held since 2007
    "Pembroke":     "AA",    # S&P 2025
    "Northbridge":  "AA+",   # S&P Jul 2021 upgrade
    "Tyngsborough": "AA+",   # S&P 2024, 8th consecutive year
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

# Wildfire (all low for coastal Essex County and inland MA towns)
WILDFIRE_UPDATES = {t: "Low" for t in [
    "Rockport","Manchester-by-the-Sea","Boxford","Hamilton","Georgetown",
    "Newbury","West Newbury","Rowley","Wenham","Essex",
    "Shrewsbury","Westborough","Northborough","Grafton","Milford",
    "Mansfield","Easton","North Attleborough","Medway","Millis",
]}


# MCAS math overrides for towns where K-8 district has the math data but HS district is used for grad/AP
MATH_OVERRIDES = {
    "Sudbury":  73.0,   # K-8 district MCAS; lincoln-sudbury HS has no district-level math pct
    "Wrentham": 66.0,   # K-8 district MCAS; King Philip Regional math (43%) covers 3 towns
    "Brewster":  60.0,   # Brewster Elementary K-5 MCAS math; Nauset Regional HS data used for grad/AP
    "Southborough": 74.0,  # Southborough Elementary K-5 MCAS; Algonquin Regional HS data used for grad/AP
    "Marion":       55.0,  # Marion Elementary K-6 MCAS; Old Rochester Regional HS data used for grad/AP
}

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

LOOKUP_ONLY = {"bond_rating", "transit", "wildfire"}

def cap(val, lo, hi):
    if val is None: return None
    try: return max(lo, min(hi, float(val)))
    except: return val

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
    }
    SM = {
        # Fiscal Health
        "bond_rating":          fv("bond_rating_sp"),
        "free_cash_pct":        fv("free_cash_pct_of_budget"),
        "pension_funded":       fv("pension_funded_ratio_pct"),
        "debt_per_capita":      h["debt_ratio"],
        # Taxes
        "effective_tax_rate":   fv("effective_tax_rate_pct"),
        "tax_burden_to_income": h["tax_burden_pct"],
        # Schools
        "rank_percentile":      h["rank_percentile"],
        "rank_trajectory":      cap(fv("district_rank_10yr_change"), -150, 150),
        "test_scores":          fv("test_scores_math_pct"),
        "graduation_rate":      fv("graduation_rate_pct"),
        # Safety
        "violent_crime":        h["violent_crime_ratio"],
        "property_crime":       h["property_crime_ratio"],
        "crime_trajectory":     cap(fv("crime_5yr_pct_change"), -75, 150),
        # Economic Vitality
        "income_level":         h["income_ratio"],
        "income_trend":         fv("income_10yr_change_pct"),
        "population_trend":     fv("population_10yr_change_pct"),
        # Quality of Life
        "transit":              fv("transit_access"),
        "electric_value":       fv("electric_savings_vs_state_avg"),
        "water_quality":        cap(fv("water_violations_5yr"), 0, 100),
        # Climate
        "flood_risk":           fv("flood_risk_pct"),
        "flood_trajectory":     fv("flood_2050_growth_pts"),
        "wildfire":             fv("wildfire_risk"),
        # Taxes — housing affordability ratio (home value / household income)
        "housing_affordability": fv("housing_affordability_ratio"),
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
    elif ter >= 6.5:      ter_r = "Exceptional"
    elif ter >= 5.5:      ter_r = "Strong"
    elif ter >= 4.0:      ter_r = "Average"
    elif ter >= 3.0:      ter_r = "Below Average"
    else:                 ter_r = "Poor"

    # Count data gaps (fields used in scoring that are missing)
    scored_fields = ["bond_rating_sp","free_cash_pct_of_budget","pension_funded_ratio_pct",
                     "debt_per_capita","effective_tax_rate_pct","median_annual_tax_bill",
                     "district_state_rank","district_rank_10yr_change",
                     "test_scores_math_pct","graduation_rate_pct",
                     "violent_crime_per_100k","property_crime_per_100k","crime_5yr_pct_change",
                     "median_household_income","income_10yr_change_pct","population_10yr_change_pct",
                     "transit_access","electric_savings_vs_state_avg",
                     "water_violations_5yr","flood_risk_pct","flood_2050_growth_pts","wildfire_risk",
                     "housing_affordability_ratio"]
    gaps = sum(1 for f in scored_fields if not td.get(f))
    conf = "high" if gaps <= 3 else ("medium" if gaps <= 8 else "low")

    return civica, ter, ter_r, gaps, conf, ps

# ─── Main update loop ─────────────────────────────────────────────────────────
print("\nLoading methodology...")
pw, sw, ri, si = load_methodology()

print("Loading towns.csv...")
rows = list(csv.DictReader(open(CSV_FILE, encoding="utf-8")))
fieldnames = list(rows[0].keys())
for f in ["p_schools","p_safety","p_taxes","p_fiscal","p_econ","p_qol","p_climate"]:
    if f not in fieldnames:
        fieldnames.append(f)
        for r in rows: r.setdefault(f, "50")
for f in ["housing_affordability_ratio"]:
    if f not in fieldnames:
        fieldnames.append(f)
        for r in rows: r.setdefault(f, "")

def setf(row, field, value):
    """Set field only if value is not None and field is in CSV."""
    if value is not None and field in fieldnames:
        row[field] = str(value)

def setf_if_empty(row, field, value):
    """Set field only if currently empty and value not None."""
    if value is not None and field in fieldnames and not row.get(field):
        row[field] = str(value)

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
    "Boston":720000,"Revere":440000,"Winthrop":520000,
    "Newton":1200000,"Waltham":720000,"Malden":545000,"Everett":530000,
    "Watertown":840000,"Framingham":575000,"Natick":775000,
    "Acton":840000,"Concord":1100000,"Stoneham":690000,
    "Quincy":535000,"Braintree":640000,"Milton":970000,"Brookline":1450000,
    "Dedham":690000,"Needham":1250000,"Wellesley":1750000,"Weymouth":530000,
    "Canton":720000,"Norwood":580000,
    "Hingham":1100000,"Duxbury":980000,"Scituate":850000,"Cohasset":1250000,
    "Norwell":850000,"Hanover":660000,"Marshfield":640000,"Kingston":520000,
    "Plymouth":540000,"Brockton":435000,
    "Lowell":425000,"Chelmsford":595000,"Billerica":682000,"Tewksbury":593000,
    "Wilmington":764000,"Melrose":843000,"Ashland":615000,"Marlborough":570000,
    "Hudson":545000,"Hopkinton":877000,
    "Walpole":620000,"Sharon":680000,"Franklin":590000,"Foxborough":540000,
    "Medfield":870000,"Westford":730000,"Weston":1620000,"Dracut":430000,
    "Littleton":555000,"Stoughton":475000,
    "Shrewsbury":530000,"Westborough":620000,"Northborough":595000,
    "Grafton":510000,"Milford":445000,
    "Mansfield":530000,"Easton":610000,"North Attleborough":430000,
    "Medway":570000,"Millis":520000,
    "Sudbury":1050000,"Westwood":1050000,"Holliston":580000,"Bedford":750000,"Lincoln":1275627,
    "Randolph":450000,"Pembroke":510000,"Northbridge":420000,"Wrentham":590000,
    "Maynard":490000,"Tyngsborough":480000,
    "Barnstable":580000,"Falmouth":660000,"Sandwich":575000,"Yarmouth":490000,
    "Dennis":520000,"Harwich":640000,"Chatham":1400000,"Brewster":680000,
    "Orleans":780000,"Mashpee":560000,
    "Worcester":310000,"Leominster":375000,"Fitchburg":310000,"Auburn":400000,
    "Holden":490000,"Southborough":790000,"Sutton":610000,"Upton":640000,
    "Millbury":430000,"Leicester":365000,
    "Attleboro":435000,"Taunton":395000,"New Bedford":295000,"Fall River":270000,
    "Dartmouth":465000,"Norton":545000,"Seekonk":445000,"Raynham":470000,
    "Rehoboth":545000,"Swansea":420000,
    "Springfield":245000,"Northampton":470000,"Amherst":545000,"Westfield":340000,
    "Chicopee":300000,"Holyoke":265000,"Agawam":360000,"West Springfield":315000,
    "Longmeadow":480000,"Easthampton":375000,
    "Abington":510000,"Whitman":455000,"Rockland":465000,"Middleborough":430000,
    "Wareham":370000,"Bridgewater":450000,"East Bridgewater":475000,
    "West Bridgewater":485000,"Carver":400000,"Marion":650000,
    # Added from Census ACS med_home_val (Zillow ZHVI not yet sourced)
    "Dover":1582164,"Sherborn":1126122,"Carlisle":1232938,"Stow":612500,
    "Groton":722853,"Plainville":629500,"Harvard":909900,"Bolton":778260,
    "Mendon":689000,"Wayland":1050000,"Boxborough":750000,
    "Norfolk":725293,"Bellingham":474575,"Pepperell":581134,"Townsend":375000,
    "Lancaster":480000,"Clinton":330000,"Sterling":475000,"Ayer":499635,
    "Spencer":421251,"Oxford":387501,"Charlton":461465,"Sturbridge":375000,
    "East Longmeadow":418463,"Ludlow":353403,"South Hadley":330000,
    "Webster":400000,"Fairhaven":385000,"Somerset":385000,
}
RATING_BANDS = [(60,"Hidden Gem"),(50,"Strong Value"),(40,"Market Rate"),(30,"Premium Town"),(0,"Luxury Market")]

COUNTY_MAP = {
    "Danvers":"Essex","Beverly":"Essex","Marblehead":"Essex","Salem":"Essex",
    "Peabody":"Essex","Gloucester":"Essex","Newburyport":"Essex","Andover":"Essex",
    "North Andover":"Essex","Swampscott":"Essex","Amesbury":"Essex","Ipswich":"Essex",
    "Lynnfield":"Essex","Rockport":"Essex","Manchester-by-the-Sea":"Essex",
    "Boxford":"Essex","Hamilton":"Essex","Georgetown":"Essex","Middleton":"Essex",
    "Salisbury":"Essex","Topsfield":"Essex","Merrimac":"Essex","Groveland":"Essex",
    "Newbury":"Essex","West Newbury":"Essex","Rowley":"Essex","Wenham":"Essex",
    "Essex":"Essex","Nahant":"Essex","Lynn":"Essex","Lawrence":"Essex",
    "Haverhill":"Essex","Methuen":"Essex","Saugus":"Essex",
    "Boston":"Suffolk","Revere":"Suffolk","Winthrop":"Suffolk","Chelsea":"Suffolk",
    "Newton":"Middlesex","Waltham":"Middlesex","Malden":"Middlesex","Everett":"Middlesex",
    "Watertown":"Middlesex","Framingham":"Middlesex","Natick":"Middlesex",
    "Acton":"Middlesex","Concord":"Middlesex","Stoneham":"Middlesex",
    "Cambridge":"Middlesex","Somerville":"Middlesex","Medford":"Middlesex",
    "Belmont":"Middlesex","Winchester":"Middlesex","Woburn":"Middlesex",
    "Wakefield":"Middlesex","Reading":"Middlesex","Burlington":"Middlesex",
    "Arlington":"Middlesex","Lexington":"Middlesex",
    "Quincy":"Norfolk","Braintree":"Norfolk","Milton":"Norfolk","Brookline":"Norfolk",
    "Dedham":"Norfolk","Needham":"Norfolk","Wellesley":"Norfolk","Weymouth":"Norfolk",
    "Canton":"Norfolk","Norwood":"Norfolk",
    "Hingham":"Plymouth","Duxbury":"Plymouth","Scituate":"Plymouth","Cohasset":"Plymouth",
    "Norwell":"Plymouth","Hanover":"Plymouth","Marshfield":"Plymouth","Kingston":"Plymouth",
    "Plymouth":"Plymouth","Brockton":"Plymouth",
    "Uxbridge":"Worcester",
    "Shrewsbury":"Worcester","Westborough":"Worcester","Northborough":"Worcester",
    "Grafton":"Worcester","Milford":"Worcester",
    "Mansfield":"Bristol","Easton":"Bristol","North Attleborough":"Bristol",
    "Medway":"Norfolk","Millis":"Norfolk",
    "Sudbury":"Middlesex","Westwood":"Norfolk","Holliston":"Middlesex",
    "Bedford":"Middlesex","Randolph":"Norfolk","Pembroke":"Plymouth",
    "Northbridge":"Worcester","Wrentham":"Norfolk","Maynard":"Middlesex",
    "Tyngsborough":"Middlesex",
    "Barnstable":"Barnstable","Falmouth":"Barnstable","Sandwich":"Barnstable",
    "Yarmouth":"Barnstable","Dennis":"Barnstable","Harwich":"Barnstable",
    "Chatham":"Barnstable","Brewster":"Barnstable","Orleans":"Barnstable","Mashpee":"Barnstable",
    "Worcester":"Worcester","Leominster":"Worcester","Fitchburg":"Worcester",
    "Auburn":"Worcester","Holden":"Worcester","Southborough":"Worcester",
    "Sutton":"Worcester","Upton":"Worcester","Millbury":"Worcester","Leicester":"Worcester",
    "Attleboro":"Bristol","Taunton":"Bristol","New Bedford":"Bristol","Fall River":"Bristol",
    "Dartmouth":"Bristol","Norton":"Bristol","Seekonk":"Bristol","Raynham":"Bristol",
    "Rehoboth":"Bristol","Swansea":"Bristol",
    "Springfield":"Hampden","Northampton":"Hampshire","Amherst":"Hampshire",
    "Westfield":"Hampden","Chicopee":"Hampden","Holyoke":"Hampden",
    "Agawam":"Hampden","West Springfield":"Hampden","Longmeadow":"Hampden","Easthampton":"Hampshire",
    "Abington":"Plymouth","Whitman":"Plymouth","Rockland":"Plymouth",
    "Middleborough":"Plymouth","Wareham":"Plymouth","Bridgewater":"Plymouth",
    "East Bridgewater":"Plymouth","West Bridgewater":"Plymouth","Carver":"Plymouth","Marion":"Plymouth",
}

# ─── Auto-generate glance/standout text ──────────────────────────────────────
def _auto_glance(town, row, civica, ter, ter_r, ps):
    """Return a 2-3 sentence glance description auto-generated from scores."""
    bond     = row.get("bond_rating_sp", "")
    d_rank   = row.get("district_state_rank", "")
    d_total  = row.get("district_state_rank_total", "") or "351"
    violent  = row.get("violent_crime_per_100k", "")
    med_tax  = row.get("median_annual_tax_bill", "")
    med_inc  = row.get("median_household_income", "")
    eff_rate = row.get("effective_tax_rate_pct", "")
    transit  = row.get("transit_access", "none").lower().strip()
    math     = row.get("test_scores_math_pct", "")
    grad     = row.get("graduation_rate_pct", "")

    pillars = sorted([
        ("schools",           ps.get("schools", 50)),
        ("safety",            ps.get("safety", 50)),
        ("taxes",             ps.get("taxes", 50)),
        ("fiscal_health",     ps.get("fiscal_health", 50)),
        ("economic_vitality", ps.get("economic_vitality", 50)),
        ("quality_of_life",   ps.get("quality_of_life", 50)),
        ("climate",           ps.get("climate", 50)),
    ], key=lambda x: x[1], reverse=True)

    # Opening sentence
    if civica >= 75:
        intro = f"{town} is a high-performing town with a Civica score of {civica}."
    elif civica >= 63:
        intro = f"{town} scores {civica} on the Civica index — above the statewide median."
    elif civica >= 50:
        intro = f"{town} scores {civica} on the Civica index, near the statewide average."
    else:
        intro = f"{town} scores {civica} on the Civica index, reflecting notable tradeoffs."

    # Top 2 strengths
    strengths = []
    for pillar, score in pillars[:3]:
        if score < 58: break
        if pillar == "schools":
            if d_rank and math and grad:
                strengths.append(f"schools ranked #{int(float(d_rank))} of {d_total} (math {math}%, grad {float(grad):.1f}%)")
            elif d_rank:
                strengths.append(f"schools ranked #{int(float(d_rank))} of {d_total}")
            else:
                strengths.append("strong school district")
        elif pillar == "safety":
            if violent:
                strengths.append(f"low crime ({float(violent):.0f} violent per 100k)")
            else:
                strengths.append("low crime rates")
        elif pillar == "fiscal_health":
            if bond and bond not in ("Not Rated", "NR", ""):
                strengths.append(f"{bond} bond rating")
            else:
                strengths.append("sound fiscal health")
        elif pillar == "taxes":
            if eff_rate:
                strengths.append(f"low effective tax rate ({float(eff_rate):.3f}%)")
            elif med_tax:
                strengths.append(f"competitive taxes (${int(float(med_tax)):,}/yr median bill)")
            else:
                strengths.append("competitive tax burden")
        elif pillar == "economic_vitality":
            if med_inc:
                strengths.append(f"strong household incomes (${int(float(med_inc)):,} median)")
            else:
                strengths.append("strong economic vitality")
        elif pillar == "quality_of_life":
            if transit and transit not in ("none", "no"):
                strengths.append("good transit access")
    strength_sent = ("Strengths: " + ", ".join(strengths[:2]) + ".") if strengths else ""

    # Bottom weakness
    weakness = ""
    for pillar, score in reversed(pillars):
        if score > 44: break
        if pillar == "taxes" and med_tax:
            weakness = f"high median tax bill (${int(float(med_tax)):,}/yr)"
        elif pillar == "safety" and violent:
            weakness = f"above-average crime ({float(violent):.0f} violent per 100k)"
        elif pillar == "schools":
            weakness = "below-average school performance"
        elif pillar == "climate":
            weakness = "elevated flood or climate risk"
        elif pillar == "fiscal_health":
            weakness = "below-average fiscal health"
        if weakness: break
    weak_sent = (f"Key tradeoff: {weakness}.") if weakness else ""

    ter_sent = ""
    if ter and ter_r not in ("N/A", "Poor", "Below Average"):
        ter_sent = f"{ter_r} value at {ter}x TER."

    parts = [p for p in [intro, strength_sent, weak_sent or ter_sent] if p]
    return " ".join(parts)


def _auto_standout(town, row, civica, ter, ter_r, ps):
    """Return a 1-2 sentence standout bullet auto-generated from scores."""
    bond    = row.get("bond_rating_sp", "")
    d_rank  = row.get("district_state_rank", "")
    d_total = row.get("district_state_rank_total", "") or "351"
    violent = row.get("violent_crime_per_100k", "")
    math    = row.get("test_scores_math_pct", "")
    grad    = row.get("graduation_rate_pct", "")
    elec    = row.get("electric_savings_vs_state_avg", "")
    transit = row.get("transit_access", "none").lower()

    highlights = []
    if bond and bond in ("AAA", "AA+", "AA"):
        highlights.append(f"{bond} bond rating")
    if d_rank:
        ri = int(float(d_rank))
        label = f"top-{ri}" if ri <= 10 else (f"top-quartile" if ri <= 90 else f"#{ri}")
        hl = f"{label} school district (#{ri} of {d_total})"
        if math: hl += f", MCAS math {math}%"
        highlights.append(hl)
    if violent:
        vf = float(violent)
        if vf < 60:
            highlights.append(f"low crime ({vf:.0f} violent/100k)")
    if elec:
        try: highlights.append(f"municipal electric saves ~${int(float(elec)):,}/yr vs MA avg")
        except: pass
    if transit and transit not in ("none", "no", ""):
        if "in_town" in transit or "in town" in transit:
            highlights.append("commuter rail in town")
        elif "nearby" in transit:
            highlights.append("commuter rail nearby")
    if ter and ter_r in ("Exceptional", "Strong"):
        highlights.append(f"{ter_r.lower()} value ({ter}x TER)")

    if not highlights:
        return f"{town}: Civica score {civica}."
    return f"{town}: {'; '.join(highlights[:4])}."


def _auto_insert_str(obj, field, val):
    """Insert a string field into a JS object only if the field is not already present."""
    if re.search(rf'{re.escape(field)}:"[^"]*"', obj):
        return obj
    safe = val.replace('"', "'").replace('\n', ' ')
    return obj[:-1].rstrip() + f',{field}:"{safe}"' + '}'


# ─── Phase 1: Fill all data ───────────────────────────────────────────────────
print("\nPhase 1: Filling data for all towns...")
for row in rows:
    town = row["town_name"]

    # 1. Census ACS data (authoritative — update all towns)
    c = census.get(town.lower()) or census.get(town.lower() + " town")
    if c:
        setf(row, "bachelors_degree_pct",       c.get("bachelors_degree_pct"))
        setf(row, "poverty_pct",                c.get("poverty_pct"))
        setf(row, "unemployment_pct",           c.get("unemployment_pct"))
        setf(row, "income_10yr_change_pct",     c.get("income_10yr_change_pct"))
        setf(row, "population_10yr_change_pct", c.get("population_10yr_change_pct"))
        setf_if_empty(row, "median_household_income", c.get("median_household_income"))

    # 2. DESE school data (update all towns)
    sc = get_school(town)
    if sc:
        setf(row, "test_scores_math_pct", sc.get("mcas_math_pct"))
        setf(row, "graduation_rate_pct",  sc.get("graduation_rate_pct"))
        setf(row, "ap_participation_pct", sc.get("ap_participation_pct"))

    # K-8 MCAS math override for towns with split K-8/HS districts
    if town in MATH_OVERRIDES:
        setf(row, "test_scores_math_pct", MATH_OVERRIDES[town])

    # Auto-fill district rank from bulk composite (only if not already set)
    if not row.get("district_state_rank"):
        auto_rank, auto_total = get_school_rank(town)
        if auto_rank:
            setf_if_empty(row, "district_state_rank", auto_rank)
            setf_if_empty(row, "district_state_rank_total", auto_total)

    # 3. Excel bulk data (authoritative — override existing values)
    fc = free_cash_bulk.get(town.lower())
    if fc is not None:
        setf(row, "free_cash_pct_of_budget", fc)
    dpc = debt_per_capita_bulk.get(town.lower())
    if dpc is not None:
        setf(row, "debt_per_capita", dpc)

    # 4. Agent data — fill gaps only
    setf_if_empty(row, "bond_rating_sp",                  BOND_UPDATES.get(town))
    setf_if_empty(row, "pension_funded_ratio_pct",         PENSION_UPDATES.get(town))
    setf_if_empty(row, "gfoa_certificate_consecutive_years", GFOA_UPDATES.get(town))
    setf_if_empty(row, "free_cash_pct_of_budget",          FREE_CASH_UPDATES.get(town))
    setf_if_empty(row, "district_rank_10yr_change",        RANK_CHANGE_UPDATES.get(town))
    setf_if_empty(row, "flood_risk_pct",                   FLOOD_RISK_UPDATES.get(town))
    setf_if_empty(row, "flood_2050_growth_pts",            FLOOD_2050_UPDATES.get(town))
    setf_if_empty(row, "wildfire_risk",                    WILDFIRE_UPDATES.get(town))

    # 5. Crime — use corrections (override if wrong)
    if town in VIOLENT_CRIME_UPDATES:
        setf(row, "violent_crime_per_100k", VIOLENT_CRIME_UPDATES[town])
    if town in PROPERTY_CRIME_UPDATES:
        setf(row, "property_crime_per_100k", PROPERTY_CRIME_UPDATES[town])

    # 6. Housing affordability ratio (home value / household income) — derived
    zhvi_val = ZHVI.get(town)
    med_inc_str = row.get("median_household_income", "")
    if zhvi_val and med_inc_str:
        try:
            ratio = round(zhvi_val / float(med_inc_str), 2)
            if "housing_affordability_ratio" in fieldnames:
                row["housing_affordability_ratio"] = str(ratio)
        except: pass

# ─── Phase 2: Score all towns ─────────────────────────────────────────────────
print("Phase 2: Scoring all towns...")
score_changes = []
for row in rows:
    town = row["town_name"]
    old_score = row.get("civica_score", "")
    civica, ter, ter_r, gaps, conf, ps = score_town(row, pw, sw, ri, si)
    row["civica_score"]     = str(civica)
    row["ter"]              = str(ter) if ter else ""
    row["ter_rating"]       = ter_r
    row["data_gaps_count"]  = str(gaps)
    row["data_confidence"]  = conf
    row["last_updated"]     = "2026-05-14"
    row["p_schools"] = str(round(ps.get("schools",           50)))
    row["p_safety"]  = str(round(ps.get("safety",            50)))
    row["p_taxes"]   = str(round(ps.get("taxes",             50)))
    row["p_fiscal"]  = str(round(ps.get("fiscal_health",     50)))
    row["p_econ"]    = str(round(ps.get("economic_vitality", 50)))
    row["p_qol"]     = str(round(ps.get("quality_of_life",   50)))
    row["p_climate"] = str(round(ps.get("climate",           50)))

    zhvi = ZHVI.get(town)
    if zhvi and civica:
        raw_vs = civica / (zhvi / MA_ZHVI)
        vs = round(raw_vs, 1)
        rating = next(label for t, label in RATING_BANDS if vs >= t)
        row["value_score"]  = str(vs)
        row["value_rating"] = rating

    score_changes.append((town, old_score, civica, 0))  # delta filled after rescale

score_changes = [(t, old, new, new - int(old) if str(old).isdigit() else 0)
                 for t, old, new, _ in score_changes]
for town, old, new, delta in score_changes:
    print(f"  {town}: {old} -> {new} ({'+' if delta>=0 else ''}{delta})")

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

    def ensure_field(obj, field, val):
        """Update existing numeric field, or insert before closing } if absent."""
        pattern = rf'{re.escape(field)}:(?:-?[\d.]+|null)'
        if re.search(pattern, obj):
            return re.sub(rf'({re.escape(field)}:)(?:-?[\d.]+|null)', rf'\g<1>{val}', obj)
        return obj[:-1].rstrip() + f',{field}:{val}' + '}'

    def ensure_str_field(obj, field, val):
        """Update existing string field, or insert before closing } if absent."""
        pattern = rf'{re.escape(field)}:(?:"[^"]*"|null)'
        if re.search(pattern, obj):
            return re.sub(rf'({re.escape(field)}:)(?:"[^"]*"|null)', rf'\g<1>{val}', obj)
        return obj[:-1].rstrip() + f',{field}:{val}' + '}'

    def patch_any(obj, field, val):
        """Patch field that may currently be a number, negative, or null."""
        return re.sub(rf'({re.escape(field)}:)(?:-?[\d.]+|null)', rf'\g<1>{val}', obj)

    def patch_str(obj, field, val):
        """Patch a string field that may currently be a quoted string or null."""
        return re.sub(rf'({re.escape(field)}:)(?:"[^"]*"|null)', rf'\g<1>{val}', obj)

    obj = patch(obj, r'score:\d+',      f'score:{score}')
    obj = patch_any(obj, 'ter',          ter)
    obj = patch(obj, r'ter_r:"[^"]*"',  f'ter_r:{ter_r}')
    obj = patch(obj, r'gaps:\d+',       f'gaps:{gaps}')
    obj = patch(obj, r'conf:"[^"]*"',   f'conf:{conf}')
    obj = patch_any(obj, 'math',         math)
    obj = patch_any(obj, 'grad',         grad)
    if fv("ap_participation_pct"):
        obj = patch_any(obj, 'ap',       ap)
    obj = patch_any(obj, 'bach',         bach)
    obj = patch_any(obj, 'unemp',        unemp)
    obj = patch_any(obj, 'pov',          pov)
    if fv("income_10yr_change_pct"):
        obj = patch_any(obj, 'inc10yr',  inc10)
    if fv("population_10yr_change_pct"):
        obj = patch_any(obj, 'pop10yr',  pop10)
    if fv("median_household_income"):
        obj = patch_any(obj, 'med_inc',  js_num("median_household_income"))
    if fv("free_cash_pct_of_budget"):
        obj = patch_any(obj, 'free_cash', free)
    if fv("debt_per_capita"):
        obj = patch_any(obj, 'debt_pc',  js_num("debt_per_capita"))
    if fv("bond_rating_sp"):
        obj = patch_str(obj, 'bond',     bond)
    if fv("district_rank_10yr_change"):
        # patch_any handles number or null; also handles old string values like "-10 spots"
        d10yr_val = js_num("district_rank_10yr_change")
        obj = re.sub(r'd_10yr:(?:-?[\d.]+|null|"[^"]*")', f'd_10yr:{d10yr_val}', obj)
    if fv("violent_crime_per_100k"):
        obj = patch_any(obj, 'violent',  viol)
    if fv("property_crime_per_100k"):
        obj = patch_any(obj, 'prop_crime', prop)
    if fv("crime_5yr_pct_change"):
        obj = patch_any(obj, 'crime5yr', js_num("crime_5yr_pct_change"))
    if fv("effective_tax_rate_pct"):
        obj = patch_any(obj, 'eff_rate', js_num("effective_tax_rate_pct"))
    if fv("median_annual_tax_bill"):
        obj = patch_any(obj, 'med_tax',  js_num("median_annual_tax_bill"))
    if fv("residential_rate_per_1000"):
        obj = patch_any(obj, 'res_rate', js_num("residential_rate_per_1000"))
    if fv("pension_funded_ratio_pct"):
        obj = patch_any(obj, 'pension',  pens)
    if fv("electric_savings_vs_state_avg"):
        obj = patch_any(obj, 'elec_save', js_num("electric_savings_vs_state_avg"))
    if fv("water_violations_5yr"):
        obj = patch_any(obj, 'water_viol', js_num("water_violations_5yr"))
    if fv("flood_risk_pct"):
        obj = patch_any(obj, 'flood',    flood)
    if fv("flood_2050_growth_pts"):
        obj = patch_any(obj, 'flood50',  fl50)
    if fv("wildfire_risk"):
        obj = patch_str(obj, 'fire',     fire)
    if fv("transit_access"):
        obj = patch_str(obj, 'transit',  js_str("transit_access"))

    obj = ensure_field(obj, 'p_schools', row["p_schools"])
    obj = ensure_field(obj, 'p_safety',  row["p_safety"])
    obj = ensure_field(obj, 'p_taxes',   row["p_taxes"])
    obj = ensure_field(obj, 'p_fiscal',  row["p_fiscal"])
    obj = ensure_field(obj, 'p_econ',    row["p_econ"])
    obj = ensure_field(obj, 'p_qol',     row["p_qol"])
    obj = ensure_field(obj, 'p_climate', row["p_climate"])

    if fv("value_rating"):
        obj = ensure_str_field(obj, 'value_rating', js_str("value_rating"))
    if fv("value_score"):
        obj = ensure_field(obj, 'value_score', js_num("value_score"))

    # Auto-generate glance/standout only if missing from this town's JS object
    _ps = {
        "schools":           float(row.get("p_schools") or 50),
        "safety":            float(row.get("p_safety") or 50),
        "taxes":             float(row.get("p_taxes") or 50),
        "fiscal_health":     float(row.get("p_fiscal") or 50),
        "economic_vitality": float(row.get("p_econ") or 50),
        "quality_of_life":   float(row.get("p_qol") or 50),
        "climate":           float(row.get("p_climate") or 50),
    }
    _cv = int(score) if score and str(score).lstrip("-").isdigit() else 0
    try:   _ter_f = float(ter) if ter and ter != "null" else None
    except: _ter_f = None
    _ter_r_s = ter_r.strip('"') if ter_r else "N/A"
    if not re.search(r'glance:"[^"]+"', obj):
        obj = _auto_insert_str(obj, "glance", _auto_glance(name, row, _cv, _ter_f, _ter_r_s, _ps))
    if not re.search(r'standout:"[^"]+"', obj):
        obj = _auto_insert_str(obj, "standout", _auto_standout(name, row, _cv, _ter_f, _ter_r_s, _ps))

    html = html[:s] + obj + html[e:]
    delta += len(obj) - (obj_end - obj_start)
    patched += 1

HTML_FILE.write_text(html, encoding="utf-8")
print(f"  Patched {patched} town objects")

# ─── Sync verification ────────────────────────────────────────────────────────
# After patching, confirm every tracked field in towns.csv matches the HTML.
# If something shows up here, it means a field was updated in towns.csv but
# the patch loop above isn't writing it back. Add a patch call for it above.
SYNC_FIELDS = [
    # (csv_column,                    html_field,   type)
    ("bond_rating_sp",               "bond",        "str"),
    ("free_cash_pct_of_budget",      "free_cash",   "num"),
    ("pension_funded_ratio_pct",     "pension",     "num"),
    ("debt_per_capita",              "debt_pc",     "num"),
    ("effective_tax_rate_pct",       "eff_rate",    "num"),
    ("median_annual_tax_bill",       "med_tax",     "num"),
    ("median_household_income",      "med_inc",     "num"),
    ("residential_rate_per_1000",    "res_rate",    "num"),
    ("test_scores_math_pct",         "math",        "num"),
    ("graduation_rate_pct",          "grad",        "num"),
    ("violent_crime_per_100k",       "violent",     "num"),
    ("property_crime_per_100k",      "prop_crime",  "num"),
    ("crime_5yr_pct_change",         "crime5yr",    "num"),
    ("income_10yr_change_pct",       "inc10yr",     "num"),
    ("population_10yr_change_pct",   "pop10yr",     "num"),
    ("flood_risk_pct",               "flood",       "num"),
    ("flood_2050_growth_pts",        "flood50",     "num"),
    ("wildfire_risk",                "fire",        "str"),
    ("transit_access",               "transit",     "str"),
    ("electric_savings_vs_state_avg","elec_save",   "num"),
    ("water_violations_5yr",         "water_viol",  "num"),
]
print("\nVerifying HTML sync with towns.csv...")
mismatches = []
for _row in rows:
    _town = _row["town_name"]
    _m = re.search(r'\{name:"' + re.escape(_town) + r'".*?\}', html)
    if not _m:
        continue
    _obj = _m.group()
    for _csv_col, _html_field, _ftype in SYNC_FIELDS:
        _csv_val = _row.get(_csv_col, "")
        if not _csv_val:
            continue
        if _ftype == "str":
            _pat = re.search(rf'{re.escape(_html_field)}:"([^"]*)"', _obj)
            _html_val = _pat.group(1) if _pat else None
            if _html_val and _html_val.lower() != str(_csv_val).lower():
                mismatches.append(f"  {_town}.{_html_field}: HTML={_html_val!r} != CSV={_csv_val!r}")
        else:
            _pat = re.search(rf'{re.escape(_html_field)}:(-?[\d.]+|null)', _obj)
            _html_val = _pat.group(1) if _pat else None
            if _html_val and _html_val != "null":
                try:
                    if abs(float(_html_val) - float(_csv_val)) > 0.05:
                        mismatches.append(f"  {_town}.{_html_field}: HTML={_html_val} != CSV={_csv_val}")
                except ValueError:
                    pass
if mismatches:
    print(f"  WARNING: {len(mismatches)} field(s) out of sync (towns.csv value not in HTML):")
    for _msg in mismatches[:25]:
        print(_msg)
    if len(mismatches) > 25:
        print(f"  ... and {len(mismatches)-25} more")
    print("  -> Add a patch call in update_all.py for each field above, or update towns.csv.")
else:
    print(f"  OK — all {len(SYNC_FIELDS)} tracked fields match across {len(rows)} towns")

# ─── Summary ──────────────────────────────────────────────────────────────────
print("\nSCORE CHANGES:")
print(f"{'Town':<28} {'Old':>5} {'New':>5} {'Delta':>7}")
print("-"*45)
for town, old, new, d in sorted(score_changes, key=lambda x: abs(x[3]), reverse=True):
    marker = " <-- LARGE CHANGE" if abs(d) >= 5 else ""
    print(f"{town:<28} {str(old):>5} {new:>5} {('+' if d>=0 else '')+str(d):>7}{marker}")
