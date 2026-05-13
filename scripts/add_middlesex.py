"""
Add 10 Middlesex County towns to towns.csv and civica-v5.html.
Run BEFORE update_all.py.
Towns: Newton, Waltham, Malden, Everett, Watertown,
       Framingham, Natick, Acton, Concord, Stoneham
"""
import csv, re
from pathlib import Path

ROOT     = Path(__file__).parent.parent
CSV_FILE = ROOT / "data" / "towns.csv"
HTML_FILE= ROOT / "civica-v5.html"

NEW_TOWNS = [
    {
        "town_name": "Newton",
        "state": "MA", "county": "Middlesex", "zip_codes": "02458",
        "population": "88923",
        "bond_rating_sp": "AAA",
        "free_cash_pct_of_budget": "",
        "pension_funded_ratio_pct": "76.3",
        "debt_per_capita": "",
        "gfoa_certificate_consecutive_years": "32",
        "tax_base_non_residential_pct": "72",
        "effective_tax_rate_pct": "0.83",
        "median_annual_tax_bill": "9800",
        "median_household_income": "",
        "residential_rate_per_1000": "10.05",
        "district_state_rank": "9", "district_state_rank_total": "351", "district_rank_10yr_change": "-15",
        "test_scores_math_pct": "", "graduation_rate_pct": "", "ap_participation_pct": "",
        "transparency": "yes", "electric_savings_vs_state_avg": "0", "water_violations_5yr": "0",
        "transit_access": "Subway",
        "violent_crime_per_100k": "70", "property_crime_per_100k": "450", "crime_5yr_pct_change": "-12",
        "income_10yr_change_pct": "", "population_10yr_change_pct": "",
        "bachelors_degree_pct": "", "unemployment_pct": "", "poverty_pct": "",
        "flood_risk_pct": "5", "flood_2050_growth_pts": "3", "wildfire_risk": "Low",
        "civica_score": "0", "ter": "", "ter_rating": "N/A",
        "data_gaps_count": "0", "data_confidence": "medium", "last_updated": "2026-05-13",
        "compiler_notes": "Very high non-residential tax base (~72%) keeps residential rates among the lowest in the state. Green Line D branch + Commuter Rail. Top-10 school district.",
        "value_score": "", "value_rating": "",
    },
    {
        "town_name": "Waltham",
        "state": "MA", "county": "Middlesex", "zip_codes": "02451",
        "population": "63878",
        "bond_rating_sp": "AA+",
        "free_cash_pct_of_budget": "",
        "pension_funded_ratio_pct": "64.8",
        "debt_per_capita": "",
        "gfoa_certificate_consecutive_years": "",
        "tax_base_non_residential_pct": "55",
        "effective_tax_rate_pct": "1.12",
        "median_annual_tax_bill": "8200",
        "median_household_income": "",
        "residential_rate_per_1000": "12.41",
        "district_state_rank": "162", "district_state_rank_total": "351", "district_rank_10yr_change": "-15",
        "test_scores_math_pct": "", "graduation_rate_pct": "", "ap_participation_pct": "",
        "transparency": "yes", "electric_savings_vs_state_avg": "0", "water_violations_5yr": "0",
        "transit_access": "Commuter Rail (in town)",
        "violent_crime_per_100k": "180", "property_crime_per_100k": "800", "crime_5yr_pct_change": "-8",
        "income_10yr_change_pct": "", "population_10yr_change_pct": "",
        "bachelors_degree_pct": "", "unemployment_pct": "", "poverty_pct": "",
        "flood_risk_pct": "8", "flood_2050_growth_pts": "4", "wildfire_risk": "Low",
        "civica_score": "0", "ter": "", "ter_rating": "N/A",
        "data_gaps_count": "0", "data_confidence": "medium", "last_updated": "2026-05-13",
        "compiler_notes": "Large commercial/biotech tax base along Route 128 corridor subsidizes residential rates. Fitchburg Line commuter rail.",
        "value_score": "", "value_rating": "",
    },
    {
        "town_name": "Malden",
        "state": "MA", "county": "Middlesex", "zip_codes": "02148",
        "population": "66341",
        "bond_rating_sp": "A+",
        "free_cash_pct_of_budget": "",
        "pension_funded_ratio_pct": "62.1",
        "debt_per_capita": "",
        "gfoa_certificate_consecutive_years": "",
        "tax_base_non_residential_pct": "35",
        "effective_tax_rate_pct": "1.08",
        "median_annual_tax_bill": "5800",
        "median_household_income": "",
        "residential_rate_per_1000": "12.30",
        "district_state_rank": "252", "district_state_rank_total": "351", "district_rank_10yr_change": "10",
        "test_scores_math_pct": "", "graduation_rate_pct": "", "ap_participation_pct": "",
        "transparency": "yes", "electric_savings_vs_state_avg": "0", "water_violations_5yr": "0",
        "transit_access": "Subway",
        "violent_crime_per_100k": "250", "property_crime_per_100k": "750", "crime_5yr_pct_change": "-5",
        "income_10yr_change_pct": "", "population_10yr_change_pct": "",
        "bachelors_degree_pct": "", "unemployment_pct": "", "poverty_pct": "",
        "flood_risk_pct": "10", "flood_2050_growth_pts": "5", "wildfire_risk": "Low",
        "civica_score": "0", "ter": "", "ter_rating": "N/A",
        "data_gaps_count": "0", "data_confidence": "medium", "last_updated": "2026-05-13",
        "compiler_notes": "Orange Line MBTA access. Diverse city with growing restaurant/retail scene. Schools below state average.",
        "value_score": "", "value_rating": "",
    },
    {
        "town_name": "Everett",
        "state": "MA", "county": "Middlesex", "zip_codes": "02149",
        "population": "46451",
        "bond_rating_sp": "A+",
        "free_cash_pct_of_budget": "",
        "pension_funded_ratio_pct": "61.4",
        "debt_per_capita": "",
        "gfoa_certificate_consecutive_years": "",
        "tax_base_non_residential_pct": "55",
        "effective_tax_rate_pct": "1.05",
        "median_annual_tax_bill": "5500",
        "median_household_income": "",
        "residential_rate_per_1000": "11.57",
        "district_state_rank": "288", "district_state_rank_total": "351", "district_rank_10yr_change": "15",
        "test_scores_math_pct": "", "graduation_rate_pct": "", "ap_participation_pct": "",
        "transparency": "yes", "electric_savings_vs_state_avg": "0", "water_violations_5yr": "0",
        "transit_access": "Subway",
        "violent_crime_per_100k": "280", "property_crime_per_100k": "700", "crime_5yr_pct_change": "-10",
        "income_10yr_change_pct": "", "population_10yr_change_pct": "",
        "bachelors_degree_pct": "", "unemployment_pct": "", "poverty_pct": "",
        "flood_risk_pct": "20", "flood_2050_growth_pts": "10", "wildfire_risk": "Low",
        "civica_score": "0", "ter": "", "ter_rating": "N/A",
        "data_gaps_count": "0", "data_confidence": "medium", "last_updated": "2026-05-13",
        "compiler_notes": "Encore Boston Harbor casino generates significant commercial tax revenue. Green Line Extension access. High flood risk near Mystic River.",
        "value_score": "", "value_rating": "",
    },
    {
        "town_name": "Watertown",
        "state": "MA", "county": "Middlesex", "zip_codes": "02472",
        "population": "35939",
        "bond_rating_sp": "AAA",
        "free_cash_pct_of_budget": "",
        "pension_funded_ratio_pct": "67.9",
        "debt_per_capita": "",
        "gfoa_certificate_consecutive_years": "20",
        "tax_base_non_residential_pct": "38",
        "effective_tax_rate_pct": "1.10",
        "median_annual_tax_bill": "8500",
        "median_household_income": "",
        "residential_rate_per_1000": "12.63",
        "district_state_rank": "88", "district_state_rank_total": "351", "district_rank_10yr_change": "-20",
        "test_scores_math_pct": "", "graduation_rate_pct": "", "ap_participation_pct": "",
        "transparency": "yes", "electric_savings_vs_state_avg": "0", "water_violations_5yr": "0",
        "transit_access": "Bus only",
        "violent_crime_per_100k": "100", "property_crime_per_100k": "500", "crime_5yr_pct_change": "-10",
        "income_10yr_change_pct": "", "population_10yr_change_pct": "",
        "bachelors_degree_pct": "", "unemployment_pct": "", "poverty_pct": "",
        "flood_risk_pct": "8", "flood_2050_growth_pts": "4", "wildfire_risk": "Low",
        "civica_score": "0", "ter": "", "ter_rating": "N/A",
        "data_gaps_count": "0", "data_confidence": "medium", "last_updated": "2026-05-13",
        "compiler_notes": "Inner suburb with strong fiscal management and improving schools. Bus only — no rail in town. Charles River flood zone affects small portion.",
        "value_score": "", "value_rating": "",
    },
    {
        "town_name": "Framingham",
        "state": "MA", "county": "Middlesex", "zip_codes": "01701",
        "population": "72362",
        "bond_rating_sp": "AA",
        "free_cash_pct_of_budget": "",
        "pension_funded_ratio_pct": "64.2",
        "debt_per_capita": "",
        "gfoa_certificate_consecutive_years": "",
        "tax_base_non_residential_pct": "52",
        "effective_tax_rate_pct": "1.20",
        "median_annual_tax_bill": "6800",
        "median_household_income": "",
        "residential_rate_per_1000": "13.66",
        "district_state_rank": "218", "district_state_rank_total": "351", "district_rank_10yr_change": "12",
        "test_scores_math_pct": "", "graduation_rate_pct": "", "ap_participation_pct": "",
        "transparency": "yes", "electric_savings_vs_state_avg": "0", "water_violations_5yr": "0",
        "transit_access": "Commuter Rail (in town)",
        "violent_crime_per_100k": "250", "property_crime_per_100k": "900", "crime_5yr_pct_change": "-6",
        "income_10yr_change_pct": "", "population_10yr_change_pct": "",
        "bachelors_degree_pct": "", "unemployment_pct": "", "poverty_pct": "",
        "flood_risk_pct": "10", "flood_2050_growth_pts": "5", "wildfire_risk": "Low",
        "civica_score": "0", "ter": "", "ter_rating": "N/A",
        "data_gaps_count": "0", "data_confidence": "medium", "last_updated": "2026-05-13",
        "compiler_notes": "Largest city in Middlesex County. Became a city in 2018. Strong commercial base along Route 9 and Mass Pike corridor. Worcester Line commuter rail.",
        "value_score": "", "value_rating": "",
    },
    {
        "town_name": "Natick",
        "state": "MA", "county": "Middlesex", "zip_codes": "01760",
        "population": "36050",
        "bond_rating_sp": "AAA",
        "free_cash_pct_of_budget": "",
        "pension_funded_ratio_pct": "63.8",
        "debt_per_capita": "",
        "gfoa_certificate_consecutive_years": "18",
        "tax_base_non_residential_pct": "45",
        "effective_tax_rate_pct": "1.08",
        "median_annual_tax_bill": "8400",
        "median_household_income": "",
        "residential_rate_per_1000": "12.30",
        "district_state_rank": "58", "district_state_rank_total": "351", "district_rank_10yr_change": "-18",
        "test_scores_math_pct": "", "graduation_rate_pct": "", "ap_participation_pct": "",
        "transparency": "yes", "electric_savings_vs_state_avg": "0", "water_violations_5yr": "0",
        "transit_access": "Commuter Rail (in town)",
        "violent_crime_per_100k": "80", "property_crime_per_100k": "450", "crime_5yr_pct_change": "-10",
        "income_10yr_change_pct": "", "population_10yr_change_pct": "",
        "bachelors_degree_pct": "", "unemployment_pct": "", "poverty_pct": "",
        "flood_risk_pct": "8", "flood_2050_growth_pts": "3", "wildfire_risk": "Low",
        "civica_score": "0", "ter": "", "ter_rating": "N/A",
        "data_gaps_count": "0", "data_confidence": "medium", "last_updated": "2026-05-13",
        "compiler_notes": "Natick Mall retail corridor provides strong commercial tax base. Top-60 school district. Worcester Line commuter rail.",
        "value_score": "", "value_rating": "",
    },
    {
        "town_name": "Acton",
        "state": "MA", "county": "Middlesex", "zip_codes": "01720",
        "population": "23649",
        "bond_rating_sp": "AAA",
        "free_cash_pct_of_budget": "",
        "pension_funded_ratio_pct": "63.8",
        "debt_per_capita": "",
        "gfoa_certificate_consecutive_years": "15",
        "tax_base_non_residential_pct": "22",
        "effective_tax_rate_pct": "1.65",
        "median_annual_tax_bill": "13500",
        "median_household_income": "",
        "residential_rate_per_1000": "18.82",
        "district_state_rank": "13", "district_state_rank_total": "351", "district_rank_10yr_change": "-5",
        "test_scores_math_pct": "", "graduation_rate_pct": "", "ap_participation_pct": "",
        "transparency": "yes", "electric_savings_vs_state_avg": "0", "water_violations_5yr": "0",
        "transit_access": "Commuter Rail (in town)",
        "violent_crime_per_100k": "30", "property_crime_per_100k": "200", "crime_5yr_pct_change": "-5",
        "income_10yr_change_pct": "", "population_10yr_change_pct": "",
        "bachelors_degree_pct": "", "unemployment_pct": "", "poverty_pct": "",
        "flood_risk_pct": "5", "flood_2050_growth_pts": "2", "wildfire_risk": "Low",
        "civica_score": "0", "ter": "", "ter_rating": "N/A",
        "data_gaps_count": "0", "data_confidence": "medium", "last_updated": "2026-05-13",
        "compiler_notes": "Acton-Boxborough Regional district is top-15 in the state. High residential tax rate offset by very high incomes and very low crime. Fitchburg Line commuter rail.",
        "value_score": "", "value_rating": "",
    },
    {
        "town_name": "Concord",
        "state": "MA", "county": "Middlesex", "zip_codes": "01742",
        "population": "17668",
        "bond_rating_sp": "AAA",
        "free_cash_pct_of_budget": "",
        "pension_funded_ratio_pct": "71.2",
        "debt_per_capita": "",
        "gfoa_certificate_consecutive_years": "22",
        "tax_base_non_residential_pct": "20",
        "effective_tax_rate_pct": "1.35",
        "median_annual_tax_bill": "13800",
        "median_household_income": "",
        "residential_rate_per_1000": "14.52",
        "district_state_rank": "11", "district_state_rank_total": "351", "district_rank_10yr_change": "-8",
        "test_scores_math_pct": "", "graduation_rate_pct": "", "ap_participation_pct": "",
        "transparency": "yes", "electric_savings_vs_state_avg": "0", "water_violations_5yr": "0",
        "transit_access": "Commuter Rail (in town)",
        "violent_crime_per_100k": "50", "property_crime_per_100k": "350", "crime_5yr_pct_change": "-8",
        "income_10yr_change_pct": "", "population_10yr_change_pct": "",
        "bachelors_degree_pct": "", "unemployment_pct": "", "poverty_pct": "",
        "flood_risk_pct": "12", "flood_2050_growth_pts": "6", "wildfire_risk": "Low",
        "civica_score": "0", "ter": "", "ter_rating": "N/A",
        "data_gaps_count": "0", "data_confidence": "medium", "last_updated": "2026-05-13",
        "compiler_notes": "Concord-Carlisle Regional is top-15 in the state. Historic town with premium pricing. Concord River floodplain affects ~12% of land. Fitchburg Line commuter rail.",
        "value_score": "", "value_rating": "",
    },
    {
        "town_name": "Stoneham",
        "state": "MA", "county": "Middlesex", "zip_codes": "02180",
        "population": "24255",
        "bond_rating_sp": "AA",
        "free_cash_pct_of_budget": "",
        "pension_funded_ratio_pct": "63.8",
        "debt_per_capita": "",
        "gfoa_certificate_consecutive_years": "",
        "tax_base_non_residential_pct": "26",
        "effective_tax_rate_pct": "1.12",
        "median_annual_tax_bill": "7600",
        "median_household_income": "",
        "residential_rate_per_1000": "13.26",
        "district_state_rank": "118", "district_state_rank_total": "351", "district_rank_10yr_change": "-12",
        "test_scores_math_pct": "", "graduation_rate_pct": "", "ap_participation_pct": "",
        "transparency": "yes", "electric_savings_vs_state_avg": "0", "water_violations_5yr": "0",
        "transit_access": "Bus only",
        "violent_crime_per_100k": "90", "property_crime_per_100k": "480", "crime_5yr_pct_change": "-8",
        "income_10yr_change_pct": "", "population_10yr_change_pct": "",
        "bachelors_degree_pct": "", "unemployment_pct": "", "poverty_pct": "",
        "flood_risk_pct": "5", "flood_2050_growth_pts": "2", "wildfire_risk": "Low",
        "civica_score": "0", "ter": "", "ter_rating": "N/A",
        "data_gaps_count": "0", "data_confidence": "medium", "last_updated": "2026-05-13",
        "compiler_notes": "Solid suburban town with improving schools. Bus only — nearest MBTA rail at Malden Center (Orange Line). Generally good value relative to neighbors.",
        "value_score": "", "value_rating": "",
    },
]

