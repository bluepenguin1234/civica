"""
Add 10 Norfolk County towns to towns.csv and civica-v5.html.
Run this BEFORE update_all.py (which fills census, school, free-cash, and debt data).

Towns: Quincy, Braintree, Milton, Brookline, Dedham,
       Needham, Wellesley, Weymouth, Canton, Norwood

Data sources hardcoded here:
  - Bond rating:        EMMA/MSRB (S&P)
  - Pension:            PERAC (Quincy own system ~70%; Brookline own system ~76%;
                                Norfolk County Retirement System ~69.5% for others)
  - Tax rates:          MA DOR FY2025 (Canton/Norwood/Braintree/Needham/Wellesley
                        confirmed; Quincy/Milton/Brookline/Dedham/Weymouth estimated)
  - School ranks:       SchoolDigger 2025 (out of 351 DESE districts)
  - Crime:              MA EOPSS / FBI UCR
  - Flood:              FEMA / First Street Foundation
  - Transit:            MBTA
  - ZHVI / home values: Zillow 2024
  - Demographics:       Census ACS 2023 estimates (commute, owner-occ, etc.)

Fields left blank are filled by update_all.py:
  bachelors_degree_pct, poverty_pct, unemployment_pct,
  income_10yr_change_pct, population_10yr_change_pct,
  median_household_income, test_scores_math_pct,
  graduation_rate_pct, ap_participation_pct,
  free_cash_pct_of_budget, debt_per_capita
"""

import csv, re
from pathlib import Path

ROOT      = Path(__file__).parent.parent
CSV_FILE  = ROOT / "data" / "towns.csv"
HTML_FILE = ROOT / "civica-v5.html"

# Norfolk County Retirement System funded ratio (PERAC ~2023)
NORFOLK_PENSION = 69.5

