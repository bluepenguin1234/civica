"""
Add 20 towns: 10 Worcester County + 10 Bristol County
Run ONCE, then run:  py scripts/update_all.py

Worcester: Worcester, Leominster, Fitchburg, Auburn, Holden,
           Southborough, Sutton, Upton, Millbury, Leicester

Bristol:   Attleboro, Taunton, New Bedford, Fall River, Dartmouth,
           Norton, Seekonk, Raynham, Rehoboth, Swansea

Census / school / free-cash / debt: pulled from data/bulk/ files
Tax rates: MA DLS FY2025 estimates
ZHVI: Zillow estimates (May 2026)
Pension:
  Worcester city / Fitchburg / Leominster = 65.0  (own city systems -- verify PERAC)
  Other Worcester County suburbs           = 67.0  (Worcester County Retirement -- verify PERAC)
  Bristol County                           = 68.0  (Bristol County Retirement -- verify PERAC)
School d_rank: SchoolDigger/DESE estimates -- verify annually
Bond ratings: all null -- verify via EMMA (emma.msrb.org)
"""

import csv, re
from pathlib import Path

ROOT      = Path(__file__).parent.parent
CSV_FILE  = ROOT / "data" / "towns.csv"
HTML_FILE = ROOT / "civica-v5.html"
PY_FILE   = ROOT / "scripts" / "update_all.py"

WCR      = 67.0   # Worcester County Retirement (suburban towns)
WCR_CITY = 65.0   # Worcester / Fitchburg / Leominster own systems
BCR      = 68.0   # Bristol County Retirement

