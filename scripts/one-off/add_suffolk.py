"""
Add Suffolk County towns (Boston, Revere, Winthrop) to towns.csv and civica-v5.html.
Chelsea is already in the dataset.  Run this BEFORE update_all.py.
"""
import csv, re
from pathlib import Path

ROOT      = Path(__file__).parent.parent
CSV_FILE  = ROOT / "data" / "towns.csv"
HTML_FILE = ROOT / "civica-v5.html"

# ─── Town data ────────────────────────────────────────────────────────────────
# Census / DESE / bulk Excel will fill: bachelors_degree_pct, poverty_pct,
# unemployment_pct, income_10yr_change_pct, population_10yr_change_pct,
# median_household_income, test_scores_math_pct, graduation_rate_pct,
# ap_participation_pct, free_cash_pct_of_budget, debt_per_capita.
# Everything else is hardcoded here from MA DOR / FBI UCR / FEMA / PERAC.

NEW_TOWNS = [
    {
        "town_name":   "Boston",
        "state":       "MA",
        "county":      "Suffolk",
        "zip_codes":   "02101",
        "population":  "663972",
        "bond_rating_sp": "AAA",
        "free_cash_pct_of_budget": "",
        "pension_funded_ratio_pct": "70.2",    # BERS PERAC 2023
        "debt_per_capita": "",
        "gfoa_certificate_consecutive_years": "28",
        "tax_base_non_residential_pct": "79",  # ~79% commercial/industrial
        "effective_tax_rate_pct":  "0.87",
        "median_annual_tax_bill":  "5500",
        "median_household_income": "",
        "residential_rate_per_1000": "10.51",  # FY2024 MA DOR
        "district_state_rank":       "308",
        "district_state_rank_total": "351",
        "district_rank_10yr_change": "12",
        "test_scores_math_pct": "",
        "graduation_rate_pct":  "",
        "ap_participation_pct": "",
        "transparency":               "yes",
        "electric_savings_vs_state_avg": "0",
        "water_violations_5yr":       "0",
        "transit_access":             "Subway",
        "violent_crime_per_100k":     "449",
        "property_crime_per_100k":    "1355",
        "crime_5yr_pct_change":       "-10",
        "income_10yr_change_pct":     "",
        "population_10yr_change_pct": "",
        "bachelors_degree_pct": "",
        "unemployment_pct":     "",
        "poverty_pct":          "",
        "flood_risk_pct":         "12",
        "flood_2050_growth_pts":  "8",
        "wildfire_risk":          "Low",
        "civica_score":     "0",
        "ter":              "",
        "ter_rating":       "N/A",
        "data_gaps_count":  "0",
        "data_confidence":  "medium",
        "last_updated":     "2026-05-13",
        "compiler_notes":   "~79% non-residential tax base subsidizes residential rates. BPS is a large urban district under state accountability.",
        "value_score":  "",
        "value_rating": "",
    },
    {
        "town_name":   "Revere",
        "state":       "MA",
        "county":      "Suffolk",
        "zip_codes":   "02151",
        "population":  "59933",
        "bond_rating_sp": "A+",
        "free_cash_pct_of_budget": "",
        "pension_funded_ratio_pct": "",
        "debt_per_capita": "",
        "gfoa_certificate_consecutive_years": "",
        "tax_base_non_residential_pct": "28",
        "effective_tax_rate_pct": "1.05",
        "median_annual_tax_bill": "5000",
        "median_household_income": "",
        "residential_rate_per_1000": "11.49",
        "district_state_rank":       "210",
        "district_state_rank_total": "351",
        "district_rank_10yr_change": "8",
        "test_scores_math_pct": "",
        "graduation_rate_pct":  "",
        "ap_participation_pct": "",
        "transparency":               "yes",
        "electric_savings_vs_state_avg": "0",
        "water_violations_5yr":       "0",
        "transit_access":             "Subway",
        "violent_crime_per_100k":     "380",
        "property_crime_per_100k":    "945",
        "crime_5yr_pct_change":       "-5",
        "income_10yr_change_pct":     "",
        "population_10yr_change_pct": "",
        "bachelors_degree_pct": "",
        "unemployment_pct":     "",
        "poverty_pct":          "",
        "flood_risk_pct":        "22",
        "flood_2050_growth_pts": "10",
        "wildfire_risk":         "Low",
        "civica_score":    "0",
        "ter":             "",
        "ter_rating":      "N/A",
        "data_gaps_count": "0",
        "data_confidence": "medium",
        "last_updated":    "2026-05-13",
        "compiler_notes":  "Blue Line MBTA access. Coastal city with Revere Beach; significant flood exposure. Diverse and growing.",
        "value_score":  "",
        "value_rating": "",
    },
    {
        "town_name":   "Winthrop",
        "state":       "MA",
        "county":      "Suffolk",
        "zip_codes":   "02152",
        "population":  "18807",
        "bond_rating_sp": "",
        "free_cash_pct_of_budget": "",
        "pension_funded_ratio_pct": "",
        "debt_per_capita": "",
        "gfoa_certificate_consecutive_years": "",
        "tax_base_non_residential_pct": "11",
        "effective_tax_rate_pct": "1.22",
        "median_annual_tax_bill": "6800",
        "median_household_income": "",
        "residential_rate_per_1000": "13.72",
        "district_state_rank":       "130",
        "district_state_rank_total": "351",
        "district_rank_10yr_change": "5",
        "test_scores_math_pct": "",
        "graduation_rate_pct":  "",
        "ap_participation_pct": "",
        "transparency":               "yes",
        "electric_savings_vs_state_avg": "0",
        "water_violations_5yr":       "0",
        "transit_access":             "Bus only",
        "violent_crime_per_100k":     "120",
        "property_crime_per_100k":    "350",
        "crime_5yr_pct_change":       "-8",
        "income_10yr_change_pct":     "",
        "population_10yr_change_pct": "",
        "bachelors_degree_pct": "",
        "unemployment_pct":     "",
        "poverty_pct":          "",
        "flood_risk_pct":        "40",
        "flood_2050_growth_pts": "15",
        "wildfire_risk":         "Low",
        "civica_score":    "0",
        "ter":             "",
        "ter_rating":      "N/A",
        "data_gaps_count": "0",
        "data_confidence": "medium",
        "last_updated":    "2026-05-13",
        "compiler_notes":  "Peninsula nearly surrounded by water; very high flood risk. Small residential community with above-average schools.",
        "value_score":  "",
        "value_rating": "",
    },
]

