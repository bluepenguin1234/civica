"""
Add 20 towns: 10 Pioneer Valley (Hampshire/Hampden) + 10 Plymouth County
Run ONCE, then run:  py scripts/update_all.py

Pioneer Valley: Springfield, Northampton, Amherst, Westfield, Chicopee,
                Holyoke, Agawam, West Springfield, Longmeadow, Easthampton

Plymouth County: Abington, Whitman, Rockland, Middleborough, Wareham,
                 Bridgewater, East Bridgewater, West Bridgewater, Carver, Marion

Census / school / free-cash / debt: pulled from data/bulk/ files
Tax rates: MA DLS FY2025 estimates
ZHVI: Zillow estimates (May 2026)
Pension:
  Springfield / Holyoke / Chicopee = 62.0  (own city systems -- verify PERAC)
  Other Hampden County             = 66.0  (Hampden County Retirement -- verify PERAC)
  Hampshire County                 = 68.0  (Hampshire County Retirement -- verify PERAC)
  Plymouth County                  = 72.0  (Plymouth County Retirement Assoc -- verify PERAC)
School d_rank: SchoolDigger/DESE estimates -- verify annually
Bond ratings: all null -- verify via EMMA (emma.msrb.org)
"""

import csv, re
from pathlib import Path

ROOT      = Path(__file__).parent.parent
CSV_FILE  = ROOT / "data" / "towns.csv"
HTML_FILE = ROOT / "civica-v5.html"
PY_FILE   = ROOT / "scripts" / "update_all.py"

HAMP_CITY = 62.0  # Springfield / Holyoke / Chicopee own systems
HAMP      = 66.0  # Hampden County Retirement
HAM       = 68.0  # Hampshire County Retirement
PCR       = 72.0  # Plymouth County Retirement Association

