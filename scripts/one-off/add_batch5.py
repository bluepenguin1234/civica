"""
Add 10 new MA towns (batch 5) to towns.csv, civica-v5.html, and update_all.py.
Run ONCE, then run:  py scripts/update_all.py

Towns:
  Middlesex: Sudbury, Holliston, Bedford, Maynard, Tyngsborough
  Norfolk:   Westwood, Randolph, Wrentham
  Plymouth:  Pembroke
  Worcester: Northbridge

Tax rates: MA DOR FY2025
School ranks: DESE / SchoolDigger estimates
Bond ratings: EMMA estimates
Pension: county retirement system estimates
ZHVI: Zillow estimates (May 2026)
Crime: FBI UCR / MA EOPSS estimates
"""

import csv, re
from pathlib import Path

ROOT      = Path(__file__).parent.parent
CSV_FILE  = ROOT / "data" / "towns.csv"
HTML_FILE = ROOT / "civica-v5.html"
PY_FILE   = ROOT / "scripts" / "update_all.py"

MDX = 64.6   # Middlesex County Retirement
NFK = 66.9   # Norfolk County Retirement
PLY = 68.4   # Plymouth County Retirement
WRC = 56.2   # Worcester Regional Retirement

# ─── 1. New CSV rows ──────────────────────────────────────────────────────────
NEW_TOWNS = [
    dict(
        town_name="Sudbury", state="MA", county="Middlesex", zip_codes="01776",
        population="19067", bond_rating_sp="AA", pension_funded_ratio_pct=str(MDX),
        tax_base_non_residential_pct="8.5", effective_tax_rate_pct="1.37",
        median_annual_tax_bill="14375", residential_rate_per_1000="13.69",
        district_state_rank="18", district_state_rank_total="351",
        transit_access="none", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        violent_crime_per_100k="18.0", property_crime_per_100k="215.0",
        flood_risk_pct="3.0", flood_2050_growth_pts="1.5", wildfire_risk="Low",
        transparency="yes",
        compiler_notes="Affluent MetroWest; K-8 MCAS math 73%, HS is Lincoln-Sudbury Regional (grad 98%, AP 29.7%). Bond AA estimated. Pension: Middlesex County Retirement (~64.6%).",
    ),
    dict(
        town_name="Westwood", state="MA", county="Norfolk", zip_codes="02090",
        population="16213", bond_rating_sp="AA", pension_funded_ratio_pct=str(NFK),
        tax_base_non_residential_pct="12.0", effective_tax_rate_pct="1.44",
        median_annual_tax_bill="15131", residential_rate_per_1000="14.41",
        district_state_rank="12", district_state_rank_total="351",
        transit_access="commuter_rail_in_town", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        violent_crime_per_100k="25.0", property_crime_per_100k="195.0",
        flood_risk_pct="0.5", flood_2050_growth_pts="0.5", wildfire_risk="Low",
        transparency="yes",
        compiler_notes="Providence/Stoughton commuter rail (Islington + Route 128 stations). Top-12 district. Bond AA estimated. Pension: Norfolk County Retirement (~66.9%).",
    ),
    dict(
        town_name="Holliston", state="MA", county="Middlesex", zip_codes="01746",
        population="14964", bond_rating_sp="Not rated", pension_funded_ratio_pct=str(MDX),
        tax_base_non_residential_pct="9.0", effective_tax_rate_pct="1.51",
        median_annual_tax_bill="8770", residential_rate_per_1000="15.12",
        district_state_rank="90", district_state_rank_total="351",
        transit_access="none", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        violent_crime_per_100k="45.0", property_crime_per_100k="385.0",
        flood_risk_pct="1.5", flood_2050_growth_pts="0.8", wildfire_risk="Low",
        transparency="yes",
        compiler_notes="MetroWest suburb; no commuter rail. Bond not rated. Pension: Middlesex County Retirement (~64.6%).",
    ),
    dict(
        town_name="Bedford", state="MA", county="Middlesex", zip_codes="01730",
        population="14343", bond_rating_sp="AA+", pension_funded_ratio_pct=str(MDX),
        tax_base_non_residential_pct="22.0", effective_tax_rate_pct="1.37",
        median_annual_tax_bill="10283", residential_rate_per_1000="13.71",
        district_state_rank="45", district_state_rank_total="351",
        transit_access="bus_only", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        violent_crime_per_100k="55.0", property_crime_per_100k="380.0",
        flood_risk_pct="1.0", flood_2050_growth_pts="0.5", wildfire_risk="Low",
        transparency="yes",
        compiler_notes="Hanscom AFB drives 22% non-res tax base; stabilizes fiscal picture. Bond AA+ estimated. Pension: Middlesex County Retirement (~64.6%).",
    ),
    dict(
        town_name="Randolph", state="MA", county="Norfolk", zip_codes="02368",
        population="34683", bond_rating_sp="A+", pension_funded_ratio_pct=str(NFK),
        tax_base_non_residential_pct="15.0", effective_tax_rate_pct="1.44",
        median_annual_tax_bill="6462", residential_rate_per_1000="14.36",
        district_state_rank="325", district_state_rank_total="351",
        transit_access="bus_only", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        violent_crime_per_100k="340.0", property_crime_per_100k="1100.0",
        flood_risk_pct="2.0", flood_2050_growth_pts="1.0", wildfire_risk="Low",
        transparency="yes",
        compiler_notes="Most diverse Norfolk County town; affordable entry. Bond A+ estimated. Pension: Norfolk County Retirement (~66.9%). Crime above MA average.",
    ),
    dict(
        town_name="Pembroke", state="MA", county="Plymouth", zip_codes="02359",
        population="18335", bond_rating_sp="Not rated", pension_funded_ratio_pct=str(PLY),
        tax_base_non_residential_pct="7.0", effective_tax_rate_pct="1.35",
        median_annual_tax_bill="6865", residential_rate_per_1000="13.46",
        district_state_rank="230", district_state_rank_total="351",
        transit_access="limited", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        violent_crime_per_100k="90.0", property_crime_per_100k="700.0",
        flood_risk_pct="3.0", flood_2050_growth_pts="1.5", wildfire_risk="Low",
        transparency="yes",
        compiler_notes="Growing South Shore suburb. Bond not rated. Pension: Plymouth County Retirement (~68.4%).",
    ),
    dict(
        town_name="Northbridge", state="MA", county="Worcester", zip_codes="01534",
        population="16358", bond_rating_sp="Not rated", pension_funded_ratio_pct=str(WRC),
        tax_base_non_residential_pct="8.0", effective_tax_rate_pct="1.50",
        median_annual_tax_bill="6283", residential_rate_per_1000="14.96",
        district_state_rank="240", district_state_rank_total="351",
        transit_access="none", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        violent_crime_per_100k="75.0", property_crime_per_100k="600.0",
        flood_risk_pct="2.5", flood_2050_growth_pts="1.0", wildfire_risk="Low",
        transparency="yes",
        compiler_notes="Growing Worcester County town along Blackstone River. Bond not rated. Pension: Worcester Regional Retirement (~56.2%).",
    ),
    dict(
        town_name="Wrentham", state="MA", county="Norfolk", zip_codes="02093",
        population="12305", bond_rating_sp="AA-", pension_funded_ratio_pct=str(NFK),
        tax_base_non_residential_pct="14.0", effective_tax_rate_pct="1.26",
        median_annual_tax_bill="7440", residential_rate_per_1000="12.61",
        district_state_rank="80", district_state_rank_total="351",
        transit_access="commuter_rail_nearby", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        violent_crime_per_100k="35.0", property_crime_per_100k="350.0",
        flood_risk_pct="1.5", flood_2050_growth_pts="0.8", wildfire_risk="Low",
        transparency="yes",
        compiler_notes="Near Franklin commuter rail. Premium Outlets drive 14% non-res base. K-8 MCAS math 66%; HS is King Philip Regional (grad 95.3%, AP 38.1%). Bond AA- estimated. Pension: Norfolk County Retirement (~66.9%).",
    ),
    dict(
        town_name="Maynard", state="MA", county="Middlesex", zip_codes="01754",
        population="10663", bond_rating_sp="Not rated", pension_funded_ratio_pct=str(MDX),
        tax_base_non_residential_pct="11.0", effective_tax_rate_pct="1.78",
        median_annual_tax_bill="8717", residential_rate_per_1000="17.79",
        district_state_rank="165", district_state_rank_total="351",
        transit_access="none", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        violent_crime_per_100k="115.0", property_crime_per_100k="750.0",
        flood_risk_pct="2.5", flood_2050_growth_pts="1.2", wildfire_risk="Low",
        transparency="yes",
        compiler_notes="Small MetroWest mill town; higher residential rate reflects limited commercial base. DFCU HQ here. Bond not rated. Pension: Middlesex County Retirement (~64.6%).",
    ),
    dict(
        town_name="Tyngsborough", state="MA", county="Middlesex", zip_codes="01879",
        population="12424", bond_rating_sp="Not rated", pension_funded_ratio_pct=str(MDX),
        tax_base_non_residential_pct="10.0", effective_tax_rate_pct="1.45",
        median_annual_tax_bill="6936", residential_rate_per_1000="14.45",
        district_state_rank="205", district_state_rank_total="351",
        transit_access="none", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        violent_crime_per_100k="55.0", property_crime_per_100k="420.0",
        flood_risk_pct="4.0", flood_2050_growth_pts="2.0", wildfire_risk="Low",
        transparency="yes",
        compiler_notes="Growing Merrimack Valley border town. Flood risk elevated from Merrimack River. Bond not rated. Pension: Middlesex County Retirement (~64.6%).",
    ),
]