# ---- 1. New CSV rows ---------------------------------------------------------
NEW_TOWNS = [
    # ── Worcester County ──────────────────────────────────────────────────────
    dict(
        town_name="Worcester", state="MA", county="Worcester",
        zip_codes="01601;01602;01603;01604;01605;01606;01607;01608;01609",
        population="205501", bond_rating_sp="Not rated", free_cash_pct_of_budget="2.7",
        pension_funded_ratio_pct=str(WCR_CITY), debt_per_capita="3360.0",
        tax_base_non_residential_pct="30.0", effective_tax_rate_pct="1.327",
        median_annual_tax_bill="4114", median_household_income="67544",
        residential_rate_per_1000="13.27",
        district_state_rank="330", district_state_rank_total="351",
        test_scores_math_pct="23.0", graduation_rate_pct="85.5", ap_participation_pct="21.8",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="commuter_rail_in_town",
        violent_crime_per_100k="550.0", property_crime_per_100k="2800.0",
        flood_risk_pct="3.0", flood_2050_growth_pts="1.0", wildfire_risk="Low",
        compiler_notes="MA's second-largest city. Framingham/Worcester Line MBTA terminus at Union Station. Schools #330 of 351 (23% MCAS math). Worcester Retirement System (own pension ~65% est -- verify PERAC). Bond not rated -- likely rated; verify EMMA. Large commercial/industrial base (30% non-res). High crime reflects urban density.",
    ),
    dict(
        town_name="Leominster", state="MA", county="Worcester", zip_codes="01453",
        population="43697", bond_rating_sp="Not rated", free_cash_pct_of_budget="9.2",
        pension_funded_ratio_pct=str(WCR_CITY), debt_per_capita="907.0",
        tax_base_non_residential_pct="20.0", effective_tax_rate_pct="1.450",
        median_annual_tax_bill="5438", median_household_income="81556",
        residential_rate_per_1000="14.50",
        district_state_rank="240", district_state_rank_total="351",
        test_scores_math_pct="35.0", graduation_rate_pct="90.9", ap_participation_pct="8.6",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="commuter_rail_in_town",
        violent_crime_per_100k="300.0", property_crime_per_100k="1800.0",
        flood_risk_pct="4.0", flood_2050_growth_pts="1.5", wildfire_risk="Low",
        compiler_notes="Mid-sized city on Fitchburg commuter rail line ('Pioneer Plastics City'). Solid free cash (9.2%) and very low debt per capita ($907). Schools #240 of 351. Own city retirement system (~65% est -- verify PERAC). Bond not rated -- verify EMMA.",
    ),
    dict(
        town_name="Fitchburg", state="MA", county="Worcester", zip_codes="01420;01430",
        population="41633", bond_rating_sp="Not rated", free_cash_pct_of_budget="6.0",
        pension_funded_ratio_pct=str(WCR_CITY), debt_per_capita="1598.0",
        tax_base_non_residential_pct="18.0", effective_tax_rate_pct="1.764",
        median_annual_tax_bill="5468", median_household_income="70659",
        residential_rate_per_1000="17.64",
        district_state_rank="325", district_state_rank_total="351",
        test_scores_math_pct="20.0", graduation_rate_pct="84.8", ap_participation_pct="13.3",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="commuter_rail_in_town",
        violent_crime_per_100k="600.0", property_crime_per_100k="2500.0",
        flood_risk_pct="5.0", flood_2050_growth_pts="2.0", wildfire_risk="Low",
        compiler_notes="Fitchburg Line MBTA terminus. Highest res rate in this batch (17.64) despite low home values -- constrained commercial base. Schools #325 of 351 (20% MCAS math). Own city retirement system (~65% est -- verify PERAC). Strong income growth (+56% over 10 yrs). Bond not rated -- verify EMMA.",
    ),
    dict(
        town_name="Auburn", state="MA", county="Worcester", zip_codes="01501",
        population="16840", bond_rating_sp="Not rated", free_cash_pct_of_budget="25.7",
        pension_funded_ratio_pct=str(WCR), debt_per_capita="2300.0",
        tax_base_non_residential_pct="15.0", effective_tax_rate_pct="1.364",
        median_annual_tax_bill="5456", median_household_income="100786",
        residential_rate_per_1000="13.64",
        district_state_rank="155", district_state_rank_total="351",
        test_scores_math_pct="47.0", graduation_rate_pct="92.3", ap_participation_pct="29.5",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="100.0", property_crime_per_100k="800.0",
        flood_risk_pct="5.0", flood_2050_growth_pts="2.0", wildfire_risk="Low",
        compiler_notes="Directly adjacent to Worcester on Route 20. Exceptional fiscal reserves (25.7% free cash -- top 5% in MA). Schools #155 of 351 (47% MCAS math, 92.3% grad). Worcester County Retirement (~67% est). Bond not rated -- verify EMMA. Worcester Union Station is nearest commuter rail (~8 mi).",
    ),
    dict(
        town_name="Holden", state="MA", county="Worcester", zip_codes="01520",
        population="19885", bond_rating_sp="Not rated", free_cash_pct_of_budget="9.2",
        pension_funded_ratio_pct=str(WCR), debt_per_capita="1941.0",
        tax_base_non_residential_pct="10.0", effective_tax_rate_pct="1.238",
        median_annual_tax_bill="6066", median_household_income="142880",
        residential_rate_per_1000="12.38",
        district_state_rank="125", district_state_rank_total="351",
        test_scores_math_pct="56.0", graduation_rate_pct="93.9", ap_participation_pct="24.3",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="35.0", property_crime_per_100k="500.0",
        flood_risk_pct="4.0", flood_2050_growth_pts="1.5", wildfire_risk="Low",
        compiler_notes="Fast-growing western suburb of Worcester (pop +13% over 10 yrs). Wachusett Regional School District (#125 of 351, 56% MCAS math, 93.9% grad). High median income ($143k). Worcester County Retirement (~67% est). Bond not rated -- verify EMMA. DISTRICT_MAP: wachusett.",
    ),
    dict(
        town_name="Southborough", state="MA", county="Worcester", zip_codes="01772",
        population="10441", bond_rating_sp="Not rated", free_cash_pct_of_budget="3.3",
        pension_funded_ratio_pct=str(WCR), debt_per_capita="3230.0",
        tax_base_non_residential_pct="8.0", effective_tax_rate_pct="1.501",
        median_annual_tax_bill="11858", median_household_income="192006",
        residential_rate_per_1000="15.01",
        district_state_rank="83", district_state_rank_total="351",
        test_scores_math_pct="74.0", graduation_rate_pct="97.7", ap_participation_pct="39.6",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="commuter_rail_in_town",
        violent_crime_per_100k="25.0", property_crime_per_100k="400.0",
        flood_risk_pct="3.0", flood_2050_growth_pts="1.0", wildfire_risk="Low",
        compiler_notes="One of central MA's wealthiest towns ($192k median income). Framingham/Worcester Line commuter rail station. Algonquin Regional HS via Northborough-Southborough district (#83 of 351, 97.7% grad, 39.6% AP). math_pct=74 is Southborough Elementary K-5 MCAS; MATH_OVERRIDE set. Worcester County Retirement (~67% est). Bond not rated -- verify EMMA.",
    ),
    dict(
        town_name="Sutton", state="MA", county="Worcester", zip_codes="01590",
        population="9383", bond_rating_sp="Not rated", free_cash_pct_of_budget="9.7",
        pension_funded_ratio_pct=str(WCR), debt_per_capita="3372.0",
        tax_base_non_residential_pct="6.0", effective_tax_rate_pct="1.600",
        median_annual_tax_bill="9600", median_household_income="156215",
        residential_rate_per_1000="16.00",
        district_state_rank="130", district_state_rank_total="351",
        test_scores_math_pct="42.0", graduation_rate_pct="94.2", ap_participation_pct="52.1",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="20.0", property_crime_per_100k="300.0",
        flood_risk_pct="4.0", flood_2050_growth_pts="1.5", wildfire_risk="Low",
        compiler_notes="Rural but growing town south of Worcester. Lowest violent crime in Worcester batch. Very low unemployment (1.8%). High AP participation (52.1%) reflects strong academic culture. Worcester County Retirement (~67% est). Bond not rated -- verify EMMA.",
    ),
    dict(
        town_name="Upton", state="MA", county="Worcester", zip_codes="01568",
        population="8095", bond_rating_sp="Not rated", free_cash_pct_of_budget="9.7",
        pension_funded_ratio_pct=str(WCR), debt_per_capita="935.0",
        tax_base_non_residential_pct="5.0", effective_tax_rate_pct="1.600",
        median_annual_tax_bill="10080", median_household_income="155952",
        residential_rate_per_1000="16.00",
        district_state_rank="110", district_state_rank_total="351",
        test_scores_math_pct="50.0", graduation_rate_pct="93.8", ap_participation_pct="38.5",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="30.0", property_crime_per_100k="350.0",
        flood_risk_pct="4.0", flood_2050_growth_pts="1.5", wildfire_risk="Low",
        compiler_notes="Small high-income town on Norfolk/Worcester border ($156k median). Mendon-Upton district (#110 of 351, 93.8% grad, 38.5% AP). Very low debt per capita ($935). Worcester County Retirement (~67% est). Bond not rated -- verify EMMA. DISTRICT_MAP: mendon-upton.",
    ),
    dict(
        town_name="Millbury", state="MA", county="Worcester", zip_codes="01527",
        population="13899", bond_rating_sp="Not rated", free_cash_pct_of_budget="7.6",
        pension_funded_ratio_pct=str(WCR), debt_per_capita="1292.0",
        tax_base_non_residential_pct="20.0", effective_tax_rate_pct="1.200",
        median_annual_tax_bill="5160", median_household_income="116000",
        residential_rate_per_1000="12.00",
        district_state_rank="185", district_state_rank_total="351",
        test_scores_math_pct="39.0", graduation_rate_pct="93.8", ap_participation_pct="22.4",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="100.0", property_crime_per_100k="700.0",
        flood_risk_pct="5.0", flood_2050_growth_pts="2.0", wildfire_risk="Low",
        compiler_notes="Affordable suburb adjacent to Worcester. Strong income growth (+62% over 10 yrs). Industrial heritage (20% non-res base) keeps res rates lower than comparable Worcester County towns. Schools #185 of 351. Worcester County Retirement (~67% est). Bond not rated -- verify EMMA.",
    ),
    dict(
        town_name="Leicester", state="MA", county="Worcester", zip_codes="01524",
        population="11076", bond_rating_sp="Not rated", free_cash_pct_of_budget="6.4",
        pension_funded_ratio_pct=str(WCR), debt_per_capita="1005.0",
        tax_base_non_residential_pct="8.0", effective_tax_rate_pct="1.630",
        median_annual_tax_bill="5950", median_household_income="95776",
        residential_rate_per_1000="16.30",
        district_state_rank="220", district_state_rank_total="351",
        test_scores_math_pct="37.0", graduation_rate_pct="91.0", ap_participation_pct="16.1",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="80.0", property_crime_per_100k="600.0",
        flood_risk_pct="5.0", flood_2050_growth_pts="2.0", wildfire_risk="Low",
        compiler_notes="Rural town west of Worcester. Very low unemployment (2.3%). Flat 10-yr population growth (0%). Schools #220 of 351. Worcester County Retirement (~67% est). Bond not rated -- verify EMMA. No transit.",
    ),
    # ── Bristol County ────────────────────────────────────────────────────────
    dict(
        town_name="Attleboro", state="MA", county="Bristol", zip_codes="02703",
        population="46499", bond_rating_sp="Not rated", free_cash_pct_of_budget="9.5",
        pension_funded_ratio_pct=str(BCR), debt_per_capita="2001.0",
        tax_base_non_residential_pct="20.0", effective_tax_rate_pct="1.337",
        median_annual_tax_bill="5816", median_household_income="93266",
        residential_rate_per_1000="13.37",
        district_state_rank="200", district_state_rank_total="351",
        test_scores_math_pct="38.0", graduation_rate_pct="92.2", ap_participation_pct="18.6",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="commuter_rail_in_town",
        violent_crime_per_100k="250.0", property_crime_per_100k="1500.0",
        flood_risk_pct="5.0", flood_2050_growth_pts="2.0", wildfire_risk="Low",
        compiler_notes="Mid-sized city on Providence/Stoughton MBTA commuter rail line. Strong free cash (9.5%). Schools #200 of 351 (38% MCAS math, 92.2% grad). Bristol County Retirement (~68% est -- verify PERAC). Bond not rated -- verify EMMA.",
    ),
    dict(
        town_name="Taunton", state="MA", county="Bristol", zip_codes="02718;02780",
        population="59719", bond_rating_sp="Not rated", free_cash_pct_of_budget="7.0",
        pension_funded_ratio_pct=str(BCR), debt_per_capita="2228.0",
        tax_base_non_residential_pct="22.0", effective_tax_rate_pct="1.487",
        median_annual_tax_bill="5874", median_household_income="79715",
        residential_rate_per_1000="14.87",
        district_state_rank="285", district_state_rank_total="351",
        test_scores_math_pct="24.0", graduation_rate_pct="89.0", ap_participation_pct="18.0",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="commuter_rail_in_town",
        violent_crime_per_100k="380.0", property_crime_per_100k="2000.0",
        flood_risk_pct="10.0", flood_2050_growth_pts="4.0", wildfire_risk="Low",
        compiler_notes="Largest city in Bristol County. South Coast Rail (opened Aug 2023) to South Station. Schools #285 of 351. Elevated crime. Taunton River flood risk affects low-lying areas. Bristol County Retirement (~68% est). Bond not rated -- verify EMMA. Strong income growth (+54% over 10 yrs).",
    ),
    dict(
        town_name="New Bedford", state="MA", county="Bristol",
        zip_codes="02740;02744;02745;02746",
        population="100731", bond_rating_sp="Not rated", free_cash_pct_of_budget="2.0",
        pension_funded_ratio_pct=str(BCR), debt_per_capita="2024.0",
        tax_base_non_residential_pct="25.0", effective_tax_rate_pct="1.437",
        median_annual_tax_bill="4239", median_household_income="56025",
        residential_rate_per_1000="14.37",
        district_state_rank="338", district_state_rank_total="351",
        test_scores_math_pct="17.0", graduation_rate_pct="79.9", ap_participation_pct="13.6",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="commuter_rail_in_town",
        violent_crime_per_100k="600.0", property_crime_per_100k="2600.0",
        flood_risk_pct="15.0", flood_2050_growth_pts="7.0", wildfire_risk="Low",
        compiler_notes="Third-largest city in MA. South Coast Rail (Aug 2023) to South Station. Historic whaling city / active working port. Schools #338 of 351 (17% MCAS math, 79.9% grad). High crime. Coastal flood risk (15%). Very low free cash (2.0%) is fiscal stress flag. Bristol County Retirement (~68% est). Bond not rated -- verify EMMA.",
    ),
    dict(
        town_name="Fall River", state="MA", county="Bristol",
        zip_codes="02720;02721;02723;02724;02725",
        population="93764", bond_rating_sp="Not rated", free_cash_pct_of_budget="1.8",
        pension_funded_ratio_pct=str(BCR), debt_per_capita="2429.0",
        tax_base_non_residential_pct="20.0", effective_tax_rate_pct="1.282",
        median_annual_tax_bill="3461", median_household_income="53933",
        residential_rate_per_1000="12.82",
        district_state_rank="342", district_state_rank_total="351",
        test_scores_math_pct="18.0", graduation_rate_pct="76.8", ap_participation_pct="17.4",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="commuter_rail_in_town",
        violent_crime_per_100k="700.0", property_crime_per_100k="2400.0",
        flood_risk_pct="10.0", flood_2050_growth_pts="5.0", wildfire_risk="Low",
        compiler_notes="Fourth-largest city in MA. South Coast Rail (Aug 2023) to South Station via Fall River Depot. Schools #342 of 351 (18% MCAS math, 76.8% grad). Highest violent crime in this batch. Very low free cash (1.8%) -- fiscal stress flag. Lowest home prices in batch (~$270k). Bristol County Retirement (~68% est). Bond not rated -- verify EMMA.",
    ),
    dict(
        town_name="Dartmouth", state="MA", county="Bristol", zip_codes="02747;02748",
        population="32621", bond_rating_sp="Not rated", free_cash_pct_of_budget="5.5",
        pension_funded_ratio_pct=str(BCR), debt_per_capita="1573.0",
        tax_base_non_residential_pct="15.0", effective_tax_rate_pct="0.994",
        median_annual_tax_bill="4622", median_household_income="98662",
        residential_rate_per_1000="9.94",
        district_state_rank="160", district_state_rank_total="351",
        test_scores_math_pct="45.0", graduation_rate_pct="92.4", ap_participation_pct="33.7",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="80.0", property_crime_per_100k="600.0",
        flood_risk_pct="12.0", flood_2050_growth_pts="5.0", wildfire_risk="Low",
        compiler_notes="Coastal suburban town south of New Bedford on Buzzards Bay. Lowest res tax rate in Bristol batch (9.94). Solid schools (#160 of 351, 92.4% grad). Negative 10-yr pop growth (-4.9%) is unusual -- verify Census. UMass Dartmouth campus. Bristol County Retirement (~68% est). Bond not rated -- verify EMMA.",
    ),
    dict(
        town_name="Norton", state="MA", county="Bristol", zip_codes="02766",
        population="19155", bond_rating_sp="Not rated", free_cash_pct_of_budget="6.4",
        pension_funded_ratio_pct=str(BCR), debt_per_capita="1264.0",
        tax_base_non_residential_pct="10.0", effective_tax_rate_pct="1.400",
        median_annual_tax_bill="7630", median_household_income="127404",
        residential_rate_per_1000="14.00",
        district_state_rank="195", district_state_rank_total="351",
        test_scores_math_pct="34.0", graduation_rate_pct="93.0", ap_participation_pct="25.2",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="commuter_rail_nearby",
        violent_crime_per_100k="60.0", property_crime_per_100k="500.0",
        flood_risk_pct="6.0", flood_2050_growth_pts="2.5", wildfire_risk="Low",
        compiler_notes="Quiet suburb north of Taunton. High incomes ($127k). Strong income growth (+57% over 10 yrs). Very low crime. Schools #195 of 351. Providence/Stoughton Line at Attleboro (~4 mi). Wheaton College in town. Bristol County Retirement (~68% est). Bond not rated -- verify EMMA.",
    ),
    dict(
        town_name="Seekonk", state="MA", county="Bristol", zip_codes="02771",
        population="15573", bond_rating_sp="Not rated", free_cash_pct_of_budget="4.8",
        pension_funded_ratio_pct=str(BCR), debt_per_capita="509.0",
        tax_base_non_residential_pct="22.0", effective_tax_rate_pct="1.275",
        median_annual_tax_bill="5674", median_household_income="116310",
        residential_rate_per_1000="12.75",
        district_state_rank="115", district_state_rank_total="351",
        test_scores_math_pct="53.0", graduation_rate_pct="96.8", ap_participation_pct="32.0",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="80.0", property_crime_per_100k="700.0",
        flood_risk_pct="7.0", flood_2050_growth_pts="3.0", wildfire_risk="Low",
        compiler_notes="Best schools in Bristol batch (#115 of 351, 96.8% grad, 53% MCAS math). Very low debt per capita ($509). Borders Providence, RI (7 mi west). Large Route 6 commercial corridor (22% non-res). No MBTA service. Bristol County Retirement (~68% est). Bond not rated -- verify EMMA.",
    ),
    dict(
        town_name="Raynham", state="MA", county="Bristol", zip_codes="02767;02768",
        population="15273", bond_rating_sp="Not rated", free_cash_pct_of_budget="7.8",
        pension_funded_ratio_pct=str(BCR), debt_per_capita="1216.0",
        tax_base_non_residential_pct="15.0", effective_tax_rate_pct="1.274",
        median_annual_tax_bill="5988", median_household_income="117950",
        residential_rate_per_1000="12.74",
        district_state_rank="215", district_state_rank_total="351",
        test_scores_math_pct="34.0", graduation_rate_pct="93.4", ap_participation_pct="25.8",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="commuter_rail_nearby",
        violent_crime_per_100k="100.0", property_crime_per_100k="700.0",
        flood_risk_pct="8.0", flood_2050_growth_pts="3.0", wildfire_risk="Low",
        compiler_notes="Fast-growing town (pop +14% over 10 yrs) adjacent to Taunton. Above-average incomes ($118k). Bridgewater-Raynham district (#215 of 351, 93.4% grad). South Coast Rail at Taunton (~5 mi). Taunton River watershed -- flood risk. Bristol County Retirement (~68% est). Bond not rated -- verify EMMA. DISTRICT_MAP: bridgewater-raynham.",
    ),
    dict(
        town_name="Rehoboth", state="MA", county="Bristol", zip_codes="02769",
        population="12809", bond_rating_sp="Not rated", free_cash_pct_of_budget="2.9",
        pension_funded_ratio_pct=str(BCR), debt_per_capita="19.0",
        tax_base_non_residential_pct="6.0", effective_tax_rate_pct="1.346",
        median_annual_tax_bill="7336", median_household_income="126161",
        residential_rate_per_1000="13.46",
        district_state_rank="140", district_state_rank_total="351",
        test_scores_math_pct="52.0", graduation_rate_pct="91.9", ap_participation_pct="18.6",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="30.0", property_crime_per_100k="350.0",
        flood_risk_pct="5.0", flood_2050_growth_pts="2.0", wildfire_risk="Low",
        compiler_notes="Rural town bordering Providence, RI. $19 debt per capita -- exceptionally debt-free (verify MA DLS). Above-average incomes ($126k). Dighton-Rehoboth district (#140 of 351, 91.9% grad). Very low crime. Bristol County Retirement (~68% est). Bond not rated -- verify EMMA. DISTRICT_MAP: dighton-rehoboth.",
    ),
    dict(
        town_name="Swansea", state="MA", county="Bristol", zip_codes="02777",
        population="17231", bond_rating_sp="Not rated", free_cash_pct_of_budget="30.4",
        pension_funded_ratio_pct=str(BCR), debt_per_capita="400.0",
        tax_base_non_residential_pct="12.0", effective_tax_rate_pct="1.237",
        median_annual_tax_bill="5195", median_household_income="116627",
        residential_rate_per_1000="12.37",
        district_state_rank="175", district_state_rank_total="351",
        test_scores_math_pct="50.0", graduation_rate_pct="93.0", ap_participation_pct="22.1",
        transparency="yes", electric_savings_vs_state_avg="0", water_violations_5yr="0",
        transit_access="none",
        violent_crime_per_100k="80.0", property_crime_per_100k="650.0",
        flood_risk_pct="8.0", flood_2050_growth_pts="3.5", wildfire_risk="Low",
        compiler_notes="Suburban town bordering Fall River. Exceptional free cash (30.4% -- among highest in MA; may reflect one-time certification, verify MA DLS). Very low debt ($400/capita). Solid schools (#175 of 351, 93% grad). Above-average incomes ($117k). Highest income growth in batch (+64% over 10 yrs). Bristol County Retirement (~68% est). Bond not rated -- verify EMMA.",
    ),
]