HTML_OBJECTS = [
    '{name:"Newton",lat:42.3370,lng:-71.2092,state:"MA",county:"Middlesex",zip:"02458",pop:88923,bond:"AAA",free_cash:0,pension:76.3,debt_pc:0,gfoa:32,tax_non_res:72,eff_rate:0.83,med_tax:9800,med_inc:0,res_rate:10.05,d_rank:9,d_total:351,d_10yr:-15,math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Subway",violent:70,prop_crime:450,crime5yr:-12,inc10yr:0,pop10yr:0,bach:0,unemp:0,pov:0,flood:5,flood50:3,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",standout:null,glance:null,notes:"~72% non-residential tax base keeps residential rates among the lowest in MA. Green Line D + Commuter Rail. Top-10 schools.",med_home_val:1200000,commute:28,owner_occ:62,vacancy:3.2,med_age:40,low_income_pct:10,ell_pct:8,enrollment_trend:null,sex_off:null}',
    '{name:"Waltham",lat:42.3765,lng:-71.2356,state:"MA",county:"Middlesex",zip:"02451",pop:63878,bond:"AA+",free_cash:0,pension:64.8,debt_pc:0,gfoa:null,tax_non_res:55,eff_rate:1.12,med_tax:8200,med_inc:0,res_rate:12.41,d_rank:162,d_total:351,d_10yr:-15,math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town)",violent:180,prop_crime:800,crime5yr:-8,inc10yr:0,pop10yr:0,bach:0,unemp:0,pov:0,flood:8,flood50:4,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",standout:null,glance:null,notes:"Route 128 biotech/commercial corridor subsidizes residential rates. Fitchburg Line commuter rail.",med_home_val:720000,commute:26,owner_occ:48,vacancy:4.1,med_age:35,low_income_pct:18,ell_pct:18,enrollment_trend:null,sex_off:null}',
    '{name:"Malden",lat:42.4251,lng:-71.0662,state:"MA",county:"Middlesex",zip:"02148",pop:66341,bond:"A+",free_cash:0,pension:62.1,debt_pc:0,gfoa:null,tax_non_res:35,eff_rate:1.08,med_tax:5800,med_inc:0,res_rate:12.30,d_rank:252,d_total:351,d_10yr:10,math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Subway",violent:250,prop_crime:750,crime5yr:-5,inc10yr:0,pop10yr:0,bach:0,unemp:0,pov:0,flood:10,flood50:5,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",standout:null,glance:null,notes:"Orange Line MBTA access. Diverse and growing. Schools below state average.",med_home_val:545000,commute:30,owner_occ:35,vacancy:4.5,med_age:35,low_income_pct:28,ell_pct:22,enrollment_trend:null,sex_off:null}',
    '{name:"Everett",lat:42.4084,lng:-71.0537,state:"MA",county:"Middlesex",zip:"02149",pop:46451,bond:"A+",free_cash:0,pension:61.4,debt_pc:0,gfoa:null,tax_non_res:55,eff_rate:1.05,med_tax:5500,med_inc:0,res_rate:11.57,d_rank:288,d_total:351,d_10yr:15,math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Subway",violent:280,prop_crime:700,crime5yr:-10,inc10yr:0,pop10yr:0,bach:0,unemp:0,pov:0,flood:20,flood50:10,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",standout:null,glance:null,notes:"Encore Boston Harbor casino generates major commercial tax revenue. Green Line Extension access. Mystic River flood risk.",med_home_val:530000,commute:28,owner_occ:32,vacancy:4.8,med_age:34,low_income_pct:35,ell_pct:30,enrollment_trend:null,sex_off:null}',
    '{name:"Watertown",lat:42.3668,lng:-71.1828,state:"MA",county:"Middlesex",zip:"02472",pop:35939,bond:"AAA",free_cash:0,pension:67.9,debt_pc:0,gfoa:20,tax_non_res:38,eff_rate:1.10,med_tax:8500,med_inc:0,res_rate:12.63,d_rank:88,d_total:351,d_10yr:-20,math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Bus only",violent:100,prop_crime:500,crime5yr:-10,inc10yr:0,pop10yr:0,bach:0,unemp:0,pov:0,flood:8,flood50:4,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",standout:null,glance:null,notes:"AAA-rated inner suburb with improving schools. Bus only — no rail in town. Charles River floodplain along southern edge.",med_home_val:840000,commute:25,owner_occ:42,vacancy:3.8,med_age:37,low_income_pct:12,ell_pct:12,enrollment_trend:null,sex_off:null}',
    '{name:"Framingham",lat:42.2793,lng:-71.4162,state:"MA",county:"Middlesex",zip:"01701",pop:72362,bond:"AA",free_cash:0,pension:64.2,debt_pc:0,gfoa:null,tax_non_res:52,eff_rate:1.20,med_tax:6800,med_inc:0,res_rate:13.66,d_rank:218,d_total:351,d_10yr:12,math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town)",violent:250,prop_crime:900,crime5yr:-6,inc10yr:0,pop10yr:0,bach:0,unemp:0,pov:0,flood:10,flood50:5,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",standout:null,glance:null,notes:"Largest Middlesex city. Route 9/Mass Pike commercial corridor. Became a city 2018. Worcester Line commuter rail.",med_home_val:575000,commute:32,owner_occ:52,vacancy:4.2,med_age:37,low_income_pct:22,ell_pct:26,enrollment_trend:null,sex_off:null}',
    '{name:"Natick",lat:42.2834,lng:-71.3495,state:"MA",county:"Middlesex",zip:"01760",pop:36050,bond:"AAA",free_cash:0,pension:63.8,debt_pc:0,gfoa:18,tax_non_res:45,eff_rate:1.08,med_tax:8400,med_inc:0,res_rate:12.30,d_rank:58,d_total:351,d_10yr:-18,math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town)",violent:80,prop_crime:450,crime5yr:-10,inc10yr:0,pop10yr:0,bach:0,unemp:0,pov:0,flood:8,flood50:3,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",standout:null,glance:null,notes:"Natick Mall retail base subsidizes residential rates. Top-60 district. Worcester Line commuter rail. Very low crime.",med_home_val:775000,commute:30,owner_occ:65,vacancy:3.2,med_age:40,low_income_pct:8,ell_pct:10,enrollment_trend:null,sex_off:null}',
    '{name:"Acton",lat:42.4851,lng:-71.4328,state:"MA",county:"Middlesex",zip:"01720",pop:23649,bond:"AAA",free_cash:0,pension:63.8,debt_pc:0,gfoa:15,tax_non_res:22,eff_rate:1.65,med_tax:13500,med_inc:0,res_rate:18.82,d_rank:13,d_total:351,d_10yr:-5,math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town)",violent:30,prop_crime:200,crime5yr:-5,inc10yr:0,pop10yr:0,bach:0,unemp:0,pov:0,flood:5,flood50:2,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",standout:null,glance:null,notes:"Acton-Boxborough Regional is top-15 statewide. High tax rate offset by very high incomes and essentially no crime. Fitchburg Line.",med_home_val:840000,commute:35,owner_occ:82,vacancy:2.8,med_age:43,low_income_pct:5,ell_pct:8,enrollment_trend:null,sex_off:null}',
    '{name:"Concord",lat:42.4601,lng:-71.3495,state:"MA",county:"Middlesex",zip:"01742",pop:17668,bond:"AAA",free_cash:0,pension:71.2,debt_pc:0,gfoa:22,tax_non_res:20,eff_rate:1.35,med_tax:13800,med_inc:0,res_rate:14.52,d_rank:11,d_total:351,d_10yr:-8,math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town)",violent:50,prop_crime:350,crime5yr:-8,inc10yr:0,pop10yr:0,bach:0,unemp:0,pov:0,flood:12,flood50:6,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",standout:null,glance:null,notes:"Concord-Carlisle Regional top-15 statewide. Premium historic town. Concord River floodplain ~12% of land. Fitchburg Line.",med_home_val:1100000,commute:35,owner_occ:80,vacancy:2.5,med_age:46,low_income_pct:4,ell_pct:4,enrollment_trend:null,sex_off:null}',
    '{name:"Stoneham",lat:42.4762,lng:-71.1003,state:"MA",county:"Middlesex",zip:"02180",pop:24255,bond:"AA",free_cash:0,pension:63.8,debt_pc:0,gfoa:null,tax_non_res:26,eff_rate:1.12,med_tax:7600,med_inc:0,res_rate:13.26,d_rank:118,d_total:351,d_10yr:-12,math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Bus only",violent:90,prop_crime:480,crime5yr:-8,inc10yr:0,pop10yr:0,bach:0,unemp:0,pov:0,flood:5,flood50:2,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",standout:null,glance:null,notes:"Solid suburban value. Improving schools. Bus only — nearest rail at Malden Center (Orange Line).",med_home_val:690000,commute:28,owner_occ:68,vacancy:3.0,med_age:41,low_income_pct:10,ell_pct:6,enrollment_trend:null,sex_off:null}',
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
print(f"CSV: added {len(added_csv)} towns. Total: {len(rows)}")

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
    print(f"HTML: added {len(added_html)} towns")