# ─── 2. New HTML objects ──────────────────────────────────────────────────────
NEW_HTML = [
    '{name:"Sudbury",lat:42.3814,lng:-71.4162,state:"MA",county:"Middlesex",zip:"01776",pop:19067,bond:"AA",free_cash:null,pension:64.6,debt_pc:null,gfoa:null,tax_non_res:8.5,eff_rate:1.37,med_tax:14375,med_inc:234634,res_rate:13.69,d_rank:18,d_total:351,d_10yr:null,math:73.0,grad:98.0,ap:29.7,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:18.0,prop_crime:215.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:84.4,unemp:null,pov:null,flood:3.0,flood50:1.5,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:0,conf:"medium",standout:"One of the highest-income municipalities in Massachusetts ($235k median household income). Lincoln-Sudbury Regional HS ranks among the top 20 MA districts. Virtually no violent crime.",glance:"Sudbury is an affluent MetroWest town with top-20 school rankings, extremely low crime, and a very high median income. The trade-offs are a home price near $1M and no commuter rail access.",notes:"K-8 MCAS math 73%; HS is Lincoln-Sudbury Regional (grad 98%, AP 29.7%). Bond AA estimated — pull from EMMA. Pension: Middlesex County Retirement.",med_home_val:985000,commute:30,owner_occ:95.0,vacancy:3.0,med_age:48.0,low_income_pct:4.0,ell_pct:3.0,enrollment_trend:null,sex_off:0.10,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Westwood",lat:42.2193,lng:-71.2209,state:"MA",county:"Norfolk",zip:"02090",pop:16213,bond:"AA",free_cash:null,pension:66.9,debt_pc:null,gfoa:null,tax_non_res:12.0,eff_rate:1.44,med_tax:15131,med_inc:205000,res_rate:14.41,d_rank:12,d_total:351,d_10yr:null,math:76.0,grad:98.6,ap:51.2,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town)",violent:25.0,prop_crime:195.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:71.0,unemp:null,pov:null,flood:0.5,flood50:0.5,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:0,conf:"medium",standout:"Providence/Stoughton commuter rail runs through Westwood (Islington + Route 128 stations). Top-12 state school district. Rare combination of exceptional schools and direct South Station rail access.",glance:"Westwood combines top-12 state school rankings with commuter rail access to South Station — a rare pairing in Norfolk County. Home prices are high but the fundamentals justify the premium.",notes:"Bond AA estimated — pull from EMMA. Pension: Norfolk County Retirement (~66.9%).",med_home_val:970000,commute:30,owner_occ:91.0,vacancy:3.5,med_age:46.0,low_income_pct:6.0,ell_pct:4.0,enrollment_trend:null,sex_off:0.12,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Holliston",lat:42.1989,lng:-71.4348,state:"MA",county:"Middlesex",zip:"01746",pop:14964,bond:"Not rated",free_cash:null,pension:64.6,debt_pc:null,gfoa:null,tax_non_res:9.0,eff_rate:1.51,med_tax:8770,med_inc:154684,res_rate:15.12,d_rank:90,d_total:351,d_10yr:null,math:65.0,grad:95.1,ap:28.5,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:45.0,prop_crime:385.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:65.7,unemp:null,pov:null,flood:1.5,flood50:0.8,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:0,conf:"medium",standout:"Solid MetroWest suburb with above-average schools and low crime at a more accessible price point than neighboring Medfield or Sherborn. Household income $155k above the MA median.",glance:"Holliston offers solid schools and low crime at a lower price than neighboring premium MetroWest towns. No transit access is the main trade-off for buyers who commute.",notes:"Bond not rated. Pension: Middlesex County Retirement (~64.6%). Pull free cash and debt from ACFR.",med_home_val:545000,commute:28,owner_occ:88.0,vacancy:4.0,med_age:44.0,low_income_pct:8.0,ell_pct:5.0,enrollment_trend:null,sex_off:0.20,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Bedford",lat:42.4912,lng:-71.2759,state:"MA",county:"Middlesex",zip:"01730",pop:14343,bond:"AA+",free_cash:null,pension:64.6,debt_pc:null,gfoa:null,tax_non_res:22.0,eff_rate:1.37,med_tax:10283,med_inc:158964,res_rate:13.71,d_rank:45,d_total:351,d_10yr:null,math:70.0,grad:98.7,ap:34.7,transp:"Yes",elec_save:0,water_viol:0,transit:"Bus only",violent:55.0,prop_crime:380.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:69.4,unemp:null,pov:null,flood:1.0,flood50:0.5,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:0,conf:"medium",standout:"Hanscom Air Force Base anchors a 22% non-residential tax base, stabilizing the fiscal picture. Top-50 MA school district with a 98.7% graduation rate. Convenient to the Route 128 tech corridor.",glance:"Bedford is a stable Middlesex suburb anchored by Hanscom AFB. Its large non-residential tax base funds top-50 schools while keeping the residential rate below the regional average.",notes:"Bond AA+ estimated — pull from EMMA. Pension: Middlesex County Retirement (~64.6%).",med_home_val:730000,commute:25,owner_occ:84.0,vacancy:4.0,med_age:44.0,low_income_pct:8.0,ell_pct:12.0,enrollment_trend:null,sex_off:0.14,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Randolph",lat:42.1640,lng:-71.0439,state:"MA",county:"Norfolk",zip:"02368",pop:34683,bond:"A+",free_cash:null,pension:66.9,debt_pc:null,gfoa:null,tax_non_res:15.0,eff_rate:1.44,med_tax:6462,med_inc:103129,res_rate:14.36,d_rank:325,d_total:351,d_10yr:null,math:22.0,grad:85.9,ap:26.9,transp:"Yes",elec_save:0,water_viol:0,transit:"Bus only",violent:340.0,prop_crime:1100.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:34.7,unemp:null,pov:null,flood:2.0,flood50:1.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:0,conf:"medium",standout:"One of the most racially and ethnically diverse communities in Norfolk County. Affordable price point near Boston with MBTA bus access to South Shore Plaza and Route 128 employers.",glance:"Randolph is one of the most affordable and diverse towns near Boston. School and safety metrics are well below average — the trade-off for the lower price point and proximity to Route 128.",notes:"Bond A+ estimated. Pension: Norfolk County Retirement (~66.9%). Crime above MA state average.",med_home_val:440000,commute:30,owner_occ:72.0,vacancy:5.5,med_age:42.0,low_income_pct:20.0,ell_pct:22.0,enrollment_trend:null,sex_off:0.26,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Pembroke",lat:42.0701,lng:-70.8009,state:"MA",county:"Plymouth",zip:"02359",pop:18335,bond:"Not rated",free_cash:null,pension:68.4,debt_pc:null,gfoa:null,tax_non_res:7.0,eff_rate:1.35,med_tax:6865,med_inc:141332,res_rate:13.46,d_rank:230,d_total:351,d_10yr:null,math:38.0,grad:95.4,ap:35.5,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:90.0,prop_crime:700.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:45.7,unemp:null,pov:null,flood:3.0,flood50:1.5,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:0,conf:"medium",standout:"Growing South Shore suburb with lower prices than coastal neighbors like Duxbury and Marshfield. Plymouth County Retirement is one of the better-funded systems in MA (~68%).",glance:"Pembroke is a growing South Shore suburb with lower home prices than coastal neighbors. School performance is below average, but Plymouth County pension funding (68%) is better than most. No commuter rail.",notes:"Bond not rated. Pension: Plymouth County Retirement (~68.4%). Pull free cash and debt from ACFR.",med_home_val:495000,commute:35,owner_occ:86.0,vacancy:5.5,med_age:47.0,low_income_pct:9.0,ell_pct:3.0,enrollment_trend:null,sex_off:0.28,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Northbridge",lat:42.1521,lng:-71.6434,state:"MA",county:"Worcester",zip:"01534",pop:16358,bond:"Not rated",free_cash:null,pension:56.2,debt_pc:null,gfoa:null,tax_non_res:8.0,eff_rate:1.50,med_tax:6283,med_inc:103355,res_rate:14.96,d_rank:240,d_total:351,d_10yr:null,math:37.0,grad:84.7,ap:16.5,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:75.0,prop_crime:600.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:34.9,unemp:null,pov:null,flood:2.5,flood50:1.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:0,conf:"medium",standout:"Growing Worcester County suburb along the Blackstone River with some of the most affordable home prices in the Civica dataset (~$420k). Improving population trend.",glance:"Northbridge offers among the lowest home prices in the dataset. School and safety metrics are below average. The Worcester Regional pension (56%) is one of the weaker in the dataset — a long-term fiscal risk.",notes:"Bond not rated. Pension: Worcester Regional Retirement (~56.2%). Pull free cash and debt from ACFR.",med_home_val:405000,commute:30,owner_occ:82.0,vacancy:5.0,med_age:42.0,low_income_pct:12.0,ell_pct:6.0,enrollment_trend:null,sex_off:0.30,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Wrentham",lat:42.0504,lng:-71.3484,state:"MA",county:"Norfolk",zip:"02093",pop:12305,bond:"AA-",free_cash:null,pension:66.9,debt_pc:null,gfoa:null,tax_non_res:14.0,eff_rate:1.26,med_tax:7440,med_inc:147930,res_rate:12.61,d_rank:80,d_total:351,d_10yr:null,math:66.0,grad:95.3,ap:38.1,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (nearby)",violent:35.0,prop_crime:350.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:53.7,unemp:null,pov:null,flood:1.5,flood50:0.8,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:0,conf:"medium",standout:"Near Franklin commuter rail station on the Providence/Stoughton line. New England Premium Outlets generate a 14% non-residential tax base and one of the lower residential rates in Norfolk County.",glance:"Wrentham offers a low tax rate for Norfolk County, proximity to Franklin commuter rail, and solid K-8 school performance. A strong value play in southwestern Norfolk County.",notes:"K-8 MCAS math 66%; HS is King Philip Regional (grad 95.3%, AP 38.1%). Bond AA- estimated. Pension: Norfolk County Retirement (~66.9%).",med_home_val:570000,commute:32,owner_occ:90.0,vacancy:4.5,med_age:46.0,low_income_pct:7.0,ell_pct:4.0,enrollment_trend:null,sex_off:0.17,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Maynard",lat:42.4260,lng:-71.4537,state:"MA",county:"Middlesex",zip:"01754",pop:10663,bond:"Not rated",free_cash:null,pension:64.6,debt_pc:null,gfoa:null,tax_non_res:11.0,eff_rate:1.78,med_tax:8717,med_inc:119549,res_rate:17.79,d_rank:165,d_total:351,d_10yr:null,math:50.0,grad:91.8,ap:41.1,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:115.0,prop_crime:750.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:64.2,unemp:null,pov:null,flood:2.5,flood50:1.2,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:0,conf:"medium",standout:"Compact MetroWest mill town reinvented as a tech and creative hub. Digital Federal Credit Union headquarters. Walkable downtown with arts venues. Affordable by Middlesex County standards.",glance:"Maynard is a small Middlesex mill town with a distinctive arts and tech identity. The higher residential rate reflects a limited commercial base, but home prices stay well below the regional median.",notes:"Bond not rated. Pension: Middlesex County Retirement (~64.6%). Pull free cash and debt from ACFR.",med_home_val:475000,commute:25,owner_occ:74.0,vacancy:5.0,med_age:43.0,low_income_pct:15.0,ell_pct:8.0,enrollment_trend:null,sex_off:0.28,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Tyngsborough",lat:42.6690,lng:-71.4237,state:"MA",county:"Middlesex",zip:"01879",pop:12424,bond:"Not rated",free_cash:null,pension:64.6,debt_pc:null,gfoa:null,tax_non_res:10.0,eff_rate:1.45,med_tax:6936,med_inc:144375,res_rate:14.45,d_rank:205,d_total:351,d_10yr:null,math:42.0,grad:97.1,ap:23.0,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:55.0,prop_crime:420.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:49.7,unemp:null,pov:null,flood:4.0,flood50:2.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:0,conf:"medium",standout:"Growing Merrimack Valley town on the NH border with low crime and above-average household income ($144k) for northern Middlesex County. More affordable than communities closer to Boston.",glance:"Tyngsborough is a growing border town with lower home prices than communities closer to Boston. Below-average school performance is the main trade-off; flood risk from the Merrimack River is a long-term concern.",notes:"Bond not rated. Pension: Middlesex County Retirement (~64.6%). Flood risk elevated — Merrimack River. Pull free cash and debt from ACFR.",med_home_val:460000,commute:30,owner_occ:84.0,vacancy:5.0,med_age:44.0,low_income_pct:10.0,ell_pct:5.0,enrollment_trend:null,sex_off:0.24,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',
]