# ---- 2. New HTML objects -----------------------------------------------------
NEW_HTML = [
    # Worcester County
    '{name:"Worcester",lat:42.2626,lng:-71.8023,state:"MA",county:"Worcester",zip:"01601 / 01603 / 01605 / 01607",pop:205501,bond:null,free_cash:2.7,pension:65.0,debt_pc:3360.0,gfoa:null,tax_non_res:30.0,eff_rate:1.327,med_tax:4114,med_inc:67544,res_rate:13.27,d_rank:330,d_total:351,d_10yr:null,math:23.0,grad:85.5,ap:21.8,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town) — Framingham/Worcester Line",violent:550.0,prop_crime:2800.0,crime5yr:null,inc10yr:47.1,pop10yr:13.0,bach:34.1,unemp:6.4,pov:19.8,flood:3.0,flood50:1.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"MA\'s second-largest city with MBTA commuter rail to South Station and a growing biotech economy. Schools #330 of 351 and urban-scale crime are the defining trade-offs at this price point.",glance:"Worcester is Massachusetts\' second-largest city — a diverse urban center with MBTA commuter rail to South Station and a growing biotech and healthcare economy. Schools rank #330 of 351 and crime runs at urban scale; both are the expected trade-offs for buyers drawn to the dramatically lower price point (~$310k median).",notes:"Worcester Retirement System (own pension ~65% est -- verify PERAC). Bond not rated -- likely rated; verify EMMA.",med_home_val:310000,commute:26,owner_occ:42.0,vacancy:8.5,med_age:32.0,low_income_pct:72.0,ell_pct:22.0,enrollment_trend:null,sex_off:0.55,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Leominster",lat:42.5251,lng:-71.7598,state:"MA",county:"Worcester",zip:"01453",pop:43697,bond:null,free_cash:9.2,pension:65.0,debt_pc:907.0,gfoa:null,tax_non_res:20.0,eff_rate:1.450,med_tax:5438,med_inc:81556,res_rate:14.50,d_rank:240,d_total:351,d_10yr:null,math:35.0,grad:90.9,ap:8.6,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town) — Fitchburg Line",violent:300.0,prop_crime:1800.0,crime5yr:null,inc10yr:38.6,pop10yr:6.9,bach:32.3,unemp:5.7,pov:10.1,flood:4.0,flood50:1.5,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Mid-sized city on the Fitchburg commuter rail line with strong free cash (9.2%) and very low debt per capita ($907). Schools #240 of 351.",glance:"Leominster is a mid-sized city on the Fitchburg commuter rail line with affordable homes and solid fiscal reserves. Schools rank #240 of 351 and crime runs elevated for a city its size — the standard trade-offs at this price point.",notes:"Own city retirement system (~65% est -- verify PERAC). Bond not rated -- verify EMMA.",med_home_val:375000,commute:29,owner_occ:52.0,vacancy:6.0,med_age:38.0,low_income_pct:45.0,ell_pct:15.0,enrollment_trend:null,sex_off:0.45,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Fitchburg",lat:42.5834,lng:-71.8023,state:"MA",county:"Worcester",zip:"01420",pop:41633,bond:null,free_cash:6.0,pension:65.0,debt_pc:1598.0,gfoa:null,tax_non_res:18.0,eff_rate:1.764,med_tax:5468,med_inc:70659,res_rate:17.64,d_rank:325,d_total:351,d_10yr:null,math:20.0,grad:84.8,ap:13.3,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town) — Fitchburg Line",violent:600.0,prop_crime:2500.0,crime5yr:null,inc10yr:55.8,pop10yr:3.2,bach:24.5,unemp:6.9,pov:15.5,flood:5.0,flood50:2.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Fitchburg Line MBTA terminus with strong income growth (+56% over 10 yrs). Highest residential tax rate in this batch (17.64) despite low home values.",glance:"Fitchburg is an affordably priced urban city at the Fitchburg commuter rail terminus with strong income growth (+56% over 10 years). Near-bottom school rankings (#325 of 351, 20% MCAS math) and high crime are the expected profile for a working-class city at this price point.",notes:"Fitchburg Retirement System (own pension ~65% est -- verify PERAC). Bond not rated -- verify EMMA.",med_home_val:310000,commute:28,owner_occ:42.0,vacancy:9.0,med_age:34.0,low_income_pct:65.0,ell_pct:20.0,enrollment_trend:null,sex_off:0.65,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Auburn",lat:42.1967,lng:-71.8376,state:"MA",county:"Worcester",zip:"01501",pop:16840,bond:null,free_cash:25.7,pension:67.0,debt_pc:2300.0,gfoa:null,tax_non_res:15.0,eff_rate:1.364,med_tax:5456,med_inc:100786,res_rate:13.64,d_rank:155,d_total:351,d_10yr:null,math:47.0,grad:92.3,ap:29.5,transp:"Yes",elec_save:0,water_viol:0,transit:"None (Worcester Union Station 8 mi)",violent:100.0,prop_crime:800.0,crime5yr:null,inc10yr:37.6,pop10yr:3.7,bach:42.0,unemp:3.9,pov:4.5,flood:5.0,flood50:2.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Directly adjacent to Worcester with exceptional fiscal reserves (25.7% free cash — top 5% in MA). Solid schools #155 of 351 at a mid-market price point.",glance:"Auburn is a quiet suburb directly adjacent to Worcester with exceptional fiscal reserves (25.7% free cash — top 5% in MA) and solid schools (#155 of 351, 92.3% graduation). No commuter rail in town; Worcester Union Station is 8 miles east.",notes:"Worcester County Retirement (~67% est -- verify PERAC). Bond not rated -- verify EMMA.",med_home_val:400000,commute:27,owner_occ:72.0,vacancy:4.0,med_age:42.0,low_income_pct:18.0,ell_pct:5.0,enrollment_trend:null,sex_off:0.25,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Holden",lat:42.3559,lng:-71.8637,state:"MA",county:"Worcester",zip:"01520",pop:19885,bond:null,free_cash:9.2,pension:67.0,debt_pc:1941.0,gfoa:null,tax_non_res:10.0,eff_rate:1.238,med_tax:6066,med_inc:142880,res_rate:12.38,d_rank:125,d_total:351,d_10yr:null,math:56.0,grad:93.9,ap:24.3,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:35.0,prop_crime:500.0,crime5yr:null,inc10yr:50.0,pop10yr:13.4,bach:57.6,unemp:5.5,pov:4.0,flood:4.0,flood50:1.5,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Fast-growing western Worcester suburb served by Wachusett Regional schools (#125 of 351, 56% MCAS math, 93.9% grad). High income ($143k) and very low crime.",glance:"Holden is a well-regarded suburb west of Worcester with strong schools through Wachusett Regional (#125 of 351, 56% MCAS math, 93.9% graduation) and a high median income ($143k). Fast population growth and very low crime are the highlights; no commuter rail is the main limitation.",notes:"Worcester County Retirement (~67% est). Bond not rated -- verify EMMA. DISTRICT_MAP: wachusett.",med_home_val:490000,commute:30,owner_occ:80.0,vacancy:3.5,med_age:45.0,low_income_pct:12.0,ell_pct:3.0,enrollment_trend:null,sex_off:0.20,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Southborough",lat:42.3084,lng:-71.5245,state:"MA",county:"Worcester",zip:"01772",pop:10441,bond:null,free_cash:3.3,pension:67.0,debt_pc:3230.0,gfoa:null,tax_non_res:8.0,eff_rate:1.501,med_tax:11858,med_inc:192006,res_rate:15.01,d_rank:83,d_total:351,d_10yr:null,math:74.0,grad:97.7,ap:39.6,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town) — Framingham/Worcester Line",violent:25.0,prop_crime:400.0,crime5yr:null,inc10yr:33.7,pop10yr:6.5,bach:75.7,unemp:4.1,pov:3.8,flood:3.0,flood50:1.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"One of central MA\'s wealthiest communities ($192k median income) on the Framingham/Worcester commuter rail line. Algonquin Regional HS (#83 of 351, 97.7% grad).",glance:"Southborough is one of central Massachusetts\' wealthiest communities — top-tier schools through Algonquin Regional (#83 of 351, 97.7% graduation), a $192k median income, and rare commuter rail access for a Worcester County town. The high median tax bill ($11,858) reflects premium home values.",notes:"Worcester County Retirement (~67% est). Bond not rated -- verify EMMA. math=74 is Southborough Elementary K-5 MCAS; MATH_OVERRIDE set. grad/AP from northborough-southborough HS district.",med_home_val:790000,commute:32,owner_occ:85.0,vacancy:3.0,med_age:42.0,low_income_pct:8.0,ell_pct:5.0,enrollment_trend:null,sex_off:0.15,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Sutton",lat:42.1223,lng:-71.7579,state:"MA",county:"Worcester",zip:"01590",pop:9383,bond:null,free_cash:9.7,pension:67.0,debt_pc:3372.0,gfoa:null,tax_non_res:6.0,eff_rate:1.600,med_tax:9600,med_inc:156215,res_rate:16.00,d_rank:130,d_total:351,d_10yr:null,math:42.0,grad:94.2,ap:52.1,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:20.0,prop_crime:300.0,crime5yr:null,inc10yr:41.5,pop10yr:4.0,bach:47.0,unemp:1.8,pov:4.5,flood:4.0,flood50:1.5,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Rural Worcester County town with the lowest violent crime in this batch (20/100k), near-zero unemployment (1.8%), and strong schools (#130 of 351, 94.2% grad).",glance:"Sutton is a rural, high-income town south of Worcester with very low crime, strong schools (#130 of 351, 94.2% graduation), and near-zero unemployment (1.8%). The high median tax bill ($9,600) and no transit are the trade-offs for the setting.",notes:"Worcester County Retirement (~67% est). Bond not rated -- verify EMMA.",med_home_val:600000,commute:32,owner_occ:90.0,vacancy:3.0,med_age:43.0,low_income_pct:10.0,ell_pct:2.0,enrollment_trend:null,sex_off:0.12,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Upton",lat:42.1667,lng:-71.6001,state:"MA",county:"Worcester",zip:"01568",pop:8095,bond:null,free_cash:9.7,pension:67.0,debt_pc:935.0,gfoa:null,tax_non_res:5.0,eff_rate:1.600,med_tax:10080,med_inc:155952,res_rate:16.00,d_rank:110,d_total:351,d_10yr:null,math:50.0,grad:93.8,ap:38.5,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:30.0,prop_crime:350.0,crime5yr:null,inc10yr:47.5,pop10yr:6.9,bach:52.8,unemp:5.6,pov:2.5,flood:4.0,flood50:1.5,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Small but high-income town on the Norfolk/Worcester border ($156k median). Mendon-Upton district (#110 of 351, 93.8% grad) with very low debt per capita ($935).",glance:"Upton is a fast-growing small town with high incomes ($156k median) and above-average schools through Mendon-Upton district (#110 of 351, 93.8% graduation). The high median tax bill ($10,080) and no transit are the trade-offs for a well-resourced suburban setting.",notes:"Worcester County Retirement (~67% est). Bond not rated -- verify EMMA. DISTRICT_MAP: mendon-upton.",med_home_val:630000,commute:35,owner_occ:88.0,vacancy:2.5,med_age:42.0,low_income_pct:8.0,ell_pct:3.0,enrollment_trend:null,sex_off:0.18,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Millbury",lat:42.1898,lng:-71.7679,state:"MA",county:"Worcester",zip:"01527",pop:13899,bond:null,free_cash:7.6,pension:67.0,debt_pc:1292.0,gfoa:null,tax_non_res:20.0,eff_rate:1.200,med_tax:5160,med_inc:116000,res_rate:12.00,d_rank:185,d_total:351,d_10yr:null,math:39.0,grad:93.8,ap:22.4,transp:"Yes",elec_save:0,water_viol:0,transit:"None (Worcester Union Station 8 mi)",violent:100.0,prop_crime:700.0,crime5yr:null,inc10yr:61.8,pop10yr:4.7,bach:33.4,unemp:3.8,pov:3.9,flood:5.0,flood50:2.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Affordable suburb adjacent to Worcester with strong income growth (+62% over 10 years). Industrial heritage (20% non-res base) keeps residential rates below comparable towns.",glance:"Millbury is an affordable suburb adjacent to Worcester with strong income growth (+62% over 10 years) and mid-tier schools (#185 of 351, 93.8% graduation). The large commercial corridor keeps residential tax rates lower than comparable Worcester County towns.",notes:"Worcester County Retirement (~67% est). Bond not rated -- verify EMMA.",med_home_val:430000,commute:28,owner_occ:72.0,vacancy:4.5,med_age:42.0,low_income_pct:22.0,ell_pct:5.0,enrollment_trend:null,sex_off:0.30,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Leicester",lat:42.2412,lng:-71.9065,state:"MA",county:"Worcester",zip:"01524",pop:11076,bond:null,free_cash:6.4,pension:67.0,debt_pc:1005.0,gfoa:null,tax_non_res:8.0,eff_rate:1.630,med_tax:5950,med_inc:95776,res_rate:16.30,d_rank:220,d_total:351,d_10yr:null,math:37.0,grad:91.0,ap:16.1,transp:"Yes",elec_save:0,water_viol:0,transit:"None",violent:80.0,prop_crime:600.0,crime5yr:null,inc10yr:34.8,pop10yr:0.0,bach:29.4,unemp:2.3,pov:3.4,flood:5.0,flood50:2.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Rural town west of Worcester with very low unemployment (2.3%) and low crime. Flat population growth and no transit reflect the quiet, bedroom-community character.",glance:"Leicester is an affordable rural town west of Worcester with very low unemployment (2.3%), low crime, and modest schools (#220 of 351). Flat 10-year population growth and no transit reflect its quiet, bedroom-community character.",notes:"Worcester County Retirement (~67% est). Bond not rated -- verify EMMA.",med_home_val:365000,commute:30,owner_occ:75.0,vacancy:5.0,med_age:42.0,low_income_pct:22.0,ell_pct:4.0,enrollment_trend:null,sex_off:0.28,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    # Bristol County
    '{name:"Attleboro",lat:41.9445,lng:-71.2856,state:"MA",county:"Bristol",zip:"02703",pop:46499,bond:null,free_cash:9.5,pension:68.0,debt_pc:2001.0,gfoa:null,tax_non_res:20.0,eff_rate:1.337,med_tax:5816,med_inc:93266,res_rate:13.37,d_rank:200,d_total:351,d_10yr:null,math:38.0,grad:92.2,ap:18.6,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town) — Providence/Stoughton Line",violent:250.0,prop_crime:1500.0,crime5yr:null,inc10yr:39.1,pop10yr:6.5,bach:33.7,unemp:4.5,pov:9.2,flood:5.0,flood50:2.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Mid-sized city on the Providence/Stoughton MBTA line. Strong free cash (9.5%). Schools #200 of 351.",glance:"Attleboro is a mid-sized city on the Providence/Stoughton commuter rail line with affordable housing and direct rail access to both Providence and South Station. Schools rank #200 of 351 and crime runs above suburban norms — the expected trade-offs for a city at this price point.",notes:"Bristol County Retirement (~68% est -- verify PERAC). Bond not rated -- verify EMMA.",med_home_val:435000,commute:31,owner_occ:62.0,vacancy:5.5,med_age:40.0,low_income_pct:40.0,ell_pct:12.0,enrollment_trend:null,sex_off:0.45,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Taunton",lat:41.9001,lng:-71.0898,state:"MA",county:"Bristol",zip:"02718 / 02780",pop:59719,bond:null,free_cash:7.0,pension:68.0,debt_pc:2228.0,gfoa:null,tax_non_res:22.0,eff_rate:1.487,med_tax:5874,med_inc:79715,res_rate:14.87,d_rank:285,d_total:351,d_10yr:null,math:24.0,grad:89.0,ap:18.0,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town) — South Coast Rail",violent:380.0,prop_crime:2000.0,crime5yr:null,inc10yr:54.4,pop10yr:6.7,bach:24.4,unemp:5.6,pov:13.7,flood:10.0,flood50:4.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Largest Bristol County city, now served by South Coast Rail to South Station (opened 2023). Affordable home prices. Schools #285 of 351.",glance:"Taunton is Bristol County\'s largest city with South Coast Rail access to South Station (opened 2023) and affordably priced homes. Schools rank #285 of 351 and crime is elevated; Taunton River flood risk affects low-lying properties.",notes:"Bristol County Retirement (~68% est -- verify PERAC). Bond not rated -- verify EMMA. South Coast Rail Phase 1 opened August 2023.",med_home_val:395000,commute:32,owner_occ:55.0,vacancy:6.0,med_age:40.0,low_income_pct:48.0,ell_pct:15.0,enrollment_trend:null,sex_off:0.55,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"New Bedford",lat:41.6362,lng:-70.9342,state:"MA",county:"Bristol",zip:"02740 / 02744 / 02745",pop:100731,bond:null,free_cash:2.0,pension:68.0,debt_pc:2024.0,gfoa:null,tax_non_res:25.0,eff_rate:1.437,med_tax:4239,med_inc:56025,res_rate:14.37,d_rank:338,d_total:351,d_10yr:null,math:17.0,grad:79.9,ap:13.6,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town) — South Coast Rail",violent:600.0,prop_crime:2600.0,crime5yr:null,inc10yr:55.6,pop10yr:6.1,bach:16.8,unemp:7.6,pov:19.9,flood:15.0,flood50:7.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Third-largest MA city with South Coast Rail access. Historic working port with the lowest home prices in this dataset. Schools #338 of 351 and high crime are the defining trade-offs.",glance:"New Bedford is a large coastal city with South Coast Rail access to South Station and the lowest home prices in this batch. The trade-offs are substantial — schools rank #338 of 351, crime is among the highest in MA, and poverty runs at 20%. The price-to-income math is the primary draw.",notes:"Bristol County Retirement (~68% est -- verify PERAC). Very low free cash (2.0%) is a fiscal stress flag. Bond not rated -- verify EMMA.",med_home_val:295000,commute:28,owner_occ:45.0,vacancy:9.0,med_age:38.0,low_income_pct:70.0,ell_pct:22.0,enrollment_trend:null,sex_off:0.75,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Fall River",lat:41.7015,lng:-71.1550,state:"MA",county:"Bristol",zip:"02720 / 02721 / 02723 / 02724",pop:93764,bond:null,free_cash:1.8,pension:68.0,debt_pc:2429.0,gfoa:null,tax_non_res:20.0,eff_rate:1.282,med_tax:3461,med_inc:53933,res_rate:12.82,d_rank:342,d_total:351,d_10yr:null,math:18.0,grad:76.8,ap:17.4,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (in town) — South Coast Rail",violent:700.0,prop_crime:2400.0,crime5yr:null,inc10yr:62.4,pop10yr:5.6,bach:16.8,unemp:8.1,pov:20.9,flood:10.0,flood50:5.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Large city with South Coast Rail access and the lowest home prices in this batch (~$270k). Schools #342 of 351 and the highest violent crime in the dataset are the principal trade-offs.",glance:"Fall River is a large city with South Coast Rail access to Providence and South Station and the lowest home prices in this batch. Schools rank #342 of 351 and crime is among the highest in Massachusetts — the very low price point (~$270k median) reflects those structural realities.",notes:"Bristol County Retirement (~68% est -- verify PERAC). Very low free cash (1.8%) -- fiscal stress flag. Bond not rated -- verify EMMA.",med_home_val:270000,commute:30,owner_occ:42.0,vacancy:10.0,med_age:38.0,low_income_pct:75.0,ell_pct:22.0,enrollment_trend:null,sex_off:0.85,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Dartmouth",lat:41.6376,lng:-70.9773,state:"MA",county:"Bristol",zip:"02747 / 02748",pop:32621,bond:null,free_cash:5.5,pension:68.0,debt_pc:1573.0,gfoa:null,tax_non_res:15.0,eff_rate:0.994,med_tax:4622,med_inc:98662,res_rate:9.94,d_rank:160,d_total:351,d_10yr:null,math:45.0,grad:92.4,ap:33.7,transp:"Yes",elec_save:0,water_viol:0,transit:"None (New Bedford South Coast Rail 5 mi)",violent:80.0,prop_crime:600.0,crime5yr:null,inc10yr:45.1,pop10yr:-4.9,bach:38.5,unemp:4.2,pov:6.0,flood:12.0,flood50:5.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Coastal suburb south of New Bedford with the lowest residential tax rate in the Bristol batch (9.94) and solid schools (#160 of 351). Home to UMass Dartmouth.",glance:"Dartmouth is a coastal suburban town with the lowest residential tax rate in the Bristol batch (0.99%) and solid schools (#160 of 351, 92.4% graduation). Negative 10-year population growth (-4.9%) and moderate coastal flood risk are the two cautionary signals for long-term buyers.",notes:"Bristol County Retirement (~68% est -- verify PERAC). Bond not rated -- verify EMMA. UMass Dartmouth campus. Negative pop growth unusual -- verify Census.",med_home_val:465000,commute:28,owner_occ:72.0,vacancy:5.0,med_age:42.0,low_income_pct:22.0,ell_pct:5.0,enrollment_trend:null,sex_off:0.30,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Norton",lat:41.9734,lng:-71.1856,state:"MA",county:"Bristol",zip:"02766",pop:19155,bond:null,free_cash:6.4,pension:68.0,debt_pc:1264.0,gfoa:null,tax_non_res:10.0,eff_rate:1.400,med_tax:7630,med_inc:127404,res_rate:14.00,d_rank:195,d_total:351,d_10yr:null,math:34.0,grad:93.0,ap:25.2,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (nearby) — Providence/Stoughton at Attleboro (4 mi)",violent:60.0,prop_crime:500.0,crime5yr:null,inc10yr:57.2,pop10yr:-0.3,bach:45.8,unemp:3.5,pov:4.8,flood:6.0,flood50:2.5,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Quiet Bristol County suburb with high incomes ($127k), very low crime, and strong income growth (+57% over 10 yrs). Wheaton College in town.",glance:"Norton is a quiet suburban town with high household incomes ($127k median), very low crime, and solid schools (#195 of 351, 93% graduation). Strong income growth (+57% over 10 years) and proximity to the Attleboro commuter rail station (4 miles) make it one of the better-value picks in Bristol County.",notes:"Bristol County Retirement (~68% est -- verify PERAC). Bond not rated -- verify EMMA. Wheaton College in town.",med_home_val:545000,commute:32,owner_occ:82.0,vacancy:4.0,med_age:40.0,low_income_pct:15.0,ell_pct:5.0,enrollment_trend:null,sex_off:0.22,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Seekonk",lat:41.8323,lng:-71.3217,state:"MA",county:"Bristol",zip:"02771",pop:15573,bond:null,free_cash:4.8,pension:68.0,debt_pc:509.0,gfoa:null,tax_non_res:22.0,eff_rate:1.275,med_tax:5674,med_inc:116310,res_rate:12.75,d_rank:115,d_total:351,d_10yr:null,math:53.0,grad:96.8,ap:32.0,transp:"Yes",elec_save:0,water_viol:0,transit:"None (Providence, RI 7 mi)",violent:80.0,prop_crime:700.0,crime5yr:null,inc10yr:63.9,pop10yr:11.8,bach:43.3,unemp:6.0,pov:4.4,flood:7.0,flood50:3.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Best schools in the Bristol County batch (#115 of 351, 96.8% grad, 53% MCAS math). Very low debt ($509/capita) and fast population growth (+12% over 10 yrs).",glance:"Seekonk has the strongest schools in the Bristol County batch (#115 of 351, 96.8% graduation, 53% MCAS math), very low debt, and fast population growth (+12% over 10 years). The bordering Providence, RI location provides effective metro access without an MBTA stop.",notes:"Bristol County Retirement (~68% est -- verify PERAC). Bond not rated -- verify EMMA. Large Route 6 commercial corridor.",med_home_val:445000,commute:25,owner_occ:75.0,vacancy:4.0,med_age:43.0,low_income_pct:15.0,ell_pct:5.0,enrollment_trend:null,sex_off:0.30,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Raynham",lat:41.9387,lng:-71.0550,state:"MA",county:"Bristol",zip:"02767 / 02768",pop:15273,bond:null,free_cash:7.8,pension:68.0,debt_pc:1216.0,gfoa:null,tax_non_res:15.0,eff_rate:1.274,med_tax:5988,med_inc:117950,res_rate:12.74,d_rank:215,d_total:351,d_10yr:null,math:34.0,grad:93.4,ap:25.8,transp:"Yes",elec_save:0,water_viol:0,transit:"Commuter Rail (nearby) — South Coast Rail at Taunton (5 mi)",violent:100.0,prop_crime:700.0,crime5yr:null,inc10yr:46.7,pop10yr:13.8,bach:40.2,unemp:5.6,pov:9.1,flood:8.0,flood50:3.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Fast-growing town (pop +14%) adjacent to Taunton with above-average incomes ($118k). Bridgewater-Raynham schools (#215 of 351, 93.4% grad). South Coast Rail 5 mi at Taunton.",glance:"Raynham is a fast-growing town (population +14% over 10 years) with above-average incomes ($118k median) and solid schools through Bridgewater-Raynham district (#215 of 351, 93.4% graduation). South Coast Rail at Taunton is 5 miles away; Taunton River flood risk affects some properties.",notes:"Bristol County Retirement (~68% est -- verify PERAC). Bond not rated -- verify EMMA. DISTRICT_MAP: bridgewater-raynham.",med_home_val:470000,commute:31,owner_occ:78.0,vacancy:3.5,med_age:41.0,low_income_pct:20.0,ell_pct:8.0,enrollment_trend:null,sex_off:0.28,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Rehoboth",lat:41.8459,lng:-71.2467,state:"MA",county:"Bristol",zip:"02769",pop:12809,bond:null,free_cash:2.9,pension:68.0,debt_pc:19.0,gfoa:null,tax_non_res:6.0,eff_rate:1.346,med_tax:7336,med_inc:126161,res_rate:13.46,d_rank:140,d_total:351,d_10yr:null,math:52.0,grad:91.9,ap:18.6,transp:"Yes",elec_save:0,water_viol:0,transit:"None (Providence, RI 15 mi)",violent:30.0,prop_crime:350.0,crime5yr:null,inc10yr:52.9,pop10yr:9.8,bach:41.6,unemp:3.5,pov:5.1,flood:5.0,flood50:2.0,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Rural town bordering Providence with the lowest debt per capita of any town in the Civica dataset ($19). Dighton-Rehoboth schools (#140 of 351, 91.9% grad). Very low crime.",glance:"Rehoboth is a rural town with the lowest debt per capita in the Civica dataset ($19), above-average incomes ($126k median), and strong schools through Dighton-Rehoboth district (#140 of 351, 91.9% graduation). Very low crime and growing population (+10% over 10 years) round out the fundamentals.",notes:"Bristol County Retirement (~68% est -- verify PERAC). Bond not rated -- verify EMMA. DISTRICT_MAP: dighton-rehoboth. $19 debt/capita is unusually low -- verify MA DLS.",med_home_val:545000,commute:30,owner_occ:90.0,vacancy:3.0,med_age:44.0,low_income_pct:10.0,ell_pct:2.0,enrollment_trend:null,sex_off:0.18,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',

    '{name:"Swansea",lat:41.7548,lng:-71.2065,state:"MA",county:"Bristol",zip:"02777",pop:17231,bond:null,free_cash:30.4,pension:68.0,debt_pc:400.0,gfoa:null,tax_non_res:12.0,eff_rate:1.237,med_tax:5195,med_inc:116627,res_rate:12.37,d_rank:175,d_total:351,d_10yr:null,math:50.0,grad:93.0,ap:22.1,transp:"Yes",elec_save:0,water_viol:0,transit:"None (Providence, RI 8 mi)",violent:80.0,prop_crime:650.0,crime5yr:null,inc10yr:64.3,pop10yr:8.0,bach:34.2,unemp:4.7,pov:2.8,flood:8.0,flood50:3.5,fire:"Low",score:0,ter:null,ter_r:"N/A",gaps:3,conf:"medium",standout:"Suburban Bristol County town with exceptional free cash (30.4% -- among highest in MA) and very low debt ($400/capita). Highest income growth in this batch (+64% over 10 yrs).",glance:"Swansea has exceptional fiscal reserves — 30.4% free cash is among the highest of any Massachusetts town — very low debt ($400/capita), and above-average incomes ($117k). Schools rank #175 of 351 and the strongest income growth in the batch (+64% over 10 years) signals a healthy trajectory.",notes:"Bristol County Retirement (~68% est -- verify PERAC). Bond not rated -- verify EMMA. Free cash 30.4% may reflect a one-time certification -- verify MA DLS for consistency.",med_home_val:420000,commute:28,owner_occ:82.0,vacancy:4.0,med_age:43.0,low_income_pct:18.0,ell_pct:4.0,enrollment_trend:null,sex_off:0.25,p_schools:50,p_safety:50,p_taxes:50,p_fiscal:50,p_econ:50,p_qol:50,p_climate:50,value_rating:"Market Rate",value_score:null}',
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

# 2a. ZHVI entries -- insert after Mashpee line
NEW_ZHVI = (
    '    "Worcester":310000,"Leominster":375000,"Fitchburg":310000,"Auburn":400000,\n'
    '    "Holden":490000,"Southborough":790000,"Sutton":610000,"Upton":640000,\n'
    '    "Millbury":430000,"Leicester":365000,\n'
    '    "Attleboro":435000,"Taunton":395000,"New Bedford":295000,"Fall River":270000,\n'
    '    "Dartmouth":465000,"Norton":545000,"Seekonk":445000,"Raynham":470000,\n'
    '    "Rehoboth":545000,"Swansea":420000,\n'
)
if '"Worcester":310000' not in py_text:
    py_text = re.sub(
        r'("Orleans":\d+,"Mashpee":\d+,\n)',
        r'\1' + NEW_ZHVI,
        py_text
    )
    print("  Added ZHVI entries")
else:
    print("  ZHVI entries already present")

# 2b. COUNTY_MAP entries -- insert after Mashpee line
NEW_COUNTY = (
    '    "Worcester":"Worcester","Leominster":"Worcester","Fitchburg":"Worcester",\n'
    '    "Auburn":"Worcester","Holden":"Worcester","Southborough":"Worcester",\n'
    '    "Sutton":"Worcester","Upton":"Worcester","Millbury":"Worcester","Leicester":"Worcester",\n'
    '    "Attleboro":"Bristol","Taunton":"Bristol","New Bedford":"Bristol","Fall River":"Bristol",\n'
    '    "Dartmouth":"Bristol","Norton":"Bristol","Seekonk":"Bristol","Raynham":"Bristol",\n'
    '    "Rehoboth":"Bristol","Swansea":"Bristol",\n'
)
if '"Worcester":"Worcester"' not in py_text:
    py_text = re.sub(
        r'("Orleans":"Barnstable","Mashpee":"Barnstable",\n)',
        r'\1' + NEW_COUNTY,
        py_text
    )
    print("  Added COUNTY_MAP entries")
else:
    print("  COUNTY_MAP entries already present")

# 2c. DISTRICT_MAP entries for regional districts
DISTRICT_ADD = (
    '    "Holden":               "wachusett",\n'
    '    "Southborough":         "northborough-southborough",\n'
    '    "Upton":                "mendon-upton",\n'
    '    "Raynham":              "bridgewater-raynham",\n'
    '    "Rehoboth":             "dighton-rehoboth",\n'
)
if '"Holden":' not in py_text.split("DISTRICT_MAP")[1].split("}")[0]:
    py_text = re.sub(
        r'(    "Orleans":               "nauset",\n)',
        r'\1' + DISTRICT_ADD,
        py_text
    )
    print("  Added DISTRICT_MAP entries")
else:
    print("  DISTRICT_MAP entries already present")

# 2d. MATH_OVERRIDE for Southborough (K-5 MCAS; HS uses northborough-southborough)
SOUTH_OVERRIDE = '    "Southborough": 74.0,  # Southborough Elementary K-5 MCAS; Algonquin Regional HS data used for grad/AP\n'
if '"Southborough"' not in py_text.split("MATH_OVERRIDES")[1].split("}")[0]:
    py_text = re.sub(
        r'("Brewster":  60\.0.*?\n)',
        r'\1' + SOUTH_OVERRIDE,
        py_text
    )
    print("  Added Southborough MATH_OVERRIDE")
else:
    print("  Southborough MATH_OVERRIDE already present")

PY_FILE.write_text(py_text, encoding="utf-8")
print("  update_all.py patched")

# ---- Step 3: Add to TOWNS array in civica-v5.html ---------------------------
print("\nStep 3: Patching civica-v5.html...")
html_text = HTML_FILE.read_text(encoding="utf-8")

added_html = 0
for entry in NEW_HTML:
    town_name = entry.split('name:"')[1].split('"')[0]
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
html_text = HTML_FILE.read_text(encoding="utf-8")

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