NEW_TOWNS = [
    {
        "town_name":   "Quincy",
        "state":       "MA",
        "county":      "Norfolk",
        "zip_codes":   "02169;02170;02171",
        "population":  "101361",
        "bond_rating_sp":                   "AA+",
        "free_cash_pct_of_budget":          "",
        "pension_funded_ratio_pct":         "70.0",   # Quincy Retirement System (own)
        "debt_per_capita":                  "",
        "gfoa_certificate_consecutive_years": "15",
        "tax_base_non_residential_pct":     "34",
        "effective_tax_rate_pct":           "1.21",
        "median_annual_tax_bill":           "6300",
        "median_household_income":          "",
        "residential_rate_per_1000":        "12.09",  # FY2025 residential (split-rate city)
        "district_state_rank":              "185",
        "district_state_rank_total":        "351",
        "district_rank_10yr_change":        "-20",
        "test_scores_math_pct":             "",
        "graduation_rate_pct":              "",
        "ap_participation_pct":             "",
        "transparency":                     "yes",
        "electric_savings_vs_state_avg":    "0",
        "water_violations_5yr":             "0",
        "transit_access":                   "Subway",
        "violent_crime_per_100k":           "175",
        "property_crime_per_100k":          "870",
        "crime_5yr_pct_change":             "-8",
        "income_10yr_change_pct":           "",
        "population_10yr_change_pct":       "",
        "bachelors_degree_pct":             "",
        "unemployment_pct":                 "",
        "poverty_pct":                      "",
        "flood_risk_pct":                   "18",
        "flood_2050_growth_pts":            "10",
        "wildfire_risk":                    "Low",
        "civica_score":     "0",
        "ter":              "",
        "ter_rating":       "N/A",
        "data_gaps_count":  "0",
        "data_confidence":  "medium",
        "last_updated":     "2026-05-13",
        "compiler_notes":   "Split residential/commercial tax rate. Red Line MBTA: Quincy Center, Quincy Adams, North Quincy, JFK/UMass, Wollaston. Quincy Retirement System (~70% funded, own system). Tax rate estimated FY2025.",
        "value_score":      "",
        "value_rating":     "",
    },
    {
        "town_name":   "Braintree",
        "state":       "MA",
        "county":      "Norfolk",
        "zip_codes":   "02184",
        "population":  "38762",
        "bond_rating_sp":                   "AAA",
        "free_cash_pct_of_budget":          "",
        "pension_funded_ratio_pct":         str(NORFOLK_PENSION),
        "debt_per_capita":                  "",
        "gfoa_certificate_consecutive_years": "15",
        "tax_base_non_residential_pct":     "33",
        "effective_tax_rate_pct":           "1.01",
        "median_annual_tax_bill":           "6400",
        "median_household_income":          "",
        "residential_rate_per_1000":        "10.06",  # FY2025 MA DOR confirmed
        "district_state_rank":              "75",
        "district_state_rank_total":        "351",
        "district_rank_10yr_change":        "3",
        "test_scores_math_pct":             "",
        "graduation_rate_pct":              "",
        "ap_participation_pct":             "",
        "transparency":                     "yes",
        "electric_savings_vs_state_avg":    "0",
        "water_violations_5yr":             "0",
        "transit_access":                   "Subway",
        "violent_crime_per_100k":           "65",
        "property_crime_per_100k":          "420",
        "crime_5yr_pct_change":             "-5",
        "income_10yr_change_pct":           "",
        "population_10yr_change_pct":       "",
        "bachelors_degree_pct":             "",
        "unemployment_pct":                 "",
        "poverty_pct":                      "",
        "flood_risk_pct":                   "4",
        "flood_2050_growth_pts":            "1",
        "wildfire_risk":                    "Low",
        "civica_score":     "0",
        "ter":              "",
        "ter_rating":       "N/A",
        "data_gaps_count":  "0",
        "data_confidence":  "medium",
        "last_updated":     "2026-05-13",
        "compiler_notes":   "Red Line MBTA terminus (Braintree station). Major commercial base: South Shore Plaza. Norfolk County Retirement System (~69.5% funded). AAA bond rating.",
        "value_score":      "",
        "value_rating":     "",
    },
    {
        "town_name":   "Milton",
        "state":       "MA",
        "county":      "Norfolk",
        "zip_codes":   "02186",
        "population":  "28481",
        "bond_rating_sp":                   "AAA",
        "free_cash_pct_of_budget":          "",
        "pension_funded_ratio_pct":         str(NORFOLK_PENSION),
        "debt_per_capita":                  "",
        "gfoa_certificate_consecutive_years": "20",
        "tax_base_non_residential_pct":     "13",
        "effective_tax_rate_pct":           "1.26",
        "median_annual_tax_bill":           "11900",
        "median_household_income":          "",
        "residential_rate_per_1000":        "12.55",  # FY2025 estimated
        "district_state_rank":              "37",
        "district_state_rank_total":        "351",
        "district_rank_10yr_change":        "10",
        "test_scores_math_pct":             "",
        "graduation_rate_pct":              "",
        "ap_participation_pct":             "",
        "transparency":                     "yes",
        "electric_savings_vs_state_avg":    "0",
        "water_violations_5yr":             "0",
        "transit_access":                   "Bus only",
        "violent_crime_per_100k":           "38",
        "property_crime_per_100k":          "175",
        "crime_5yr_pct_change":             "-12",
        "income_10yr_change_pct":           "",
        "population_10yr_change_pct":       "",
        "bachelors_degree_pct":             "",
        "unemployment_pct":                 "",
        "poverty_pct":                      "",
        "flood_risk_pct":                   "6",
        "flood_2050_growth_pts":            "2",
        "wildfire_risk":                    "Low",
        "civica_score":     "0",
        "ter":              "",
        "ter_rating":       "N/A",
        "data_gaps_count":  "0",
        "data_confidence":  "medium",
        "last_updated":     "2026-05-13",
        "compiler_notes":   "AAA bond rating. Predominantly residential tax base (~13% non-res). Near Mattapan trolley border. School district ranked 37th of 351 statewide. Tax rate estimated FY2025.",
        "value_score":      "",
        "value_rating":     "",
    },
    {
        "town_name":   "Brookline",
        "state":       "MA",
        "county":      "Norfolk",
        "zip_codes":   "02445;02446;02467",
        "population":  "62822",
        "bond_rating_sp":                   "AAA",
        "free_cash_pct_of_budget":          "",
        "pension_funded_ratio_pct":         "76.0",   # Brookline Retirement System (own)
        "debt_per_capita":                  "",
        "gfoa_certificate_consecutive_years": "32",
        "tax_base_non_residential_pct":     "32",
        "effective_tax_rate_pct":           "0.99",
        "median_annual_tax_bill":           "14400",
        "median_household_income":          "",
        "residential_rate_per_1000":        "9.92",   # FY2025 estimated
        "district_state_rank":              "18",
        "district_state_rank_total":        "351",
        "district_rank_10yr_change":        "5",
        "test_scores_math_pct":             "",
        "graduation_rate_pct":              "",
        "ap_participation_pct":             "",
        "transparency":                     "yes",
        "electric_savings_vs_state_avg":    "0",
        "water_violations_5yr":             "0",
        "transit_access":                   "Subway",
        "violent_crime_per_100k":           "72",
        "property_crime_per_100k":          "580",
        "crime_5yr_pct_change":             "-3",
        "income_10yr_change_pct":           "",
        "population_10yr_change_pct":       "",
        "bachelors_degree_pct":             "",
        "unemployment_pct":                 "",
        "poverty_pct":                      "",
        "flood_risk_pct":                   "3",
        "flood_2050_growth_pts":            "1",
        "wildfire_risk":                    "Low",
        "civica_score":     "0",
        "ter":              "",
        "ter_rating":       "N/A",
        "data_gaps_count":  "0",
        "data_confidence":  "medium",
        "last_updated":     "2026-05-13",
        "compiler_notes":   "Green Line B/C/D access throughout town. Brookline Retirement System (~76% funded, own system). AAA bond rating. 32+ consecutive GFOA certificates. Tax rate estimated FY2025.",
        "value_score":      "",
        "value_rating":     "",
    },
    {
        "town_name":   "Dedham",
        "state":       "MA",
        "county":      "Norfolk",
        "zip_codes":   "02026",
        "population":  "25109",
        "bond_rating_sp":                   "AA+",
        "free_cash_pct_of_budget":          "",
        "pension_funded_ratio_pct":         str(NORFOLK_PENSION),
        "debt_per_capita":                  "",
        "gfoa_certificate_consecutive_years": "10",
        "tax_base_non_residential_pct":     "29",
        "effective_tax_rate_pct":           "1.35",
        "median_annual_tax_bill":           "9300",
        "median_household_income":          "",
        "residential_rate_per_1000":        "13.47",  # FY2025 estimated
        "district_state_rank":              "174",
        "district_state_rank_total":        "351",
        "district_rank_10yr_change":        "-15",
        "test_scores_math_pct":             "",
        "graduation_rate_pct":              "",
        "ap_participation_pct":             "",
        "transparency":                     "yes",
        "electric_savings_vs_state_avg":    "0",
        "water_violations_5yr":             "0",
        "transit_access":                   "Commuter Rail (in town)",
        "violent_crime_per_100k":           "95",
        "property_crime_per_100k":          "490",
        "crime_5yr_pct_change":             "-5",
        "income_10yr_change_pct":           "",
        "population_10yr_change_pct":       "",
        "bachelors_degree_pct":             "",
        "unemployment_pct":                 "",
        "poverty_pct":                      "",
        "flood_risk_pct":                   "12",
        "flood_2050_growth_pts":            "5",
        "wildfire_risk":                    "Low",
        "civica_score":     "0",
        "ter":              "",
        "ter_rating":       "N/A",
        "data_gaps_count":  "0",
        "data_confidence":  "medium",
        "last_updated":     "2026-05-13",
        "compiler_notes":   "Needham Branch commuter rail: Dedham Corporate Center, Endicott. Legacy Place retail complex. Some Charles River/Mother Brook flood exposure. School rank slipped ~15 spots past decade. Tax rate estimated FY2025.",
        "value_score":      "",
        "value_rating":     "",
    },
    {
        "town_name":   "Needham",
        "state":       "MA",
        "county":      "Norfolk",
        "zip_codes":   "02492;02494",
        "population":  "32059",
        "bond_rating_sp":                   "AAA",
        "free_cash_pct_of_budget":          "",
        "pension_funded_ratio_pct":         str(NORFOLK_PENSION),
        "debt_per_capita":                  "",
        "gfoa_certificate_consecutive_years": "20",
        "tax_base_non_residential_pct":     "22",
        "effective_tax_rate_pct":           "1.06",
        "median_annual_tax_bill":           "13300",
        "median_household_income":          "",
        "residential_rate_per_1000":        "10.60",  # FY2025 MA DOR confirmed
        "district_state_rank":              "14",
        "district_state_rank_total":        "351",
        "district_rank_10yr_change":        "5",
        "test_scores_math_pct":             "",
        "graduation_rate_pct":              "",
        "ap_participation_pct":             "",
        "transparency":                     "yes",
        "electric_savings_vs_state_avg":    "0",
        "water_violations_5yr":             "0",
        "transit_access":                   "Commuter Rail (in town)",
        "violent_crime_per_100k":           "28",
        "property_crime_per_100k":          "230",
        "crime_5yr_pct_change":             "-8",
        "income_10yr_change_pct":           "",
        "population_10yr_change_pct":       "",
        "bachelors_degree_pct":             "",
        "unemployment_pct":                 "",
        "poverty_pct":                      "",
        "flood_risk_pct":                   "4",
        "flood_2050_growth_pts":            "1",
        "wildfire_risk":                    "Low",
        "civica_score":     "0",
        "ter":              "",
        "ter_rating":       "N/A",
        "data_gaps_count":  "0",
        "data_confidence":  "medium",
        "last_updated":     "2026-05-13",
        "compiler_notes":   "AAA bond rating. Needham Branch commuter rail: Needham Heights, Needham Center, Needham Junction. Route 9 tech corridor / Needham Business Park. Free cash consistently 7-10%. Top 4% of MA school districts.",
        "value_score":      "",
        "value_rating":     "",
    },
    {
        "town_name":   "Wellesley",
        "state":       "MA",
        "county":      "Norfolk",
        "zip_codes":   "02481;02482",
        "population":  "29906",
        "bond_rating_sp":                   "AAA",
        "free_cash_pct_of_budget":          "",
        "pension_funded_ratio_pct":         str(NORFOLK_PENSION),
        "debt_per_capita":                  "",
        "gfoa_certificate_consecutive_years": "25",
        "tax_base_non_residential_pct":     "20",
        "effective_tax_rate_pct":           "1.17",
        "median_annual_tax_bill":           "20400",
        "median_household_income":          "",
        "residential_rate_per_1000":        "11.68",  # FY2025 MA DOR confirmed
        "district_state_rank":              "7",
        "district_state_rank_total":        "351",
        "district_rank_10yr_change":        "3",
        "test_scores_math_pct":             "",
        "graduation_rate_pct":              "",
        "ap_participation_pct":             "",
        "transparency":                     "yes",
        "electric_savings_vs_state_avg":    "0",
        "water_violations_5yr":             "0",
        "transit_access":                   "Commuter Rail (in town)",
        "violent_crime_per_100k":           "18",
        "property_crime_per_100k":          "185",
        "crime_5yr_pct_change":             "-10",
        "income_10yr_change_pct":           "",
        "population_10yr_change_pct":       "",
        "bachelors_degree_pct":             "",
        "unemployment_pct":                 "",
        "poverty_pct":                      "",
        "flood_risk_pct":                   "3",
        "flood_2050_growth_pts":            "1",
        "wildfire_risk":                    "Low",
        "civica_score":     "0",
        "ter":              "",
        "ter_rating":       "N/A",
        "data_gaps_count":  "0",
        "data_confidence":  "medium",
        "last_updated":     "2026-05-13",
        "compiler_notes":   "AAA bond rating. Framingham/Worcester Commuter Rail: Wellesley Farms, Wellesley Hills, Wellesley Square. Free cash ~13% — among highest in MA. 7th of 351 school districts statewide. Home of Wellesley College.",
        "value_score":      "",
        "value_rating":     "",
    },
    {
        "town_name":   "Weymouth",
        "state":       "MA",
        "county":      "Norfolk",
        "zip_codes":   "02188;02189;02190;02191",
        "population":  "57786",
        "bond_rating_sp":                   "AA+",
        "free_cash_pct_of_budget":          "",
        "pension_funded_ratio_pct":         str(NORFOLK_PENSION),
        "debt_per_capita":                  "",
        "gfoa_certificate_consecutive_years": "12",
        "tax_base_non_residential_pct":     "24",
        "effective_tax_rate_pct":           "1.10",
        "median_annual_tax_bill":           "5900",
        "median_household_income":          "",
        "residential_rate_per_1000":        "11.04",  # FY2025 estimated
        "district_state_rank":              "196",
        "district_state_rank_total":        "351",
        "district_rank_10yr_change":        "-20",
        "test_scores_math_pct":             "",
        "graduation_rate_pct":              "",
        "ap_participation_pct":             "",
        "transparency":                     "yes",
        "electric_savings_vs_state_avg":    "0",
        "water_violations_5yr":             "0",
        "transit_access":                   "Commuter Rail (in town)",
        "violent_crime_per_100k":           "145",
        "property_crime_per_100k":          "780",
        "crime_5yr_pct_change":             "-5",
        "income_10yr_change_pct":           "",
        "population_10yr_change_pct":       "",
        "bachelors_degree_pct":             "",
        "unemployment_pct":                 "",
        "poverty_pct":                      "",
        "flood_risk_pct":                   "18",
        "flood_2050_growth_pts":            "8",
        "wildfire_risk":                    "Low",
        "civica_score":     "0",
        "ter":              "",
        "ter_rating":       "N/A",
        "data_gaps_count":  "0",
        "data_confidence":  "medium",
        "last_updated":     "2026-05-13",
        "compiler_notes":   "Old Colony/Greenbush Commuter Rail: East Weymouth, South Weymouth, Weymouth Landing/East Braintree. Coastal and tidal river flood exposure. School rank declined ~20 spots past decade. Tax rate estimated FY2025.",
        "value_score":      "",
        "value_rating":     "",
    },
    {
        "town_name":   "Canton",
        "state":       "MA",
        "county":      "Norfolk",
        "zip_codes":   "02021",
        "population":  "24459",
        "bond_rating_sp":                   "AAA",
        "free_cash_pct_of_budget":          "",
        "pension_funded_ratio_pct":         str(NORFOLK_PENSION),
        "debt_per_capita":                  "",
        "gfoa_certificate_consecutive_years": "18",
        "tax_base_non_residential_pct":     "30",
        "effective_tax_rate_pct":           "0.98",
        "median_annual_tax_bill":           "7000",
        "median_household_income":          "",
        "residential_rate_per_1000":        "9.75",   # FY2025 MA DOR confirmed
        "district_state_rank":              "60",
        "district_state_rank_total":        "351",
        "district_rank_10yr_change":        "5",
        "test_scores_math_pct":             "",
        "graduation_rate_pct":              "",
        "ap_participation_pct":             "",
        "transparency":                     "yes",
        "electric_savings_vs_state_avg":    "0",
        "water_violations_5yr":             "0",
        "transit_access":                   "Commuter Rail (in town)",
        "violent_crime_per_100k":           "48",
        "property_crime_per_100k":          "290",
        "crime_5yr_pct_change":             "-8",
        "income_10yr_change_pct":           "",
        "population_10yr_change_pct":       "",
        "bachelors_degree_pct":             "",
        "unemployment_pct":                 "",
        "poverty_pct":                      "",
        "flood_risk_pct":                   "5",
        "flood_2050_growth_pts":            "2",
        "wildfire_risk":                    "Low",
        "civica_score":     "0",
        "ter":              "",
        "ter_rating":       "N/A",
        "data_gaps_count":  "0",
        "data_confidence":  "medium",
        "last_updated":     "2026-05-13",
        "compiler_notes":   "Lowest residential tax rate in Norfolk County (FY2025: $9.75). AAA bond rating. Providence/Stoughton Commuter Rail: Canton Center, Canton Junction. Strong commercial base along Route 138.",
        "value_score":      "",
        "value_rating":     "",
    },
    {
        "town_name":   "Norwood",
        "state":       "MA",
        "county":      "Norfolk",
        "zip_codes":   "02062",
        "population":  "31380",
        "bond_rating_sp":                   "AA+",
        "free_cash_pct_of_budget":          "",
        "pension_funded_ratio_pct":         str(NORFOLK_PENSION),
        "debt_per_capita":                  "",
        "gfoa_certificate_consecutive_years": "8",
        "tax_base_non_residential_pct":     "37",
        "effective_tax_rate_pct":           "0.98",
        "median_annual_tax_bill":           "5700",
        "median_household_income":          "",
        "residential_rate_per_1000":        "9.82",   # FY2025 MA DOR confirmed
        "district_state_rank":              "229",
        "district_state_rank_total":        "351",
        "district_rank_10yr_change":        "-15",
        "test_scores_math_pct":             "",
        "graduation_rate_pct":              "",
        "ap_participation_pct":             "",
        "transparency":                     "yes",
        "electric_savings_vs_state_avg":    "0",
        "water_violations_5yr":             "0",
        "transit_access":                   "Commuter Rail (in town)",
        "violent_crime_per_100k":           "128",
        "property_crime_per_100k":          "670",
        "crime_5yr_pct_change":             "-3",
        "income_10yr_change_pct":           "",
        "population_10yr_change_pct":       "",
        "bachelors_degree_pct":             "",
        "unemployment_pct":                 "",
        "poverty_pct":                      "",
        "flood_risk_pct":                   "10",
        "flood_2050_growth_pts":            "4",
        "wildfire_risk":                    "Low",
        "civica_score":     "0",
        "ter":              "",
        "ter_rating":       "N/A",
        "data_gaps_count":  "0",
        "data_confidence":  "medium",
        "last_updated":     "2026-05-13",
        "compiler_notes":   "Providence Commuter Rail: Norwood Depot, Norwood Central. Very high non-residential tax base (~37%) — Route 1, University Ave industrial corridor. Free cash FY2026: 14.65%. School rank declined ~15 spots past decade.",
        "value_score":      "",
        "value_rating":     "",
    },
]

