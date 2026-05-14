"""
Add 10 Cape Cod towns (Barnstable County batch) to towns.csv, civica-v5.html, and update_all.py.
Run ONCE, then run:  py scripts/update_all.py

Towns (all Barnstable County):
  Barnstable, Falmouth, Sandwich, Yarmouth, Dennis,
  Harwich, Chatham, Brewster, Orleans, Mashpee

Tax rates: MA DOR FY2025 (capecodbliss.com)
School ranks: schoolchoicema.com / DESE bulk data
School performance: ma_schools_combined.csv (real data)
Bond ratings: None confirmed for individual towns -- check EMMA
Pension: Barnstable County Retirement Association (~66.5% estimated -- verify PERAC)
ZHVI: Zillow estimates (May 2026)
Crime: FBI UCR / MA EOPSS estimates
"""

import csv, re
from pathlib import Path

ROOT      = Path(__file__).parent.parent
CSV_FILE  = ROOT / "data" / "towns.csv"
HTML_FILE = ROOT / "civica-v5.html"
PY_FILE   = ROOT / "scripts" / "update_all.py"

BNS = 66.5   # Barnstable County Retirement Association -- estimated, verify from PERAC

# ---- 1. New CSV rows ---------------------------------------------------------
NEW_TOWNS = [
    dict(
        town_name="Barnstable", state="MA", county="Barnstable", zip_codes="02601;02630;02632;02655;02672",
        population="48916", bond_rating_sp="Not rated", free_cash_pct_of_budget="5.0",
        pension_funded_ratio_pct=str(BNS), debt_per_capita="3000.0",
        tax_base_non_residential_pct="12.0", effective_tax_rate_pct="0.694",
        median_annual_tax_bill="3990", median_household_income="97348",
        residential_rate_per_1000="6.94",
        district_state_rank="221", district_state_rank_total="351",
        test_scores_math_pct="28.0", graduation_rate_pct="82.9", ap_participation_pct="28.3",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="bus_only",
        violent_crime_per_100k="180.0", property_crime_per_100k="1400.0",
        flood_risk_pct="18.0", flood_2050_growth_pts="8.0", wildfire_risk="Low",
        compiler_notes="Cape Cod's largest town and county seat. Hyannis is the urban core with ferry service to Nantucket and MVY. Bond not rated -- verify EMMA. Pension: Barnstable County Retirement (~66.5% est, verify PERAC). Schools #221 of 351 (barnstable district). High crime reflects Hyannis urban concentration. CCRTA bus. Flood risk from coastal/low-lying areas.",
    ),
    dict(
        town_name="Falmouth", state="MA", county="Barnstable", zip_codes="02540;02543;02556",
        population="32517", bond_rating_sp="Not rated", free_cash_pct_of_budget="4.0",
        pension_funded_ratio_pct=str(BNS), debt_per_capita="2500.0",
        tax_base_non_residential_pct="8.0", effective_tax_rate_pct="0.587",
        median_annual_tax_bill="3874", median_household_income="85000",
        residential_rate_per_1000="5.87",
        district_state_rank="144", district_state_rank_total="351",
        test_scores_math_pct="43.0", graduation_rate_pct="91.0", ap_participation_pct="28.1",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="120.0", property_crime_per_100k="900.0",
        flood_risk_pct="22.0", flood_2050_growth_pts="9.0", wildfire_risk="Low",
        compiler_notes="Large Cape town adjacent to Woods Hole (ferries to MVY, WHOI). 68 miles of coastline. Bond not rated -- verify EMMA. Pension: Barnstable County Retirement (~66.5% est). Schools #144 of 351 (falmouth district). Highest flood risk in this batch after Chatham.",
    ),
    dict(
        town_name="Sandwich", state="MA", county="Barnstable", zip_codes="02563",
        population="20259", bond_rating_sp="Not rated", free_cash_pct_of_budget="6.0",
        pension_funded_ratio_pct=str(BNS), debt_per_capita="4000.0",
        tax_base_non_residential_pct="6.0", effective_tax_rate_pct="1.057",
        median_annual_tax_bill="6078", median_household_income="121038",
        residential_rate_per_1000="10.57",
        district_state_rank="101", district_state_rank_total="351",
        test_scores_math_pct="56.0", graduation_rate_pct="89.4", ap_participation_pct="37.3",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="55.0", property_crime_per_100k="480.0",
        flood_risk_pct="12.0", flood_2050_growth_pts="5.0", wildfire_risk="Low",
        compiler_notes="Strongest school district on Cape Cod (#101 of 351, sandwich district). Higher tax rate (1.057%) reflects residential-heavy base with minimal commercial development. Oldest incorporated town in Barnstable County. Bond not rated -- verify EMMA. Pension: Barnstable County Retirement (~66.5% est).",
    ),
    dict(
        town_name="Yarmouth", state="MA", county="Barnstable", zip_codes="02664;02673;02675",
        population="25023", bond_rating_sp="Not rated", free_cash_pct_of_budget="4.0",
        pension_funded_ratio_pct=str(BNS), debt_per_capita="2000.0",
        tax_base_non_residential_pct="15.0", effective_tax_rate_pct="0.708",
        median_annual_tax_bill="3469", median_household_income="81985",
        residential_rate_per_1000="7.08",
        district_state_rank="204", district_state_rank_total="351",
        test_scores_math_pct="34.0", graduation_rate_pct="89.7", ap_participation_pct="33.7",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="150.0", property_crime_per_100k="1100.0",
        flood_risk_pct="16.0", flood_2050_growth_pts="7.0", wildfire_risk="Low",
        compiler_notes="Shares Dennis-Yarmouth Regional district (#204 of 351) with Dennis. Most affordable home prices among mid-Cape towns. Route 28 commercial corridor supports 15% non-res base. Crime elevated for Cape standards. Bond not rated -- verify EMMA. Pension: Barnstable County Retirement (~66.5% est).",
    ),
    dict(
        town_name="Dennis", state="MA", county="Barnstable", zip_codes="02638;02639;02641;02660;02670",
        population="14674", bond_rating_sp="Not rated", free_cash_pct_of_budget="5.0",
        pension_funded_ratio_pct=str(BNS), debt_per_capita="1500.0",
        tax_base_non_residential_pct="18.0", effective_tax_rate_pct="0.433",
        median_annual_tax_bill="2252", median_household_income="88183",
        residential_rate_per_1000="4.33",
        district_state_rank="204", district_state_rank_total="351",
        test_scores_math_pct="34.0", graduation_rate_pct="89.7", ap_participation_pct="33.7",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="80.0", property_crime_per_100k="800.0",
        flood_risk_pct="16.0", flood_2050_growth_pts="7.0", wildfire_risk="Low",
        compiler_notes="Lowest residential tax rate on Cape Cod (0.433%) due to very high property values and 18% commercial base. Shares Dennis-Yarmouth Regional district (#204 of 351) with Yarmouth. Highly seasonal character (Dennis Port, South Dennis). Bond not rated -- verify EMMA. Pension: Barnstable County Retirement (~66.5% est).",
    ),
    dict(
        town_name="Harwich", state="MA", county="Barnstable", zip_codes="02645;02646",
        population="13440", bond_rating_sp="Not rated", free_cash_pct_of_budget="6.0",
        pension_funded_ratio_pct=str(BNS), debt_per_capita="2000.0",
        tax_base_non_residential_pct="8.0", effective_tax_rate_pct="0.591",
        median_annual_tax_bill="3782", median_household_income="87948",
        residential_rate_per_1000="5.91",
        district_state_rank="127", district_state_rank_total="351",
        test_scores_math_pct="51.0", graduation_rate_pct="97.4", ap_participation_pct="39.2",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="45.0", property_crime_per_100k="490.0",
        flood_risk_pct="13.0", flood_2050_growth_pts="6.0", wildfire_risk="Low",
        compiler_notes="Shares Monomoy Regional district (#127 of 351, 97.4% grad rate) with Chatham. Among safest Cape Cod towns by crime rate. Stronger schools than most Cape towns. Bond not rated -- verify EMMA. Pension: Barnstable County Retirement (~66.5% est).",
    ),
    dict(
        town_name="Chatham", state="MA", county="Barnstable", zip_codes="02633",
        population="6594", bond_rating_sp="Not rated", free_cash_pct_of_budget="8.0",
        pension_funded_ratio_pct=str(BNS), debt_per_capita="2500.0",
        tax_base_non_residential_pct="10.0", effective_tax_rate_pct="0.347",
        median_annual_tax_bill="4858", median_household_income="86674",
        residential_rate_per_1000="3.47",
        district_state_rank="127", district_state_rank_total="351",
        test_scores_math_pct="51.0", graduation_rate_pct="97.4", ap_participation_pct="39.2",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="146.0", property_crime_per_100k="511.0",
        flood_risk_pct="28.0", flood_2050_growth_pts="12.0", wildfire_risk="Low",
        compiler_notes="Most prestigious and expensive Cape Cod address. Lowest tax rate in batch (0.347%) due to very high home values. Highest flood risk on Cape (28% / +12pts 2050). Shares Monomoy Regional (#127, 97.4% grad) with Harwich. Violent crime 146/100k likely reflects small permanent population denominator with seasonal incidents. Bond not rated -- verify EMMA. Pension: Barnstable County Retirement (~66.5% est).",
    ),
    dict(
        town_name="Brewster", state="MA", county="Barnstable", zip_codes="02631",
        population="10318", bond_rating_sp="Not rated", free_cash_pct_of_budget="5.0",
        pension_funded_ratio_pct=str(BNS), debt_per_capita="1500.0",
        tax_base_non_residential_pct="6.0", effective_tax_rate_pct="0.688",
        median_annual_tax_bill="4678", median_household_income="95000",
        residential_rate_per_1000="6.88",
        district_state_rank="108", district_state_rank_total="351",
        test_scores_math_pct="60.0", graduation_rate_pct="96.1", ap_participation_pct="37.6",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="35.0", property_crime_per_100k="340.0",
        flood_risk_pct="10.0", flood_2050_growth_pts="4.5", wildfire_risk="Low",
        compiler_notes="Quietest and safest Upper Cape town. Nauset Regional for 6-12 (#108 of 351, 96.1% grad); Brewster Elementary (K-5) has 60% MCAS math. Lowest crime in batch. Lowest flood risk in batch. Direct Cape Cod National Seashore beach access. Bond not rated -- verify EMMA. Pension: Barnstable County Retirement (~66.5% est). Math_pct reflects K-5 Brewster Elementary MCAS (60%), not Nauset Regional.",
    ),
    dict(
        town_name="Orleans", state="MA", county="Barnstable", zip_codes="02653",
        population="6307", bond_rating_sp="Not rated", free_cash_pct_of_budget="6.0",
        pension_funded_ratio_pct=str(BNS), debt_per_capita="2000.0",
        tax_base_non_residential_pct="12.0", effective_tax_rate_pct="0.624",
        median_annual_tax_bill="4867", median_household_income="90000",
        residential_rate_per_1000="6.24",
        district_state_rank="108", district_state_rank_total="351",
        test_scores_math_pct="44.0", graduation_rate_pct="96.1", ap_participation_pct="37.6",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="153.0", property_crime_per_100k="749.0",
        flood_risk_pct="20.0", flood_2050_growth_pts="9.0", wildfire_risk="Low",
        compiler_notes="Small Outer Cape town at Cape Cod's 'elbow'. Nauset Regional for 6-12 (#108 of 351, 96.1% grad); Orleans Elementary (K-5) is standalone. Violent crime rate (153/100k) elevated -- likely small permanent pop denominator with seasonal incidents (confirmed via areavibes). Bond not rated -- verify EMMA. Pension: Barnstable County Retirement (~66.5% est).",
    ),
    dict(
        town_name="Mashpee", state="MA", county="Barnstable", zip_codes="02649",
        population="15060", bond_rating_sp="Not rated", free_cash_pct_of_budget="4.0",
        pension_funded_ratio_pct=str(BNS), debt_per_capita="2500.0",
        tax_base_non_residential_pct="8.0", effective_tax_rate_pct="0.642",
        median_annual_tax_bill="3595", median_household_income="90000",
        residential_rate_per_1000="6.42",
        district_state_rank="142", district_state_rank_total="351",
        test_scores_math_pct="39.0", graduation_rate_pct="89.7", ap_participation_pct="38.9",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="75.0", property_crime_per_100k="560.0",
        flood_risk_pct="15.0", flood_2050_growth_pts="6.0", wildfire_risk="Low",
        compiler_notes="Fastest-growing Cape Cod town. Mashpee Commons is largest mixed-use development on Cape. Wampanoag Tribal government HQ. Schools #142 of 351 (mashpee district, 89.7% grad). Bond not rated -- verify EMMA. Pension: Barnstable County Retirement (~66.5% est).",
    ),
]

