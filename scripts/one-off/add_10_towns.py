"""
One-time script: adds 10 new towns to towns.csv and civica-v5.html.
Run ONCE, then run update_all.py to score them.
"""
import csv, re
from pathlib import Path

ROOT     = Path(r"C:\Users\Brian\Desktop\Civica")
CSV_FILE = ROOT / "data" / "towns.csv"
HTML_FILE= ROOT / "civica-v5.html"

# ─── CSV rows ────────────────────────────────────────────────────────────────
# Fields auto-filled by update_all.py (leave blank here):
#   free_cash_pct_of_budget, debt_per_capita  → Excel bulk
#   test_scores_math_pct, graduation_rate_pct, ap_participation_pct → school bulk
#   median_household_income, income_10yr_change_pct, population_10yr_change_pct,
#   bachelors_degree_pct, unemployment_pct, poverty_pct → Census bulk

NEW_CSV = [
    dict(
        town_name="Shrewsbury", state="MA", county="Worcester", zip_codes="01545",
        population="37667", bond_rating_sp="AA", pension_funded_ratio_pct="73.0",
        tax_base_non_residential_pct="15.0", effective_tax_rate_pct="1.18",
        median_annual_tax_bill="7900", residential_rate_per_1000="13.15",
        district_state_rank="115", district_state_rank_total="351",
        transit_access="bus_only", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        violent_crime_per_100k="80.0", property_crime_per_100k="850.0",
        flood_risk_pct="2.0", flood_2050_growth_pts="0.8", wildfire_risk="Low",
        transparency="yes",
        compiler_notes="Bond AA estimated — verify EMMA. Pension: Shrewsbury Retirement Board — verify PERAC. Crime estimated from MA EOPSS Worcester County data.",
    ),
    dict(
        town_name="Westborough", state="MA", county="Worcester", zip_codes="01581",
        population="18272", bond_rating_sp="AA+", pension_funded_ratio_pct="71.0",
        tax_base_non_residential_pct="30.0", effective_tax_rate_pct="1.22",
        median_annual_tax_bill="9200", residential_rate_per_1000="13.87",
        district_state_rank="80", district_state_rank_total="351",
        transit_access="commuter_rail_in_town", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        violent_crime_per_100k="50.0", property_crime_per_100k="600.0",
        flood_risk_pct="1.5", flood_2050_growth_pts="0.5", wildfire_risk="Low",
        transparency="yes",
        compiler_notes="Bond AA+ estimated — verify EMMA. Pension: Westborough Retirement Board — verify PERAC. Commuter Rail: Framingham/Worcester Line (Westborough station). Large I-495 commercial corridor lowers residential burden.",
    ),
    dict(
        town_name="Northborough", state="MA", county="Worcester", zip_codes="01532",
        population="15707", bond_rating_sp="AA", pension_funded_ratio_pct="70.0",
        tax_base_non_residential_pct="20.0", effective_tax_rate_pct="1.20",
        median_annual_tax_bill="8100", residential_rate_per_1000="13.30",
        district_state_rank="75", district_state_rank_total="351",
        transit_access="none", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        violent_crime_per_100k="30.0", property_crime_per_100k="450.0",
        flood_risk_pct="1.5", flood_2050_growth_pts="0.5", wildfire_risk="Low",
        transparency="yes",
        compiler_notes="Bond AA estimated — verify EMMA. Pension: Worcester Regional Retirement — verify PERAC. School district is Northborough-Southborough Regional (Algonquin Regional HS). Rank estimated — verify DESE.",
    ),
    dict(
        town_name="Grafton", state="MA", county="Worcester", zip_codes="01519",
        population="20167", bond_rating_sp="AA-", pension_funded_ratio_pct="68.0",
        tax_base_non_residential_pct="12.0", effective_tax_rate_pct="1.28",
        median_annual_tax_bill="7100", residential_rate_per_1000="14.20",
        district_state_rank="160", district_state_rank_total="351",
        transit_access="commuter_rail_in_town", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        violent_crime_per_100k="60.0", property_crime_per_100k="550.0",
        flood_risk_pct="2.5", flood_2050_growth_pts="1.0", wildfire_risk="Low",
        transparency="yes",
        compiler_notes="Bond AA- estimated — verify EMMA. Pension: Worcester Regional Retirement — verify PERAC. Commuter Rail: Framingham/Worcester Line (Grafton station). Blackstone River corridor adds modest flood exposure.",
    ),
    dict(
        town_name="Milford", state="MA", county="Worcester", zip_codes="01757",
        population="29079", bond_rating_sp="A+", pension_funded_ratio_pct="65.0",
        tax_base_non_residential_pct="17.0", effective_tax_rate_pct="1.40",
        median_annual_tax_bill="6200", residential_rate_per_1000="15.18",
        district_state_rank="215", district_state_rank_total="351",
        transit_access="none", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        violent_crime_per_100k="150.0", property_crime_per_100k="1200.0",
        flood_risk_pct="3.0", flood_2050_growth_pts="1.2", wildfire_risk="Low",
        transparency="yes",
        compiler_notes="Bond A+ estimated — verify EMMA. Pension: Milford Retirement Board — verify PERAC. No commuter rail; bus service only. Crime rates higher than surrounding suburbs — verify FBI CDE / MA EOPSS.",
    ),
    dict(
        town_name="Mansfield", state="MA", county="Bristol", zip_codes="02048",
        population="24112", bond_rating_sp="AA", pension_funded_ratio_pct="65.0",
        tax_base_non_residential_pct="25.0", effective_tax_rate_pct="1.12",
        median_annual_tax_bill="7400", residential_rate_per_1000="12.44",
        district_state_rank="145", district_state_rank_total="351",
        transit_access="commuter_rail_in_town", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        violent_crime_per_100k="90.0", property_crime_per_100k="900.0",
        flood_risk_pct="2.0", flood_2050_growth_pts="0.8", wildfire_risk="Low",
        transparency="yes",
        compiler_notes="Bond AA estimated — verify EMMA. Pension: Bristol County Retirement (~65%) — verify PERAC. Commuter Rail: Providence/Stoughton Line (Mansfield station, in town). Mansfield Crossing commercial corridor anchors non-residential base.",
    ),
    dict(
        town_name="Easton", state="MA", county="Bristol", zip_codes="02356",
        population="24558", bond_rating_sp="AA", pension_funded_ratio_pct="65.0",
        tax_base_non_residential_pct="15.0", effective_tax_rate_pct="1.16",
        median_annual_tax_bill="8500", residential_rate_per_1000="12.85",
        district_state_rank="120", district_state_rank_total="351",
        transit_access="none", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        violent_crime_per_100k="40.0", property_crime_per_100k="500.0",
        flood_risk_pct="2.0", flood_2050_growth_pts="0.8", wildfire_risk="Low",
        transparency="yes",
        compiler_notes="Bond AA estimated — verify EMMA. Pension: Bristol County Retirement (~65%) — verify PERAC. No commuter rail; nearest stations Mansfield or Stoughton. Low crime, strong schools relative to Bristol County peers.",
    ),
    dict(
        town_name="North Attleborough", state="MA", county="Bristol", zip_codes="02760",
        population="29639", bond_rating_sp="AA-", pension_funded_ratio_pct="63.0",
        tax_base_non_residential_pct="23.0", effective_tax_rate_pct="1.05",
        median_annual_tax_bill="5800", residential_rate_per_1000="11.63",
        district_state_rank="195", district_state_rank_total="351",
        transit_access="commuter_rail_in_town", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        violent_crime_per_100k="130.0", property_crime_per_100k="1100.0",
        flood_risk_pct="3.0", flood_2050_growth_pts="1.2", wildfire_risk="Low",
        transparency="yes",
        compiler_notes="Bond AA- estimated — verify EMMA. Pension: North Attleborough Retirement Board — verify PERAC. Commuter Rail: Providence/Stoughton Line (North Attleborough station). Low tax rate offset by below-average schools and elevated crime vs. town peers.",
    ),
    dict(
        town_name="Medway", state="MA", county="Norfolk", zip_codes="02053",
        population="13323", bond_rating_sp="AA", pension_funded_ratio_pct="75.0",
        tax_base_non_residential_pct="10.0", effective_tax_rate_pct="1.20",
        median_annual_tax_bill="8000", residential_rate_per_1000="13.30",
        district_state_rank="130", district_state_rank_total="351",
        transit_access="none", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        violent_crime_per_100k="30.0", property_crime_per_100k="400.0",
        flood_risk_pct="2.5", flood_2050_growth_pts="1.0", wildfire_risk="Low",
        transparency="yes",
        compiler_notes="Bond AA estimated — verify EMMA. Pension: Norfolk County Retirement (~75%) — verify PERAC. No commuter rail; primarily car-dependent. Low crime, quiet residential character. Charles River watershed adds minor flood exposure.",
    ),
    dict(
        town_name="Millis", state="MA", county="Norfolk", zip_codes="02054",
        population="8163", bond_rating_sp="A+", pension_funded_ratio_pct="75.0",
        tax_base_non_residential_pct="8.0", effective_tax_rate_pct="1.24",
        median_annual_tax_bill="7400", residential_rate_per_1000="13.74",
        district_state_rank="170", district_state_rank_total="351",
        transit_access="none", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        violent_crime_per_100k="25.0", property_crime_per_100k="350.0",
        flood_risk_pct="3.0", flood_2050_growth_pts="1.2", wildfire_risk="Low",
        transparency="yes",
        compiler_notes="Bond A+ estimated — verify EMMA. Pension: Norfolk County Retirement (~75%) — verify PERAC. No commuter rail. Small, predominantly residential town. Stop River watershed adds minor flood exposure. Very low crime.",
    ),
]

