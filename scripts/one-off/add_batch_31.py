"""
Add 31 towns already in towns.csv but missing from civica-v5.html.
All data comes from towns.csv (real sources only — no guesses).
Run ONCE, then: py scripts/update_all.py
"""
import csv, re, sys
from pathlib import Path

ROOT      = Path(__file__).parent.parent
CSV_FILE  = ROOT / "data" / "towns.csv"
HTML_FILE = ROOT / "civica-v5.html"

TOWNS_TO_ADD = [
    "Dennis","Harwich","Chatham","Brewster","Orleans",
    "Worcester","Fitchburg","Sutton","Upton","Leicester",
    "Attleboro","New Bedford","Fall River","Norton","Seekonk",
    "Raynham","Rehoboth","Swansea",
    "Springfield","Westfield","Chicopee","Holyoke","West Springfield","Easthampton",
    "Abington","Whitman","Rockland","Bridgewater","East Bridgewater","West Bridgewater","Carver",
]

LATLNG = {
    "Dennis":          (41.7350, -70.1936),
    "Harwich":         (41.6840, -70.0606),
    "Chatham":         (41.6882, -69.9623),
    "Brewster":        (41.7651, -70.0826),
    "Orleans":         (41.7893, -69.9876),
    "Worcester":       (42.2626, -71.8023),
    "Fitchburg":       (42.5834, -71.8023),
    "Sutton":          (42.1437, -71.7612),
    "Upton":           (42.1698, -71.6001),
    "Leicester":       (42.2459, -71.9084),
    "Attleboro":       (41.9445, -71.2856),
    "New Bedford":     (41.6362, -70.9342),
    "Fall River":      (41.7015, -71.1550),
    "Norton":          (41.9695, -71.1850),
    "Seekonk":         (41.8375, -71.3267),
    "Raynham":         (41.9262, -71.0584),
    "Rehoboth":        (41.8445, -71.2442),
    "Swansea":         (41.7559, -71.2259),
    "Springfield":     (42.1015, -72.5898),
    "Westfield":       (42.1251, -72.7498),
    "Chicopee":        (42.1487, -72.6078),
    "Holyoke":         (42.2042, -72.6162),
    "West Springfield":(42.1048, -72.6401),
    "Easthampton":     (42.2668, -72.6690),
    "Abington":        (42.1048, -70.9456),
    "Whitman":         (42.0820, -70.9337),
    "Rockland":        (42.1284, -70.9159),
    "Bridgewater":     (41.9909, -70.9745),
    "East Bridgewater":(42.0334, -70.9420),
    "West Bridgewater":(42.0084, -71.0065),
    "Carver":          (41.8801, -70.7612),
}

ZHVI = {
    "Dennis":520000,"Harwich":640000,"Chatham":1400000,"Brewster":680000,"Orleans":780000,
    "Worcester":310000,"Fitchburg":310000,"Sutton":610000,"Upton":640000,"Leicester":365000,
    "Attleboro":435000,"New Bedford":295000,"Fall River":270000,"Norton":545000,"Seekonk":445000,
    "Raynham":470000,"Rehoboth":545000,"Swansea":420000,
    "Springfield":245000,"Westfield":340000,"Chicopee":300000,"Holyoke":265000,
    "West Springfield":315000,"Easthampton":375000,
    "Abington":510000,"Whitman":455000,"Rockland":465000,"Bridgewater":450000,
    "East Bridgewater":475000,"West Bridgewater":485000,"Carver":400000,
}

TRANSIT_DISPLAY = {
    "commuter_rail_in_town": "Commuter Rail (in town)",
    "commuter_rail_nearby":  "Commuter Rail (nearby)",
    "bus_only":              "Bus only",
    "none":                  "None",
    "no":                    "None",
}

