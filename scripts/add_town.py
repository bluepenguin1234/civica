"""
Add a single new MA town to towns.csv and civica-v5.html in one command.

Auto-fills from bulk data: census (income, pop, education), schools (math%, grad%, AP%),
free-cash Excel, debt Excel, and computes district rank from bulk composite.

Usage:
  py scripts/add_town.py "Northampton" ^
      --lat 42.3251 --lng -72.6412 ^
      --zip "01060,01062" --zhvi 470000 --county Hampshire ^
      --transit "none"

Required:
  town_name          Town name (must match DLS / census spelling)
  --lat              Latitude
  --lng              Longitude
  --zip              Zip code(s), comma-separated if multiple
  --zhvi             Median home value in dollars (Zillow ZHVI)
  --county           County name

Optional (can be added later / updated by update_all.py):
  --transit          commuter_rail_in_town | commuter_rail_nearby | bus_only | none
  --bond             S&P bond rating (AAA, AA+, AA, AA-, A+, A, etc.)
  --pension          Pension funded ratio (%)
  --eff-rate         Effective tax rate (%)
  --res-rate         Residential rate per $1000
  --med-tax          Median annual tax bill ($)
  --violent          Violent crime per 100k
  --prop-crime       Property crime per 100k
  --water-viol       Water violations (5yr count)
  --elec-save        Electric savings vs MA avg ($/yr)
  --flood            Flood risk (%)
  --flood50          Flood 2050 growth points
  --wildfire         Wildfire risk: Low | Medium | High
  --commute          Median commute time (minutes)
  --lat-dry-run      Print JS object without modifying files
"""

import sys, csv, re, argparse, openpyxl
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path

ROOT      = Path(__file__).parent.parent
CSV_FILE  = ROOT / "data" / "towns.csv"
HTML_FILE = ROOT / "civica-v5.html"
BULK      = ROOT / "data" / "bulk"

# ─── Parse args ───────────────────────────────────────────────────────────────
ap = argparse.ArgumentParser(description="Add a new town to the Civica data pipeline")
ap.add_argument("town", help="Town name")
ap.add_argument("--lat",        type=float, required=True)
ap.add_argument("--lng",        type=float, required=True)
ap.add_argument("--zip",        required=True, dest="zip_codes")
ap.add_argument("--zhvi",       type=float, required=True, help="Median home value (Zillow)")
ap.add_argument("--county",     required=True)
ap.add_argument("--transit",    default="none")
ap.add_argument("--bond",       default="")
ap.add_argument("--pension",    type=float, default=None)
ap.add_argument("--eff-rate",   type=float, default=None, dest="eff_rate")
ap.add_argument("--res-rate",   type=float, default=None, dest="res_rate")
ap.add_argument("--med-tax",    type=float, default=None, dest="med_tax")
ap.add_argument("--violent",    type=float, default=None)
ap.add_argument("--prop-crime", type=float, default=None, dest="prop_crime")
ap.add_argument("--water-viol", type=int,   default=None, dest="water_viol")
ap.add_argument("--elec-save",  type=float, default=None, dest="elec_save")
ap.add_argument("--flood",      type=float, default=None)
ap.add_argument("--flood50",    type=float, default=None)
ap.add_argument("--wildfire",   default="Low")
ap.add_argument("--commute",    type=float, default=None)
ap.add_argument("--dry-run",    action="store_true")
args = ap.parse_args()

town = args.town
print(f"\nAdding: {town}")

# ─── Load bulk data ────────────────────────────────────────────────────────────
def load_csv_index(path, key_col, transform=None):
    idx = {}
    if not path.exists():
        print(f"  WARNING: missing {path.name}")
        return idx
    for r in csv.DictReader(open(path, encoding="utf-8")):
        k = (transform(r[key_col]) if transform else r[key_col]).strip()
        idx[k] = r
    return idx