# ─── Step 1: Add to towns.csv ─────────────────────────────────────────────────
print("Step 1: Adding to towns.csv...")
with open(CSV_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = list(reader.fieldnames)
    existing = list(reader)

existing_names = {r["town_name"] for r in existing}
added_csv = 0
for t in NEW_TOWNS:
    if t["town_name"] in existing_names:
        print(f"  SKIP (already in CSV): {t['town_name']}")
        continue
    row = {f: "" for f in fieldnames}
    row.update(t)
    existing.append(row)
    added_csv += 1
    print(f"  + {t['town_name']}")

with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(existing)

total_towns = len(existing)
print(f"  CSV: {total_towns} towns total ({added_csv} added)")

# ─── Step 2: Patch update_all.py ─────────────────────────────────────────────
print("\nStep 2: Patching update_all.py...")
py_text = PY_FILE.read_text(encoding="utf-8")

# 2a. ZHVI entries — insert after Medway/Millis line
NEW_ZHVI = '    "Sudbury":1050000,"Westwood":1050000,"Holliston":580000,"Bedford":750000,\n    "Randolph":450000,"Pembroke":510000,"Northbridge":420000,"Wrentham":590000,\n    "Maynard":490000,"Tyngsborough":480000,\n'
if '"Sudbury"' not in py_text:
    py_text = re.sub(
        r'("Medway":\d+,"Millis":\d+,\n)',
        r'\1' + NEW_ZHVI,
        py_text
    )
    print("  Added ZHVI entries")
else:
    print("  ZHVI entries already present")

# 2b. COUNTY_MAP entries
NEW_COUNTY = '    "Sudbury":"Middlesex","Westwood":"Norfolk","Holliston":"Middlesex",\n    "Bedford":"Middlesex","Randolph":"Norfolk","Pembroke":"Plymouth",\n    "Northbridge":"Worcester","Wrentham":"Norfolk","Maynard":"Middlesex",\n    "Tyngsborough":"Middlesex",\n'
if '"Sudbury":"Middlesex"' not in py_text:
    py_text = re.sub(
        r'("Medway":"Norfolk","Millis":"Norfolk",\n)',
        r'\1' + NEW_COUNTY,
        py_text
    )
    print("  Added COUNTY_MAP entries")
else:
    print("  COUNTY_MAP entries already present")

# 2c. DISTRICT_MAP entries for split K-8/HS district towns
DISTRICT_ADD = '    "Sudbury":               "lincoln-sudbury",\n    "Wrentham":              "king philip",\n'
if '"Sudbury":' not in py_text:
    py_text = re.sub(
        r'(    "Northborough":         "northborough-southborough",\n)',
        r'\1' + DISTRICT_ADD,
        py_text
    )
    print("  Added DISTRICT_MAP entries")
else:
    print("  DISTRICT_MAP entries already present")

# 2d. MATH_OVERRIDES dict — add after WILDFIRE_UPDATES block, before Load methodology comment
MATH_OVERRIDES_CODE = '''
# MCAS math overrides for towns where K-8 district has the math data but HS district is used for grad/AP
MATH_OVERRIDES = {
    "Sudbury":  73.0,   # K-8 district MCAS; lincoln-sudbury HS has no district-level math pct
    "Wrentham": 66.0,   # K-8 district MCAS; King Philip Regional math (43%) covers 3 towns
}
'''
if "MATH_OVERRIDES" not in py_text:
    py_text = re.sub(
        r'(# ─── Load methodology )',
        MATH_OVERRIDES_CODE + r'\n\1',
        py_text
    )
    print("  Added MATH_OVERRIDES dict")
else:
    print("  MATH_OVERRIDES already present")

# 2e. Apply MATH_OVERRIDES in Phase 1 loop after school data fill
MATH_APPLY_CODE = '''    # K-8 MCAS math override for towns with split K-8/HS districts
    if town in MATH_OVERRIDES:
        setf(row, "test_scores_math_pct", MATH_OVERRIDES[town])

'''
if "MATH_OVERRIDES[town]" not in py_text:
    py_text = re.sub(
        r'(    # 3\. Excel bulk data)',
        MATH_APPLY_CODE + r'\1',
        py_text
    )
    print("  Added MATH_OVERRIDES application in Phase 1 loop")
else:
    print("  MATH_OVERRIDES application already present")

PY_FILE.write_text(py_text, encoding="utf-8")
print("  update_all.py saved")

# ─── Step 3: Add HTML town objects ───────────────────────────────────────────
print("\nStep 3: Adding HTML town objects...")
html = HTML_FILE.read_text(encoding="utf-8")
existing_html_names = set(re.findall(r'\{name:"([^"]+)"', html))

to_insert = []
for obj_str in NEW_HTML:
    m = re.search(r'\{name:"([^"]+)"', obj_str)
    name = m.group(1) if m else "?"
    if name in existing_html_names:
        print(f"  SKIP (already in HTML): {name}")
    else:
        to_insert.append(obj_str)
        print(f"  + {name}")

if to_insert:
    # Find the closing ] of the TOWNS array
    marker = "const TOWNS = ["
    ts = html.index(marker) + len(marker)
    depth = 1; i = ts
    while i < len(html) and depth > 0:
        if html[i] == "[": depth += 1
        elif html[i] == "]": depth -= 1
        i += 1
    te = i - 1  # index of closing ]
    insertion = "\n" + ",\n".join(to_insert) + ","
    html = html[:te] + insertion + html[te:]

# ─── Step 4: Update count badges ─────────────────────────────────────────────
html = re.sub(
    r'Now live · Massachusetts · \d+ towns and cities',
    f'Now live · Massachusetts · {total_towns} towns and cities', html
)
html = re.sub(
    r'<span class="sn-num">\d+</span>',
    f'<span class="sn-num">{total_towns}</span>', html
)
html = re.sub(
    r'Civica scores \d+ towns and cities across',
    f'Civica scores {total_towns} towns and cities across', html
)

HTML_FILE.write_text(html, encoding="utf-8")
print(f"\nStep 4: Count badges updated to {total_towns}")
print(f"\nDone. Run next:  py scripts/update_all.py")