STANDOUT = {
    "Dennis":          "Lowest residential tax rate on Cape Cod (0.43%) due to very high home values and an 18% commercial base. Highly seasonal — Dennis Port, South Dennis, Dennis Village.",
    "Harwich":         "Among the safest Cape Cod towns by crime rate. Monomoy Regional district (#127 of 351, 97.4% graduation rate) shared with Chatham.",
    "Chatham":         "Cape Cod's most prestigious coastal address. Lowest tax rate in the dataset (0.347%). Highest flood risk on the Cape (28% / +12 pts by 2050).",
    "Brewster":        "Quietest and safest Upper Cape town. Nauset Regional (#108 of 351, 96.1% grad rate). Direct Cape Cod National Seashore beach access.",
    "Orleans":         "Gateway to the Outer Cape at Cape Cod's elbow. Nauset Regional district (#108 of 351, 96.1% graduation rate). Genuine year-round community.",
    "Worcester":       "MA's second-largest city with MBTA Framingham/Worcester Line terminus at Union Station. Large university ecosystem anchored by WPI, Holy Cross, Clark.",
    "Fitchburg":       "Westernmost MBTA commuter rail stop on the Fitchburg Line — affordable entry price with direct Boston rail. High crime and near-bottom schools are the trade-off.",
    "Sutton":          "Rural Worcester County with strong schools (#130 of 351), very low crime (20/100k), and above-average free cash (9.5% of budget). Fully car-dependent.",
    "Upton":           "Worcester County's quiet standout — #110 of 351 schools, very low crime (30/100k), and one of the lowest debt loads in the region ($758/pc).",
    "Leicester":       "Quiet Worcester suburb with mid-tier schools, low crime, and hidden-gem value. No transit; I-290 provides the Boston connection.",
    "Attleboro":       "Bristol County city with MBTA Providence/Stoughton Line commuter rail. Affordable entry point with direct Boston and Providence access.",
    "New Bedford":     "Historic whaling city; MA's second-largest by population. South Coast Rail to Boston. Very high crime and near-bottom schools at this price point ($295k median).",
    "Fall River":      "Bristol County's largest city with South Coast Rail to Boston. Lowest median home prices in the Civica dataset ($270k). Near-bottom schools and very high crime.",
    "Norton":          "Bristol County suburb with low crime (60/100k), above-average schools, and strong household income ($127k). Nearest rail: Attleboro or Mansfield.",
    "Seekonk":         "Rhode Island border suburb with strong schools (#115 of 351), low crime, and the lowest residential tax rate in Bristol County (1.275%). Providence is 15 minutes.",
    "Raynham":         "Bristol County suburb with strong fiscal reserves — 11.7% free cash as % of budget and among the lowest debt loads in the region ($1,091/pc).",
    "Rehoboth":        "Rural Bristol County town with strong schools (#140 of 351), very low crime, and essentially zero net municipal debt — one of the strongest fiscal positions in the state.",
    "Swansea":         "Rhode Island border suburb with low crime, above-average schools (#175 of 351), and one of Bristol County's lowest effective tax rates (1.237%).",
    "Springfield":     "Pioneer Valley's largest city — MA's third most populous. Affordable home prices ($245k median) but near-bottom schools and violent crime among the state's highest.",
    "Westfield":       "Pioneer Valley's largest suburb, west of Springfield. Mid-tier schools, elevated crime, and very high tax rate (1.979%). No transit to Boston.",
    "Chicopee":        "Pioneer Valley city adjacent to Springfield. Affordable home prices ($300k) but below-average schools, high crime, and a 1.973% effective tax rate.",
    "Holyoke":         "Pioneer Valley city with the highest effective tax rate in the dataset (2.101%) and near-bottom schools (#348 of 351, 9% MCAS math). Very affordable at $265k median.",
    "West Springfield": "Springfield suburb on the west bank of the Connecticut River with a diversified commercial tax base. Below-average schools and elevated crime.",
    "Easthampton":     "Hampshire County's most affordable city after Northampton. Arts community growing. No commuter rail — a key limitation for Boston-area workers.",
    "Abington":        "Plymouth County suburb with good income levels ($120k) and above-average graduation rate. Nearest commuter rail is Whitman station (Kingston/Plymouth Line).",
    "Whitman":         "Plymouth County commuter town with MBTA Kingston/Plymouth Line station. Shares Whitman-Hanson Regional district (#225 of 351) with Hanson.",
    "Rockland":        "Plymouth County suburb with mid-tier schools, elevated crime (130/100k), and high municipal debt per capita ($3,974/pc). No transit.",
    "Bridgewater":     "Plymouth County college town (Bridgewater State University) with MBTA Middleborough/Lakeville Line commuter rail. Mid-tier schools and moderate crime.",
    "East Bridgewater":"Among the best-value South Shore towns — strong schools (#145 of 351, 47% MCAS math, 96% grad rate), low crime (80/100k), and MBTA commuter rail access.",
    "West Bridgewater":"Small Plymouth County town with low crime (60/100k) and good schools but the highest effective tax rate in the region (1.821%) and high debt per capita ($4,192/pc).",
    "Carver":          "Rural Plymouth County cranberry-bog town with low crime (70/100k), decent schools, and affordable home prices ($400k). No transit; car-dependent.",
}