# ---- 2. New HTML objects -----------------------------------------------------
NEW_HTML = [
    '{name:"Barnstable",lat:41.6548,lng:-70.2800,state:"MA",county:"Barnstable",zip:"02601 / 02630 / 02632",pop:48916,bond:null,free_cash:5.0,pension:66.5,debt_pc:3000.0,gfoa:null,tax_non_res:12.0,eff_rate:0.694,med_tax:3990,med_inc:97348,res_rate:6.94,d_rank:221,d_total:351,d_10yr:null,math:28.0,grad:82.9,ap:28.3,transp:"Yes",elec_save:0,water_viol:0,transit:"CCRTA Bus",violent:180.0,prop_crime:1400.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:42.0,unemp:6.5,pov:10.0,flood:18.0,flood50:8.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Cape Cod\'s largest town and county seat. Hyannis serves as the regional hub with ferry service to Nantucket and Martha\'s Vineyard.",glance:"Barnstable is Cape Cod\'s most urban and diverse town, anchored by Hyannis. Schools rank #221 of 351 and crime runs higher than Cape norms — both products of the urban concentration. The lowest home prices on the Cape come with those tradeoffs.",notes:"Bond not rated -- verify EMMA. Pension: Barnstable County Retirement (~66.5% est -- verify PERAC). Crime reflects Hyannis urban core.",med_home_val:580000,commute:28,owner_occ:70.0,vacancy:12.0,med_age:48.0,low_income_pct:38.0,ell_pct:8.0,enrollment_trend:null,sex_off:0.35,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Falmouth",lat:41.5534,lng:-70.6178,state:"MA",county:"Barnstable",zip:"02540 / 02543",pop:32517,bond:null,free_cash:4.0,pension:66.5,debt_pc:2500.0,gfoa:null,tax_non_res:8.0,eff_rate:0.587,med_tax:3874,med_inc:85000,res_rate:5.87,d_rank:144,d_total:351,d_10yr:null,math:43.0,grad:91.0,ap:28.1,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:120.0,prop_crime:900.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:40.0,unemp:5.5,pov:9.5,flood:22.0,flood50:9.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Adjacent to Woods Hole with ferry access to Martha\'s Vineyard. 68 miles of coastline including Old Silver Beach.",glance:"Falmouth is a large, coastal Cape Cod town with solid schools (#144 of 351) and access to the Woods Hole ferry. The highest flood risk in this batch after Chatham is the principal long-term concern for buyers drawn to the waterfront.",notes:"Bond not rated -- verify EMMA. Pension: Barnstable County Retirement (~66.5% est).",med_home_val:660000,commute:30,owner_occ:75.0,vacancy:20.0,med_age:52.0,low_income_pct:22.0,ell_pct:5.0,enrollment_trend:null,sex_off:0.25,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Sandwich",lat:41.7573,lng:-70.4896,state:"MA",county:"Barnstable",zip:"02563",pop:20259,bond:null,free_cash:6.0,pension:66.5,debt_pc:4000.0,gfoa:null,tax_non_res:6.0,eff_rate:1.057,med_tax:6078,med_inc:121038,res_rate:10.57,d_rank:101,d_total:351,d_10yr:null,math:56.0,grad:89.4,ap:37.3,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:55.0,prop_crime:480.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:52.0,unemp:4.5,pov:6.5,flood:12.0,flood50:5.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Strongest school district on Cape Cod (#101 of 351, 56% MCAS math). Low crime and lower flood risk than coastal neighbors.",glance:"Sandwich offers the strongest schools on Cape Cod (#101 of 351) and relatively low crime. The higher tax rate (1.06%) reflects a residential-heavy base — the typical trade-off for inland Cape towns without significant commercial development.",notes:"Bond not rated -- verify EMMA. Pension: Barnstable County Retirement (~66.5% est). Higher tax rate reflects nearly all-residential tax base.",med_home_val:575000,commute:32,owner_occ:85.0,vacancy:9.0,med_age:48.0,low_income_pct:12.0,ell_pct:4.0,enrollment_trend:null,sex_off:0.15,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Yarmouth",lat:41.7076,lng:-70.2286,state:"MA",county:"Barnstable",zip:"02664 / 02673 / 02675",pop:25023,bond:null,free_cash:4.0,pension:66.5,debt_pc:2000.0,gfoa:null,tax_non_res:15.0,eff_rate:0.708,med_tax:3469,med_inc:81985,res_rate:7.08,d_rank:204,d_total:351,d_10yr:null,math:34.0,grad:89.7,ap:33.7,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:150.0,prop_crime:1100.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:36.0,unemp:7.0,pov:11.0,flood:16.0,flood50:7.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Most affordable home prices among mid-Cape towns. Route 28 commercial corridor supports a 15% non-residential tax base.",glance:"Yarmouth has the most affordable home prices among mid-Cape towns and a solid commercial tax base. The Dennis-Yarmouth district ranks #204 of 351 and crime runs above Cape norms — the expected trade-offs at this price point.",notes:"Bond not rated -- verify EMMA. Pension: Barnstable County Retirement (~66.5% est). Shares Dennis-Yarmouth Regional with Dennis.",med_home_val:490000,commute:28,owner_occ:73.0,vacancy:18.0,med_age:55.0,low_income_pct:40.0,ell_pct:12.0,enrollment_trend:null,sex_off:0.30,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Dennis",lat:41.7350,lng:-70.1936,state:"MA",county:"Barnstable",zip:"02638 / 02639 / 02660",pop:14674,bond:null,free_cash:5.0,pension:66.5,debt_pc:1500.0,gfoa:null,tax_non_res:18.0,eff_rate:0.433,med_tax:2252,med_inc:88183,res_rate:4.33,d_rank:204,d_total:351,d_10yr:null,math:34.0,grad:89.7,ap:33.7,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:80.0,prop_crime:800.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:40.0,unemp:6.5,pov:9.0,flood:16.0,flood50:7.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Lowest residential tax rate on Cape Cod (0.43%) and lowest median tax bill in this batch. Highly seasonal character across Dennis Port, South Dennis, and Dennis Village.",glance:"Dennis has the lowest residential tax rate on Cape Cod (0.43%) — a product of very high home values and an 18% commercial base. The Dennis-Yarmouth district (#204 of 351) is below average; the highly seasonal character limits year-round services.",notes:"Bond not rated -- verify EMMA. Pension: Barnstable County Retirement (~66.5% est). Shares Dennis-Yarmouth Regional with Yarmouth. Tax rate is legitimately low -- not a data error.",med_home_val:520000,commute:30,owner_occ:72.0,vacancy:35.0,med_age:60.0,low_income_pct:30.0,ell_pct:5.0,enrollment_trend:null,sex_off:0.22,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Harwich",lat:41.6840,lng:-70.0606,state:"MA",county:"Barnstable",zip:"02645 / 02646",pop:13440,bond:null,free_cash:6.0,pension:66.5,debt_pc:2000.0,gfoa:null,tax_non_res:8.0,eff_rate:0.591,med_tax:3782,med_inc:87948,res_rate:5.91,d_rank:127,d_total:351,d_10yr:null,math:51.0,grad:97.4,ap:39.2,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:45.0,prop_crime:490.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:42.0,unemp:5.0,pov:7.5,flood:13.0,flood50:6.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Among the safest Cape Cod towns by crime rate. Monomoy Regional district (#127 of 351) has a 97.4% graduation rate.",glance:"Harwich combines among the lowest crime rates on the Cape with strong schools through Monomoy Regional (#127 of 351, 97.4% graduation rate). No transit is the main limitation for buyers who commute off-Cape.",notes:"Bond not rated -- verify EMMA. Pension: Barnstable County Retirement (~66.5% est). Shares Monomoy Regional with Chatham.",med_home_val:640000,commute:28,owner_occ:80.0,vacancy:25.0,med_age:58.0,low_income_pct:18.0,ell_pct:4.0,enrollment_trend:null,sex_off:0.20,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Chatham",lat:41.6882,lng:-69.9623,state:"MA",county:"Barnstable",zip:"02633",pop:6594,bond:null,free_cash:8.0,pension:66.5,debt_pc:2500.0,gfoa:null,tax_non_res:10.0,eff_rate:0.347,med_tax:4858,med_inc:86674,res_rate:3.47,d_rank:127,d_total:351,d_10yr:null,math:51.0,grad:97.4,ap:39.2,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:146.0,prop_crime:511.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:55.0,unemp:4.0,pov:6.0,flood:28.0,flood50:12.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"One of Cape Cod\'s most prestigious coastal addresses. Lowest tax rate in the dataset (0.347%). Monomoy Regional district 97.4% graduation rate.",glance:"Chatham is Cape Cod\'s most prestigious coastal address — ultra-low crime, an exceptional 97.4% graduation rate through Monomoy Regional, and the lowest tax rate in the batch. The highest flood risk on the Cape (28% / +12 pts by 2050) is the principal long-term concern.",notes:"Bond not rated -- verify EMMA. Pension: Barnstable County Retirement (~66.5% est). Shares Monomoy Regional with Harwich. Violent crime 146/100k likely inflated by small permanent population denominator vs seasonal incidents.",med_home_val:1400000,commute:28,owner_occ:77.0,vacancy:40.0,med_age:62.0,low_income_pct:12.0,ell_pct:3.0,enrollment_trend:null,sex_off:0.10,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Brewster",lat:41.7651,lng:-70.0826,state:"MA",county:"Barnstable",zip:"02631",pop:10318,bond:null,free_cash:5.0,pension:66.5,debt_pc:1500.0,gfoa:null,tax_non_res:6.0,eff_rate:0.688,med_tax:4678,med_inc:95000,res_rate:6.88,d_rank:108,d_total:351,d_10yr:null,math:60.0,grad:96.1,ap:37.6,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:35.0,prop_crime:340.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:50.0,unemp:4.5,pov:7.0,flood:10.0,flood50:4.5,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Lowest crime rate in this batch. Nauset Regional district (#108 of 351, 96.1% grad rate). Direct Cape Cod National Seashore beach access.",glance:"Brewster is the quietest and safest Upper Cape town — the lowest crime in this batch and strong school access through Nauset Regional (#108 of 351, 96.1% graduation rate). No transit is the key limitation for buyers who work off-Cape.",notes:"Bond not rated -- verify EMMA. Pension: Barnstable County Retirement (~66.5% est). Nauset Regional for 6-12; Brewster Elementary K-5 MCAS math 60%. Uses nauset in DISTRICT_MAP for HS grad/AP data.",med_home_val:680000,commute:32,owner_occ:80.0,vacancy:30.0,med_age:58.0,low_income_pct:12.0,ell_pct:3.0,enrollment_trend:null,sex_off:0.12,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Orleans",lat:41.7893,lng:-69.9876,state:"MA",county:"Barnstable",zip:"02653",pop:6307,bond:null,free_cash:6.0,pension:66.5,debt_pc:2000.0,gfoa:null,tax_non_res:12.0,eff_rate:0.624,med_tax:4867,med_inc:90000,res_rate:6.24,d_rank:108,d_total:351,d_10yr:null,math:44.0,grad:96.1,ap:37.6,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:153.0,prop_crime:749.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:52.0,unemp:5.0,pov:8.0,flood:20.0,flood50:9.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Gateway to the Outer Cape at Cape Cod\'s \'elbow\'. Nauset Regional district (#108 of 351, 96.1% graduation rate). Vibrant year-round town center.",glance:"Orleans is a small Outer Cape town with access to Nauset Regional schools (#108 of 351, 96.1% graduation rate) and a genuine year-round community feel. Crime rates run elevated for a town this size — likely a seasonal population denominator effect.",notes:"Bond not rated -- verify EMMA. Pension: Barnstable County Retirement (~66.5% est). Nauset Regional for 6-12; Orleans Elementary K-5 standalone. Violent crime 153/100k confirmed via areavibes -- small permanent pop inflates rate.",med_home_val:780000,commute:32,owner_occ:77.0,vacancy:35.0,med_age:60.0,low_income_pct:15.0,ell_pct:4.0,enrollment_trend:null,sex_off:0.18,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Mashpee",lat:41.6298,lng:-70.4726,state:"MA",county:"Barnstable",zip:"02649",pop:15060,bond:null,free_cash:4.0,pension:66.5,debt_pc:2500.0,gfoa:null,tax_non_res:8.0,eff_rate:0.642,med_tax:3595,med_inc:90000,res_rate:6.42,d_rank:142,d_total:351,d_10yr:null,math:39.0,grad:89.7,ap:38.9,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:75.0,prop_crime:560.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:38.0,unemp:5.5,pov:8.5,flood:15.0,flood50:6.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Fastest-growing Cape Cod town. Mashpee Commons is the Cape\'s largest mixed-use development. Home to the Wampanoag Tribal government.",glance:"Mashpee is the fastest-growing Cape Cod town, anchored by Mashpee Commons and the Wampanoag Tribal government. Schools are mid-tier (#142 of 351) and the fiscal outlook is solid for a developing community. Moderate flood risk with no transit.",notes:"Bond not rated -- verify EMMA. Pension: Barnstable County Retirement (~66.5% est). Growing population base; newer infrastructure.",med_home_val:560000,commute:30,owner_occ:76.0,vacancy:18.0,med_age:53.0,low_income_pct:25.0,ell_pct:5.0,enrollment_trend:null,sex_off:0.20,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',
]