# ─── HTML TOWNS array objects ─────────────────────────────────────────────────
# Numeric 0 placeholders for census/school fields; update_all.py patches them.
HTML_OBJECTS = [
    '{name:"Quincy",lat:42.2529,lng:-71.0023,state:"MA",county:"Norfolk",zip:"02169",pop:101361,'
    'bond:"AA+",free_cash:0,pension:70.0,debt_pc:0,gfoa:15,tax_non_res:34,eff_rate:1.21,'
    'med_tax:6300,med_inc:0,res_rate:12.09,d_rank:185,d_total:351,d_10yr:-20,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Subway",'
    'violent:175,prop_crime:870,crime5yr:-8,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:18,flood50:10,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Quincy offers Red Line MBTA access at 5 stations, a 34% non-residential tax base, and home prices well below neighboring Boston neighborhoods — one of the most affordable transit-served cities in Greater Boston.",'
    'glance:"Quincy is the largest city south of Boston, with strong Red Line access, a growing commercial base, and relatively accessible home prices. Schools rank in the middle third statewide. Free cash has been very tight (under 1% in recent years), and the city carries meaningful pension obligations.",'
    'notes:"Split residential/commercial tax rate. Red Line: Quincy Center, Quincy Adams, North Quincy, JFK/UMass, Wollaston. Quincy Retirement System (~70% funded, own system).",'
    'med_home_val:535000,commute:26,owner_occ:43,vacancy:5.0,med_age:38,low_income_pct:30,ell_pct:18,enrollment_trend:null,sex_off:0.25}',

    '{name:"Braintree",lat:42.2042,lng:-71.0023,state:"MA",county:"Norfolk",zip:"02184",pop:38762,'
    'bond:"AAA",free_cash:0,pension:69.5,debt_pc:0,gfoa:15,tax_non_res:33,eff_rate:1.01,'
    'med_tax:6400,med_inc:0,res_rate:10.06,d_rank:75,d_total:351,d_10yr:3,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Subway",'
    'violent:65,prop_crime:420,crime5yr:-5,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:4,flood50:1,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Braintree is the Red Line\'s southern terminus, giving residents direct subway access to Boston and Cambridge. South Shore Plaza and major retail generate a 33% non-residential tax base that keeps the FY2025 residential rate at just $10.06/thousand — 3rd lowest in Norfolk County.",'
    'glance:"Braintree combines Red Line MBTA access, an AAA bond rating, and one of the lowest residential tax rates in Norfolk County thanks to South Shore Plaza\'s commercial base. The school district ranks in the top quarter statewide. Municipal finances are strong.",'
    'notes:"Red Line terminus (Braintree station). Major commercial base: South Shore Plaza. Norfolk County Retirement System (~69.5% funded). AAA bond rating.",'
    'med_home_val:640000,commute:27,owner_occ:66,vacancy:3.5,med_age:43,low_income_pct:18,ell_pct:6,enrollment_trend:null,sex_off:0.15}',

    '{name:"Milton",lat:42.2501,lng:-71.0667,state:"MA",county:"Norfolk",zip:"02186",pop:28481,'
    'bond:"AAA",free_cash:0,pension:69.5,debt_pc:0,gfoa:20,tax_non_res:13,eff_rate:1.26,'
    'med_tax:11900,med_inc:0,res_rate:12.55,d_rank:37,d_total:351,d_10yr:10,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Bus only",'
    'violent:38,prop_crime:175,crime5yr:-12,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:6,flood50:2,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Milton ranks in the top 11% of Massachusetts school districts (37th of 351) with a rising 10-year trajectory, some of the lowest violent crime rates in Greater Boston, and an AAA bond rating — making it a top-tier destination for families prioritizing academics and safety.",'
    'glance:"Milton is a quiet, high-income suburb with top-tier schools, very low crime, and strong property values. The school district has climbed in state rankings over the past decade. The almost entirely residential tax base puts the full levy on homeowners, and there is limited public transit.",'
    'notes:"AAA bond rating. Predominantly residential tax base (~13% non-res). Bus service; near Mattapan trolley border. District ranked 37th of 351 statewide and improving.",'
    'med_home_val:970000,commute:24,owner_occ:78,vacancy:2.8,med_age:44,low_income_pct:10,ell_pct:4,enrollment_trend:null,sex_off:0.08}',

    '{name:"Brookline",lat:42.3318,lng:-71.1209,state:"MA",county:"Norfolk",zip:"02445",pop:62822,'
    'bond:"AAA",free_cash:0,pension:76.0,debt_pc:0,gfoa:32,tax_non_res:32,eff_rate:0.99,'
    'med_tax:14400,med_inc:0,res_rate:9.92,d_rank:18,d_total:351,d_10yr:5,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Subway",'
    'violent:72,prop_crime:580,crime5yr:-3,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:3,flood50:1,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Brookline has one of the most extensive subway networks of any single town in Massachusetts — Green Line B, C, and D branches run through town — giving residents walkable rail access that rivals Boston neighborhoods, paired with a top-5% school district (18th of 351).",'
    'glance:"Brookline is an affluent inner suburb adjacent to Boston with excellent Green Line MBTA access, top-5% schools statewide, and a large commercial base that moderates residential rates. Home prices are among the highest in the state. The town has its own well-funded pension system and 32+ consecutive GFOA certificates.",'
    'notes:"Green Line B/C/D access throughout. Brookline Retirement System (~76% funded, own system). AAA bond. 32+ GFOA certificates. Home of Longwood Medical Area employers.",'
    'med_home_val:1450000,commute:22,owner_occ:36,vacancy:6.0,med_age:34,low_income_pct:18,ell_pct:8,enrollment_trend:null,sex_off:0.12}',

    '{name:"Dedham",lat:42.2415,lng:-71.1648,state:"MA",county:"Norfolk",zip:"02026",pop:25109,'
    'bond:"AA+",free_cash:0,pension:69.5,debt_pc:0,gfoa:10,tax_non_res:29,eff_rate:1.35,'
    'med_tax:9300,med_inc:0,res_rate:13.47,d_rank:174,d_total:351,d_10yr:-15,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town)",'
    'violent:95,prop_crime:490,crime5yr:-5,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:12,flood50:5,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Legacy Place and the Route 1 commercial corridor give Dedham a 29% non-residential tax base — among the stronger commercial bases for a town its size in Norfolk County — helping offset the residential levy.",'
    'glance:"Dedham is a mid-range commuter suburb with Needham Branch commuter rail access, reasonable home prices, and a commercial base anchored by Legacy Place. School rankings have slipped over the past decade and sit in the bottom half statewide. Some Charles River flood exposure.",'
    'notes:"Needham Branch commuter rail: Dedham Corporate Center, Endicott. Legacy Place / Route 1 retail. Some Charles River/Mother Brook flood exposure (~12%).",'
    'med_home_val:690000,commute:26,owner_occ:62,vacancy:3.8,med_age:41,low_income_pct:20,ell_pct:6,enrollment_trend:null,sex_off:0.18}',

    '{name:"Needham",lat:42.2793,lng:-71.2329,state:"MA",county:"Norfolk",zip:"02492",pop:32059,'
    'bond:"AAA",free_cash:0,pension:69.5,debt_pc:0,gfoa:20,tax_non_res:22,eff_rate:1.06,'
    'med_tax:13300,med_inc:0,res_rate:10.60,d_rank:14,d_total:351,d_10yr:5,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town)",'
    'violent:28,prop_crime:230,crime5yr:-8,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:4,flood50:1,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Needham ranks 14th of 351 Massachusetts school districts — top 4% statewide — with a near-98% graduation rate, very low crime, and one of the strongest free cash positions in Norfolk County. Three Needham Branch commuter rail stops connect to Back Bay and South Station.",'
    'glance:"Needham consistently ranks among Massachusetts\'s top 15 school districts, with near-perfect graduation rates, strong MCAS scores, and healthy municipal finances. Home prices reflect the premium. Route 9 tech employers and Needham Business Park anchor a diversified commercial tax base.",'
    'notes:"AAA bond rating. Needham Branch commuter rail: Needham Heights, Needham Center, Needham Junction. Route 9 tech corridor. Free cash consistently 7-10%.",'
    'med_home_val:1250000,commute:24,owner_occ:78,vacancy:2.5,med_age:44,low_income_pct:8,ell_pct:4,enrollment_trend:null,sex_off:0.10}',

    '{name:"Wellesley",lat:42.2968,lng:-71.2924,state:"MA",county:"Norfolk",zip:"02481",pop:29906,'
    'bond:"AAA",free_cash:0,pension:69.5,debt_pc:0,gfoa:25,tax_non_res:20,eff_rate:1.17,'
    'med_tax:20400,med_inc:0,res_rate:11.68,d_rank:7,d_total:351,d_10yr:3,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town)",'
    'violent:18,prop_crime:185,crime5yr:-10,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:3,flood50:1,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Wellesley ranks 7th of 351 Massachusetts school districts — consistently top 2% statewide — with 76% MCAS math proficiency, 43% AP participation, and 95%+ graduation rates, alongside some of the lowest crime and best municipal finances of any town in Greater Boston.",'
    'glance:"Wellesley is one of Massachusetts\'s premier school districts (7th of 351), paired with exceptional municipal finances, very low crime, and three commuter rail stops on the Framingham/Worcester line. Free cash is ~13% of budget — among the highest in the state. Home prices are among the highest in the state.",'
    'notes:"AAA bond rating. Framingham/Worcester Commuter Rail: Wellesley Farms, Wellesley Hills, Wellesley Square. Free cash ~13% — among highest in MA. Home of Wellesley College.",'
    'med_home_val:1750000,commute:23,owner_occ:80,vacancy:2.5,med_age:43,low_income_pct:7,ell_pct:5,enrollment_trend:null,sex_off:0.07}',

    '{name:"Weymouth",lat:42.2196,lng:-71.0412,state:"MA",county:"Norfolk",zip:"02188",pop:57786,'
    'bond:"AA+",free_cash:0,pension:69.5,debt_pc:0,gfoa:12,tax_non_res:24,eff_rate:1.10,'
    'med_tax:5900,med_inc:0,res_rate:11.04,d_rank:196,d_total:351,d_10yr:-20,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town)",'
    'violent:145,prop_crime:780,crime5yr:-5,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:18,flood50:8,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Weymouth offers Old Colony commuter rail access at three stations and among the most affordable single-family homes in Norfolk County — making it one of the stronger value propositions for South Shore buyers priced out of Braintree or Milton.",'
    'glance:"Weymouth is a large, affordable South Shore community with commuter rail access and reasonable home prices. School rankings are mid-table and have slipped over the past decade. Coastal and tidal flood exposure is meaningful (18% of properties). Free cash has tightened in recent years.",'
    'notes:"Old Colony/Greenbush Commuter Rail: East Weymouth, South Weymouth, Weymouth Landing. Coastal and tidal river flood exposure. Tax rate estimated FY2025.",'
    'med_home_val:530000,commute:28,owner_occ:60,vacancy:4.0,med_age:40,low_income_pct:25,ell_pct:5,enrollment_trend:null,sex_off:0.22}',

    '{name:"Canton",lat:42.1584,lng:-71.1432,state:"MA",county:"Norfolk",zip:"02021",pop:24459,'
    'bond:"AAA",free_cash:0,pension:69.5,debt_pc:0,gfoa:18,tax_non_res:30,eff_rate:0.98,'
    'med_tax:7000,med_inc:0,res_rate:9.75,d_rank:60,d_total:351,d_10yr:5,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town)",'
    'violent:48,prop_crime:290,crime5yr:-8,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:5,flood50:2,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Canton has the lowest residential tax rate in Norfolk County ($9.75/thousand, FY2025) while maintaining an AAA bond rating, a top-quarter school district (60th of 351), and strong free cash reserves — a rare combination among well-regarded Greater Boston suburbs.",'
    'glance:"Canton is a financially strong suburb with an AAA bond rating, the lowest residential tax rate in Norfolk County, solid schools (top 18% statewide), and commuter rail access on the Providence/Stoughton line. A significant Route 138 commercial corridor diversifies the tax base.",'
    'notes:"Lowest residential tax rate in Norfolk County (FY2025: $9.75). AAA bond rating. Providence/Stoughton Commuter Rail: Canton Center, Canton Junction. Route 138 commercial corridor.",'
    'med_home_val:720000,commute:26,owner_occ:75,vacancy:3.0,med_age:43,low_income_pct:12,ell_pct:4,enrollment_trend:null,sex_off:0.12}',

    '{name:"Norwood",lat:42.1943,lng:-71.1995,state:"MA",county:"Norfolk",zip:"02062",pop:31380,'
    'bond:"AA+",free_cash:0,pension:69.5,debt_pc:0,gfoa:8,tax_non_res:37,eff_rate:0.98,'
    'med_tax:5700,med_inc:0,res_rate:9.82,d_rank:229,d_total:351,d_10yr:-15,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town)",'
    'violent:128,prop_crime:670,crime5yr:-3,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:10,flood50:4,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"With ~37% of its tax base in commercial and industrial property — among the highest in Norfolk County — Norwood keeps its residential rate at just $9.82/thousand, giving homeowners a structural subsidy built into the commercial corridor along Route 1 and University Avenue.",'
    'glance:"Norwood is an affordable, transit-served community with a heavy commercial and industrial tax base that subsidizes residential rates. Providence line commuter rail reaches South Station in under 35 minutes. School rankings sit in the bottom third statewide. Free cash has been exceptionally strong (14%+) in recent years.",'
    'notes:"Providence Commuter Rail: Norwood Depot, Norwood Central. Very high non-res tax base (~37%) — Route 1, University Ave industrial corridor. Free cash FY2026: 14.65%. School rank declined ~15 spots past decade.",'
    'med_home_val:580000,commute:28,owner_occ:64,vacancy:4.0,med_age:41,low_income_pct:22,ell_pct:5,enrollment_trend:null,sex_off:0.20}',
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
ts = html.index("const TOWNS = [") + len("const TOWNS = [")
depth = 1; i = ts
while i < len(html) and depth > 0:
    if html[i] == "[": depth += 1
    elif html[i] == "]": depth -= 1
    i += 1
insert_pos = i - 1  # closing ]

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
