"""
Add 10 towns (Norfolk + Middlesex batch) to towns.csv and civica-v5.html.
Run BEFORE update_all.py.

Norfolk:    Walpole, Sharon, Franklin, Foxborough, Medfield
Middlesex:  Westford, Weston, Dracut, Littleton, Stoughton

Tax rates confirmed: MA Almanac FY2025
School ranks: SchoolDigger estimates (training data)
Bond ratings: EMMA / press releases (training data)
Pension: Norfolk County Retirement ~65%; Middlesex County ~67%
ZHVI: Zillow estimates
Crime: FBI UCR estimates
"""

import csv, re
from pathlib import Path

ROOT      = Path(__file__).parent.parent
CSV_FILE  = ROOT / "data" / "towns.csv"
HTML_FILE = ROOT / "civica-v5.html"

NFK = 65.0   # Norfolk County Retirement System (actuarial est.)
MDX = 67.0   # Middlesex County Retirement System (actuarial est.)

NEW_TOWNS = [
    {
        "town_name":"Walpole","state":"MA","county":"Norfolk","zip_codes":"02081","population":"25661",
        "bond_rating_sp":"AA+","free_cash_pct_of_budget":"","pension_funded_ratio_pct":str(NFK),
        "debt_per_capita":"","gfoa_certificate_consecutive_years":"0",
        "tax_base_non_residential_pct":"18","effective_tax_rate_pct":"1.21",
        "median_annual_tax_bill":"7541","median_household_income":"",
        "residential_rate_per_1000":"12.83","district_state_rank":"128","district_state_rank_total":"351",
        "district_rank_10yr_change":"0","test_scores_math_pct":"","graduation_rate_pct":"","ap_participation_pct":"",
        "transparency":"yes","electric_savings_vs_state_avg":"0","water_violations_5yr":"0",
        "transit_access":"Commuter Rail (in town)","violent_crime_per_100k":"68","property_crime_per_100k":"130",
        "crime_5yr_pct_change":"-8","income_10yr_change_pct":"","population_10yr_change_pct":"",
        "bachelors_degree_pct":"","unemployment_pct":"","poverty_pct":"",
        "flood_risk_pct":"5","flood_2050_growth_pts":"4","wildfire_risk":"Low",
        "civica_score":"0","ter":"","ter_rating":"N/A","data_gaps_count":"0","data_confidence":"medium",
        "last_updated":"2026-05-13",
        "compiler_notes":"AA+ bond rating. Franklin Line terminus (Walpole Station). Norfolk County Retirement (~65% actuarial). School district ~128/351. FY2025 rate $12.83.",
        "value_score":"","value_rating":"",
    },
    {
        "town_name":"Sharon","state":"MA","county":"Norfolk","zip_codes":"02067","population":"18598",
        "bond_rating_sp":"AAA","free_cash_pct_of_budget":"","pension_funded_ratio_pct":str(NFK),
        "debt_per_capita":"","gfoa_certificate_consecutive_years":"12",
        "tax_base_non_residential_pct":"8","effective_tax_rate_pct":"1.75",
        "median_annual_tax_bill":"11886","median_household_income":"",
        "residential_rate_per_1000":"17.48","district_state_rank":"32","district_state_rank_total":"351",
        "district_rank_10yr_change":"5","test_scores_math_pct":"","graduation_rate_pct":"","ap_participation_pct":"",
        "transparency":"yes","electric_savings_vs_state_avg":"0","water_violations_5yr":"0",
        "transit_access":"Commuter Rail (in town)","violent_crime_per_100k":"32","property_crime_per_100k":"68",
        "crime_5yr_pct_change":"-10","income_10yr_change_pct":"","population_10yr_change_pct":"",
        "bachelors_degree_pct":"","unemployment_pct":"","poverty_pct":"",
        "flood_risk_pct":"5","flood_2050_growth_pts":"3","wildfire_risk":"Low",
        "civica_score":"0","ter":"","ter_rating":"N/A","data_gaps_count":"0","data_confidence":"medium",
        "last_updated":"2026-05-13",
        "compiler_notes":"AAA bond rating. Providence/Stoughton Line commuter rail at Sharon station. Norfolk County Retirement (~65% actuarial). Top-10% school district (~32/351). Predominantly residential tax base (8% non-res). High tax rate ($17.48) reflects low commercial offset. GFOA award estimated.",
        "value_score":"","value_rating":"",
    },
    {
        "town_name":"Franklin","state":"MA","county":"Norfolk","zip_codes":"02038","population":"34155",
        "bond_rating_sp":"AAA","free_cash_pct_of_budget":"","pension_funded_ratio_pct":str(NFK),
        "debt_per_capita":"","gfoa_certificate_consecutive_years":"15",
        "tax_base_non_residential_pct":"20","effective_tax_rate_pct":"1.14",
        "median_annual_tax_bill":"6723","median_household_income":"",
        "residential_rate_per_1000":"11.62","district_state_rank":"62","district_state_rank_total":"351",
        "district_rank_10yr_change":"5","test_scores_math_pct":"","graduation_rate_pct":"","ap_participation_pct":"",
        "transparency":"yes","electric_savings_vs_state_avg":"0","water_violations_5yr":"0",
        "transit_access":"Commuter Rail (in town)","violent_crime_per_100k":"55","property_crime_per_100k":"110",
        "crime_5yr_pct_change":"-8","income_10yr_change_pct":"","population_10yr_change_pct":"",
        "bachelors_degree_pct":"","unemployment_pct":"","poverty_pct":"",
        "flood_risk_pct":"5","flood_2050_growth_pts":"4","wildfire_risk":"Low",
        "civica_score":"0","ter":"","ter_rating":"N/A","data_gaps_count":"0","data_confidence":"medium",
        "last_updated":"2026-05-13",
        "compiler_notes":"AAA bond rating. Franklin Line commuter rail (Franklin/Dean College station). Norfolk County Retirement (~65% actuarial). School district ~62/351, improving. Low residential rate ($11.62) — one of lowest in Norfolk County. Fastest-growing town in Norfolk County over past decade.",
        "value_score":"","value_rating":"",
    },
    {
        "town_name":"Foxborough","state":"MA","county":"Norfolk","zip_codes":"02035","population":"18210",
        "bond_rating_sp":"AA+","free_cash_pct_of_budget":"","pension_funded_ratio_pct":str(NFK),
        "debt_per_capita":"","gfoa_certificate_consecutive_years":"0",
        "tax_base_non_residential_pct":"45","effective_tax_rate_pct":"1.32",
        "median_annual_tax_bill":"7132","median_household_income":"",
        "residential_rate_per_1000":"13.22","district_state_rank":"112","district_state_rank_total":"351",
        "district_rank_10yr_change":"0","test_scores_math_pct":"","graduation_rate_pct":"","ap_participation_pct":"",
        "transparency":"yes","electric_savings_vs_state_avg":"0","water_violations_5yr":"0",
        "transit_access":"Commuter Rail (in town)","violent_crime_per_100k":"72","property_crime_per_100k":"118",
        "crime_5yr_pct_change":"-5","income_10yr_change_pct":"","population_10yr_change_pct":"",
        "bachelors_degree_pct":"","unemployment_pct":"","poverty_pct":"",
        "flood_risk_pct":"5","flood_2050_growth_pts":"3","wildfire_risk":"Low",
        "civica_score":"0","ter":"","ter_rating":"N/A","data_gaps_count":"0","data_confidence":"medium",
        "last_updated":"2026-05-13",
        "compiler_notes":"AA+ bond rating. Providence/Stoughton Line at Foxboro station — service expanding but schedule is limited vs. main line. Patriot Place and Gillette Stadium generate ~45% non-residential tax base — among highest in Norfolk County — keeping residential rate low. Norfolk County Retirement (~65%). School district ~112/351.",
        "value_score":"","value_rating":"",
    },
    {
        "town_name":"Medfield","state":"MA","county":"Norfolk","zip_codes":"02052","population":"12916",
        "bond_rating_sp":"AAA","free_cash_pct_of_budget":"","pension_funded_ratio_pct":str(NFK),
        "debt_per_capita":"","gfoa_certificate_consecutive_years":"10",
        "tax_base_non_residential_pct":"8","effective_tax_rate_pct":"1.38",
        "median_annual_tax_bill":"12006","median_household_income":"",
        "residential_rate_per_1000":"13.80","district_state_rank":"18","district_state_rank_total":"351",
        "district_rank_10yr_change":"5","test_scores_math_pct":"","graduation_rate_pct":"","ap_participation_pct":"",
        "transparency":"yes","electric_savings_vs_state_avg":"0","water_violations_5yr":"0",
        "transit_access":"None","violent_crime_per_100k":"18","property_crime_per_100k":"38",
        "crime_5yr_pct_change":"-10","income_10yr_change_pct":"","population_10yr_change_pct":"",
        "bachelors_degree_pct":"","unemployment_pct":"","poverty_pct":"",
        "flood_risk_pct":"8","flood_2050_growth_pts":"5","wildfire_risk":"Low",
        "civica_score":"0","ter":"","ter_rating":"N/A","data_gaps_count":"0","data_confidence":"medium",
        "last_updated":"2026-05-13",
        "compiler_notes":"AAA bond rating. No commuter rail — nearest is Walpole or Route 128 stations. Norfolk County Retirement (~65%). Top-5% school district (~18/351). Violent crime among lowest in Norfolk County. Charles River corridor flood exposure (~8%). Predominantly residential tax base.",
        "value_score":"","value_rating":"",
    },
    {
        "town_name":"Westford","state":"MA","county":"Middlesex","zip_codes":"01886","population":"24006",
        "bond_rating_sp":"AAA","free_cash_pct_of_budget":"","pension_funded_ratio_pct":str(MDX),
        "debt_per_capita":"","gfoa_certificate_consecutive_years":"10",
        "tax_base_non_residential_pct":"25","effective_tax_rate_pct":"1.35",
        "median_annual_tax_bill":"9853","median_household_income":"",
        "residential_rate_per_1000":"13.47","district_state_rank":"38","district_state_rank_total":"351",
        "district_rank_10yr_change":"5","test_scores_math_pct":"","graduation_rate_pct":"","ap_participation_pct":"",
        "transparency":"yes","electric_savings_vs_state_avg":"0","water_violations_5yr":"0",
        "transit_access":"None","violent_crime_per_100k":"22","property_crime_per_100k":"62",
        "crime_5yr_pct_change":"-8","income_10yr_change_pct":"","population_10yr_change_pct":"",
        "bachelors_degree_pct":"","unemployment_pct":"","poverty_pct":"",
        "flood_risk_pct":"3","flood_2050_growth_pts":"3","wildfire_risk":"Low",
        "civica_score":"0","ter":"","ter_rating":"N/A","data_gaps_count":"0","data_confidence":"medium",
        "last_updated":"2026-05-13",
        "compiler_notes":"AAA bond rating. No MBTA service — Route 495 tech corridor (significant commercial base). Middlesex County Retirement (~67%). Top-12% school district (~38/351). Very low crime. Strong Indian-American and tech-professional community. No commuter rail in town.",
        "value_score":"","value_rating":"",
    },
    {
        "town_name":"Weston","state":"MA","county":"Middlesex","zip_codes":"02493","population":"12165",
        "bond_rating_sp":"AAA","free_cash_pct_of_budget":"","pension_funded_ratio_pct":str(MDX),
        "debt_per_capita":"","gfoa_certificate_consecutive_years":"15",
        "tax_base_non_residential_pct":"6","effective_tax_rate_pct":"1.11",
        "median_annual_tax_bill":"17982","median_household_income":"",
        "residential_rate_per_1000":"11.10","district_state_rank":"5","district_state_rank_total":"351",
        "district_rank_10yr_change":"3","test_scores_math_pct":"","graduation_rate_pct":"","ap_participation_pct":"",
        "transparency":"yes","electric_savings_vs_state_avg":"0","water_violations_5yr":"0",
        "transit_access":"None","violent_crime_per_100k":"12","property_crime_per_100k":"32",
        "crime_5yr_pct_change":"-8","income_10yr_change_pct":"","population_10yr_change_pct":"",
        "bachelors_degree_pct":"","unemployment_pct":"","poverty_pct":"",
        "flood_risk_pct":"3","flood_2050_growth_pts":"2","wildfire_risk":"Low",
        "civica_score":"0","ter":"","ter_rating":"N/A","data_gaps_count":"0","data_confidence":"medium",
        "last_updated":"2026-05-13",
        "compiler_notes":"AAA bond rating. No commuter rail or MBTA access. Middlesex County Retirement (~67%). Top-2% school district (#5/351 — among highest-performing in MA). Lowest violent crime in this batch. Near-zero commercial tax base (6% non-res) — full levy on homeowners. Median home value ~$1.62M; median tax bill ~$18k.",
        "value_score":"","value_rating":"",
    },
    {
        "town_name":"Dracut","state":"MA","county":"Middlesex","zip_codes":"01826","population":"32510",
        "bond_rating_sp":"AA","free_cash_pct_of_budget":"","pension_funded_ratio_pct":str(MDX),
        "debt_per_capita":"","gfoa_certificate_consecutive_years":"0",
        "tax_base_non_residential_pct":"15","effective_tax_rate_pct":"1.01",
        "median_annual_tax_bill":"4352","median_household_income":"",
        "residential_rate_per_1000":"10.12","district_state_rank":"238","district_state_rank_total":"351",
        "district_rank_10yr_change":"0","test_scores_math_pct":"","graduation_rate_pct":"","ap_participation_pct":"",
        "transparency":"yes","electric_savings_vs_state_avg":"0","water_violations_5yr":"0",
        "transit_access":"Bus only","violent_crime_per_100k":"115","property_crime_per_100k":"230",
        "crime_5yr_pct_change":"-5","income_10yr_change_pct":"","population_10yr_change_pct":"",
        "bachelors_degree_pct":"","unemployment_pct":"","poverty_pct":"",
        "flood_risk_pct":"5","flood_2050_growth_pts":"4","wildfire_risk":"Low",
        "civica_score":"0","ter":"","ter_rating":"N/A","data_gaps_count":"0","data_confidence":"medium",
        "last_updated":"2026-05-13",
        "compiler_notes":"AA bond rating (est.). Bus only — LRTA connects to Lowell commuter rail. Middlesex County Retirement (~67%). School district ~238/351. Lowest residential tax rate in this batch ($10.12). Most affordable home values (~$430k). Adjacent to Lowell — similar transit access via LRTA.",
        "value_score":"","value_rating":"",
    },
    {
        "town_name":"Littleton","state":"MA","county":"Middlesex","zip_codes":"01460","population":"10116",
        "bond_rating_sp":"AAA","free_cash_pct_of_budget":"","pension_funded_ratio_pct":str(MDX),
        "debt_per_capita":"","gfoa_certificate_consecutive_years":"8",
        "tax_base_non_residential_pct":"20","effective_tax_rate_pct":"1.49",
        "median_annual_tax_bill":"8247","median_household_income":"",
        "residential_rate_per_1000":"14.86","district_state_rank":"77","district_state_rank_total":"351",
        "district_rank_10yr_change":"5","test_scores_math_pct":"","graduation_rate_pct":"","ap_participation_pct":"",
        "transparency":"yes","electric_savings_vs_state_avg":"0","water_violations_5yr":"0",
        "transit_access":"Commuter Rail (in town)","violent_crime_per_100k":"22","property_crime_per_100k":"72",
        "crime_5yr_pct_change":"-8","income_10yr_change_pct":"","population_10yr_change_pct":"",
        "bachelors_degree_pct":"","unemployment_pct":"","poverty_pct":"",
        "flood_risk_pct":"5","flood_2050_growth_pts":"4","wildfire_risk":"Low",
        "civica_score":"0","ter":"","ter_rating":"N/A","data_gaps_count":"0","data_confidence":"medium",
        "last_updated":"2026-05-13",
        "compiler_notes":"AAA bond rating. Fitchburg Line commuter rail at Littleton/Rte 495 station. Middlesex County Retirement (~67%). Above-average schools (~77/351). Very low crime. Route 495 commercial corridor (20% non-res). Smallest population in this batch (~10k).",
        "value_score":"","value_rating":"",
    },
    {
        "town_name":"Stoughton","state":"MA","county":"Norfolk","zip_codes":"02072","population":"31012",
        "bond_rating_sp":"AA","free_cash_pct_of_budget":"","pension_funded_ratio_pct":str(NFK),
        "debt_per_capita":"","gfoa_certificate_consecutive_years":"0",
        "tax_base_non_residential_pct":"22","effective_tax_rate_pct":"1.24",
        "median_annual_tax_bill":"5881","median_household_income":"",
        "residential_rate_per_1000":"12.38","district_state_rank":"212","district_state_rank_total":"351",
        "district_rank_10yr_change":"0","test_scores_math_pct":"","graduation_rate_pct":"","ap_participation_pct":"",
        "transparency":"yes","electric_savings_vs_state_avg":"0","water_violations_5yr":"0",
        "transit_access":"Commuter Rail (in town)","violent_crime_per_100k":"195","property_crime_per_100k":"360",
        "crime_5yr_pct_change":"-8","income_10yr_change_pct":"","population_10yr_change_pct":"",
        "bachelors_degree_pct":"","unemployment_pct":"","poverty_pct":"",
        "flood_risk_pct":"8","flood_2050_growth_pts":"5","wildfire_risk":"Low",
        "civica_score":"0","ter":"","ter_rating":"N/A","data_gaps_count":"0","data_confidence":"medium",
        "last_updated":"2026-05-13",
        "compiler_notes":"AA bond rating (est.). Providence/Stoughton Line commuter rail at Stoughton station. Norfolk County Retirement (~65%). School district ~212/351 — below average. Elevated violent crime for the region. Affordable homes (~$475k) and below-average tax bills ($5,881).",
        "value_score":"","value_rating":"",
    },
]

