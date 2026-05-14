"""
Master update pipeline — applies all new data, recomputes scores,
updates towns.csv and civica-v5.html in one pass.
"""

import csv, re, openpyxl, bisect
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

# Direction for percentile scoring: True = higher raw value is better, False = lower is better
DIRECTION = {
    # Higher raw value = better score
    "free_cash_pct": True,  "pension_funded": True,  "rank_percentile": True,
    "test_scores": True,  "graduation_rate": True,
    "electric_value": True,  "income_level": True,
    "income_trend": True,  "population_trend": True,
    # Lower raw value = better score
    "debt_per_capita": False,  "effective_tax_rate": False,  "tax_burden_to_income": False,
    "rank_trajectory": False,  "water_quality": False,  "violent_crime": False,
    "property_crime": False,  "crime_trajectory": False,
    "flood_risk": False,  "flood_trajectory": False,
}
LOOKUP_ONLY = {"bond_rating", "transit", "wildfire"}

def cap(val, lo, hi):
    if val is None: return None
    try: return max(lo, min(hi, float(val)))
    except: return val

def percentile_score(value, sorted_vals, higher_is_better):
    n = len(sorted_vals)
    below = bisect.bisect_left(sorted_vals, value)
    above = bisect.bisect_right(sorted_vals, value)
    pct = 100.0 * (below + (above - below) / 2.0) / n
    return round(100.0 - pct if not higher_is_better else pct)

def score_submetric(sm_id, raw, ri, dists=None):
    if sm_id not in ri: return 50
    rules = ri[sm_id]
    default = float(rules[0]["default_if_missing"])
    if raw is None or raw == "": return default
    if dists and sm_id in dists and sm_id not in LOOKUP_ONLY and sm_id in DIRECTION:
        try:
            v = float(raw)
            if len(dists[sm_id]) >= 5:
                return percentile_score(v, dists[sm_id], DIRECTION[sm_id])
        except: pass
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

def score_town(td, pw, sw, ri, si, dists=None):
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
    ss = {sm: score_submetric(sm, val, ri, dists) for sm, val in SM.items()}
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

def build_distributions(rows, si):
    """First pass: collect all SM values to build percentile distributions."""
    raw_vals = {}
    for td in rows:
        ctx = si.get(td.get("state","MA"), si["MA"])
        def sf(a, b):
            try: return float(a)/float(b)
            except: return None
        def fv(k): return td.get(k) or None
        h = {
            "tax_burden_pct":      (float(td["median_annual_tax_bill"])/float(td["median_household_income"])*100)
                                    if td.get("median_annual_tax_bill") and td.get("median_household_income") else None,
            "rank_percentile":     (1-float(td["district_state_rank"])/float(td["district_state_rank_total"]))*100
                                    if td.get("district_state_rank") and td.get("district_state_rank_total") else None,
            "debt_ratio":          sf(fv("debt_per_capita"), ctx["debt_per_capita_median"]),
            "violent_crime_ratio": sf(fv("violent_crime_per_100k"), ctx["violent_crime_per_100k"]),
            "property_crime_ratio":sf(fv("property_crime_per_100k"), ctx["property_crime_per_100k"]),
            "income_ratio":        sf(fv("median_household_income"), ctx["median_household_income"]),
        }
        sm_vals = {
            "free_cash_pct":        fv("free_cash_pct_of_budget"),
            "pension_funded":       fv("pension_funded_ratio_pct"),
            "debt_per_capita":      h["debt_ratio"],
            "effective_tax_rate":   fv("effective_tax_rate_pct"),
            "tax_burden_to_income": h["tax_burden_pct"],
            "rank_percentile":      h["rank_percentile"],
            "rank_trajectory":      cap(fv("district_rank_10yr_change"), -150, 150),
            "test_scores":          fv("test_scores_math_pct"),
            "graduation_rate":      fv("graduation_rate_pct"),
            "violent_crime":        h["violent_crime_ratio"],
            "property_crime":       h["property_crime_ratio"],
            "crime_trajectory":     cap(fv("crime_5yr_pct_change"), -75, 150),
            "income_level":         h["income_ratio"],
            "income_trend":         fv("income_10yr_change_pct"),
            "population_trend":     fv("population_10yr_change_pct"),
            "electric_value":       fv("electric_savings_vs_state_avg"),
            "water_quality":        cap(fv("water_violations_5yr"), 0, 100),
            "flood_risk":           fv("flood_risk_pct"),
            "flood_trajectory":     fv("flood_2050_growth_pts"),
        }
        for sm_id, val in sm_vals.items():
            if val is not None:
                try: raw_vals.setdefault(sm_id, []).append(float(val))
                except: pass
    return {sm_id: sorted(vals) for sm_id, vals in raw_vals.items()}

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
    "Sudbury":1050000,"Westwood":1050000,"Holliston":580000,"Bedford":750000,
    "Randolph":450000,"Pembroke":510000,"Northbridge":420000,"Wrentham":590000,
    "Maynard":490000,"Tyngsborough":480000,
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
}

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

# ─── Phase 2: Build percentile distributions ──────────────────────────────────
print("Phase 2: Building percentile distributions...")
dists = build_distributions(rows, si)
for sm_id, vals in sorted(dists.items()):
    print(f"  {sm_id}: n={len(vals)}, range=[{min(vals):.2f}, {max(vals):.2f}]")

# ─── Phase 3: Score all towns ─────────────────────────────────────────────────
print("Phase 3: Scoring all towns...")
score_changes = []
for row in rows:
    town = row["town_name"]
    old_score = row.get("civica_score", "")
    civica, ter, ter_r, gaps, conf, ps = score_town(row, pw, sw, ri, si, dists)
    row["civica_score"]     = str(civica)
    row["ter"]              = str(ter) if ter else ""
    row["ter_rating"]       = ter_r
    row["data_gaps_count"]  = str(gaps)
    row["data_confidence"]  = conf
    row["last_updated"]     = "2026-05-13"
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