# ─── HTML objects ─────────────────────────────────────────────────────────────
NEW_HTML = [
    '{name:"Shrewsbury",lat:42.2959,lng:-71.7148,state:"MA",county:"Worcester",zip:"01545",pop:37667,bond:"AA",free_cash:null,pension:73.0,debt_pc:null,gfoa:null,tax_non_res:15.0,eff_rate:1.18,med_tax:7900,med_inc:null,res_rate:13.15,d_rank:115,d_total:351,d_10yr:null,math:null,grad:null,ap:null,transp:"Yes",elec_save:0,water_viol:0,transit:"Bus only",violent:80.0,prop_crime:850.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:null,unemp:null,pov:null,flood:2.0,flood50:0.8,fire:"Low",score:50,ter:null,ter_r:"N/A",gaps:10,conf:"low",standout:"Shrewsbury\'s position along Route 9 and I-290 puts it within 10 minutes of Worcester\'s hospital corridor and 40 minutes of Boston via the Pike. Consistent AA bond rating and above-average schools make it one of the most balanced mid-tier suburban buys in Worcester County.",glance:"Shrewsbury is a well-managed Worcester County suburb with strong schools, low crime, and solid fiscal health. No commuter rail — primarily car-dependent via Route 9 or I-290. Home prices are moderate relative to comparable Middlesex County suburbs.",notes:"Bond AA estimated — verify EMMA. Pension: Shrewsbury Retirement Board — verify PERAC. Crime estimated from MA EOPSS. School rank estimated — verify DESE district profiles.",med_home_val:530000,commute:27,owner_occ:76.0,vacancy:3.5,med_age:41.0,low_income_pct:null,ell_pct:null,enrollment_trend:null,sex_off:null,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50}',

    '{name:"Westborough",lat:42.2695,lng:-71.6142,state:"MA",county:"Worcester",zip:"01581",pop:18272,bond:"AA+",free_cash:null,pension:71.0,debt_pc:null,gfoa:null,tax_non_res:30.0,eff_rate:1.22,med_tax:9200,med_inc:null,res_rate:13.87,d_rank:80,d_total:351,d_10yr:null,math:null,grad:null,ap:null,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town)",violent:50.0,prop_crime:600.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:null,unemp:null,pov:null,flood:1.5,flood50:0.5,fire:"Low",score:50,ter:null,ter_r:"N/A",gaps:10,conf:"low",standout:"Westborough\'s 30% non-residential tax base — anchored by pharmaceutical and tech employers along I-495 — subsidizes residential taxes while the Framingham/Worcester commuter rail connects to South Station in under an hour.",glance:"Westborough is one of the strongest mid-tier suburban values in Massachusetts. Excellent schools, a significant commercial tax base, commuter rail access, and AA+ fiscal health make it a compelling alternative to pricier Middlesex County towns.",notes:"Bond AA+ estimated — verify EMMA. Pension: Westborough Retirement Board — verify PERAC. Commercial base includes significant pharma/biotech along I-495. School rank estimated — verify DESE.",med_home_val:620000,commute:32,owner_occ:79.0,vacancy:3.0,med_age:42.0,low_income_pct:null,ell_pct:null,enrollment_trend:null,sex_off:null,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50}',

    '{name:"Northborough",lat:42.3195,lng:-71.6467,state:"MA",county:"Worcester",zip:"01532",pop:15707,bond:"AA",free_cash:null,pension:70.0,debt_pc:null,gfoa:null,tax_non_res:20.0,eff_rate:1.20,med_tax:8100,med_inc:null,res_rate:13.30,d_rank:75,d_total:351,d_10yr:null,math:null,grad:null,ap:null,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:30.0,prop_crime:450.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:null,unemp:null,pov:null,flood:1.5,flood50:0.5,fire:"Low",score:50,ter:null,ter_r:"N/A",gaps:10,conf:"low",standout:"Northborough\'s partnership with Southborough in the Northborough-Southborough Regional School District gives residents access to Algonquin Regional High School, one of the top-ranked high schools in central Massachusetts.",glance:"Northborough is a quiet, family-oriented Worcester County suburb with excellent schools, very low crime, and a modest Route 9 commercial base. No commuter rail — car-dependent. Home prices are competitive with stronger Middlesex County alternatives.",notes:"Bond AA estimated — verify EMMA. Pension: Worcester Regional Retirement — verify PERAC. School district is Northborough-Southborough Regional (Algonquin Regional HS). Rank estimated — verify DESE.",med_home_val:595000,commute:28,owner_occ:81.0,vacancy:2.5,med_age:43.0,low_income_pct:null,ell_pct:null,enrollment_trend:null,sex_off:null,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50}',

    '{name:"Grafton",lat:42.2079,lng:-71.6828,state:"MA",county:"Worcester",zip:"01519",pop:20167,bond:"AA-",free_cash:null,pension:68.0,debt_pc:null,gfoa:null,tax_non_res:12.0,eff_rate:1.28,med_tax:7100,med_inc:null,res_rate:14.20,d_rank:160,d_total:351,d_10yr:null,math:null,grad:null,ap:null,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town)",violent:60.0,prop_crime:550.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:null,unemp:null,pov:null,flood:2.5,flood50:1.0,fire:"Low",score:50,ter:null,ter_r:"N/A",gaps:10,conf:"low",standout:"Grafton is one of the most affordable commuter rail towns in the state — Framingham/Worcester Line service to South Station and a median home price well below comparable Middlesex suburbs makes it a strong value play for Boston-area buyers.",glance:"Grafton is a growing Worcester County town with direct commuter rail to Boston, average schools, and modest home prices. The Blackstone River corridor adds minor flood exposure. Primarily residential with limited commercial tax base.",notes:"Bond AA- estimated — verify EMMA. Pension: Worcester Regional Retirement — verify PERAC. Commuter rail: Framingham/Worcester Line (Grafton station). Crime estimated from MA EOPSS. School rank estimated — verify DESE.",med_home_val:510000,commute:32,owner_occ:74.0,vacancy:3.5,med_age:39.0,low_income_pct:null,ell_pct:null,enrollment_trend:null,sex_off:null,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50}',

    '{name:"Milford",lat:42.1398,lng:-71.5187,state:"MA",county:"Worcester",zip:"01757",pop:29079,bond:"A+",free_cash:null,pension:65.0,debt_pc:null,gfoa:null,tax_non_res:17.0,eff_rate:1.40,med_tax:6200,med_inc:null,res_rate:15.18,d_rank:215,d_total:351,d_10yr:null,math:null,grad:null,ap:null,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:150.0,prop_crime:1200.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:null,unemp:null,pov:null,flood:3.0,flood50:1.2,fire:"Low",score:50,ter:null,ter_r:"N/A",gaps:10,conf:"low",standout:"Milford offers some of the lowest home prices of any town in the greater MetroWest corridor, making it accessible for first-time buyers. The 495 interchange and Route 16 provide good highway access to Boston and Providence.",glance:"Milford is an affordable Worcester County option for buyers priced out of MetroWest. Below-average schools, higher crime relative to suburban peers, and no commuter rail are the tradeoffs. Tax rates are among the highest in this sample.",notes:"Bond A+ estimated — verify EMMA. Pension: Milford Retirement Board — verify PERAC. No commuter rail; bus service only. Crime rates higher than surrounding suburbs — verify FBI CDE / MA EOPSS.",med_home_val:445000,commute:30,owner_occ:65.0,vacancy:4.5,med_age:38.0,low_income_pct:null,ell_pct:null,enrollment_trend:null,sex_off:null,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50}',

    '{name:"Mansfield",lat:42.0334,lng:-71.2187,state:"MA",county:"Bristol",zip:"02048",pop:24112,bond:"AA",free_cash:null,pension:65.0,debt_pc:null,gfoa:null,tax_non_res:25.0,eff_rate:1.12,med_tax:7400,med_inc:null,res_rate:12.44,d_rank:145,d_total:351,d_10yr:null,math:null,grad:null,ap:null,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town)",violent:90.0,prop_crime:900.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:null,unemp:null,pov:null,flood:2.0,flood50:0.8,fire:"Low",score:50,ter:null,ter_r:"N/A",gaps:10,conf:"low",standout:"Mansfield\'s 25% non-residential tax base — anchored by Mansfield Crossing and regional retail along Routes 106 and 140 — keeps residential taxes low. Direct commuter rail to Boston (South Station) completes a strong suburban value package.",glance:"Mansfield is one of the most balanced commuter towns on the Providence/Stoughton rail line. Moderate schools, low taxes, direct MBTA access to South Station, and competitive home prices make it a popular choice for Boston commuters.",notes:"Bond AA estimated — verify EMMA. Pension: Bristol County Retirement (~65%) — verify PERAC. Commuter rail: Providence/Stoughton Line (Mansfield station). Crime estimated from MA EOPSS Bristol County data.",med_home_val:530000,commute:28,owner_occ:77.0,vacancy:3.0,med_age:42.0,low_income_pct:null,ell_pct:null,enrollment_trend:null,sex_off:null,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50}',

    '{name:"Easton",lat:42.0390,lng:-71.1084,state:"MA",county:"Bristol",zip:"02356",pop:24558,bond:"AA",free_cash:null,pension:65.0,debt_pc:null,gfoa:null,tax_non_res:15.0,eff_rate:1.16,med_tax:8500,med_inc:null,res_rate:12.85,d_rank:120,d_total:351,d_10yr:null,math:null,grad:null,ap:null,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:40.0,prop_crime:500.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:null,unemp:null,pov:null,flood:2.0,flood50:0.8,fire:"Low",score:50,ter:null,ter_r:"N/A",gaps:10,conf:"low",standout:"Easton pairs strong schools (top-40% statewide) with very low crime, making it one of the best family-oriented towns in Bristol County. Stonehill College adds cultural amenities to an otherwise quiet, wooded community.",glance:"Easton is a family-friendly Bristol County suburb with above-average schools, very low crime, and competitive home prices. No commuter rail — nearest stations are Mansfield and Stoughton. Primarily residential character with limited commercial base.",notes:"Bond AA estimated — verify EMMA. Pension: Bristol County Retirement (~65%) — verify PERAC. No commuter rail in town. School rank estimated — verify DESE. Crime estimated from MA EOPSS.",med_home_val:610000,commute:33,owner_occ:82.0,vacancy:2.5,med_age:44.0,low_income_pct:null,ell_pct:null,enrollment_trend:null,sex_off:null,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50}',

    '{name:"North Attleborough",lat:41.9759,lng:-71.3328,state:"MA",county:"Bristol",zip:"02760",pop:29639,bond:"AA-",free_cash:null,pension:63.0,debt_pc:null,gfoa:null,tax_non_res:23.0,eff_rate:1.05,med_tax:5800,med_inc:null,res_rate:11.63,d_rank:195,d_total:351,d_10yr:null,math:null,grad:null,ap:null,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town)",violent:130.0,prop_crime:1100.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:null,unemp:null,pov:null,flood:3.0,flood50:1.2,fire:"Low",score:50,ter:null,ter_r:"N/A",gaps:10,conf:"low",standout:"North Attleborough has the lowest effective tax rate in this group — a 23% non-residential base and lean municipal government keep the median bill under $6,000. Direct commuter rail to Providence (8 min) and Boston (65 min) adds commuter optionality.",glance:"North Attleborough is an affordable Bristol County option with commuter rail access and low taxes. The tradeoffs are below-average schools and crime rates higher than the suburban peer group. Home prices are among the most accessible in this analysis.",notes:"Bond AA- estimated — verify EMMA. Pension: North Attleborough Retirement Board — verify PERAC. Commuter rail: Providence/Stoughton Line (North Attleborough station). Crime data estimated — verify FBI CDE / MA EOPSS.",med_home_val:430000,commute:48,owner_occ:72.0,vacancy:4.0,med_age:40.0,low_income_pct:null,ell_pct:null,enrollment_trend:null,sex_off:null,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50}',

    '{name:"Medway",lat:42.1537,lng:-71.3923,state:"MA",county:"Norfolk",zip:"02053",pop:13323,bond:"AA",free_cash:null,pension:75.0,debt_pc:null,gfoa:null,tax_non_res:10.0,eff_rate:1.20,med_tax:8000,med_inc:null,res_rate:13.30,d_rank:130,d_total:351,d_10yr:null,math:null,grad:null,ap:null,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:30.0,prop_crime:400.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:null,unemp:null,pov:null,flood:2.5,flood50:1.0,fire:"Low",score:50,ter:null,ter_r:"N/A",gaps:10,conf:"low",standout:"Medway combines one of the better-funded pension systems in the region (Norfolk County Retirement, ~75%) with very low crime and decent schools — a quietly strong fiscal story often overlooked next to its Franklin and Millis neighbors.",glance:"Medway is a small, well-managed Norfolk County town with low crime, solid schools, and better-than-average pension funding. No commuter rail. The predominantly residential tax base means limited fiscal flexibility. Charles River watershed adds minor flood exposure.",notes:"Bond AA estimated — verify EMMA. Pension: Norfolk County Retirement (~75%) — verify PERAC. No commuter rail. Crime estimated from MA EOPSS. School rank estimated — verify DESE.",med_home_val:570000,commute:33,owner_occ:82.0,vacancy:2.0,med_age:42.0,low_income_pct:null,ell_pct:null,enrollment_trend:null,sex_off:null,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50}',

    '{name:"Millis",lat:42.1676,lng:-71.3606,state:"MA",county:"Norfolk",zip:"02054",pop:8163,bond:"A+",free_cash:null,pension:75.0,debt_pc:null,gfoa:null,tax_non_res:8.0,eff_rate:1.24,med_tax:7400,med_inc:null,res_rate:13.74,d_rank:170,d_total:351,d_10yr:null,math:null,grad:null,ap:null,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:25.0,prop_crime:350.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:null,unemp:null,pov:null,flood:3.0,flood50:1.2,fire:"Low",score:50,ter:null,ter_r:"N/A",gaps:10,conf:"low",standout:"Millis has the lowest violent crime rate of any town in this expanded sample — a small-town character and tight community make it one of the safest options in Norfolk County for families who don\'t need commuter rail access.",glance:"Millis is a small, quiet Norfolk County town with very low crime and a Norfolk County pension system funded at ~75% — well above the Essex Regional average. The tradeoffs are average schools, no transit, and a nearly all-residential tax base.",notes:"Bond A+ estimated — verify EMMA. Pension: Norfolk County Retirement (~75%) — verify PERAC. No commuter rail. Very small town — limited data available. Crime and school rank estimated — verify from MA EOPSS and DESE.",med_home_val:520000,commute:35,owner_occ:79.0,vacancy:3.0,med_age:44.0,low_income_pct:null,ell_pct:null,enrollment_trend:null,sex_off:null,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50}',
]