census  = load_csv_index(BULK / "census_acs_ma_towns.csv", "town_name", str.lower)
schools = load_csv_index(BULK / "ma_schools_combined.csv", "district_name", str.lower)

# Compute district ranks (same composite as update_all.py: math 50%, grad 30%, AP 20%)
_rank_scored = []
for _dname, _d in schools.items():
    try:
        _m = float(_d.get("mcas_math_pct") or 0)
        _g = float(_d.get("graduation_rate_pct") or 0)
        _a = float(_d.get("ap_participation_pct") or 0)
        if _m > 0 or _g > 0:
            _rank_scored.append((_dname, _m * 0.5 + _g * 0.3 + _a * 0.2))
    except: pass
_rank_scored.sort(key=lambda x: x[1], reverse=True)
RANK_TOTAL = len(_rank_scored)
DISTRICT_RANKS = {name: rank + 1 for rank, (name, _) in enumerate(_rank_scored)}

# Free Cash Excel
free_cash_val = None
fc_path = BULK / "CFC_PerBudg.xlsx"
if fc_path.exists():
    wb = openpyxl.load_workbook(fc_path, read_only=True, data_only=True)
    ws = wb.active
    rows_it = ws.iter_rows(values_only=True)
    hdrs = [str(h).strip() if h else "" for h in next(rows_it)]
    def _fc(hs, *kw): return next((i for i, h in enumerate(hs) if all(k in h.lower() for k in kw)), None)
    mi = _fc(hdrs, "municipality"); fi = _fc(hdrs, "fiscal year") or _fc(hdrs, "fy")
    ci = _fc(hdrs, "%", "budget") or _fc(hdrs, "% of")
    if None not in (mi, fi, ci):
        best = {}
        for r in rows_it:
            muni = str(r[mi]).strip().lower() if r[mi] else ""
            if not muni or muni == "none": continue
            try: fy = int(float(str(r[fi])))
            except: continue
            try: pct = round(float(r[ci]) * 100, 2) if r[ci] else None
            except: pct = None
            if pct is not None:
                best.setdefault(muni, {})[fy] = pct
        if town.lower() in best:
            yrs = best[town.lower()]
            free_cash_val = yrs[max(yrs)]
    wb.close()

# Debt per capita Excel
debt_pc_val = None
debt_path = BULK / "municipaldebt2022.xlsx"
if debt_path.exists():
    wb = openpyxl.load_workbook(debt_path, read_only=True, data_only=True)
    ws = wb["Debt"] if "Debt" in wb.sheetnames else wb.active
    rows_it = ws.iter_rows(values_only=True)
    hdrs = None
    for _ in range(20):
        r = next(rows_it, None)
        if r and any(str(c).strip().lower() == "municipality" for c in r if c):
            hdrs = [str(c).strip() if c else "" for c in r]; break
    if hdrs:
        def _fc2(hs, *kw): return next((i for i, h in enumerate(hs) if all(k in h.lower() for k in kw)), None)
        mi2 = _fc2(hdrs, "municipality"); fi2 = _fc2(hdrs, "fy")
        di2 = _fc2(hdrs, "total outstanding debt") or _fc2(hdrs, "outstanding debt")
        if None not in (mi2, fi2, di2):
            cur_muni = ""; raw = {}
            for r in rows_it:
                if r[mi2]: cur_muni = str(r[mi2]).strip()
                if not cur_muni: continue
                try: fy = int(float(str(r[fi2])))
                except: continue
                try: dv = float(r[di2]) if r[di2] else None
                except: dv = None
                if dv: raw.setdefault(cur_muni.lower(), {})[fy] = dv
            if town.lower() in raw:
                best_debt = raw[town.lower()]
                best_debt = best_debt[max(best_debt)]
                c = census.get(town.lower()) or census.get(town.lower() + " town")
                if c:
                    try:
                        pop = float(c.get("population") or 0)
                        if pop > 0: debt_pc_val = round(best_debt / pop, 0)
                    except: pass
    wb.close()