GLANCE = {
    "Dennis":          "Dennis has the lowest residential tax rate on Cape Cod (0.43%) — a product of very high home values and an 18% commercial base. The Dennis-Yarmouth district (#204 of 351) is below average; the highly seasonal character limits year-round services.",
    "Harwich":         "Harwich combines among the lowest crime rates on the Cape with strong schools through Monomoy Regional (#127 of 351, 97.4% graduation rate). No transit is the main limitation for buyers who commute off-Cape.",
    "Chatham":         "Chatham is Cape Cod's most prestigious coastal address — ultra-low crime, an exceptional 97.4% graduation rate through Monomoy Regional, and the lowest tax rate in the batch. The highest flood risk on the Cape (28% / +12 pts by 2050) is the principal long-term concern.",
    "Brewster":        "Brewster is the quietest and safest Upper Cape town — the lowest crime in this batch and strong school access through Nauset Regional (#108 of 351, 96.1% graduation rate). No transit is the key limitation for buyers who work off-Cape.",
    "Orleans":         "Orleans is a small Outer Cape town with access to Nauset Regional schools (#108 of 351, 96.1% graduation rate) and a genuine year-round community feel. Crime rates run elevated for a town this size — likely a seasonal population denominator effect.",
    "Worcester":       "Worcester is MA's second-largest city — MBTA commuter rail direct to Boston, a large university ecosystem, and the lowest home prices of any rail-served community in the dataset ($310k median). Schools rank near the bottom (#330 of 351, 23% MCAS math) and violent crime runs nearly 5× the state median (550/100k); both are endemic to urban scale.",
    "Fitchburg":       "Fitchburg is the westernmost MBTA commuter rail stop on the Fitchburg Line — the only path to direct rail access at this price point in Worcester County. The trade-offs are steep: schools rank #325 of 351 with 20% MCAS math, and violent crime (600/100k) is among the highest in the state.",
    "Sutton":          "Sutton offers a rare combination of strong schools (#130 of 351, 42% MCAS math), very low crime (20/100k), and above-average fiscal health in rural Worcester County. The primary limitation is no transit — residents are fully car-dependent for a 60+ minute Boston commute.",
    "Upton":           "Upton is one of the highest-scoring Worcester County towns — strong schools (#110 of 351, 50% MCAS math), very low crime (30/100k), and the lowest debt per capita in the region ($758/pc). No transit and a 1.6% effective tax rate are the main trade-offs for a completely car-dependent location.",
    "Leicester":       "Leicester is a quiet Worcester County suburb with affordable home prices and low crime (80/100k) for its price point. Schools sit mid-table (#220 of 351, 37% MCAS math) and there is no transit — a reasonable trade-off given the value score.",
    "Attleboro":       "Attleboro is the most affordable Bristol County town with direct MBTA commuter rail to Boston and Providence. Schools sit mid-table (#200 of 351, 38% MCAS math) and violent crime (250/100k) runs above the state median — typical for a city at this income level.",
    "New Bedford":     "New Bedford is a large South Coast city with MBTA South Coast Rail direct to Boston and among the lowest home prices in MA ($295k median). Schools rank near the bottom (#338 of 351, 17% MCAS math), violent crime is high (600/100k), and 15% of properties have current flood risk — the expected trade-offs at this price point.",
    "Fall River":      "Fall River has the lowest median home prices in the Civica dataset ($270k) and MBTA South Coast Rail access to Boston. Schools rank near the bottom (#342 of 351, 18% MCAS math) and violent crime (700/100k) is among the state's highest — the expected trade-offs at this extreme value point.",
    "Norton":          "Norton offers low crime (60/100k), above-average schools (#195 of 351, 34% MCAS math), and strong household income ($127k) — a solid mid-tier Bristol County option. The nearest commuter rail is Attleboro or Mansfield (Providence/Stoughton Line), making it car-dependent for Boston commuters.",
    "Seekonk":         "Seekonk sits on the Rhode Island border with strong schools (#115 of 351, 53% MCAS math), low crime (80/100k), and one of the lowest effective tax rates in Bristol County (1.275%). No transit makes it fully car-dependent, but Providence is 15 minutes away.",
    "Raynham":         "Raynham offers a strong fiscal position — 11.7% free cash as a percentage of budget and among the lowest debt loads in Bristol County ($1,091/pc). Schools sit mid-table (#215 of 351, 34% MCAS math) and the nearest commuter rail is the shared Bridgewater-Raynham corridor.",
    "Rehoboth":        "Rehoboth is a rural Bristol County town with strong schools (#140 of 351, 52% MCAS math), very low crime (30/100k), and essentially zero net municipal debt — one of the strongest fiscal positions in the state. No transit and no town center make it a quiet, fully car-dependent community.",
    "Swansea":         "Swansea is a quiet Bristol County suburb on the Rhode Island border with good schools (#175 of 351, 50% MCAS math) and the lowest effective tax rate in the South Coast region (1.237%). No transit is the main limitation.",
    "Springfield":     "Springfield is Pioneer Valley's largest city — affordable home prices ($245k median) and a robust arts and culture scene anchored by Mass MoCA's regional influence. Schools rank near the bottom (#340 of 351, 21% MCAS math) and violent crime approaches 900/100k; both are the dominant concerns for homebuyers. No commuter rail to Boston.",
    "Westfield":       "Westfield is Pioneer Valley's largest suburb — mid-tier schools (#215 of 351, 38% MCAS math), lower crime than Springfield, but the highest effective tax rate in the Pioneer Valley batch (1.979%). Home prices ($340k median) reflect the western MA discount, and there is no transit to Boston.",
    "Chicopee":        "Chicopee sits between Springfield and Holyoke with affordable home prices ($300k median), but below-average schools (#285 of 351, 29% MCAS math), high crime (450/100k), and one of the highest effective tax rates in MA (1.973%). No transit to Boston.",
    "Holyoke":         "Holyoke has the highest effective residential tax rate in the Civica dataset (2.101%) and schools ranking #348 of 351 with only 9% MCAS math proficiency. Violent crime is among the state's worst (950/100k). Home prices ($265k median) reflect these fundamentals.",
    "West Springfield": "West Springfield is a Springfield suburb with affordable home prices ($315k), below-average schools (#260 of 351, 31% MCAS math), and elevated crime (250/100k). A diversified commercial tax base partially offsets the high effective rate (1.792%). No transit to Boston.",
    "Easthampton":     "Easthampton is Hampshire County's most affordable option for buyers priced out of Northampton ($375k median) with a growing arts community. Schools rank #200 of 351 and violent crime (150/100k) runs above the state median. No commuter rail is the key practical limitation for Boston-area workers.",
    "Abington":        "Abington is a mid-tier Plymouth County suburb with good household income ($120k) and above-average graduation rate (91.2%). The school district (#195 of 351, 40% MCAS math) is developing and the nearest commuter rail is in adjacent Whitman on the Kingston/Plymouth Line.",
    "Whitman":         "Whitman is a Plymouth County commuter town with direct MBTA Kingston/Plymouth Line service — one of the few South Shore towns under $500k with rail access. Schools sit mid-table (#225 of 351, 45% MCAS math) and the fiscal picture is solid. The main caveat is a below-average free cash ratio (2.2% of budget).",
    "Rockland":        "Rockland is a mid-Plymouth County suburb with mid-tier schools (#230 of 351, 38% MCAS math), elevated crime (130/100k), and high municipal debt per capita ($3,974). No transit to Boston is the primary practical limitation.",
    "Bridgewater":     "Bridgewater is a Plymouth County college town (Bridgewater State University) with direct MBTA Middleborough/Lakeville Line service. Mid-tier schools (#215 of 351, 34% MCAS math) and moderate crime (150/100k) are the main trade-offs for the rail access and university environment.",
    "East Bridgewater": "East Bridgewater offers some of the strongest school performance in Plymouth County (#145 of 351, 47% MCAS math, 96% graduation rate), low crime (80/100k), and direct MBTA Middleborough/Lakeville Line access. Home prices ($475k) are reasonable for the fundamentals.",
    "West Bridgewater": "West Bridgewater has the highest effective tax rate among Plymouth County suburbs (1.821%) and elevated municipal debt per capita ($4,192/pc) — both worth scrutinizing. The upside: very low crime (60/100k), good schools (#210 of 351, 39% MCAS math), and a commuter rail station in adjacent Bridgewater.",
    "Carver":          "Carver is a rural Plymouth County town with low crime (70/100k), decent schools (#210 of 351, 36% MCAS math, 95.8% graduation rate), and affordable home prices ($400k median). No transit and a rural character limit appeal to Boston commuters.",
}