# Minimal HTML objects — numeric 0 placeholders will be overwritten by update_all.py
HTML_OBJECTS = [
    '{name:"Boston",lat:42.3601,lng:-71.0589,state:"MA",county:"Suffolk",zip:"02101",pop:663972,'
    'bond:"AAA",free_cash:0,pension:70.2,debt_pc:0,gfoa:28,tax_non_res:79,eff_rate:0.87,'
    'med_tax:5500,med_inc:0,res_rate:10.51,d_rank:308,d_total:351,d_10yr:12,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Subway",'
    'violent:449,prop_crime:1355,crime5yr:-10,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:12,flood50:8,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:null,glance:null,notes:"~79% non-residential tax base significantly subsidizes residential rates. BPS under state accountability.",'
    'med_home_val:720000,commute:30,owner_occ:34,vacancy:5.8,med_age:33,low_income_pct:42,ell_pct:28,enrollment_trend:null,sex_off:null}',

    '{name:"Revere",lat:42.4084,lng:-71.0120,state:"MA",county:"Suffolk",zip:"02151",pop:59933,'
    'bond:"A+",free_cash:0,pension:null,debt_pc:0,gfoa:null,tax_non_res:28,eff_rate:1.05,'
    'med_tax:5000,med_inc:0,res_rate:11.49,d_rank:210,d_total:351,d_10yr:8,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Subway",'
    'violent:380,prop_crime:945,crime5yr:-5,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:22,flood50:10,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:null,glance:null,notes:"Blue Line MBTA access. Coastal city with Revere Beach; significant flood exposure. Diverse and growing.",'
    'med_home_val:440000,commute:28,owner_occ:38,vacancy:4.2,med_age:37,low_income_pct:38,ell_pct:32,enrollment_trend:null,sex_off:null}',

    '{name:"Winthrop",lat:42.3740,lng:-70.9820,state:"MA",county:"Suffolk",zip:"02152",pop:18807,'
    'bond:null,free_cash:0,pension:null,debt_pc:0,gfoa:null,tax_non_res:11,eff_rate:1.22,'
    'med_tax:6800,med_inc:0,res_rate:13.72,d_rank:130,d_total:351,d_10yr:5,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Bus only",'
    'violent:120,prop_crime:350,crime5yr:-8,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:40,flood50:15,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:null,glance:null,notes:"Peninsula nearly surrounded by water; very high flood risk. Above-average schools for the urban area.",'
    'med_home_val:520000,commute:32,owner_occ:52,vacancy:3.8,med_age:40,low_income_pct:28,ell_pct:12,enrollment_trend:null,sex_off:null}',
]

# ─── Append to towns.csv ──────────────────────────────────────────────────────
rows = list(csv.DictReader(open(CSV_FILE, encoding="utf-8")))
fieldnames = list(rows[0].keys())
existing = {r["town_name"] for r in rows}

added_csv = []
for td in NEW_TOWNS:
    if td["town_name"] in existing:
        print(f"  {td['town_name']} already in CSV — skipping")
        continue
    new_row = {f: "" for f in fieldnames}
    new_row.update({k: v for k, v in td.items() if k in fieldnames})
    rows.append(new_row)
    added_csv.append(td["town_name"])

with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)
print(f"CSV: added {len(added_csv)} towns ({', '.join(added_csv)}). Total: {len(rows)}")

# ─── Append to HTML TOWNS array ───────────────────────────────────────────────
html = HTML_FILE.read_text(encoding="utf-8")
existing_html = set(re.findall(r'name:"([^"]+)"', html))

added_html = []
insert_pos = None
# Find the closing ] of the TOWNS array
ts = html.index("const TOWNS = [") + len("const TOWNS = [")
depth = 1; i = ts
while i < len(html) and depth > 0:
    if html[i] == "[": depth += 1
    elif html[i] == "]": depth -= 1
    i += 1
insert_pos = i - 1  # position of the closing ]

inserts = []
for obj_str, td in zip(HTML_OBJECTS, NEW_TOWNS):
    name = td["town_name"]
    if name in existing_html:
        print(f"  {name} already in HTML — skipping")
        continue
    inserts.append(",\n  " + obj_str)
    added_html.append(name)

if inserts:
    html = html[:insert_pos] + "".join(inserts) + html[insert_pos:]
    HTML_FILE.write_text(html, encoding="utf-8")
    print(f"HTML: added {len(added_html)} towns ({', '.join(added_html)})")
else:
    print("HTML: no new towns added")