# ---- Step 1: Add to towns.csv ------------------------------------------------
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

# ---- Step 2: Patch update_all.py --------------------------------------------
print("\nStep 2: Patching update_all.py...")
py_text = PY_FILE.read_text(encoding="utf-8")

# 2a. ZHVI entries -- insert after Tyngsborough line
NEW_ZHVI = '    "Barnstable":580000,"Falmouth":660000,"Sandwich":575000,"Yarmouth":490000,\n    "Dennis":520000,"Harwich":640000,"Chatham":1400000,"Brewster":680000,\n    "Orleans":780000,"Mashpee":560000,\n'
if '"Barnstable"' not in py_text.split("ZHVI")[1].split("}")[0]:
    py_text = re.sub(
        r'("Maynard":\d+,"Tyngsborough":\d+,\n)',
        r'\1' + NEW_ZHVI,
        py_text
    )
    print("  Added ZHVI entries")
else:
    print("  ZHVI entries already present")

# 2b. COUNTY_MAP entries -- insert after Tyngsborough line
NEW_COUNTY = '    "Barnstable":"Barnstable","Falmouth":"Barnstable","Sandwich":"Barnstable",\n    "Yarmouth":"Barnstable","Dennis":"Barnstable","Harwich":"Barnstable",\n    "Chatham":"Barnstable","Brewster":"Barnstable","Orleans":"Barnstable","Mashpee":"Barnstable",\n'
if '"Barnstable":"Barnstable"' not in py_text:
    py_text = re.sub(
        r'("Tyngsborough":"Middlesex",\n)',
        r'\1' + NEW_COUNTY,
        py_text
    )
    print("  Added COUNTY_MAP entries")