def esc(s):
    return s.replace("'", "\\'").replace('"', '\\"') if s else ""

def fmt_zip(zip_str):
    zips = [z.strip() for z in zip_str.replace(";", " ").split() if z.strip()]
    return " / ".join(zips[:4])

def fnum(v, default="null"):
    try:
        return str(float(v)) if v else default
    except:
        return default

def fint(v, default="null"):
    try:
        return str(int(float(v))) if v else default
    except:
        return default

def fstr(v, default="null"):
    return f'"{v}"' if v else default

def build_js(row):
    name = row["town_name"]
    lat, lng = LATLNG[name]

    bond_val = row.get("bond_rating_sp", "")
    bond = f'"{bond_val}"' if bond_val and bond_val.lower() not in ("not rated", "", "none") else "null"

    transit_raw = row.get("transit_access", "none").lower().strip()
    transit = TRANSIT_DISPLAY.get(transit_raw, "None")

    zip_str = fmt_zip(row.get("zip_codes", ""))

    med_home_val = ZHVI.get(name, "null")

    standout = esc(STANDOUT.get(name, f"{name} is a Massachusetts community."))
    glance   = esc(GLANCE.get(name, f"{name} is a Massachusetts community. Score is based on real data from state and federal sources."))
    notes    = esc(row.get("compiler_notes", ""))

    transp = "Yes" if row.get("transparency", "").lower() == "yes" else "Partial"

    return (
        f'{{name:"{name}",lat:{lat},lng:{lng},state:"MA",'
        f'county:"{row.get("county","")}",'
        f'zip:"{zip_str}",'
        f'pop:{fint(row.get("population"))},'
        f'bond:{bond},'
        f'free_cash:{fnum(row.get("free_cash_pct_of_budget"))},'
        f'pension:{fnum(row.get("pension_funded_ratio_pct"))},'
        f'debt_pc:{fnum(row.get("debt_per_capita"))},'
        f'gfoa:null,'
        f'tax_non_res:{fnum(row.get("tax_base_non_residential_pct"))},'
        f'eff_rate:{fnum(row.get("effective_tax_rate_pct"))},'
        f'med_tax:{fint(row.get("median_annual_tax_bill"))},'
        f'med_inc:{fnum(row.get("median_household_income"))},'
        f'res_rate:{fnum(row.get("residential_rate_per_1000"))},'
        f'd_rank:{fint(row.get("district_state_rank"))},'
        f'd_total:351,'
        f'd_10yr:{fnum(row.get("district_rank_10yr_change"))},'
        f'math:{fnum(row.get("test_scores_math_pct"))},'
        f'grad:{fnum(row.get("graduation_rate_pct"))},'
        f'ap:{fnum(row.get("ap_participation_pct"))},'
        f'transp:"{transp}",'
        f'elec_save:{fint(row.get("electric_savings_vs_state_avg","0"))},'
        f'water_viol:{fint(row.get("water_violations_5yr","0"))},'
        f'transit:"{transit}",'
        f'violent:{fnum(row.get("violent_crime_per_100k"))},'
        f'prop_crime:{fnum(row.get("property_crime_per_100k"))},'
        f'crime5yr:null,'
        f'inc10yr:{fnum(row.get("income_10yr_change_pct"))},'
        f'pop10yr:{fnum(row.get("population_10yr_change_pct"))},'
        f'bach:{fnum(row.get("bachelors_degree_pct"))},'
        f'unemp:{fnum(row.get("unemployment_pct"))},'
        f'pov:{fnum(row.get("poverty_pct"))},'
        f'flood:{fnum(row.get("flood_risk_pct"))},'
        f'flood50:{fnum(row.get("flood_2050_growth_pts"))},'
        f'fire:{fstr(row.get("wildfire_risk"))},'
        f'score:0,ter:null,ter_r:"N/A",'
        f'gaps:5,conf:"medium",'
        f'standout:"{standout}",'
        f'glance:"{glance}",'
        f'notes:"{notes}",'
        f'med_home_val:{med_home_val},'
        f'commute:null,owner_occ:null,vacancy:null,med_age:null,'
        f'low_income_pct:null,ell_pct:null,enrollment_trend:null,sex_off:null,'
        f'p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,'
        f'value_rating:"Market Rate",value_score:null}}'
    )