# ---- 1. New CSV rows ---------------------------------------------------------
NEW_TOWNS = [
    # ── Pioneer Valley (Hampden + Hampshire) ─────────────────────────────────
    dict(
        town_name="Springfield", state="MA", county="Hampden",
        zip_codes="01101;01103;01104;01105;01107;01108;01109",
        population="154751", bond_rating_sp="Not rated", free_cash_pct_of_budget="3.9",
        pension_funded_ratio_pct=str(HAMP_CITY), debt_per_capita="1234.0",
        tax_base_non_residential_pct="28.0", effective_tax_rate_pct="1.969",
        median_annual_tax_bill="4824", median_household_income="51339",
        residential_rate_per_1000="19.69",
        district_state_rank="340", district_state_rank_total="351",
        test_scores_math_pct="21.0", graduation_rate_pct="82.0", ap_participation_pct="10.8",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="900.0", property_crime_per_100k="3000.0",
        flood_risk_pct="8.0", flood_2050_growth_pts="3.0", wildfire_risk="Low",
        compiler_notes="MA's fourth-largest city. Amtrak service (Vermonter, Lake Shore Limited) at Union Station -- not MBTA commuter rail. Schools #340 of 351 (21% MCAS math, 82% grad). High crime. Connecticut River flood risk. Springfield Retirement System (own pension ~62% est -- verify PERAC). Bond not rated -- likely rated; verify EMMA. Lowest home prices in Pioneer Valley.",
    ),
    dict(
        town_name="Northampton", state="MA", county="Hampshire", zip_codes="01060;01061",
        population="28640", bond_rating_sp="Not rated", free_cash_pct_of_budget="6.2",
        pension_funded_ratio_pct=str(HAM), debt_per_capita="1674.0",
        tax_base_non_residential_pct="18.0", effective_tax_rate_pct="1.635",
        median_annual_tax_bill="7685", median_household_income="78467",
        residential_rate_per_1000="16.35",
        district_state_rank="130", district_state_rank_total="351",
        test_scores_math_pct="48.0", graduation_rate_pct="92.4", ap_participation_pct="38.9",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="200.0", property_crime_per_100k="1400.0",
        flood_risk_pct="10.0", flood_2050_growth_pts="4.0", wildfire_risk="Low",
        compiler_notes="Pioneer Valley's most desirable small city. Smith College anchor. Walkable downtown, arts scene. Schools #130 of 351 (48% MCAS math, 92.4% grad). Hampshire County Retirement (~68% est -- verify PERAC). Bond not rated -- verify EMMA. Connecticut River meadow flood risk. No MBTA -- 90 mi west of Boston.",
    ),
    dict(
        town_name="Amherst", state="MA", county="Hampshire", zip_codes="01002;01003",
        population="35472", bond_rating_sp="Not rated", free_cash_pct_of_budget="10.6",
        pension_funded_ratio_pct=str(HAM), debt_per_capita="287.0",
        tax_base_non_residential_pct="15.0", effective_tax_rate_pct="2.487",
        median_annual_tax_bill="13554", median_household_income="65938",
        residential_rate_per_1000="24.87",
        district_state_rank="120", district_state_rank_total="351",
        test_scores_math_pct="55.0", graduation_rate_pct="88.5", ap_participation_pct="35.0",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="180.0", property_crime_per_100k="1200.0",
        flood_risk_pct="5.0", flood_2050_growth_pts="2.0", wildfire_risk="Low",
        compiler_notes="College town (UMass Amherst, Amherst College, Hampshire College). Highest residential tax rate in this batch (24.87) -- reflects residential base and high ed demand on services. Very low debt per capita ($287). Schools #120 of 351 (Amherst-Pelham district est). Hampshire County Retirement (~68% est). Bond not rated -- verify EMMA. grad_rate and ap are estimates -- verify from DESE Amherst-Pelham HS data.",
    ),
    dict(
        town_name="Westfield", state="MA", county="Hampden", zip_codes="01085;01086",
        population="40673", bond_rating_sp="Not rated", free_cash_pct_of_budget="6.5",
        pension_funded_ratio_pct=str(HAMP), debt_per_capita="2392.0",
        tax_base_non_residential_pct="18.0", effective_tax_rate_pct="1.979",
        median_annual_tax_bill="6729", median_household_income="82847",
        residential_rate_per_1000="19.79",
        district_state_rank="215", district_state_rank_total="351",
        test_scores_math_pct="38.0", graduation_rate_pct="91.7", ap_participation_pct="11.9",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="300.0", property_crime_per_100k="1800.0",
        flood_risk_pct="6.0", flood_2050_growth_pts="2.0", wildfire_risk="Low",
        compiler_notes="Affordable small city west of Springfield. Westfield State University campus. Schools #215 of 351 (38% math, 91.7% grad). Negative 10-yr pop growth (-1.3%). Hampden County Retirement (~66% est -- verify PERAC). Bond not rated -- verify EMMA.",
    ),
    dict(
        town_name="Chicopee", state="MA", county="Hampden",
        zip_codes="01013;01020;01021",
        population="55213", bond_rating_sp="Not rated", free_cash_pct_of_budget="6.4",
        pension_funded_ratio_pct=str(HAMP_CITY), debt_per_capita="3262.0",
        tax_base_non_residential_pct="25.0", effective_tax_rate_pct="1.973",
        median_annual_tax_bill="5919", median_household_income="66927",
        residential_rate_per_1000="19.73",
        district_state_rank="285", district_state_rank_total="351",
        test_scores_math_pct="29.0", graduation_rate_pct="88.1", ap_participation_pct="14.7",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="450.0", property_crime_per_100k="2200.0",
        flood_risk_pct="7.0", flood_2050_growth_pts="3.0", wildfire_risk="Low",
        compiler_notes="Springfield suburb with Westover Air Reserve Base (large employer). Schools #285 of 351 (29% math, 88.1% grad). Elevated crime. Chicopee Retirement System (own pension ~62% est -- verify PERAC). Bond not rated -- verify EMMA. Connecticut River flood risk.",
    ),
    dict(
        town_name="Holyoke", state="MA", county="Hampden", zip_codes="01040;01041",
        population="37949", bond_rating_sp="Not rated", free_cash_pct_of_budget="1.5",
        pension_funded_ratio_pct=str(HAMP_CITY), debt_per_capita="2031.0",
        tax_base_non_residential_pct="22.0", effective_tax_rate_pct="2.101",
        median_annual_tax_bill="5568", median_household_income="51892",
        residential_rate_per_1000="21.01",
        district_state_rank="348", district_state_rank_total="351",
        test_scores_math_pct="9.0", graduation_rate_pct="80.8", ap_participation_pct="9.0",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="950.0", property_crime_per_100k="2800.0",
        flood_risk_pct="9.0", flood_2050_growth_pts="4.0", wildfire_risk="Low",
        compiler_notes="Historic paper mill city, now growing data center hub (hydropower advantage). Schools #348 of 351 (9% MCAS math -- near bottom in MA). Highest violent crime in Pioneer Valley. Very low free cash (1.5%) -- fiscal stress flag. Holyoke Retirement System (own pension ~62% est -- verify PERAC). Bond not rated -- verify EMMA. Connecticut River flood risk. Lowest home prices in Pioneer Valley.",
    ),
    dict(
        town_name="Agawam", state="MA", county="Hampden", zip_codes="01001",
        population="28510", bond_rating_sp="Not rated", free_cash_pct_of_budget="13.0",
        pension_funded_ratio_pct=str(HAMP), debt_per_capita="783.0",
        tax_base_non_residential_pct="20.0", effective_tax_rate_pct="1.628",
        median_annual_tax_bill="5861", median_household_income="82359",
        residential_rate_per_1000="16.28",
        district_state_rank="200", district_state_rank_total="351",
        test_scores_math_pct="38.0", graduation_rate_pct="92.5", ap_participation_pct="25.1",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="120.0", property_crime_per_100k="900.0",
        flood_risk_pct="8.0", flood_2050_growth_pts="3.0", wildfire_risk="Low",
        compiler_notes="Best fiscal fundamentals in the Pioneer Valley batch -- exceptional free cash (13%) and very low debt per capita ($783). Six Flags New England is here (commercial tax base). Schools #200 of 351 (38% math, 92.5% grad). Low crime for the region. Connecticut River floodplain. Hampden County Retirement (~66% est). Bond not rated -- verify EMMA.",
    ),
    dict(
        town_name="West Springfield", state="MA", county="Hampden",
        zip_codes="01089;01090",
        population="28635", bond_rating_sp="Not rated", free_cash_pct_of_budget="11.0",
        pension_funded_ratio_pct=str(HAMP), debt_per_capita="2103.0",
        tax_base_non_residential_pct="30.0", effective_tax_rate_pct="1.792",
        median_annual_tax_bill="5645", median_household_income="70401",
        residential_rate_per_1000="17.92",
        district_state_rank="260", district_state_rank_total="351",
        test_scores_math_pct="31.0", graduation_rate_pct="91.4", ap_participation_pct="28.9",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="250.0", property_crime_per_100k="1600.0",
        flood_risk_pct="10.0", flood_2050_growth_pts="5.0", wildfire_risk="Low",
        compiler_notes="Springfield suburb with large Route 5 commercial corridor (30% non-res base, which subsidizes residential rates). Strong free cash (11%). Schools #260 of 351 (31% math). Eastern States Exposition (Big E) fairgrounds here. Highest flood risk in batch due to Connecticut River floodplain. Hampden County Retirement (~66% est). Bond not rated -- verify EMMA.",
    ),
    dict(
        town_name="Longmeadow", state="MA", county="Hampden", zip_codes="01106",
        population="15724", bond_rating_sp="Not rated", free_cash_pct_of_budget="3.9",
        pension_funded_ratio_pct=str(HAMP), debt_per_capita="3895.0",
        tax_base_non_residential_pct="5.0", effective_tax_rate_pct="2.213",
        median_annual_tax_bill="10622", median_household_income="144639",
        residential_rate_per_1000="22.13",
        district_state_rank="70", district_state_rank_total="351",
        test_scores_math_pct="63.0", graduation_rate_pct="96.6", ap_participation_pct="28.3",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="50.0", property_crime_per_100k="600.0",
        flood_risk_pct="12.0", flood_2050_growth_pts="5.0", wildfire_risk="Low",
        compiler_notes="Pioneer Valley's most affluent suburb ($145k median income). Best schools in batch (#70 of 351, 63% MCAS math, 96.6% grad). Very low crime. High tax rate (22.13) reflects nearly all-residential base (5% non-res). High debt per capita ($3,895) and Connecticut River flood risk are the key flags. Hampden County Retirement (~66% est). Bond not rated -- verify EMMA.",
    ),
    dict(
        town_name="Easthampton", state="MA", county="Hampshire", zip_codes="01027",
        population="16103", bond_rating_sp="Not rated", free_cash_pct_of_budget="8.1",
        pension_funded_ratio_pct=str(HAM), debt_per_capita="3697.0",
        tax_base_non_residential_pct="12.0", effective_tax_rate_pct="1.606",
        median_annual_tax_bill="6023", median_household_income="72925",
        residential_rate_per_1000="16.06",
        district_state_rank="200", district_state_rank_total="351",
        test_scores_math_pct="36.0", graduation_rate_pct="93.1", ap_participation_pct="28.5",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="150.0", property_crime_per_100k="900.0",
        flood_risk_pct="5.0", flood_2050_growth_pts="2.0", wildfire_risk="Low",
        compiler_notes="Up-and-coming small city west of Northampton with growing arts and creative economy. Solid schools (#200 of 351, 93.1% grad). Strong free cash (8.1%). High debt per capita ($3,697) is the main fiscal flag. Hampshire County Retirement (~68% est). Bond not rated -- verify EMMA.",
    ),
    # ── Plymouth County ───────────────────────────────────────────────────────
    dict(
        town_name="Abington", state="MA", county="Plymouth", zip_codes="02351",
        population="17008", bond_rating_sp="Not rated", free_cash_pct_of_budget="1.9",
        pension_funded_ratio_pct=str(PCR), debt_per_capita="2942.0",
        tax_base_non_residential_pct="10.0", effective_tax_rate_pct="1.549",
        median_annual_tax_bill="7900", median_household_income="119787",
        residential_rate_per_1000="15.49",
        district_state_rank="195", district_state_rank_total="351",
        test_scores_math_pct="40.0", graduation_rate_pct="91.2", ap_participation_pct="12.1",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="commuter_rail_nearby",
        violent_crime_per_100k="120.0", property_crime_per_100k="850.0",
        flood_risk_pct="5.0", flood_2050_growth_pts="2.0", wildfire_risk="Low",
        compiler_notes="South Shore suburb with above-average incomes ($120k) and strong income growth (+53% over 10 yrs). Very low free cash (1.9%) is a fiscal stress flag. Schools #195 of 351. Whitman MBTA station (Kingston/Plymouth Line) is adjacent. Plymouth County Retirement (~72% est -- verify PERAC). Bond not rated -- verify EMMA.",
    ),
    dict(
        town_name="Whitman", state="MA", county="Plymouth", zip_codes="02382",
        population="15215", bond_rating_sp="Not rated", free_cash_pct_of_budget="7.1",
        pension_funded_ratio_pct=str(PCR), debt_per_capita="855.0",
        tax_base_non_residential_pct="10.0", effective_tax_rate_pct="1.589",
        median_annual_tax_bill="7230", median_household_income="107794",
        residential_rate_per_1000="15.89",
        district_state_rank="225", district_state_rank_total="351",
        test_scores_math_pct="45.0", graduation_rate_pct="88.9", ap_participation_pct="27.3",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="commuter_rail_in_town",
        violent_crime_per_100k="100.0", property_crime_per_100k="750.0",
        flood_risk_pct="5.0", flood_2050_growth_pts="2.0", wildfire_risk="Low",
        compiler_notes="South Shore town directly on Kingston/Plymouth MBTA commuter rail line. Above-average incomes ($108k). Very low debt per capita ($855). Whitman-Hanson district (#225 of 351, 88.9% grad, 45% MCAS math). Plymouth County Retirement (~72% est). Bond not rated -- verify EMMA. DISTRICT_MAP: whitman-hanson.",
    ),
    dict(
        town_name="Rockland", state="MA", county="Plymouth", zip_codes="02370",
        population="17709", bond_rating_sp="Not rated", free_cash_pct_of_budget="6.1",
        pension_funded_ratio_pct=str(PCR), debt_per_capita="2714.0",
        tax_base_non_residential_pct="10.0", effective_tax_rate_pct="1.672",
        median_annual_tax_bill="7775", median_household_income="101475",
        residential_rate_per_1000="16.72",
        district_state_rank="230", district_state_rank_total="351",
        test_scores_math_pct="38.0", graduation_rate_pct="85.3", ap_participation_pct="26.3",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="130.0", property_crime_per_100k="850.0",
        flood_risk_pct="6.0", flood_2050_growth_pts="2.0", wildfire_risk="Low",
        compiler_notes="South Shore suburb with above-average incomes ($101k) and strong income growth (+53% over 10 yrs). Schools #230 of 351 -- graduation rate (85.3%) is the notable weak spot. Plymouth County Retirement (~72% est). Bond not rated -- verify EMMA. No commuter rail in town.",
    ),
    dict(
        town_name="Middleborough", state="MA", county="Plymouth",
        zip_codes="02346;02347",
        population="24360", bond_rating_sp="Not rated", free_cash_pct_of_budget="7.6",
        pension_funded_ratio_pct=str(PCR), debt_per_capita="2298.0",
        tax_base_non_residential_pct="15.0", effective_tax_rate_pct="1.343",
        median_annual_tax_bill="5775", median_household_income="91914",
        residential_rate_per_1000="13.43",
        district_state_rank="225", district_state_rank_total="351",
        test_scores_math_pct="38.0", graduation_rate_pct="88.8", ap_participation_pct="23.9",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="commuter_rail_in_town",
        violent_crime_per_100k="150.0", property_crime_per_100k="1100.0",
        flood_risk_pct="8.0", flood_2050_growth_pts="3.0", wildfire_risk="Low",
        compiler_notes="Fast-growing South Shore town (pop +5%) on Old Colony/Middleborough MBTA Line to South Station. Affordable pricing (~$430k). Solid free cash (7.6%). Schools #225 of 351. Taunton River watershed flood risk. Plymouth County Retirement (~72% est). Bond not rated -- verify EMMA.",
    ),
    dict(
        town_name="Wareham", state="MA", county="Plymouth",
        zip_codes="02538;02571;02576",
        population="23226", bond_rating_sp="Not rated", free_cash_pct_of_budget="8.2",
        pension_funded_ratio_pct=str(PCR), debt_per_capita="1229.0",
        tax_base_non_residential_pct="12.0", effective_tax_rate_pct="1.097",
        median_annual_tax_bill="4059", median_household_income="82741",
        residential_rate_per_1000="10.97",
        district_state_rank="290", district_state_rank_total="351",
        test_scores_math_pct="31.0", graduation_rate_pct="79.4", ap_participation_pct="16.2",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="200.0", property_crime_per_100k="1200.0",
        flood_risk_pct="12.0", flood_2050_growth_pts="5.0", wildfire_risk="Low",
        compiler_notes="Gateway to Cape Cod on Buzzards Bay. Lowest res tax rate in Plymouth batch (10.97) and lowest home prices (~$370k). Schools #290 of 351 (79.4% grad -- below average). Coastal flood risk. Old Colony Line at Middleborough/Lakeville is ~12 mi north. Plymouth County Retirement (~72% est). Bond not rated -- verify EMMA.",
    ),
    dict(
        town_name="Bridgewater", state="MA", county="Plymouth",
        zip_codes="02324;02325",
        population="28669", bond_rating_sp="Not rated", free_cash_pct_of_budget="6.5",
        pension_funded_ratio_pct=str(PCR), debt_per_capita="534.0",
        tax_base_non_residential_pct="10.0", effective_tax_rate_pct="1.567",
        median_annual_tax_bill="7052", median_household_income="112482",
        residential_rate_per_1000="15.67",
        district_state_rank="215", district_state_rank_total="351",
        test_scores_math_pct="34.0", graduation_rate_pct="93.4", ap_participation_pct="25.8",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="commuter_rail_in_town",
        violent_crime_per_100k="150.0", property_crime_per_100k="800.0",
        flood_risk_pct="7.0", flood_2050_growth_pts="3.0", wildfire_risk="Low",
        compiler_notes="South Shore town with MBTA commuter rail on Kingston/Plymouth Line. Very low debt per capita ($534). Bridgewater State University campus. Bridgewater-Raynham district (#215 of 351, 93.4% grad). Plymouth County Retirement (~72% est). Bond not rated -- verify EMMA. DISTRICT_MAP: bridgewater-raynham.",
    ),
    dict(
        town_name="East Bridgewater", state="MA", county="Plymouth", zip_codes="02333",
        population="14420", bond_rating_sp="Not rated", free_cash_pct_of_budget="8.3",
        pension_funded_ratio_pct=str(PCR), debt_per_capita="3265.0",
        tax_base_non_residential_pct="8.0", effective_tax_rate_pct="1.486",
        median_annual_tax_bill="7059", median_household_income="128679",
        residential_rate_per_1000="14.86",
        district_state_rank="145", district_state_rank_total="351",
        test_scores_math_pct="47.0", graduation_rate_pct="96.0", ap_participation_pct="25.7",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="commuter_rail_in_town",
        violent_crime_per_100k="80.0", property_crime_per_100k="600.0",
        flood_risk_pct="6.0", flood_2050_growth_pts="2.0", wildfire_risk="Low",
        compiler_notes="Underrated South Shore suburb with strong schools (#145 of 351, 96% grad, 47% MCAS math) and MBTA commuter rail on Kingston/Plymouth Line. Above-average incomes ($129k). High debt per capita ($3,265) is the main fiscal flag. Plymouth County Retirement (~72% est). Bond not rated -- verify EMMA.",
    ),
    dict(
        town_name="West Bridgewater", state="MA", county="Plymouth", zip_codes="02379",
        population="7682", bond_rating_sp="Not rated", free_cash_pct_of_budget="4.1",
        pension_funded_ratio_pct=str(PCR), debt_per_capita="4705.0",
        tax_base_non_residential_pct="8.0", effective_tax_rate_pct="1.821",
        median_annual_tax_bill="8832", median_household_income="124483",
        residential_rate_per_1000="18.21",
        district_state_rank="210", district_state_rank_total="351",
        test_scores_math_pct="39.0", graduation_rate_pct="95.0", ap_participation_pct="20.7",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="commuter_rail_nearby",
        violent_crime_per_100k="60.0", property_crime_per_100k="500.0",
        flood_risk_pct="5.0", flood_2050_growth_pts="2.0", wildfire_risk="Low",
        compiler_notes="Small, high-income South Shore town (pop +11% over 10 yrs, $124k median income). Strong schools (#210 of 351, 95% grad). Highest residential tax rate in Plymouth batch (18.21) and very high debt per capita ($4,705) are the key fiscal flags. Bridgewater MBTA station is nearby. Plymouth County Retirement (~72% est). Bond not rated -- verify EMMA.",
    ),
    dict(
        town_name="Carver", state="MA", county="Plymouth", zip_codes="02330",
        population="11645", bond_rating_sp="Not rated", free_cash_pct_of_budget="6.4",
        pension_funded_ratio_pct=str(PCR), debt_per_capita="3598.0",
        tax_base_non_residential_pct="8.0", effective_tax_rate_pct="1.528",
        median_annual_tax_bill="6112", median_household_income="78955",
        residential_rate_per_1000="15.28",
        district_state_rank="210", district_state_rank_total="351",
        test_scores_math_pct="36.0", graduation_rate_pct="95.8", ap_participation_pct="22.4",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="70.0", property_crime_per_100k="550.0",
        flood_risk_pct="5.0", flood_2050_growth_pts="2.0", wildfire_risk="Low",
        compiler_notes="Rural Plymouth County town -- cranberry capital of the world. Very low unemployment (2.9%) and low crime. Strong graduation rate (95.8%). High debt per capita ($3,598) is a flag. Flat population growth (+1.3% over 10 yrs). No transit. Plymouth County Retirement (~72% est). Bond not rated -- verify EMMA.",
    ),
    dict(
        town_name="Marion", state="MA", county="Plymouth", zip_codes="02738",
        population="5312", bond_rating_sp="Not rated", free_cash_pct_of_budget="14.6",
        pension_funded_ratio_pct=str(PCR), debt_per_capita="4807.0",
        tax_base_non_residential_pct="8.0", effective_tax_rate_pct="1.148",
        median_annual_tax_bill="7462", median_household_income="120227",
        residential_rate_per_1000="11.48",
        district_state_rank="115", district_state_rank_total="351",
        test_scores_math_pct="55.0", graduation_rate_pct="96.1", ap_participation_pct="30.8",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="40.0", property_crime_per_100k="400.0",
        flood_risk_pct="15.0", flood_2050_growth_pts="7.0", wildfire_risk="Low",
        compiler_notes="Small coastal town on Buzzards Bay. Exceptional free cash (14.6%) and very low crime. Old Rochester Regional HS (#115 of 351, 96.1% grad, 30.8% AP). Math_pct=55 is Marion elementary K-6 MCAS; MATH_OVERRIDE set. Very high debt per capita ($4,807) and coastal flood risk (15%) are the key flags. Plymouth County Retirement (~72% est). Bond not rated -- verify EMMA. DISTRICT_MAP: old rochester.",
    ),
]