else:
    print("  COUNTY_MAP entries already present")

# 2c. DISTRICT_MAP entries for regional districts
DISTRICT_ADD = (
    '    "Yarmouth":              "dennis-yarmouth",\n'
    '    "Dennis":                "dennis-yarmouth",\n'
    '    "Harwich":               "monomoy regional school district",\n'
    '    "Chatham":               "monomoy regional school district",\n'
    '    "Brewster":              "nauset",\n'
    '    "Orleans":               "nauset",\n'
)
if '"Yarmouth":' not in py_text.split("DISTRICT_MAP")[1].split("}")[0]:
    py_text = re.sub(
        r'(    "North Attleborough":   "north attleborough",\n)',
        r'\1' + DISTRICT_ADD,
        py_text
    )
    print("  Added DISTRICT_MAP entries")
else:
    print("  DISTRICT_MAP entries already present")

# 2d. MATH_OVERRIDES for Brewster (K-5 MCAS is more meaningful than Nauset district math)
BREWSTER_OVERRIDE = '    "Brewster":  60.0,   # Brewster Elementary K-5 MCAS math; Nauset Regional HS data used for grad/AP\n'
if '"Brewster"' not in py_text.split("MATH_OVERRIDES")[1].split("}")[0]:
    py_text = re.sub(
        r'("Wrentham": 66\.0.*?\n)',
        r'\1' + BREWSTER_OVERRIDE,
        py_text
    )
    print("  Added Brewster MATH_OVERRIDE")