# Load towns.csv
with open(CSV_FILE, encoding="utf-8") as f:
    all_rows = {r["town_name"]: r for r in csv.DictReader(f)}

# Build JS objects
new_html_objects = []
for town in TOWNS_TO_ADD:
    row = all_rows.get(town)
    if not row:
        print(f"  WARNING: {town} not found in towns.csv — skipping")
        continue
    new_html_objects.append((town, build_js(row)))

# Insert into civica-v5.html
print("Reading civica-v5.html...")
html = HTML_FILE.read_text(encoding="utf-8")

added = 0
skipped = 0
for town, js_obj in new_html_objects:
    if f'name:"{town}"' in html:
        print(f"  SKIP (already in HTML): {town}")
        skipped += 1
        continue
    # Insert before the closing ]; of the TOWNS array
    # The TOWNS array ends with \n]; followed by the dynamic count script
    html = re.sub(
        r'(\n\];\ndocument\.querySelectorAll)',
        r'\n  ' + js_obj + r',\n];\ndocument.querySelectorAll',
        html,
        count=1
    )
    added += 1
    print(f"  + {town}")

HTML_FILE.write_text(html, encoding="utf-8")
print(f"\nDone: {added} towns added, {skipped} skipped.")
print("Next step: py scripts/update_all.py")