# ---- 2. New HTML objects -----------------------------------------------------
NEW_HTML = [
    # Pioneer Valley
    '{name:"Springfield",lat:42.1015,lng:-72.5898,state:"MA",county:"Hampden",zip:"01103 / 01104 / 01105 / 01108",pop:154751,bond:null,free_cash:3.9,pension:62.0,debt_pc:1234.0,gfoa:null,tax_non_res:28.0,eff_rate:1.969,med_tax:4824,med_inc:51339,res_rate:19.69,d_rank:340,d_total:351,d_10yr:null,math:21.0,grad:82.0,ap:10.8,transp:"Yes",elec_save:0,water_viol:0,transit:"None — Amtrak intercity at Union Station",violent:900.0,prop_crime:3000.0,crime5yr:null,inc10yr:49.6,pop10yr:0.9,bach:19.7,unemp:8.2,pov:25.3,flood:8.0,flood50:3.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"MA\'s fourth-largest city with Amtrak service and the lowest home prices in the Pioneer Valley. Schools #340 of 351 and the highest violent crime in this batch are the defining trade-offs.",glance:"Springfield is Massachusetts\' fourth-largest city with Amtrak intercity service and the lowest home prices in the Pioneer Valley (~$245k). Schools rank #340 of 351 and crime is among the highest in MA — the expected profile for a mid-sized city with structural economic challenges.",notes:"Springfield Retirement System (own pension ~62% est -- verify PERAC). Bond not rated -- likely rated; verify EMMA. Amtrak only -- not MBTA commuter rail.",med_home_val:245000,commute:25,owner_occ:42.0,vacancy:10.0,med_age:34.0,low_income_pct:75.0,ell_pct:20.0,enrollment_trend:null,sex_off:0.65,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Northampton",lat:42.3251,lng:-72.6412,state:"MA",county:"Hampshire",zip:"01060",pop:28640,bond:null,free_cash:6.2,pension:68.0,debt_pc:1674.0,gfoa:null,tax_non_res:18.0,eff_rate:1.635,med_tax:7685,med_inc:78467,res_rate:16.35,d_rank:130,d_total:351,d_10yr:null,math:48.0,grad:92.4,ap:38.9,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:200.0,prop_crime:1400.0,crime5yr:null,inc10yr:35.3,pop10yr:0.2,bach:61.3,unemp:5.3,pov:12.5,flood:10.0,flood50:4.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Pioneer Valley\'s most desirable small city. Smith College anchor, walkable downtown, strong schools (#130 of 351, 92.4% graduation). Connecticut River meadow flood risk.",glance:"Northampton is the Pioneer Valley\'s most desirable small city — walkable downtown, strong schools (#130 of 351, 92.4% graduation), and a vibrant arts scene anchored by Smith College. The high residential tax rate (1.64%) and 90-mile distance from Boston are the main limitations for commuters.",notes:"Hampshire County Retirement (~68% est -- verify PERAC). Bond not rated -- verify EMMA.",med_home_val:470000,commute:22,owner_occ:52.0,vacancy:6.0,med_age:38.0,low_income_pct:28.0,ell_pct:8.0,enrollment_trend:null,sex_off:0.35,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Amherst",lat:42.3732,lng:-72.5199,state:"MA",county:"Hampshire",zip:"01002 / 01003",pop:35472,bond:null,free_cash:10.6,pension:68.0,debt_pc:287.0,gfoa:null,tax_non_res:15.0,eff_rate:2.487,med_tax:13554,med_inc:65938,res_rate:24.87,d_rank:120,d_total:351,d_10yr:null,math:55.0,grad:88.5,ap:35.0,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:180.0,prop_crime:1200.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:73.8,unemp:9.0,pov:24.1,flood:5.0,flood50:2.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:4,conf:"medium",standout:"College town (UMass Amherst, Amherst College, Hampshire College) with top-quartile schools and the highest residential tax rate in this batch (24.87). Very low debt per capita ($287).",glance:"Amherst is a classic New England college town anchoring UMass Amherst, Amherst College, and Hampshire College, with strong schools and exceptional educational attainment (74% bachelor\'s degree). The highest residential tax rate in this batch (2.49%) and 90-mile distance from Boston are the defining limitations for buyers.",notes:"Hampshire County Retirement (~68% est). Bond not rated -- verify EMMA. grad/ap are estimates -- verify DESE Amherst-Pelham HS. Inc10yr/pop10yr not in bulk data.",med_home_val:545000,commute:22,owner_occ:38.0,vacancy:8.0,med_age:24.0,low_income_pct:30.0,ell_pct:10.0,enrollment_trend:null,sex_off:0.25,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Westfield",lat:42.1251,lng:-72.7498,state:"MA",county:"Hampden",zip:"01085 / 01086",pop:40673,bond:null,free_cash:6.5,pension:66.0,debt_pc:2392.0,gfoa:null,tax_non_res:18.0,eff_rate:1.979,med_tax:6729,med_inc:82847,res_rate:19.79,d_rank:215,d_total:351,d_10yr:null,math:38.0,grad:91.7,ap:11.9,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:300.0,prop_crime:1800.0,crime5yr:null,inc10yr:39.0,pop10yr:-1.3,bach:32.6,unemp:4.0,pov:11.0,flood:6.0,flood50:2.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Affordable small city west of Springfield with Westfield State University. Schools #215 of 351 (91.7% graduation). Negative 10-yr population growth (-1.3%).",glance:"Westfield is an affordable small city west of Springfield with solid schools (#215 of 351, 91.7% graduation) and a stable economy anchored by Westfield State University and manufacturing. Negative 10-year population growth (-1.3%) and no commuter rail reflect its regional character.",notes:"Hampden County Retirement (~66% est -- verify PERAC). Bond not rated -- verify EMMA.",med_home_val:340000,commute:24,owner_occ:60.0,vacancy:6.5,med_age:40.0,low_income_pct:32.0,ell_pct:8.0,enrollment_trend:null,sex_off:0.40,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Chicopee",lat:42.1487,lng:-72.6079,state:"MA",county:"Hampden",zip:"01013 / 01020 / 01021",pop:55213,bond:null,free_cash:6.4,pension:62.0,debt_pc:3262.0,gfoa:null,tax_non_res:25.0,eff_rate:1.973,med_tax:5919,med_inc:66927,res_rate:19.73,d_rank:285,d_total:351,d_10yr:null,math:29.0,grad:88.1,ap:14.7,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:450.0,prop_crime:2200.0,crime5yr:null,inc10yr:43.3,pop10yr:-0.5,bach:23.2,unemp:6.5,pov:15.2,flood:7.0,flood50:3.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Springfield suburb with Westover Air Reserve Base as a major employer. Schools #285 of 351. Elevated crime and Connecticut River flood risk.",glance:"Chicopee is an affordable Springfield suburb anchored by Westover Air Reserve Base, with improving income fundamentals (+43% over 10 years). Schools rank #285 of 351 and crime is elevated — the standard trade-offs for a working-class city at this price point.",notes:"Chicopee Retirement System (own pension ~62% est -- verify PERAC). Bond not rated -- verify EMMA.",med_home_val:300000,commute:22,owner_occ:52.0,vacancy:7.0,med_age:40.0,low_income_pct:50.0,ell_pct:15.0,enrollment_trend:null,sex_off:0.50,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Holyoke",lat:42.2043,lng:-72.6162,state:"MA",county:"Hampden",zip:"01040 / 01041",pop:37949,bond:null,free_cash:1.5,pension:62.0,debt_pc:2031.0,gfoa:null,tax_non_res:22.0,eff_rate:2.101,med_tax:5568,med_inc:51892,res_rate:21.01,d_rank:348,d_total:351,d_10yr:null,math:9.0,grad:80.8,ap:9.0,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:950.0,prop_crime:2800.0,crime5yr:null,inc10yr:64.1,pop10yr:-5.2,bach:24.3,unemp:6.9,pov:23.7,flood:9.0,flood50:4.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Historic paper mill city, now a growing data center hub powered by Connecticut River hydropower. Schools #348 of 351 (9% MCAS math) and the highest violent crime in the Pioneer Valley batch are the defining trade-offs.",glance:"Holyoke is a historic mill city with a growing data center economy powered by Connecticut River hydropower. Schools rank #348 of 351 and crime is among the highest in Massachusetts — the very low home prices (~$265k) and strong income growth (+64% over 10 years) are the signals to watch.",notes:"Holyoke Retirement System (own pension ~62% est -- verify PERAC). Very low free cash (1.5%) -- fiscal stress flag. Bond not rated -- verify EMMA. Negative pop growth (-5.2%).",med_home_val:265000,commute:22,owner_occ:38.0,vacancy:12.0,med_age:34.0,low_income_pct:72.0,ell_pct:25.0,enrollment_trend:null,sex_off:0.80,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Agawam",lat:42.0701,lng:-72.6223,state:"MA",county:"Hampden",zip:"01001",pop:28510,bond:null,free_cash:13.0,pension:66.0,debt_pc:783.0,gfoa:null,tax_non_res:20.0,eff_rate:1.628,med_tax:5861,med_inc:82359,res_rate:16.28,d_rank:200,d_total:351,d_10yr:null,math:38.0,grad:92.5,ap:25.1,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:120.0,prop_crime:900.0,crime5yr:null,inc10yr:29.5,pop10yr:-0.2,bach:34.9,unemp:4.5,pov:6.9,flood:8.0,flood50:3.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Best fiscal fundamentals in the Pioneer Valley batch — exceptional free cash (13%) and very low debt ($783/capita). Six Flags New England\'s commercial tax base helps subsidize residential rates.",glance:"Agawam has the strongest fiscal fundamentals in the Pioneer Valley batch — exceptional free cash (13%) and very low debt per capita ($783), aided by Six Flags New England\'s commercial tax base. Schools rank #200 of 351 and Connecticut River flood risk affects low-lying properties.",notes:"Hampden County Retirement (~66% est -- verify PERAC). Bond not rated -- verify EMMA.",med_home_val:360000,commute:23,owner_occ:70.0,vacancy:5.0,med_age:44.0,low_income_pct:22.0,ell_pct:5.0,enrollment_trend:null,sex_off:0.28,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"West Springfield",lat:42.1015,lng:-72.6384,state:"MA",county:"Hampden",zip:"01089 / 01090",pop:28635,bond:null,free_cash:11.0,pension:66.0,debt_pc:2103.0,gfoa:null,tax_non_res:30.0,eff_rate:1.792,med_tax:5645,med_inc:70401,res_rate:17.92,d_rank:260,d_total:351,d_10yr:null,math:31.0,grad:91.4,ap:28.9,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:250.0,prop_crime:1600.0,crime5yr:null,inc10yr:30.1,pop10yr:0.5,bach:34.9,unemp:5.6,pov:10.4,flood:10.0,flood50:5.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Springfield suburb with a large Route 5 commercial corridor (30% non-res base) and exceptional free cash (11%). Eastern States Exposition (Big E) is located here.",glance:"West Springfield is an affordable Springfield suburb with a large commercial corridor that keeps residential taxes lower than comparable Pioneer Valley towns, and strong free cash (11%). Schools rank #260 of 351 and Connecticut River flood risk is the principal long-term concern.",notes:"Hampden County Retirement (~66% est -- verify PERAC). Bond not rated -- verify EMMA. 30% non-res base is unusually high.",med_home_val:315000,commute:22,owner_occ:60.0,vacancy:6.0,med_age:42.0,low_income_pct:30.0,ell_pct:10.0,enrollment_trend:null,sex_off:0.38,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Longmeadow",lat:42.0418,lng:-72.5831,state:"MA",county:"Hampden",zip:"01106",pop:15724,bond:null,free_cash:3.9,pension:66.0,debt_pc:3895.0,gfoa:null,tax_non_res:5.0,eff_rate:2.213,med_tax:10622,med_inc:144639,res_rate:22.13,d_rank:70,d_total:351,d_10yr:null,math:63.0,grad:96.6,ap:28.3,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:50.0,prop_crime:600.0,crime5yr:null,inc10yr:36.2,pop10yr:-0.7,bach:66.1,unemp:6.3,pov:3.9,flood:12.0,flood50:5.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Pioneer Valley\'s most affluent suburb ($145k median income) with the strongest schools in this batch (#70 of 351, 63% MCAS math, 96.6% graduation). Very low crime.",glance:"Longmeadow is the Pioneer Valley\'s most affluent suburb — top-tier schools (#70 of 351, 63% MCAS math, 96.6% graduation), a $145k median income, and very low crime. The high residential tax rate (2.21%) and Connecticut River flood risk are the key trade-offs; there is no commuter rail to Boston.",notes:"Hampden County Retirement (~66% est -- verify PERAC). Bond not rated -- verify EMMA. Near-fully residential base (5% non-res) drives high tax rate.",med_home_val:480000,commute:22,owner_occ:80.0,vacancy:3.5,med_age:48.0,low_income_pct:8.0,ell_pct:3.0,enrollment_trend:null,sex_off:0.15,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Easthampton",lat:42.2668,lng:-72.6690,state:"MA",county:"Hampshire",zip:"01027",pop:16103,bond:null,free_cash:8.1,pension:68.0,debt_pc:3697.0,gfoa:null,tax_non_res:12.0,eff_rate:1.606,med_tax:6023,med_inc:72925,res_rate:16.06,d_rank:200,d_total:351,d_10yr:null,math:36.0,grad:93.1,ap:28.5,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:150.0,prop_crime:900.0,crime5yr:null,inc10yr:26.6,pop10yr:0.4,bach:41.0,unemp:5.2,pov:8.9,flood:5.0,flood50:2.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Up-and-coming small city west of Northampton with growing arts and creative economy. Solid free cash (8.1%) and schools #200 of 351 (93.1% graduation). High debt per capita is the main fiscal flag.",glance:"Easthampton is an up-and-coming small city adjacent to Northampton with a growing arts and creative economy, solid free cash (8.1%), and decent schools (#200 of 351, 93.1% graduation). High debt per capita ($3,697) and the 90-mile distance from Boston are the principal limitations.",notes:"Hampshire County Retirement (~68% est -- verify PERAC). Bond not rated -- verify EMMA.",med_home_val:375000,commute:22,owner_occ:60.0,vacancy:5.5,med_age:42.0,low_income_pct:20.0,ell_pct:5.0,enrollment_trend:null,sex_off:0.28,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    # Plymouth County
    '{name:"Abington",lat:42.1245,lng:-70.9455,state:"MA",county:"Plymouth",zip:"02351",pop:17008,bond:null,free_cash:1.9,pension:72.0,debt_pc:2942.0,gfoa:null,tax_non_res:10.0,eff_rate:1.549,med_tax:7900,med_inc:119787,res_rate:15.49,d_rank:195,d_total:351,d_10yr:null,math:40.0,grad:91.2,ap:12.1,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (nearby) — Kingston/Plymouth Line at Whitman (adjacent)",violent:120.0,prop_crime:850.0,crime5yr:null,inc10yr:52.8,pop10yr:6.2,bach:39.8,unemp:5.2,pov:5.7,flood:5.0,flood50:2.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"South Shore suburb with above-average incomes ($120k) and strong income growth (+53% over 10 yrs). Very low free cash (1.9%) is the key fiscal flag. Whitman MBTA station is in the adjacent town.",glance:"Abington is a South Shore suburb with above-average incomes ($120k median) and strong income growth (+53% over 10 years). The very low free cash (1.9%) is the key fiscal caution; the Kingston/Plymouth commuter rail line at adjacent Whitman provides Boston access.",notes:"Plymouth County Retirement (~72% est -- verify PERAC). Bond not rated -- verify EMMA.",med_home_val:510000,commute:34,owner_occ:70.0,vacancy:4.0,med_age:41.0,low_income_pct:18.0,ell_pct:4.0,enrollment_trend:null,sex_off:0.28,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Whitman",lat:42.0815,lng:-70.9312,state:"MA",county:"Plymouth",zip:"02382",pop:15215,bond:null,free_cash:7.1,pension:72.0,debt_pc:855.0,gfoa:null,tax_non_res:10.0,eff_rate:1.589,med_tax:7230,med_inc:107794,res_rate:15.89,d_rank:225,d_total:351,d_10yr:null,math:45.0,grad:88.9,ap:27.3,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town) — Kingston/Plymouth Line",violent:100.0,prop_crime:750.0,crime5yr:null,inc10yr:48.8,pop10yr:4.4,bach:29.2,unemp:4.6,pov:7.5,flood:5.0,flood50:2.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"South Shore town directly on Kingston/Plymouth MBTA commuter rail line. Above-average incomes ($108k) and very low debt per capita ($855). Whitman-Hanson schools (#225 of 351, 88.9% grad).",glance:"Whitman is a South Shore town directly on the Kingston/Plymouth MBTA commuter rail line with above-average incomes ($108k median) and very low debt. Schools rank #225 of 351 via Whitman-Hanson district (88.9% graduation) — solid but not a differentiator.",notes:"Plymouth County Retirement (~72% est -- verify PERAC). Bond not rated -- verify EMMA. DISTRICT_MAP: whitman-hanson.",med_home_val:455000,commute:38,owner_occ:72.0,vacancy:4.0,med_age:41.0,low_income_pct:20.0,ell_pct:4.0,enrollment_trend:null,sex_off:0.25,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Rockland",lat:42.1312,lng:-70.9162,state:"MA",county:"Plymouth",zip:"02370",pop:17709,bond:null,free_cash:6.1,pension:72.0,debt_pc:2714.0,gfoa:null,tax_non_res:10.0,eff_rate:1.672,med_tax:7775,med_inc:101475,res_rate:16.72,d_rank:230,d_total:351,d_10yr:null,math:38.0,grad:85.3,ap:26.3,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:130.0,prop_crime:850.0,crime5yr:null,inc10yr:53.0,pop10yr:0.9,bach:34.3,unemp:3.9,pov:7.5,flood:6.0,flood50:2.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"South Shore suburb with above-average incomes ($101k) and strong income growth (+53% over 10 yrs). Graduation rate (85.3%) is the weak spot relative to South Shore peers.",glance:"Rockland is a South Shore suburb with above-average incomes ($101k median) and strong income growth (+53% over 10 years). The graduation rate (85.3%) is notably below South Shore norms — the key caveat for family buyers. No commuter rail in town.",notes:"Plymouth County Retirement (~72% est -- verify PERAC). Bond not rated -- verify EMMA.",med_home_val:465000,commute:34,owner_occ:68.0,vacancy:4.5,med_age:41.0,low_income_pct:22.0,ell_pct:5.0,enrollment_trend:null,sex_off:0.28,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Middleborough",lat:41.8945,lng:-70.8978,state:"MA",county:"Plymouth",zip:"02346 / 02347",pop:24360,bond:null,free_cash:7.6,pension:72.0,debt_pc:2298.0,gfoa:null,tax_non_res:15.0,eff_rate:1.343,med_tax:5775,med_inc:91914,res_rate:13.43,d_rank:225,d_total:351,d_10yr:null,math:38.0,grad:88.8,ap:23.9,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town) — Old Colony/Middleborough Line",violent:150.0,prop_crime:1100.0,crime5yr:null,inc10yr:18.4,pop10yr:4.8,bach:30.3,unemp:4.8,pov:7.7,flood:8.0,flood50:3.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Growing South Shore town on Old Colony MBTA commuter rail line. Affordable pricing (~$430k) and solid free cash (7.6%). Schools #225 of 351 (88.8% grad).",glance:"Middleborough is a growing South Shore town on the Old Colony MBTA commuter rail line with affordable pricing (~$430k) and solid fiscal reserves (7.6% free cash). Schools rank #225 of 351 and the relatively low 10-year income growth (+18%) is a cautionary note compared to South Shore peers.",notes:"Plymouth County Retirement (~72% est -- verify PERAC). Bond not rated -- verify EMMA.",med_home_val:430000,commute:42,owner_occ:72.0,vacancy:5.0,med_age:41.0,low_income_pct:22.0,ell_pct:5.0,enrollment_trend:null,sex_off:0.30,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Wareham",lat:41.7626,lng:-70.7134,state:"MA",county:"Plymouth",zip:"02538 / 02571 / 02576",pop:23226,bond:null,free_cash:8.2,pension:72.0,debt_pc:1229.0,gfoa:null,tax_non_res:12.0,eff_rate:1.097,med_tax:4059,med_inc:82741,res_rate:10.97,d_rank:290,d_total:351,d_10yr:null,math:31.0,grad:79.4,ap:16.2,transp:"Yes",elec_save:0,water_viol:0,transit:"None (Old Colony at Middleborough 12 mi north)",violent:200.0,prop_crime:1200.0,crime5yr:null,inc10yr:39.8,pop10yr:5.2,bach:27.8,unemp:6.0,pov:7.2,flood:12.0,flood50:5.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Gateway to Cape Cod on Buzzards Bay with the lowest residential tax rate in this batch (1.10%) and most affordable home prices (~$370k). Schools #290 of 351 (79.4% grad) and coastal flood risk are the main trade-offs.",glance:"Wareham is the gateway to Cape Cod on Buzzards Bay with the lowest residential tax rate in the Plymouth batch (1.10%) and the most affordable home prices (~$370k). Schools rank #290 of 351 (79.4% graduation rate) and coastal flood risk are the principal trade-offs.",notes:"Plymouth County Retirement (~72% est -- verify PERAC). Bond not rated -- verify EMMA. Seasonal character affects some services.",med_home_val:370000,commute:38,owner_occ:68.0,vacancy:12.0,med_age:45.0,low_income_pct:25.0,ell_pct:5.0,enrollment_trend:null,sex_off:0.35,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Bridgewater",lat:41.9901,lng:-70.9748,state:"MA",county:"Plymouth",zip:"02324 / 02325",pop:28669,bond:null,free_cash:6.5,pension:72.0,debt_pc:534.0,gfoa:null,tax_non_res:10.0,eff_rate:1.567,med_tax:7052,med_inc:112482,res_rate:15.67,d_rank:215,d_total:351,d_10yr:null,math:34.0,grad:93.4,ap:25.8,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town) — Kingston/Plymouth Line",violent:150.0,prop_crime:800.0,crime5yr:null,inc10yr:null,pop10yr:null,bach:39.7,unemp:5.5,pov:4.9,flood:7.0,flood50:3.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:4,conf:"medium",standout:"South Shore town with MBTA commuter rail, very low debt per capita ($534), and Bridgewater State University. Bridgewater-Raynham district (#215 of 351, 93.4% grad).",glance:"Bridgewater is a South Shore town with MBTA commuter rail access, very low debt per capita ($534), and Bridgewater State University. Solid schools via Bridgewater-Raynham district (#215 of 351, 93.4% graduation) make it one of the better-value picks in Plymouth County.",notes:"Plymouth County Retirement (~72% est -- verify PERAC). Bond not rated -- verify EMMA. DISTRICT_MAP: bridgewater-raynham. inc10yr/pop10yr not in bulk data.",med_home_val:450000,commute:42,owner_occ:70.0,vacancy:5.0,med_age:36.0,low_income_pct:18.0,ell_pct:5.0,enrollment_trend:null,sex_off:0.30,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"East Bridgewater",lat:42.0312,lng:-70.9398,state:"MA",county:"Plymouth",zip:"02333",pop:14420,bond:null,free_cash:8.3,pension:72.0,debt_pc:3265.0,gfoa:null,tax_non_res:8.0,eff_rate:1.486,med_tax:7059,med_inc:128679,res_rate:14.86,d_rank:145,d_total:351,d_10yr:null,math:47.0,grad:96.0,ap:25.7,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town) — Kingston/Plymouth Line",violent:80.0,prop_crime:600.0,crime5yr:null,inc10yr:49.8,pop10yr:3.8,bach:34.3,unemp:4.6,pov:4.1,flood:6.0,flood50:2.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Underrated South Shore suburb with strong schools (#145 of 351, 96% graduation), MBTA commuter rail, and above-average incomes ($129k). High debt per capita ($3,265) is the main fiscal flag.",glance:"East Bridgewater is an underrated South Shore suburb with strong schools (#145 of 351, 96% graduation), MBTA commuter rail access, and above-average incomes ($129k median). High debt per capita ($3,265) is the key fiscal flag for buyers who care about long-term municipal health.",notes:"Plymouth County Retirement (~72% est -- verify PERAC). Bond not rated -- verify EMMA.",med_home_val:475000,commute:42,owner_occ:78.0,vacancy:3.5,med_age:41.0,low_income_pct:12.0,ell_pct:3.0,enrollment_trend:null,sex_off:0.20,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"West Bridgewater",lat:42.0168,lng:-71.0073,state:"MA",county:"Plymouth",zip:"02379",pop:7682,bond:null,free_cash:4.1,pension:72.0,debt_pc:4705.0,gfoa:null,tax_non_res:8.0,eff_rate:1.821,med_tax:8832,med_inc:124483,res_rate:18.21,d_rank:210,d_total:351,d_10yr:null,math:39.0,grad:95.0,ap:20.7,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (nearby) — Kingston/Plymouth Line at Bridgewater (3 mi)",violent:60.0,prop_crime:500.0,crime5yr:null,inc10yr:54.9,pop10yr:10.9,bach:42.6,unemp:4.6,pov:4.6,flood:5.0,flood50:2.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Small, fast-growing South Shore town ($124k median income, pop +11%). Strong schools (#210 of 351, 95% graduation). Highest residential tax rate in Plymouth batch (18.21) and very high debt per capita ($4,705).",glance:"West Bridgewater is a small, fast-growing South Shore town with high incomes ($124k median), strong schools (#210 of 351, 95% graduation), and low crime. The highest residential tax rate in the Plymouth batch (1.82%) and very high debt per capita ($4,705) are the principal trade-offs.",notes:"Plymouth County Retirement (~72% est -- verify PERAC). Bond not rated -- verify EMMA.",med_home_val:485000,commute:40,owner_occ:82.0,vacancy:3.0,med_age:43.0,low_income_pct:8.0,ell_pct:3.0,enrollment_trend:null,sex_off:0.18,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Carver",lat:41.8751,lng:-70.7662,state:"MA",county:"Plymouth",zip:"02330",pop:11645,bond:null,free_cash:6.4,pension:72.0,debt_pc:3598.0,gfoa:null,tax_non_res:8.0,eff_rate:1.528,med_tax:6112,med_inc:78955,res_rate:15.28,d_rank:210,d_total:351,d_10yr:null,math:36.0,grad:95.8,ap:22.4,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:70.0,prop_crime:550.0,crime5yr:null,inc10yr:9.4,pop10yr:1.3,bach:27.2,unemp:2.9,pov:6.6,flood:5.0,flood50:2.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Rural Plymouth County town — cranberry capital of the world. Very low unemployment (2.9%), low crime, and strong graduation rate (95.8%). Low income growth (+9%) and flat population growth are the cautionary signals.",glance:"Carver is a rural Plymouth County town with very low unemployment (2.9%), low crime, and a strong 95.8% graduation rate. The low 10-year income growth (+9% — well below state average) and high debt per capita ($3,598) are the cautions for buyers seeking long-term appreciation.",notes:"Plymouth County Retirement (~72% est -- verify PERAC). Bond not rated -- verify EMMA.",med_home_val:400000,commute:38,owner_occ:80.0,vacancy:5.0,med_age:44.0,low_income_pct:18.0,ell_pct:3.0,enrollment_trend:null,sex_off:0.22,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Marion",lat:41.7001,lng:-70.7584,state:"MA",county:"Plymouth",zip:"02738",pop:5312,bond:null,free_cash:14.6,pension:72.0,debt_pc:4807.0,gfoa:null,tax_non_res:8.0,eff_rate:1.148,med_tax:7462,med_inc:120227,res_rate:11.48,d_rank:115,d_total:351,d_10yr:null,math:55.0,grad:96.1,ap:30.8,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:40.0,prop_crime:400.0,crime5yr:null,inc10yr:49.4,pop10yr:8.1,bach:45.2,unemp:6.4,pov:5.9,flood:15.0,flood50:7.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Small coastal town on Buzzards Bay with exceptional free cash (14.6%), strong Old Rochester Regional schools (#115 of 351, 96.1% grad), and very low crime. Coastal flood risk (15%) and high debt per capita ($4,807) are the key flags.",glance:"Marion is a small coastal Buzzards Bay town with exceptional free cash (14.6%), strong schools through Old Rochester Regional (#115 of 351, 96.1% graduation), and very low crime. Coastal flood risk (15% / +7 pts by 2050) and high debt per capita ($4,807) are the two flags buyers should scrutinize.",notes:"Plymouth County Retirement (~72% est -- verify PERAC). Bond not rated -- verify EMMA. math=55 is Marion Elementary K-6 MCAS; MATH_OVERRIDE set. grad/AP from old rochester district.",med_home_val:650000,commute:40,owner_occ:78.0,vacancy:10.0,med_age:52.0,low_income_pct:10.0,ell_pct:3.0,enrollment_trend:null,sex_off:0.12,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',
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

# 2a. ZHVI entries
NEW_ZHVI = (
    '    "Springfield":245000,"Northampton":470000,"Amherst":545000,"Westfield":340000,\n'
    '    "Chicopee":300000,"Holyoke":265000,"Agawam":360000,"West Springfield":315000,\n'
    '    "Longmeadow":480000,"Easthampton":375000,\n'
    '    "Abington":510000,"Whitman":455000,"Rockland":465000,"Middleborough":430000,\n'
    '    "Wareham":370000,"Bridgewater":450000,"East Bridgewater":475000,\n'
    '    "West Bridgewater":485000,"Carver":400000,"Marion":650000,\n'
)
if '"Springfield":245000' not in py_text:
    py_text = re.sub(r'("Swansea":\d+,\n)', r'\1' + NEW_ZHVI, py_text)
    print("  Added ZHVI entries")
else:
    print("  ZHVI entries already present")

# 2b. COUNTY_MAP entries
NEW_COUNTY = (
    '    "Springfield":"Hampden","Northampton":"Hampshire","Amherst":"Hampshire",\n'
    '    "Westfield":"Hampden","Chicopee":"Hampden","Holyoke":"Hampden",\n'
    '    "Agawam":"Hampden","West Springfield":"Hampden","Longmeadow":"Hampden","Easthampton":"Hampshire",\n'
    '    "Abington":"Plymouth","Whitman":"Plymouth","Rockland":"Plymouth",\n'
    '    "Middleborough":"Plymouth","Wareham":"Plymouth","Bridgewater":"Plymouth",\n'
    '    "East Bridgewater":"Plymouth","West Bridgewater":"Plymouth","Carver":"Plymouth","Marion":"Plymouth",\n'
)
if '"Springfield":"Hampden"' not in py_text:
    py_text = re.sub(r'("Swansea":"Bristol",\n)', r'\1' + NEW_COUNTY, py_text)
    print("  Added COUNTY_MAP entries")
else:
    print("  COUNTY_MAP entries already present")

# 2c. DISTRICT_MAP entries
DISTRICT_ADD = (
    '    "Whitman":              "whitman-hanson",\n'
    '    "Bridgewater":          "bridgewater-raynham",\n'
    '    "Marion":               "old rochester",\n'
)
if '"Whitman":' not in py_text.split("DISTRICT_MAP")[1].split("}")[0]:
    py_text = re.sub(
        r'(    "Rehoboth":             "dighton-rehoboth",\n)',
        r'\1' + DISTRICT_ADD,
        py_text
    )
    print("  Added DISTRICT_MAP entries")
else:
    print("  DISTRICT_MAP entries already present")

# 2d. MATH_OVERRIDE for Marion (K-6 MCAS; Old Rochester HS data used for grad/AP)
MARION_OVERRIDE = '    "Marion":       55.0,  # Marion Elementary K-6 MCAS; Old Rochester Regional HS data used for grad/AP\n'
if '"Marion"' not in py_text.split("MATH_OVERRIDES")[1].split("}")[0]:
    py_text = re.sub(r'("Southborough": 74\.0.*?\n)', r'\1' + MARION_OVERRIDE, py_text)
    print("  Added Marion MATH_OVERRIDE")
else:
    print("  Marion MATH_OVERRIDE already present")

PY_FILE.write_text(py_text, encoding="utf-8")
print("  update_all.py patched")

# ---- Step 3: Add to TOWNS array in civica-v5.html ---------------------------
print("\nStep 3: Patching civica-v5.html...")
html_text = HTML_FILE.read_text(encoding="utf-8")

added_html = 0
for entry in NEW_HTML:
    town_name = entry.split('name:"')[1].split('"')[0]
    if f'name:"{town_name}"' in html_text:
        print(f"  SKIP (already in HTML): {town_name}")
        continue
    html_text = re.sub(
        r'(\];\s*\nconst PERSONAS)',
        r'  ' + entry + ',\n];\nconst PERSONAS',
        html_text, count=1
    )
    added_html += 1
    print(f"  + {town_name}")

HTML_FILE.write_text(html_text, encoding="utf-8")
print(f"  HTML: {added_html} towns added")

# ---- Step 4: Update town count strings --------------------------------------
print("\nStep 4: Updating town count strings...")
html_text = HTML_FILE.read_text(encoding="utf-8")
for pattern, label in [
    (r'Now live · Massachusetts · \d+ towns and cities', f'Now live · Massachusetts · {total_towns} towns and cities'),
    (r'Civica scores \d+ towns and cities', f'Civica scores {total_towns} towns and cities'),
]:
    updated = re.sub(pattern, label, html_text)
    if updated != html_text:
        html_text = updated
        print(f"  Updated: {label}")
HTML_FILE.write_text(html_text, encoding="utf-8")

print(f"\nDone. Total towns: {total_towns}")
print("Next step: py scripts/update_all.py")