else:
    print("  Brewster MATH_OVERRIDE already present")

PY_FILE.write_text(py_text, encoding="utf-8")
print("  update_all.py patched")

# ---- Step 3: Add to TOWNS array in civica-v5.html ---------------------------
print("\nStep 3: Patching civica-v5.html...")
html_text = HTML_FILE.read_text(encoding="utf-8")

added_html = 0
for entry in NEW_HTML:
    town_name = entry.split('"name":"')[1].split('"')[0] if '"name":"' in entry else entry.split('name:"')[1].split('"')[0]
    if f'name:"{town_name}"' in html_text or f'"name":"{town_name}"' in html_text:
        print(f"  SKIP (already in HTML): {town_name}")
        continue
    html_text = re.sub(
        r'(\];\s*\nconst PERSONAS)',
        r'  ' + entry + ',\n];\nconst PERSONAS',
        html_text,
        count=1
    )
    added_html += 1
    print(f"  + {town_name}")

HTML_FILE.write_text(html_text, encoding="utf-8")
print(f"  HTML: {added_html} towns added")

# ---- Step 4: Update town count strings --------------------------------------
print("\nStep 4: Updating town count strings...")
new_count = total_towns

for pattern, label in [
    (r'Now live · Massachusetts · \d+ towns and cities', f'Now live · Massachusetts · {new_count} towns and cities'),
    (r'Civica scores \d+ towns and cities', f'Civica scores {new_count} towns and cities'),
]:
    updated = re.sub(pattern, label, html_text)
    if updated != html_text:
        html_text = updated
        print(f"  Updated: {label}")

HTML_FILE.write_text(html_text, encoding="utf-8")

print(f"\nDone. Total towns: {total_towns}")
print("Next step: py scripts/update_all.py")