# ─── Regional school districts ────────────────────────────────────────────────
DISTRICT_MAP = {
    "Boxford": "masconomet", "Topsfield": "masconomet", "Middleton": "masconomet",
    "Hamilton": "hamilton-wenham", "Wenham": "hamilton-wenham",
    "Manchester-by-the-Sea": "manchester essex", "Essex": "manchester essex",
    "Merrimac": "pentucket", "Groveland": "pentucket",
    "West Newbury": "pentucket", "Georgetown": "pentucket",
    "Rowley": "triton", "Salisbury": "triton", "Newbury": "triton",
    "Nahant": "lynn", "Acton": "acton-boxborough", "Concord": "concord-carlisle",
    "Kingston": "silver lake", "Northborough": "northborough-southborough",
    "North Attleborough": "north attleborough",
    "Yarmouth": "dennis-yarmouth", "Dennis": "dennis-yarmouth",
    "Harwich": "monomoy regional school district",
    "Chatham": "monomoy regional school district",
    "Brewster": "nauset", "Orleans": "nauset",
    "Holden": "wachusett", "Southborough": "northborough-southborough",
    "Upton": "mendon-upton", "Raynham": "bridgewater-raynham",
    "Rehoboth": "dighton-rehoboth", "Whitman": "whitman-hanson",
    "Bridgewater": "bridgewater-raynham", "Marion": "old rochester",
}

def get_school(t):
    d = DISTRICT_MAP.get(t, t).lower()
    if d in schools: return schools[d]
    for k, v in schools.items():
        if d.split()[0] in k: return v
    return None

def get_school_rank(t):
    d = DISTRICT_MAP.get(t, t).lower()
    if d in DISTRICT_RANKS: return DISTRICT_RANKS[d], RANK_TOTAL
    for k in DISTRICT_RANKS:
        if d.split()[0] in k: return DISTRICT_RANKS[k], RANK_TOTAL
    return None, None

# ─── Gather data ──────────────────────────────────────────────────────────────
c   = census.get(town.lower()) or census.get(town.lower() + " town")
sc  = get_school(town)
d_rank, d_total = get_school_rank(town)

med_inc    = float(c["median_household_income"])    if c and c.get("median_household_income") else None
pop        = int(float(c["population"]))             if c and c.get("population") else None
bach       = float(c["bachelors_degree_pct"])        if c and c.get("bachelors_degree_pct") else None
pov        = float(c["poverty_pct"])                 if c and c.get("poverty_pct") else None
unemp      = float(c["unemployment_pct"])            if c and c.get("unemployment_pct") else None
inc10yr    = float(c["income_10yr_change_pct"])      if c and c.get("income_10yr_change_pct") else None
pop10yr    = float(c["population_10yr_change_pct"])  if c and c.get("population_10yr_change_pct") else None

math  = float(sc["mcas_math_pct"])       if sc and sc.get("mcas_math_pct") else None
grad  = float(sc["graduation_rate_pct"]) if sc and sc.get("graduation_rate_pct") else None
ap    = float(sc["ap_participation_pct"]) if sc and sc.get("ap_participation_pct") else None

ha_ratio = round(args.zhvi / med_inc, 2) if med_inc and args.zhvi else None

TRANSIT_DISPLAY = {
    "commuter_rail_in_town": "Commuter Rail (in town)",
    "commuter_rail_nearby":  "Commuter Rail (nearby)",
    "bus_only":              "Bus only",
    "none":                  "None",
    "no":                    "None",
}
transit_disp = TRANSIT_DISPLAY.get(args.transit.lower().strip(), args.transit)

def _js_num(v):  return str(v) if v is not None else "null"
def _js_str(v):  return f'"{v}"' if v else "null"
def _js_str_req(v): return f'"{v}"'