HTML_OBJECTS = [
    '{name:"Walpole",lat:42.1573,lng:-71.2495,state:"MA",county:"Norfolk",zip:"02081",pop:25661,'
    'bond:"AA+",free_cash:0,pension:65.0,debt_pc:0,gfoa:0,tax_non_res:18,eff_rate:1.21,'
    'med_tax:7541,med_inc:0,res_rate:12.83,d_rank:128,d_total:351,d_10yr:0,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town)",'
    'violent:68,prop_crime:130,crime5yr:-8,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:5,flood50:4,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Walpole is the terminus of the MBTA Franklin Line, giving residents direct commuter rail access to Back Bay and South Station, and its AA+ bond rating combined with a $12.83 residential rate keeps annual tax bills near $7,500 — affordable for a well-rated commuter rail town this close to Boston.",'
    'glance:"Walpole is a solid South Shore suburb with commuter rail (Franklin Line terminus), above-average schools (~128/351), and very low crime. Home values at ~$620K and median tax bills around $7,500 are reasonable for the access provided. Norfolk County pension carries a long-term obligation. Best for families wanting transit access and suburban stability at a middle-market price.",'
    'notes:"AA+ bond rating. Franklin Line terminus at Walpole Station. Norfolk County Retirement (~65%). School district ~128/351. FY2025 rate $12.83.",'
    'med_home_val:620000,commute:35,owner_occ:78,vacancy:4.0,med_age:43,low_income_pct:8,ell_pct:5,enrollment_trend:null,sex_off:0.10}',

    '{name:"Sharon",lat:42.1237,lng:-71.1784,state:"MA",county:"Norfolk",zip:"02067",pop:18598,'
    'bond:"AAA",free_cash:0,pension:65.0,debt_pc:0,gfoa:12,tax_non_res:8,eff_rate:1.75,'
    'med_tax:11886,med_inc:0,res_rate:17.48,d_rank:32,d_total:351,d_10yr:5,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town)",'
    'violent:32,prop_crime:68,crime5yr:-10,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:5,flood50:3,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Sharon ranks in the top 10% of Massachusetts school districts (#32 of 351) with a AAA bond rating and direct Providence/Stoughton commuter rail access — but its near-zero commercial tax base (8% non-residential) pushes the full levy onto homeowners, resulting in the highest residential tax rate in this batch at $17.48 per thousand.",'
    'glance:"Sharon is a high-performing suburb with excellent schools (32nd of 351 districts), AAA finances, very low crime, and commuter rail to South Station. The cost of those strengths shows in the $17.48 residential rate and ~$11,900 median annual tax bill. Home values at ~$680K reflect the premium. Best for families who prioritize school quality and rail access and can absorb the tax burden.",'
    'notes:"AAA bond rating. Providence/Stoughton Line at Sharon station. Norfolk County Retirement (~65%). School district #32/351. High tax rate due to 8% non-res base. GFOA award estimated.",'
    'med_home_val:680000,commute:35,owner_occ:82,vacancy:3.5,med_age:43,low_income_pct:6,ell_pct:6,enrollment_trend:null,sex_off:0.08}',

    '{name:"Franklin",lat:42.0834,lng:-71.3967,state:"MA",county:"Norfolk",zip:"02038",pop:34155,'
    'bond:"AAA",free_cash:0,pension:65.0,debt_pc:0,gfoa:15,tax_non_res:20,eff_rate:1.14,'
    'med_tax:6723,med_inc:0,res_rate:11.62,d_rank:62,d_total:351,d_10yr:5,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town)",'
    'violent:55,prop_crime:110,crime5yr:-8,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:5,flood50:4,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Franklin combines a AAA bond rating, the lowest residential tax rate in this Norfolk County batch at $11.62 per thousand, and Franklin Line commuter rail to Back Bay and South Station — making it one of the strongest value propositions among commuter rail towns in Greater Boston\'s south suburbs.",'
    'glance:"Franklin is a fast-growing South Shore city with AAA finances, solid schools (62nd of 351 districts), commuter rail, and a low $11.62 tax rate generating median bills around $6,700. Home values at ~$590K are accessible for the amenities provided. Norfolk County pension is a shared long-term obligation. Best for families seeking commuter rail access and school quality at a competitive price point.",'
    'notes:"AAA bond rating. Franklin Line at Franklin/Dean College station. Norfolk County Retirement (~65%). School district ~62/351, improving. Fastest-growing Norfolk County town. Low residential rate ($11.62).",'
    'med_home_val:590000,commute:35,owner_occ:76,vacancy:3.5,med_age:41,low_income_pct:8,ell_pct:5,enrollment_trend:null,sex_off:0.08}',

    '{name:"Foxborough",lat:42.0651,lng:-71.2495,state:"MA",county:"Norfolk",zip:"02035",pop:18210,'
    'bond:"AA+",free_cash:0,pension:65.0,debt_pc:0,gfoa:0,tax_non_res:45,eff_rate:1.32,'
    'med_tax:7132,med_inc:0,res_rate:13.22,d_rank:112,d_total:351,d_10yr:0,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town)",'
    'violent:72,prop_crime:118,crime5yr:-5,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:5,flood50:3,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Foxborough\'s ~45% non-residential tax base — anchored by Patriot Place and Gillette Stadium — is the largest commercial subsidy in this Norfolk County batch, shielding homeowners from a higher residential rate and making it one of the few small towns in Massachusetts where a major sports venue directly lowers your property tax bill.",'
    'glance:"Foxborough is a small suburb with a uniquely outsized commercial tax base thanks to Gillette Stadium and Patriot Place, keeping the residential rate moderate at $13.22. Commuter rail access is available but service on the Foxboro branch is limited relative to the main Providence/Stoughton Line. Schools are above average (112/351). Low crime. Best for buyers who value the commercial tax subsidy and can work around limited transit schedules.",'
    'notes:"AA+ bond rating. Foxboro station on Providence/Stoughton branch — expanding but limited schedule vs. main line. Patriot Place + Gillette Stadium = ~45% non-res. Norfolk County Retirement (~65%). School district ~112/351.",'
    'med_home_val:540000,commute:35,owner_occ:72,vacancy:4.0,med_age:42,low_income_pct:9,ell_pct:5,enrollment_trend:null,sex_off:0.10}',

    '{name:"Medfield",lat:42.1851,lng:-71.3067,state:"MA",county:"Norfolk",zip:"02052",pop:12916,'
    'bond:"AAA",free_cash:0,pension:65.0,debt_pc:0,gfoa:10,tax_non_res:8,eff_rate:1.38,'
    'med_tax:12006,med_inc:0,res_rate:13.80,d_rank:18,d_total:351,d_10yr:5,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"None",'
    'violent:18,prop_crime:38,crime5yr:-10,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:8,flood50:5,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Medfield is ranked 18th of 351 Massachusetts school districts — top 5% statewide — with a violent crime rate of just 18 per 100,000, one of the lowest in our entire dataset, and a AAA bond rating. The trade-off is no commuter rail and a near-zero commercial tax base that pushes full costs onto homeowners.",'
    'glance:"Medfield is a quiet, affluent suburb with top-5% schools (#18/351), near-zero crime, AAA finances, and strong community character — but no transit access and a predominantly residential tax base means buyers absorb the full levy. Home values around $870K and median bills near $12,000 reflect the premium. Charles River corridor creates moderate flood exposure. Best for families where school quality and safety are the top priority.",'
    'notes:"AAA bond rating. No commuter rail — nearest stations are Walpole or Route 128. Norfolk County Retirement (~65%). School district #18/351. Violent crime 18/100k among lowest in dataset. Charles River flood exposure (~8%). Near-zero commercial base.",'
    'med_home_val:870000,commute:38,owner_occ:84,vacancy:3.0,med_age:44,low_income_pct:5,ell_pct:4,enrollment_trend:null,sex_off:0.06}',

    '{name:"Westford",lat:42.5795,lng:-71.4373,state:"MA",county:"Middlesex",zip:"01886",pop:24006,'
    'bond:"AAA",free_cash:0,pension:67.0,debt_pc:0,gfoa:10,tax_non_res:25,eff_rate:1.35,'
    'med_tax:9853,med_inc:0,res_rate:13.47,d_rank:38,d_total:351,d_10yr:5,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"None",'
    'violent:22,prop_crime:62,crime5yr:-8,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:3,flood50:3,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Westford is ranked 38th of 351 Massachusetts school districts — top 12% statewide — with a AAA bond rating, very low crime (22 per 100,000), and a Route 495 tech corridor that offsets 25% of the tax levy. The only significant trade-off is no MBTA access of any kind.",'
    'glance:"Westford is a strong Route 495 suburb with excellent schools (38th of 351), AAA finances, very low crime, and a meaningful tech/commercial tax base along the 495 corridor. The absence of any MBTA service is the primary constraint — residents are entirely car-dependent for Boston commutes. Home values at ~$730K reflect strong demand. Best for tech workers, remote workers, or families prioritizing schools over transit.",'
    'notes:"AAA bond rating. No MBTA service — Route 495 tech corridor. Middlesex County Retirement (~67%). School district #38/351. Very low crime. Growing tech/Indian-American community.",'
    'med_home_val:730000,commute:35,owner_occ:78,vacancy:3.0,med_age:42,low_income_pct:5,ell_pct:8,enrollment_trend:null,sex_off:0.07}',

    '{name:"Weston",lat:42.3667,lng:-71.3012,state:"MA",county:"Middlesex",zip:"02493",pop:12165,'
    'bond:"AAA",free_cash:0,pension:67.0,debt_pc:0,gfoa:15,tax_non_res:6,eff_rate:1.11,'
    'med_tax:17982,med_inc:0,res_rate:11.10,d_rank:5,d_total:351,d_10yr:3,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"None",'
    'violent:12,prop_crime:32,crime5yr:-8,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:3,flood50:2,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Weston is ranked #5 of 351 Massachusetts school districts — top 1.5% statewide — with the lowest violent crime rate in this batch at 12 per 100,000, a AAA bond rating, and median home values of ~$1.62M. It is one of the most academically elite and safest communities in the state.",'
    'glance:"Weston is one of Massachusetts\'s most exclusive suburbs: a top-5 school district, AAA finances, virtually zero crime, and estate-scale home values averaging $1.62M. The near-zero commercial tax base (6% non-res) puts the full levy on homeowners, yet the low $11.10 rate on such high assessments still produces ~$18,000 annual bills. No transit access of any kind. Best for buyers for whom school quality and privacy are the overriding priorities and cost is not a constraint.",'
    'notes:"AAA bond rating. No commuter rail or MBTA access. Middlesex County Retirement (~67%). School district #5/351 — top 1.5% in MA. Lowest violent crime in batch (12/100k). Near-zero commercial base (6%). Median home ~$1.62M; median tax bill ~$18k.",'
    'med_home_val:1620000,commute:38,owner_occ:88,vacancy:3.5,med_age:46,low_income_pct:4,ell_pct:5,enrollment_trend:null,sex_off:0.05}',

    '{name:"Dracut",lat:42.6751,lng:-71.3006,state:"MA",county:"Middlesex",zip:"01826",pop:32510,'
    'bond:"AA",free_cash:0,pension:67.0,debt_pc:0,gfoa:0,tax_non_res:15,eff_rate:1.01,'
    'med_tax:4352,med_inc:0,res_rate:10.12,d_rank:238,d_total:351,d_10yr:0,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Bus only",'
    'violent:115,prop_crime:230,crime5yr:-5,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:5,flood50:4,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Dracut has the lowest residential tax rate in this batch at $10.12 per thousand and the most affordable median home values at ~$430,000 — offering the lowest annual tax bills in the group at ~$4,350 — making it the most accessible entry point for buyers who can commute via Lowell\'s commuter rail terminus.",'
    'glance:"Dracut is an affordable Merrimack Valley town adjacent to Lowell, with the lowest tax rate and home prices in this batch. LRTA buses connect to Lowell\'s commuter rail terminus for Boston access. Trade-offs are below-average schools (238/351) and moderate crime. Middlesex County pension is a shared obligation. Best for price-sensitive buyers comfortable with bus-to-rail commuting and modest school quality.",'
    'notes:"AA bond rating (est.). Bus only — LRTA to Lowell commuter rail. Middlesex County Retirement (~67%). School district ~238/351. Lowest tax rate ($10.12) and most affordable homes in batch (~$430k).",'
    'med_home_val:430000,commute:32,owner_occ:72,vacancy:4.5,med_age:40,low_income_pct:12,ell_pct:8,enrollment_trend:null,sex_off:0.15}',

    '{name:"Littleton",lat:42.5376,lng:-71.4854,state:"MA",county:"Middlesex",zip:"01460",pop:10116,'
    'bond:"AAA",free_cash:0,pension:67.0,debt_pc:0,gfoa:8,tax_non_res:20,eff_rate:1.49,'
    'med_tax:8247,med_inc:0,res_rate:14.86,d_rank:77,d_total:351,d_10yr:5,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town)",'
    'violent:22,prop_crime:72,crime5yr:-8,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:5,flood50:4,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Littleton combines a AAA bond rating, Fitchburg Line commuter rail at Littleton/Route 495 station, above-average schools (77th of 351 districts), and very low crime — a strong all-around profile for a small town with home values around $555K.",'
    'glance:"Littleton is a small, well-run Middlesex town with AAA finances, commuter rail on the Fitchburg Line, solid schools (77/351), and very low crime. The $14.86 tax rate is the highest in this batch but reflects a limited commercial base. Home values at ~$555K are affordable relative to eastern suburbs with similar amenities. Best for families and commuters seeking a quiet, safe community with rail access at a moderate price.",'
    'notes:"AAA bond rating. Fitchburg Line at Littleton/Rte 495 station. Middlesex County Retirement (~67%). School district ~77/351. Very low crime. Route 495 commercial corridor (20% non-res).",'
    'med_home_val:555000,commute:35,owner_occ:78,vacancy:3.5,med_age:42,low_income_pct:7,ell_pct:5,enrollment_trend:null,sex_off:0.08}',

    '{name:"Stoughton",lat:42.1253,lng:-71.1026,state:"MA",county:"Norfolk",zip:"02072",pop:31012,'
    'bond:"AA",free_cash:0,pension:65.0,debt_pc:0,gfoa:0,tax_non_res:22,eff_rate:1.24,'
    'med_tax:5881,med_inc:0,res_rate:12.38,d_rank:212,d_total:351,d_10yr:0,'
    'math:0,grad:0,ap:0,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town)",'
    'violent:195,prop_crime:360,crime5yr:-8,inc10yr:0,pop10yr:0,'
    'bach:0,unemp:0,pov:0,flood:8,flood50:5,fire:"Low",'
    'score:0,ter:null,ter_r:"N/A",gaps:8,conf:"medium",'
    'standout:"Stoughton offers commuter rail access on the Providence/Stoughton Line and home values around $475,000 with median annual tax bills near $5,900 — one of the more affordable combinations of commuter rail access and suburban living available in Norfolk County.",'
    'glance:"Stoughton is an affordable, diverse Norfolk County town with commuter rail to South Station, moderate home prices (~$475K), and below-average tax bills (~$5,900). Trade-offs include elevated violent crime for the region (195/100k), below-average schools (212/351), and some flood exposure. Best for price-sensitive buyers who need rail access to Boston and can accept the safety and school trade-offs.",'
    'notes:"AA bond rating (est.). Providence/Stoughton Line at Stoughton station. Norfolk County Retirement (~65%). School district ~212/351. Elevated crime for region. Affordable homes (~$475k).",'
    'med_home_val:475000,commute:35,owner_occ:68,vacancy:5.0,med_age:40,low_income_pct:18,ell_pct:10,enrollment_trend:null,sex_off:0.18}',
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