# ─── Update CSV ───────────────────────────────────────────────────────────────
existing = list(csv.DictReader(open(CSV_FILE, encoding="utf-8")))
fieldnames = list(existing[0].keys())
existing_names = {r["town_name"] for r in existing}

added_csv = 0
for nr in NEW_CSV:
    if nr["town_name"] in existing_names:
        print(f"  SKIP (already in CSV): {nr['town_name']}")
        continue
    row = {f: "" for f in fieldnames}
    row.update(nr)
    existing.append(row)
    added_csv += 1

with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(existing)
print(f"CSV: added {added_csv} towns ({len(existing)} total)")

# ─── Update HTML ──────────────────────────────────────────────────────────────
html = HTML_FILE.read_text(encoding="utf-8")
existing_html_names = set(re.findall(r'name:"([^"]+)"', html))

to_insert = []
for obj_str in NEW_HTML:
    m = re.search(r'name:"([^"]+)"', obj_str)
    name = m.group(1) if m else "?"
    if name in existing_html_names:
        print(f"  SKIP (already in HTML): {name}")
    else:
        to_insert.append(obj_str)

if to_insert:
    # Find the closing ] of TOWNS array
    marker = "const TOWNS = ["
    ts = html.index(marker) + len(marker)
    depth = 1; i = ts
    while i < len(html) and depth > 0:
        if html[i] == "[": depth += 1
        elif html[i] == "]": depth -= 1
        i += 1
    te = i - 1  # index of closing ]

    insertion = "\n  " + ",\n  ".join(to_insert) + ","
    html = html[:te] + insertion + html[te:]
    HTML_FILE.write_text(html, encoding="utf-8")
    print(f"HTML: inserted {len(to_insert)} town objects")
else:
    print("HTML: nothing to insert")