# ─── Build CSV row ─────────────────────────────────────────────────────────────
existing_towns = []
fieldnames = []
with open(CSV_FILE, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = list(reader.fieldnames)
    existing_towns = list(reader)

if any(r["town_name"] == town for r in existing_towns):
    print(f"  ERROR: {town} already exists in towns.csv — aborting.")
    sys.exit(1)

new_row = {f: "" for f in fieldnames}
new_row.update({
    "town_name":                   town,
    "state":                       "MA",
    "county":                      args.county,
    "zip_codes":                   args.zip_codes,
    "population":                  str(pop) if pop else "",
    "bond_rating_sp":              args.bond or "",
    "free_cash_pct_of_budget":     str(free_cash_val) if free_cash_val else "",
    "pension_funded_ratio_pct":    str(args.pension) if args.pension else "",
    "debt_per_capita":             str(debt_pc_val) if debt_pc_val else "",
    "effective_tax_rate_pct":      str(args.eff_rate) if args.eff_rate else "",
    "residential_rate_per_1000":   str(args.res_rate) if args.res_rate else "",
    "median_annual_tax_bill":      str(args.med_tax) if args.med_tax else "",
    "median_household_income":     str(med_inc) if med_inc else "",
    "district_state_rank":         str(d_rank) if d_rank else "",
    "district_state_rank_total":   str(d_total) if d_total else "351",
    "test_scores_math_pct":        str(math) if math else "",
    "graduation_rate_pct":         str(grad) if grad else "",
    "ap_participation_pct":        str(ap) if ap else "",
    "transit_access":              args.transit,
    "violent_crime_per_100k":      str(args.violent) if args.violent else "",
    "property_crime_per_100k":     str(args.prop_crime) if args.prop_crime else "",
    "water_violations_5yr":        str(args.water_viol) if args.water_viol is not None else "",
    "electric_savings_vs_state_avg": str(args.elec_save) if args.elec_save else "",
    "flood_risk_pct":              str(args.flood) if args.flood else "",
    "flood_2050_growth_pts":       str(args.flood50) if args.flood50 else "",
    "wildfire_risk":               args.wildfire,
    "income_10yr_change_pct":      str(inc10yr) if inc10yr else "",
    "population_10yr_change_pct":  str(pop10yr) if pop10yr else "",
    "bachelors_degree_pct":        str(bach) if bach else "",
    "unemployment_pct":            str(unemp) if unemp else "",
    "poverty_pct":                 str(pov) if pov else "",
    "housing_affordability_ratio": str(ha_ratio) if ha_ratio else "",
    "data_confidence":             "low",
    "last_updated":                "2026-05-14",
})

# ─── Build JS object ───────────────────────────────────────────────────────────
def _js(v, default="null"):
    if v is None or v == "": return default
    try: return str(float(v)) if "." in str(v) else str(int(float(v)))
    except: return default

fields = {
    "name":       f'"{town}"',
    "lat":        str(args.lat),
    "lng":        str(args.lng),
    "state":      '"MA"',
    "county":     f'"{args.county}"',
    "zip":        f'"{args.zip_codes}"',
    "pop":        _js(pop),
    "bond":       f'"{args.bond}"' if args.bond else "null",
    "free_cash":  _js(free_cash_val),
    "pension":    _js(args.pension),
    "debt_pc":    _js(debt_pc_val),
    "eff_rate":   _js(args.eff_rate),
    "med_tax":    _js(args.med_tax),
    "med_inc":    _js(med_inc),
    "res_rate":   _js(args.res_rate),
    "d_rank":     _js(d_rank),
    "d_total":    _js(d_total, "351"),
    "d_10yr":     "null",
    "math":       _js(math),
    "grad":       _js(grad),
    "ap":         _js(ap),
    "transp":     '"Yes"',
    "elec_save":  _js(args.elec_save),
    "water_viol": _js(args.water_viol),
    "transit":    f'"{transit_disp}"',
    "violent":    _js(args.violent),
    "prop_crime": _js(args.prop_crime),
    "crime5yr":   "null",
    "inc10yr":    _js(inc10yr),
    "pop10yr":    _js(pop10yr),
    "bach":       _js(bach),
    "unemp":      _js(unemp),
    "pov":        _js(pov),
    "flood":      _js(args.flood),
    "flood50":    _js(args.flood50),
    "fire":       f'"{args.wildfire}"',
    "score":      "0",
    "ter":        "null",
    "ter_r":      '"N/A"',
    "gaps":       "99",
    "conf":       '"low"',
    "med_home_val": str(int(args.zhvi)),
    "commute":    _js(args.commute),
}

js_obj = "{" + ",".join(f"{k}:{v}" for k, v in fields.items()) + "}"

# ─── Report what was found vs missing ─────────────────────────────────────────
print("\n  Auto-filled from bulk data:")
if c:   print(f"    census: pop={pop:,}, med_inc=${int(med_inc):,}, bach={bach}%, pov={pov}%, unemp={unemp}%")
else:   print(f"    census: NOT FOUND — check spelling matches census_acs_ma_towns.csv")
if sc:  print(f"    schools: math={math}%, grad={grad}%, ap={ap}%")
else:   print(f"    schools: NOT FOUND — check DISTRICT_MAP in add_town.py")
if d_rank: print(f"    district rank: #{d_rank} of {d_total} (computed from bulk composite)")
else:      print(f"    district rank: NOT COMPUTED")
if free_cash_val: print(f"    free cash: {free_cash_val}%")
else:             print(f"    free cash: not in Excel bulk")
if debt_pc_val:   print(f"    debt/capita: ${debt_pc_val:,.0f}")
else:             print(f"    debt/capita: not in Excel bulk")

print("\n  Still needs manual lookup (or will default to null):")
missing = []
if not args.bond:      missing.append("bond_rating (S&P MFOB or Moody's)")
if not args.pension:   missing.append("pension_funded_ratio_pct (PERAC)")
if not args.eff_rate:  missing.append("effective_tax_rate_pct (DLS Gateway)")
if not args.res_rate:  missing.append("residential_rate_per_1000 (DLS Gateway)")
if not args.med_tax:   missing.append("median_annual_tax_bill (DLS)")
if not args.violent:   missing.append("violent_crime_per_100k (beyond2020.com)")
if not args.prop_crime: missing.append("property_crime_per_100k (beyond2020.com)")
if not args.flood:     missing.append("flood_risk_pct (RiskFactor.com)")
if not args.elec_save: missing.append("electric_savings (only if municipal electric)")
for m in missing:
    print(f"    - {m}")

if args.dry_run:
    print(f"\n  [DRY RUN] JS object:\n{js_obj}")
    print("\n  No files modified (--dry-run).")
    sys.exit(0)

# ─── Write to towns.csv ────────────────────────────────────────────────────────
existing_towns.append(new_row)
with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(existing_towns)
print(f"\n  Added to towns.csv ({len(existing_towns)} total towns)")

# ─── Insert into civica-v5.html ────────────────────────────────────────────────
html = HTML_FILE.read_text(encoding="utf-8")
insertion_pat = r'(\n\];\s*\ndocument\.querySelectorAll)'
if not re.search(insertion_pat, html):
    print("  ERROR: Could not find TOWNS array closing in HTML. Pattern not matched.")
    sys.exit(1)

html = re.sub(insertion_pat, r'\n  ' + js_obj + r',\1', html, count=1)
HTML_FILE.write_text(html, encoding="utf-8")
print(f"  Inserted JS object into civica-v5.html")

print(f"""
  Next steps:
    1. Run: py scripts\\update_all.py
       (scores the town, fills remaining bulk data, patches HTML)
    2. Add missing data fields above (bond, pension, tax, crime, flood)
    3. Edit glance/standout text in the HTML if auto-generated text needs refinement
    4. Validate: node _t.js  (quick JS syntax check)
""")
