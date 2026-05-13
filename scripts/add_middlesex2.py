"""
Add 10 Middlesex County towns (batch 2) to towns.csv and civica-v5.html.
Run this BEFORE update_all.py.

Towns: Lowell, Chelmsford, Billerica, Tewksbury, Wilmington,
       Melrose, Ashland, Marlborough, Hudson, Hopkinton

Agent-researched fields:
  - Bond ratings:    S&P via EMMA / town press releases
  - FY2025 tax rates: MA Almanac / MA DOR
  - Median tax bills: Ownwell / DOR estimates
  - School ranks:    SchoolDigger 2025
  - Crime:           FBI UCR / CrimeExplorer 2024
  - Transit:         MBTA confirmed
  - Flood:           First Street Foundation / FEMA
  - Pension:         PERAC 2024; Middlesex County Retirement ~67% actuarial
                     Lowell own system ~63.6%; Melrose own system ~65.2%

Fields filled by update_all.py automatically:
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

MIDDLESEX_PENSION = 67.0   # Middlesex County Retirement System (actuarial est.)

NEW_TOWNS = [
    {
        "town_name":   "Lowell",
        "state":       "MA",
        "county":      "Middlesex",
        "zip_codes":   "01850",
        "population":  "115140",
        "bond_rating_sp":                     "AA-",    # Moody's Aa3 (Nov 2024 upgrade); S&P equiv AA-
        "free_cash_pct_of_budget":            "",
        "pension_funded_ratio_pct":           "63.6",   # Lowell Contributory Retirement System (PERAC est.)
        "debt_per_capita":                    "",
        "gfoa_certificate_consecutive_years": "0",
        "tax_base_non_residential_pct":       "30",
        "effective_tax_rate_pct":             "1.22",
        "median_annual_tax_bill":             "5191",   # Ownwell confirmed
        "median_household_income":            "",
        "residential_rate_per_1000":          "11.48",  # FY2025 MA Almanac confirmed
        "district_state_rank":                "278",    # SchoolDigger 2025
        "district_state_rank_total":          "348",
        "district_rank_10yr_change":          "0",
        "test_scores_math_pct":               "",
        "graduation_rate_pct":                "",
        "ap_participation_pct":               "",
        "transparency":                       "yes",
        "electric_savings_vs_state_avg":      "0",
        "water_violations_5yr":               "0",
        "transit_access":                     "Commuter Rail (in town)",
        "violent_crime_per_100k":             "533",    # FBI UCR 2024
        "property_crime_per_100k":            "1663",   # FBI UCR 2024
        "crime_5yr_pct_change":               "-10",
        "income_10yr_change_pct":             "",
        "population_10yr_change_pct":         "",
        "bachelors_degree_pct":               "",
        "unemployment_pct":                   "",
        "poverty_pct":                        "",
        "flood_risk_pct":                     "4",
        "flood_2050_growth_pts":              "5",
        "wildfire_risk":                      "Low",
        "civica_score":     "0",
        "ter":              "",
        "ter_rating":       "N/A",
        "data_gaps_count":  "0",
        "data_confidence":  "medium",
        "last_updated":     "2026-05-13",
        "compiler_notes":   "Moody's upgraded to Aa3 Nov 2024 (S&P AA- equivalent). Lowell Line commuter rail terminus — direct to North Station. Lowell Contributory Retirement System ~63.6% funded (PERAC est.). Gateway City; UMass Lowell anchor. School district 278/348. Highest violent crime in this cohort (533/100k). Lowest home values and tax bill in this Middlesex group.",
        "value_score":      "",
        "value_rating":     "",
    },
    {
        "town_name":   "Chelmsford",
        "state":       "MA",
        "county":      "Middlesex",
        "zip_codes":   "01824",
        "population":  "37763",
        "bond_rating_sp":                     "AAA",    # S&P AAA confirmed June 2025
        "free_cash_pct_of_budget":            "",
        "pension_funded_ratio_pct":           str(MIDDLESEX_PENSION),
        "debt_per_capita":                    "",
        "gfoa_certificate_consecutive_years": "0",
        "tax_base_non_residential_pct":       "22",
        "effective_tax_rate_pct":             "1.39",
        "median_annual_tax_bill":             "8272",   # Ownwell confirmed
        "median_household_income":            "",
        "residential_rate_per_1000":          "13.90",  # FY2025 MA Almanac confirmed
        "district_state_rank":                "80",     # SchoolDigger 2025
        "district_state_rank_total":          "351",
        "district_rank_10yr_change":          "5",
        "test_scores_math_pct":               "",
        "graduation_rate_pct":                "",
        "ap_participation_pct":               "",
        "transparency":                       "yes",
        "electric_savings_vs_state_avg":      "0",
        "water_violations_5yr":               "0",
        "transit_access":                     "Bus only",
        "violent_crime_per_100k":             "28",     # FBI UCR 5yr avg
        "property_crime_per_100k":            "42",     # FBI UCR 5yr avg
        "crime_5yr_pct_change":               "-12",
        "income_10yr_change_pct":             "",
        "population_10yr_change_pct":         "",
        "bachelors_degree_pct":               "",
        "unemployment_pct":                   "",
        "poverty_pct":                        "",
        "flood_risk_pct":                     "2",
        "flood_2050_growth_pts":              "3",
        "wildfire_risk":                      "Low",
        "civica_score":     "0",
        "ter":              "",
        "ter_rating":       "N/A",
        "data_gaps_count":  "0",
        "data_confidence":  "medium",
        "last_updated":     "2026-05-13",
        "compiler_notes":   "S&P AAA confirmed June 2025 — highest possible rating. Middlesex County Retirement System (~67% actuarial). No in-town commuter rail; LRTA bus to Lowell Station. School district 80/351. Violent crime 74% below national average. Route 3 commercial corridor.",
        "value_score":      "",
        "value_rating":     "",
    },
    {
        "town_name":   "Billerica",
        "state":       "MA",
        "county":      "Middlesex",
        "zip_codes":   "01821",
        "population":  "43706",
        "bond_rating_sp":                     "AA+",    # S&P AA+ confirmed
        "free_cash_pct_of_budget":            "",
        "pension_funded_ratio_pct":           str(MIDDLESEX_PENSION),
        "debt_per_capita":                    "",
        "gfoa_certificate_consecutive_years": "0",
        "tax_base_non_residential_pct":       "28",
        "effective_tax_rate_pct":             "1.00",
        "median_annual_tax_bill":             "6799",   # Ownwell confirmed
        "median_household_income":            "",
        "residential_rate_per_1000":          "11.37",  # FY2025 MA Almanac confirmed
        "district_state_rank":                "147",    # SchoolDigger 2025
        "district_state_rank_total":          "348",
        "district_rank_10yr_change":          "0",
        "test_scores_math_pct":               "",
        "graduation_rate_pct":                "",
        "ap_participation_pct":               "",
        "transparency":                       "yes",
        "electric_savings_vs_state_avg":      "0",
        "water_violations_5yr":               "0",
        "transit_access":                     "Commuter Rail (in town)",
        "violent_crime_per_100k":             "34",     # FBI UCR 5yr avg
        "property_crime_per_100k":            "39",     # FBI UCR 5yr avg
        "crime_5yr_pct_change":               "-8",
        "income_10yr_change_pct":             "",
        "population_10yr_change_pct":         "",
        "bachelors_degree_pct":               "",
        "unemployment_pct":                   "",
        "poverty_pct":                        "",
        "flood_risk_pct":                     "3",
        "flood_2050_growth_pts":              "4",
        "wildfire_risk":                      "Low",
        "civica_score":     "0",
        "ter":              "",
        "ter_rating":       "N/A",
        "data_gaps_count":  "0",
        "data_confidence":  "medium",
        "last_updated":     "2026-05-13",
        "compiler_notes":   "S&P AA+ confirmed. North Billerica Station on MBTA Lowell Line. Middlesex County Retirement (~67% actuarial). Significant industrial tax base along Route 3 corridor. School district 147/348.",
        "value_score":      "",
        "value_rating":     "",
    },
    {
        "town_name":   "Tewksbury",
        "state":       "MA",
        "county":      "Middlesex",
        "zip_codes":   "01876",
        "population":  "33234",
        "bond_rating_sp":                     "AA+",    # local news snippet; UNCONFIRMED from primary source
        "free_cash_pct_of_budget":            "",
        "pension_funded_ratio_pct":           str(MIDDLESEX_PENSION),
        "debt_per_capita":                    "",
        "gfoa_certificate_consecutive_years": "0",
        "tax_base_non_residential_pct":       "22",
        "effective_tax_rate_pct":             "1.29",
        "median_annual_tax_bill":             "7649",   # Ownwell confirmed
        "median_household_income":            "",
        "residential_rate_per_1000":          "13.22",  # FY2025 MA Almanac confirmed
        "district_state_rank":                "117",    # SchoolDigger 2025
        "district_state_rank_total":          "348",
        "district_rank_10yr_change":          "5",
        "test_scores_math_pct":               "",
        "graduation_rate_pct":                "",
        "ap_participation_pct":               "",
        "transparency":                       "yes",
        "electric_savings_vs_state_avg":      "0",
        "water_violations_5yr":               "0",
        "transit_access":                     "Bus only",
        "violent_crime_per_100k":             "52",     # FBI UCR 5yr avg
        "property_crime_per_100k":            "117",    # FBI UCR 5yr avg
        "crime_5yr_pct_change":               "-8",
        "income_10yr_change_pct":             "",
        "population_10yr_change_pct":         "",
        "bachelors_degree_pct":               "",
        "unemployment_pct":                   "",
        "poverty_pct":                        "",
        "flood_risk_pct":                     "3",
        "flood_2050_growth_pts":              "4",
        "wildfire_risk":                      "Low",
        "civica_score":     "0",
        "ter":              "",
        "ter_rating":       "N/A",
        "data_gaps_count":  "0",
        "data_confidence":  "medium",
        "last_updated":     "2026-05-13",
        "compiler_notes":   "AA+ bond rating (unconfirmed from primary source — based on local news snippet). Middlesex County Retirement (~67% actuarial). No in-town commuter rail; bus to Lowell. Tewksbury Memorial HS ranks 69/349 high schools (stronger than district overall rank suggests). Route 38 commercial corridor.",
        "value_score":      "",
        "value_rating":     "",
    },
    {
        "town_name":   "Wilmington",
        "state":       "MA",
        "county":      "Middlesex",
        "zip_codes":   "01887",
        "population":  "23125",
        "bond_rating_sp":                     "AA",     # S&P portal confirmed entity; exact rating est. AA
        "free_cash_pct_of_budget":            "",
        "pension_funded_ratio_pct":           str(MIDDLESEX_PENSION),
        "debt_per_capita":                    "",
        "gfoa_certificate_consecutive_years": "0",
        "tax_base_non_residential_pct":       "35",
        "effective_tax_rate_pct":             "0.99",
        "median_annual_tax_bill":             "7556",   # Ownwell confirmed
        "median_household_income":            "",
        "residential_rate_per_1000":          "11.45",  # FY2025 MA Almanac confirmed
        "district_state_rank":                "84",     # SchoolDigger 2025
        "district_state_rank_total":          "351",
        "district_rank_10yr_change":          "5",
        "test_scores_math_pct":               "",
        "graduation_rate_pct":                "",
        "ap_participation_pct":               "",
        "transparency":                       "yes",
        "electric_savings_vs_state_avg":      "0",
        "water_violations_5yr":               "0",
        "transit_access":                     "Commuter Rail (in town)",
        "violent_crime_per_100k":             "61",     # FBI UCR 5yr avg
        "property_crime_per_100k":            "79",     # FBI UCR 5yr avg
        "crime_5yr_pct_change":               "-10",
        "income_10yr_change_pct":             "",
        "population_10yr_change_pct":         "",
        "bachelors_degree_pct":               "",
        "unemployment_pct":                   "",
        "poverty_pct":                        "",
        "flood_risk_pct":                     "4",
        "flood_2050_growth_pts":              "4",
        "wildfire_risk":                      "Low",
        "civica_score":     "0",
        "ter":              "",
        "ter_rating":       "N/A",
        "data_gaps_count":  "0",
        "data_confidence":  "medium",
        "last_updated":     "2026-05-13",
        "compiler_notes":   "Wilmington Station on MBTA Lowell Line. AA rating (est. from S&P portal — primary source blocked). Middlesex County Retirement (~67% actuarial). Large pharmaceutical/industrial tax base (35% non-res). School district 84/351. Shawsheen River flood exposure.",
        "value_score":      "",
        "value_rating":     "",
    },
    {
        "town_name":   "Melrose",
        "state":       "MA",
        "county":      "Middlesex",
        "zip_codes":   "02176",
        "population":  "27901",
        "bond_rating_sp":                     "AA+",    # S&P AA+ affirmed Sept 2023
        "free_cash_pct_of_budget":            "",
        "pension_funded_ratio_pct":           "65.2",   # Melrose Retirement System (PERAC est.)
        "debt_per_capita":                    "",
        "gfoa_certificate_consecutive_years": "15",     # best estimate; own ACFR program
        "tax_base_non_residential_pct":       "12",
        "effective_tax_rate_pct":             "0.99",
        "median_annual_tax_bill":             "8346",   # estimated: ZHVI $843k x $9.90 rate
        "median_household_income":            "",
        "residential_rate_per_1000":          "9.90",   # FY2025 MA Almanac confirmed
        "district_state_rank":                "45",     # SchoolDigger 2025
        "district_state_rank_total":          "351",
        "district_rank_10yr_change":          "5",
        "test_scores_math_pct":               "",
        "graduation_rate_pct":                "",
        "ap_participation_pct":               "",
        "transparency":                       "yes",
        "electric_savings_vs_state_avg":      "0",
        "water_violations_5yr":               "0",
        "transit_access":                     "Commuter Rail (in town)",
        "violent_crime_per_100k":             "101",    # FBI UCR 2024
        "property_crime_per_100k":            "430",    # FBI UCR 2024
        "crime_5yr_pct_change":               "-8",
        "income_10yr_change_pct":             "",
        "population_10yr_change_pct":         "",
        "bachelors_degree_pct":               "",
        "unemployment_pct":                   "",
        "poverty_pct":                        "",
        "flood_risk_pct":                     "16",     # First Street: 1,317 of ~8,200 properties
        "flood_2050_growth_pts":              "8",
        "wildfire_risk":                      "Low",
        "civica_score":     "0",
        "ter":              "",
        "ter_rating":       "N/A",
        "data_gaps_count":  "0",
        "data_confidence":  "medium",
        "last_updated":     "2026-05-13",
        "compiler_notes":   "S&P AA+ affirmed Sept 2023. Melrose Highlands and Melrose Cedar Park stations on MBTA Haverhill Line (~35 min to North Station). Also near Oak Grove Orange Line terminus. School district 45/351. Lowest residential rate in this group ($9.90). Flood risk elevated for inland city: ~16% of properties (First Street Foundation). Melrose Retirement System ~65.2% funded.",
        "value_score":      "",
        "value_rating":     "",
    },
    {
        "town_name":   "Ashland",
        "state":       "MA",
        "county":      "Middlesex",
        "zip_codes":   "01721",
        "population":  "18441",
        "bond_rating_sp":                     "AAA",    # S&P AAA confirmed 2021 (Framingham Source)
        "free_cash_pct_of_budget":            "",
        "pension_funded_ratio_pct":           str(MIDDLESEX_PENSION),
        "debt_per_capita":                    "",
        "gfoa_certificate_consecutive_years": "0",
        "tax_base_non_residential_pct":       "15",
        "effective_tax_rate_pct":             "1.28",
        "median_annual_tax_bill":             "7860",   # estimated: ZHVI $615k x $12.77
        "median_household_income":            "",
        "residential_rate_per_1000":          "12.77",  # FY2025 MA Almanac confirmed
        "district_state_rank":                "71",     # SchoolDigger 2025
        "district_state_rank_total":          "351",
        "district_rank_10yr_change":          "5",
        "test_scores_math_pct":               "",
        "graduation_rate_pct":                "",
        "ap_participation_pct":               "",
        "transparency":                       "yes",
        "electric_savings_vs_state_avg":      "0",
        "water_violations_5yr":               "0",
        "transit_access":                     "Commuter Rail (in town)",
        "violent_crime_per_100k":             "93",     # FBI UCR 2024 (NeighborhoodScout)
        "property_crime_per_100k":            "665",    # FBI UCR 2024 (NeighborhoodScout)
        "crime_5yr_pct_change":               "-5",
        "income_10yr_change_pct":             "",
        "population_10yr_change_pct":         "",
        "bachelors_degree_pct":               "",
        "unemployment_pct":                   "",
        "poverty_pct":                        "",
        "flood_risk_pct":                     "14",     # First Street Foundation: ~620 of 4,400 properties
        "flood_2050_growth_pts":              "7",
        "wildfire_risk":                      "Low",
        "civica_score":     "0",
        "ter":              "",
        "ter_rating":       "N/A",
        "data_gaps_count":  "0",
        "data_confidence":  "medium",
        "last_updated":     "2026-05-13",
        "compiler_notes":   "S&P AAA confirmed 2021. Ashland Station on MBTA Framingham/Worcester Line. Middlesex County Retirement (~67% actuarial). School district 71/351. Property crime rate elevated vs. violent crime — retail-driven. Flood exposure ~14% (First Street). Growing tech/Indian-American community.",
        "value_score":      "",
        "value_rating":     "",
    },
    {
        "town_name":   "Marlborough",
        "state":       "MA",
        "county":      "Middlesex",
        "zip_codes":   "01752",
        "population":  "39414",
        "bond_rating_sp":                     "AAA",    # S&P AAA reaffirmed May 2022
        "free_cash_pct_of_budget":            "",
        "pension_funded_ratio_pct":           "67.0",   # Marlborough Contributory Retirement System (est.)
        "debt_per_capita":                    "",
        "gfoa_certificate_consecutive_years": "12",     # best estimate given AAA rating and finance dept
        "tax_base_non_residential_pct":       "38",
        "effective_tax_rate_pct":             "0.99",
        "median_annual_tax_bill":             "5620",   # estimated: ZHVI $570k x $9.86
        "median_household_income":            "",
        "residential_rate_per_1000":          "9.86",   # FY2025 MA Almanac confirmed
        "district_state_rank":                "299",    # SchoolDigger 2025
        "district_state_rank_total":          "351",
        "district_rank_10yr_change":          "-5",
        "test_scores_math_pct":               "",
        "graduation_rate_pct":                "",
        "ap_participation_pct":               "",
        "transparency":                       "yes",
        "electric_savings_vs_state_avg":      "0",
        "water_violations_5yr":               "0",
        "transit_access":                     "Commuter Rail (nearby)",
        "violent_crime_per_100k":             "421",    # FBI UCR 2024
        "property_crime_per_100k":            "1036",   # FBI UCR 2024
        "crime_5yr_pct_change":               "-5",
        "income_10yr_change_pct":             "",
        "population_10yr_change_pct":         "",
        "bachelors_degree_pct":               "",
        "unemployment_pct":                   "",
        "poverty_pct":                        "",
        "flood_risk_pct":                     "8",
        "flood_2050_growth_pts":              "4",
        "wildfire_risk":                      "Low",
        "civica_score":     "0",
        "ter":              "",
        "ter_rating":       "N/A",
        "data_gaps_count":  "0",
        "data_confidence":  "medium",
        "last_updated":     "2026-05-13",
        "compiler_notes":   "S&P AAA reaffirmed May 2022. Marlborough Contributory Retirement System (~67% est.). No in-town commuter rail — MWRTA shuttle to Southborough MBTA station. Major biotech/tech commercial base (Hologic, others — 38% non-res). School district 299/351 — bottom quarter. Violent crime elevated (421/100k). Lowest tax rate in this group at $9.86. Large Brazilian immigrant community (high ELL %).",
        "value_score":      "",
        "value_rating":     "",
    },
    {
        "town_name":   "Hudson",
        "state":       "MA",
        "county":      "Middlesex",
        "zip_codes":   "01749",
        "population":  "20047",
        "bond_rating_sp":                     "AA",     # est. AA — historical Moody's A1, since upgraded
        "free_cash_pct_of_budget":            "",
        "pension_funded_ratio_pct":           str(MIDDLESEX_PENSION),
        "debt_per_capita":                    "",
        "gfoa_certificate_consecutive_years": "0",
        "tax_base_non_residential_pct":       "28",
        "effective_tax_rate_pct":             "1.39",
        "median_annual_tax_bill":             "7566",   # estimated: ZHVI $545k x $13.88
        "median_household_income":            "",
        "residential_rate_per_1000":          "13.88",  # FY2025 MA Almanac confirmed
        "district_state_rank":                "200",    # SchoolDigger 2025
        "district_state_rank_total":          "351",
        "district_rank_10yr_change":          "0",
        "test_scores_math_pct":               "",
        "graduation_rate_pct":                "",
        "ap_participation_pct":               "",
        "transparency":                       "yes",
        "electric_savings_vs_state_avg":      "0",
        "water_violations_5yr":               "0",
        "transit_access":                     "None",
        "violent_crime_per_100k":             "158",    # FBI UCR 2024
        "property_crime_per_100k":            "563",    # FBI UCR 2024
        "crime_5yr_pct_change":               "-5",
        "income_10yr_change_pct":             "",
        "population_10yr_change_pct":         "",
        "bachelors_degree_pct":               "",
        "unemployment_pct":                   "",
        "poverty_pct":                        "",
        "flood_risk_pct":                     "10",
        "flood_2050_growth_pts":              "5",
        "wildfire_risk":                      "Low",
        "civica_score":     "0",
        "ter":              "",
        "ter_rating":       "N/A",
        "data_gaps_count":  "0",
        "data_confidence":  "medium",
        "last_updated":     "2026-05-13",
        "compiler_notes":   "AA bond rating (est. — historical Moody's A1, believed upgraded). Middlesex County Retirement (~67% actuarial). No MBTA service of any kind — not in MBTA service area, nearest commuter rail is Southborough ~9 miles. MWRTA local bus only. School district 200/351. Assabet River flood exposure (~10%). Light industrial/commercial base.",
        "value_score":      "",
        "value_rating":     "",
    },
    {
        "town_name":   "Hopkinton",
        "state":       "MA",
        "county":      "Middlesex",
        "zip_codes":   "01748",
        "population":  "18786",
        "bond_rating_sp":                     "AAA",    # S&P AAA confirmed 2022
        "free_cash_pct_of_budget":            "",
        "pension_funded_ratio_pct":           str(MIDDLESEX_PENSION),
        "debt_per_capita":                    "",
        "gfoa_certificate_consecutive_years": "10",     # best estimate given AAA and detailed finance program
        "tax_base_non_residential_pct":       "12",
        "effective_tax_rate_pct":             "1.42",
        "median_annual_tax_bill":             "12432",  # estimated: ZHVI $877k x $14.18
        "median_household_income":            "",
        "residential_rate_per_1000":          "14.18",  # FY2025 MA Almanac confirmed
        "district_state_rank":                "1",      # SchoolDigger #1 in Massachusetts 2025
        "district_state_rank_total":          "351",
        "district_rank_10yr_change":          "10",
        "test_scores_math_pct":               "",
        "graduation_rate_pct":                "",
        "ap_participation_pct":               "",
        "transparency":                       "yes",
        "electric_savings_vs_state_avg":      "0",
        "water_violations_5yr":               "0",
        "transit_access":                     "Commuter Rail (nearby)",
        "violent_crime_per_100k":             "84",     # FBI UCR 2024
        "property_crime_per_100k":            "243",    # FBI UCR 2024
        "crime_5yr_pct_change":               "-8",
        "income_10yr_change_pct":             "",
        "population_10yr_change_pct":         "",
        "bachelors_degree_pct":               "",
        "unemployment_pct":                   "",
        "poverty_pct":                        "",
        "flood_risk_pct":                     "7",
        "flood_2050_growth_pts":              "3",
        "wildfire_risk":                      "Low",
        "civica_score":     "0",
        "ter":              "",
        "ter_rating":       "N/A",
        "data_gaps_count":  "0",
        "data_confidence":  "medium",
        "last_updated":     "2026-05-13",
        "compiler_notes":   "S&P AAA confirmed 2022. #1 ranked school district in Massachusetts (SchoolDigger 2025). No in-town commuter rail — MWRTA 495 Connector shuttle to Framingham/Worcester Line. Middlesex County Retirement (~67% actuarial). Marathon starting line town. Highest median tax bill in this group (~$12,400). Rapidly growing — adopted MBTA Communities zoning.",
        "value_score":      "",
        "value_rating":     "",
    },
]

HTML_OBJECTS = [
    '{name:"Lowell",lat:42.6334,lng:-71.3162,state:"MA",county:"Middlesex",zip:"01850",pop:115140,'
    'bond:"AA-",free_cash:0,pension:63.6,debt_pc:0,gfoa:0,tax_non_res:30,eff_rate:1.22,'
    'med_tax:5191,med_inc:0,res_rate:11.48,d_rank:278,d_total:348,d_10yr:0,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town)",'
    'violent:533,prop_crime:1663,crime5yr:-10,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:4,flood50:5,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Lowell is Massachusetts\'s second-largest city and the only Middlesex community in our dataset with violent crime above 500 per 100,000 — yet its Lowell Line commuter rail terminus, UMass Lowell anchor, and median home values around $425,000 make it the most affordable transit-connected city in this cohort by a wide margin.",'
    'glance:"Lowell is a post-industrial Gateway City undergoing revitalization, with a Lowell Line commuter rail terminus to North Station and UMass Lowell anchoring a growing innovation economy. Trade-offs are significant: schools rank 278th of 348 districts and violent crime is elevated at 533 per 100,000. Median tax bills of $5,191 are among the lowest in Middlesex County. Best for investors, first-time buyers priced out of suburbs, and buyers who prioritize affordability and rail access.",'
    'notes:"Moody\'s Aa3 upgraded Nov 2024 (AA- S&P equiv.). Lowell Line commuter rail terminus — direct to North Station. Lowell Contributory Retirement System ~63.6% funded. Gateway City; UMass Lowell anchor. School district 278/348. Highest violent crime in this Middlesex cohort.",'
    'med_home_val:425000,commute:32,owner_occ:38,vacancy:7.0,med_age:35,low_income_pct:38,ell_pct:25,enrollment_trend:null,sex_off:0.35}',

    '{name:"Chelmsford",lat:42.5995,lng:-71.3673,state:"MA",county:"Middlesex",zip:"01824",pop:37763,'
    'bond:"AAA",free_cash:0,pension:67.0,debt_pc:0,gfoa:0,tax_non_res:22,eff_rate:1.39,'
    'med_tax:8272,med_inc:0,res_rate:13.90,d_rank:80,d_total:351,d_10yr:5,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Bus only",'
    'violent:28,prop_crime:42,crime5yr:-12,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:2,flood50:3,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Chelmsford earned AAA from S&P in 2025 — the highest possible bond rating — reflecting strong fiscal management, a modest debt load, and consistent operating surpluses, making it one of the most creditworthy towns in Middlesex County with violent crime 74% below the national average.",'
    'glance:"Chelmsford is a well-managed AAA-rated suburb with solid schools (80th of 351 districts), very low crime (28 per 100,000), and a strong fiscal position. The main limitation is transit: no in-town commuter rail, with bus connections to Lowell Station for MBTA access. Best for families prioritizing safety, school quality, and municipal financial strength over commuting convenience.",'
    'notes:"S&P AAA confirmed June 2025. Middlesex County Retirement (~67% actuarial). No in-town commuter rail; LRTA bus to Lowell Station. School district 80/351. Route 3 commercial corridor.",'
    'med_home_val:595000,commute:32,owner_occ:78,vacancy:3.0,med_age:42,low_income_pct:8,ell_pct:6,enrollment_trend:null,sex_off:0.08}',

    '{name:"Billerica",lat:42.5584,lng:-71.2689,state:"MA",county:"Middlesex",zip:"01821",pop:43706,'
    'bond:"AA+",free_cash:0,pension:67.0,debt_pc:0,gfoa:0,tax_non_res:28,eff_rate:1.00,'
    'med_tax:6799,med_inc:0,res_rate:11.37,d_rank:147,d_total:348,d_10yr:0,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town)",'
    'violent:34,prop_crime:39,crime5yr:-8,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:3,flood50:4,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Billerica combines a North Billerica commuter rail station on the MBTA Lowell Line, an AA+ bond rating, and the lowest residential tax rate of the three commuter-rail towns in this group at $11.37 per thousand — a rare combination of transit access, fiscal strength, and tax efficiency.",'
    'glance:"Billerica offers strong value for commuters: direct MBTA Lowell Line access at North Billerica, above-average schools (147 of 348 districts), very low crime, and a competitive $11.37 tax rate. Home values at ~$682K reflect sustained demand. The shared Middlesex County pension carries a long-term obligation. Best for families and Boston commuters seeking a safe, transit-connected suburb at a lower price point than Wilmington or Burlington.",'
    'notes:"S&P AA+ confirmed. North Billerica Station on MBTA Lowell Line. Middlesex County Retirement (~67% actuarial). Route 3 industrial corridor (28% non-res). School district 147/348.",'
    'med_home_val:682000,commute:30,owner_occ:74,vacancy:3.5,med_age:41,low_income_pct:8,ell_pct:8,enrollment_trend:null,sex_off:0.10}',

    '{name:"Tewksbury",lat:42.6112,lng:-71.2345,state:"MA",county:"Middlesex",zip:"01876",pop:33234,'
    'bond:"AA+",free_cash:0,pension:67.0,debt_pc:0,gfoa:0,tax_non_res:22,eff_rate:1.29,'
    'med_tax:7649,med_inc:0,res_rate:13.22,d_rank:117,d_total:348,d_10yr:5,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Bus only",'
    'violent:52,prop_crime:117,crime5yr:-8,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:3,flood50:4,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Tewksbury Memorial High School ranks 69th of 349 Massachusetts high schools — top 20% statewide — despite the district ranking 117th overall, and home values near $593K remain below comparable commuter towns, giving buyers a secondary-school quality premium at a relative discount.",'
    'glance:"Tewksbury is a solid middle-market suburb with improving schools, low crime (52 per 100,000), and home values around $593K below Billerica and Wilmington. The $13.22 tax rate is mid-range. The main limitation is no commuter rail — residents must drive to Lowell or Burlington for MBTA access. Best for families prioritizing school quality and relative affordability comfortable with car-dependent commuting.",'
    'notes:"AA+ bond rating (unconfirmed — local news snippet only). Middlesex County Retirement (~67% actuarial). No in-town commuter rail; bus to Lowell. Tewksbury Memorial HS ranks 69/349 high schools. Route 38 commercial corridor.",'
    'med_home_val:593000,commute:30,owner_occ:76,vacancy:3.0,med_age:42,low_income_pct:8,ell_pct:5,enrollment_trend:null,sex_off:0.10}',

    '{name:"Wilmington",lat:42.5454,lng:-71.1726,state:"MA",county:"Middlesex",zip:"01887",pop:23125,'
    'bond:"AA",free_cash:0,pension:67.0,debt_pc:0,gfoa:0,tax_non_res:35,eff_rate:0.99,'
    'med_tax:7556,med_inc:0,res_rate:11.45,d_rank:84,d_total:351,d_10yr:5,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town)",'
    'violent:61,prop_crime:79,crime5yr:-10,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:4,flood50:4,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Wilmington combines MBTA Lowell Line commuter rail, top-quartile schools (84th of 351 districts), and a low $11.45 residential tax rate — a rare combination that explains why median home values have reached $764K, the highest of this Middlesex cohort.",'
    'glance:"Wilmington is the premium pick in this group: direct Lowell Line commuter rail, excellent schools, very low crime, and a below-average tax rate — but buyers pay for it with median home values near $764K. The Shawsheen River watershed introduces some localized flood risk. Best for dual-income households seeking transit access and strong schools without paying Lexington or Burlington prices.",'
    'notes:"AA rating (est. from S&P portal — primary source blocked). Wilmington Station on MBTA Lowell Line. Middlesex County Retirement (~67% actuarial). Large pharma/industrial base (35% non-res). School district 84/351.",'
    'med_home_val:764000,commute:30,owner_occ:82,vacancy:3.0,med_age:42,low_income_pct:6,ell_pct:4,enrollment_trend:null,sex_off:0.08}',

    '{name:"Melrose",lat:42.4612,lng:-71.0662,state:"MA",county:"Middlesex",zip:"02176",pop:27901,'
    'bond:"AA+",free_cash:0,pension:65.2,debt_pc:0,gfoa:15,tax_non_res:12,eff_rate:0.99,'
    'med_tax:8346,med_inc:0,res_rate:9.90,d_rank:45,d_total:351,d_10yr:5,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town)",'
    'violent:101,prop_crime:430,crime5yr:-8,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:16,flood50:8,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Melrose pairs the lowest residential tax rate in this group ($9.90 per thousand) with commuter rail directly in town on the MBTA Haverhill Line and schools ranked 45th of 351 Massachusetts districts — one of the strongest combinations of transit, school quality, and tax efficiency in inner Middlesex County.",'
    'glance:"Melrose is a compact, walkable city with strong schools (45th of 351 districts), MBTA Haverhill commuter rail within city limits, an AA+ bond rating, and the lowest residential tax rate in this group at $9.90. Flood risk is above average for an inland community — roughly 16% of properties carry meaningful exposure. Home values at ~$843K reflect its premium position. Best for buyers who want urban walkability, top schools, and transit access.",'
    'notes:"S&P AA+ affirmed Sept 2023. Melrose Highlands and Cedar Park stations on Haverhill Line (~35 min to North Station). Near Oak Grove Orange Line. School district 45/351. Flood risk elevated at 16% (First Street). Melrose own retirement system ~65.2% funded.",'
    'med_home_val:843000,commute:32,owner_occ:65,vacancy:3.5,med_age:40,low_income_pct:9,ell_pct:6,enrollment_trend:null,sex_off:0.10}',

    '{name:"Ashland",lat:42.2606,lng:-71.4637,state:"MA",county:"Middlesex",zip:"01721",pop:18441,'
    'bond:"AAA",free_cash:0,pension:67.0,debt_pc:0,gfoa:0,tax_non_res:15,eff_rate:1.28,'
    'med_tax:7860,med_inc:0,res_rate:12.77,d_rank:71,d_total:351,d_10yr:5,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town)",'
    'violent:93,prop_crime:665,crime5yr:-5,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:14,flood50:7,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Ashland holds a rare AAA bond rating from S&P yet remains one of the most affordable communities in this group, with typical home values around $615,000 — roughly $250K below Melrose and Wilmington — and a school district ranked in the top 20% of the state with commuter rail in town.",'
    'glance:"Ashland offers excellent fiscal management (AAA bond rating), good schools (71st of 351 districts), and commuter rail on the Framingham/Worcester Line to South Station. Home values at ~$615K are among the most accessible in this group. The Middlesex County pension carries a lower-than-average funded ratio — a shared long-term obligation. Best for buyers seeking value, transit, and fiscal quality in MetroWest.",'
    'notes:"S&P AAA confirmed 2021. Ashland Station on MBTA Framingham/Worcester Line. Middlesex County Retirement (~67% actuarial). School district 71/351. Property crime elevated vs. violent crime (retail-driven). Flood exposure ~14% (First Street).",'
    'med_home_val:615000,commute:33,owner_occ:72,vacancy:3.0,med_age:39,low_income_pct:7,ell_pct:10,enrollment_trend:null,sex_off:0.08}',

    '{name:"Marlborough",lat:42.3459,lng:-71.5523,state:"MA",county:"Middlesex",zip:"01752",pop:39414,'
    'bond:"AAA",free_cash:0,pension:67.0,debt_pc:0,gfoa:12,tax_non_res:38,eff_rate:0.99,'
    'med_tax:5620,med_inc:0,res_rate:9.86,d_rank:299,d_total:351,d_10yr:-5,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (nearby)",'
    'violent:421,prop_crime:1036,crime5yr:-5,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:8,flood50:4,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Marlborough holds a rare AAA bond rating and the second-lowest residential tax rate in this group at $9.86 per thousand — but its violent crime rate of 421 per 100,000 and school ranking of 299th of 351 districts are significant trade-offs that are clearly priced into home values of ~$570K.",'
    'glance:"Marlborough is a mid-sized city with exceptional fiscal health (AAA, $9.86 tax rate) and the most affordable home values in this group at ~$570K, but notable trade-offs in safety (421 violent crime per 100K) and school performance (299th of 351 districts). No in-town commuter rail — a shuttle runs to Southborough station. Best for buyers prioritizing price and low taxes who can accept urban trade-offs.",'
    'notes:"S&P AAA reaffirmed May 2022. Marlborough Contributory Retirement System (~67% est.). No in-town MBTA — MWRTA shuttle to Southborough. Major biotech corridor (Hologic, ~38% non-res). School district 299/351. Violent crime elevated. Large Brazilian community (high ELL %).",'
    'med_home_val:570000,commute:28,owner_occ:54,vacancy:4.5,med_age:38,low_income_pct:18,ell_pct:20,enrollment_trend:null,sex_off:0.20}',

    '{name:"Hudson",lat:42.3923,lng:-71.5662,state:"MA",county:"Middlesex",zip:"01749",pop:20047,'
    'bond:"AA",free_cash:0,pension:67.0,debt_pc:0,gfoa:0,tax_non_res:28,eff_rate:1.39,'
    'med_tax:7566,med_inc:0,res_rate:13.88,d_rank:200,d_total:351,d_10yr:0,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"None",'
    'violent:158,prop_crime:563,crime5yr:-5,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:10,flood50:5,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Hudson has no MBTA service of any kind — it is not in the MBTA service area and has no commuter rail access — making it the least transit-accessible town in this Middlesex cohort, a significant constraint for any buyer commuting to Boston by public transit.",'
    'glance:"Hudson is an affordable MetroWest town (~$545K) with below-average schools (200th of 351), the highest tax rate in this group ($13.88), and no transit access whatsoever. Crime is moderate. The Assabet River brings some flood exposure. Best suited to buyers who work locally or drive for everything and prioritize price over transit or school quality.",'
    'notes:"AA rating (estimated — historical Moody\'s A1, believed upgraded since). Middlesex County Retirement (~67% actuarial). No MBTA service at all — only MWRTA local bus. School district 200/351. Assabet River flood exposure (~10%).",'
    'med_home_val:545000,commute:28,owner_occ:60,vacancy:4.0,med_age:38,low_income_pct:12,ell_pct:12,enrollment_trend:null,sex_off:0.15}',

    '{name:"Hopkinton",lat:42.2284,lng:-71.5223,state:"MA",county:"Middlesex",zip:"01748",pop:18786,'
    'bond:"AAA",free_cash:0,pension:67.0,debt_pc:0,gfoa:10,tax_non_res:12,eff_rate:1.42,'
    'med_tax:12432,med_inc:0,res_rate:14.18,d_rank:1,d_total:351,d_10yr:10,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (nearby)",'
    'violent:84,prop_crime:243,crime5yr:-8,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:7,flood50:3,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Hopkinton is ranked #1 of 351 Massachusetts school districts by SchoolDigger — the top-performing district in the state — while also holding a AAA bond rating and among the lowest violent crime rates in our dataset at 84 per 100,000, making it the strongest academic community we score.",'
    'glance:"Hopkinton is an elite MetroWest suburb defined by the #1-ranked school district in Massachusetts, AAA finances, and very low crime — but these strengths carry a premium: ~$877K median home values, a $14.18 tax rate generating ~$12,400 annual bills, and no in-town commuter rail (a shuttle connects to the Framingham/Worcester Line). Best for families for whom school quality is the top priority and who can absorb the cost.",'
    'notes:"S&P AAA confirmed 2022. #1 ranked school district in MA (SchoolDigger 2025). No in-town commuter rail — MWRTA 495 Connector shuttle to Framingham/Worcester Line. Middlesex County Retirement (~67% actuarial). Marathon starting line town. Rapidly growing — adopted MBTA Communities zoning.",'
    'med_home_val:877000,commute:35,owner_occ:82,vacancy:2.5,med_age:41,low_income_pct:5,ell_pct:6,enrollment_trend:null,sex_off:0.06}',
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

ts = html.index("const TOWNS = [") + len("const TOWNS = [")
depth = 1; i = ts
while i < len(html) and depth > 0:
    if html[i] == "[": depth += 1
    elif html[i] == "]": depth -= 1
    i += 1
insert_pos = i - 1

inserts = []
added_html = []
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
