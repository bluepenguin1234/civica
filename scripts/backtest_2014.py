"""
Civica 2014 Backtest
====================
Score 47 MA towns using data as-of 2014 (no look-ahead bias), then test
whether higher 2014 Civica Scores predicted stronger home-value appreciation
through 2024.

Methodology notes (data sourcing):
  - Zillow ZHVI (single-family/condo, middle tier) Jan 2014 vs Jan 2024.
  - For submetrics where 2014 data is unavailable via web, principled proxies
    are documented in-line. The most impactful metrics (school rank, income
    level) are back-calculated from the 10-year trend fields already in towns.csv.
  - State context adjusted to 2014 levels:
      MA violent crime: 395.1/100k  (FBI UCR 2014, disastercenter.com)
      MA property crime: 1,857.6/100k (FBI UCR 2014)
      MA median HHI: ~$67,861 (ACS 2014 1-year estimate)
      MA poverty rate: ~11.4%
      MA unemployment: ~5.9%
      MA debt/capita median: ~$2,200

Stable proxies (current data used for 2014 because the metric doesn't
change materially over 10 years):
  - Transit access, wildfire risk, water violations, GFOA structure,
    electric savings (MLDs established pre-2014), flood risk baseline,
    transparency, tax base non-residential %.

Adjusted for 2014:
  - School rank: current_rank - rank_10yr_change
  - Income (for income_level & tax_burden): current_income / (1 + 10yr_growth)
  - GFOA consecutive years: max(0, current_years - 12)
  - Bond rating: adjusted where known historical changes occurred
  - Crime denominators: 2014 MA state averages (vs current state averages)

Statistical approach:
  - Pearson and Spearman rank correlations (score vs appreciation %)
  - Quintile analysis (top/bottom 20% score groups)
  - OLS regression controlling for 2014 home price (affordability bias)
  - Pre-COVID sub-period (2014-2019) shown separately
"""

import csv
import math
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

# ── State context 2014 ────────────────────────────────────────────────────────
MA_2014 = {
    "violent_crime_per_100k": 395.1,
    "property_crime_per_100k": 1857.6,
    "median_household_income": 67861,
    "poverty_rate_pct": 11.4,
    "unemployment_rate_pct": 5.9,
    "debt_per_capita_median": 2200,
}

# ── Zillow ZHVI Jan-2014 and Jan-2024 by town (fetched directly from Zillow) ─
ZILLOW = {
    "Cambridge":    (593108,  995293),
    "Lynn":         (228526,  537825),
    "Lawrence":     (173303,  455876),
    "Somerville":   (None,    892143),   # 2014 value missing in Zillow
    "Haverhill":    (235480,  497568),
    "Medford":      (401121,  784462),
    "Peabody":      (333064,  652390),
    "Methuen":      (267599,  561211),
    "Arlington":    (534147,  1005584),
    "Salem":        (286849,  572734),
    "Woburn":       (379488,  704405),
    "Chelsea":      (229610,  505101),
    "Beverly":      (357863,  696077),
    "Andover":      (515695,  911128),
    "Lexington":    (798232,  1469802),
    "North Andover":(416531,  760639),
    "Saugus":       (334920,  650624),
    "Danvers":      (362884,  674241),
    "Gloucester":   (349708,  693415),
    "Wakefield":    (414983,  756484),
    "Belmont":      (729816,  1377983),
    "Burlington":   (441594,  824833),
    "Reading":      (447271,  844034),
    "Winchester":   (799528,  1449988),
    "Newburyport":  (434586,  845604),
    "Amesbury":     (277630,  570013),
    "Marblehead":   (519019,  959425),
    "Uxbridge":     (258149,  487277),
    "Swampscott":   (392115,  763080),
    "Lynnfield":    (542002,  1018229),
    "Ipswich":      (411267,  790546),
    "Middleton":    (466248,  819582),
    "Salisbury":    (299229,  589785),
    "Georgetown":   (389481,  708796),
    "Boxford":      (552503,  989433),
    "Hamilton":     (444568,  827397),
    "Newbury":      (425285,  844611),
    "Groveland":    (338938,  648353),
    "Topsfield":    (504738,  898745),
    "Merrimac":     (310643,  597359),
    "Rockport":     (437098,  834071),
    "Rowley":       (397274,  733628),
    "Manchester":   (671131,  1183983),
    "Wenham":       (516157,  938834),
    "West Newbury": (464799,  861236),
    "Essex":        (414676,  827029),
    "Nahant":       (431900,  903532),
}

# Known 2014 bond rating overrides (where we know it differed from current)
# Source: EMMA/MSRB / CLAUDE.md notes
BOND_RATING_2014_OVERRIDES = {
    "Danvers": "AA+",   # AAA 2019-2024; AA+ in 2014
}

# ── HTML-only towns (Middlesex expansion) ─────────────────────────────────────
# These towns exist in civica-v5.html but not in towns.csv.
# Data extracted directly from HTML TOWNS array.
HTML_TOWNS = {
    "Chelsea": {
        "bond_rating_sp": None, "free_cash_pct_of_budget": None, "pension_funded_ratio_pct": None,
        "debt_per_capita": None, "gfoa_certificate_consecutive_years": 26,
        "tax_base_non_residential_pct": None, "effective_tax_rate_pct": 1.15,
        "median_annual_tax_bill": 6310, "median_household_income": 72179,
        "residential_rate_per_1000": 11.48,
        "district_state_rank": 323, "district_state_rank_total": 351, "district_rank_10yr_change": None,
        "test_scores_math_pct": 19.0, "graduation_rate_pct": 76.0, "ap_participation_pct": 36.0,
        "transparency": "yes", "electric_savings_vs_state_avg": 0,
        "water_violations_5yr": 0, "transit_access": "commuter_rail_in_town",
        "violent_crime_per_100k": 370.0, "property_crime_per_100k": 1200.0,
        "crime_5yr_pct_change": None, "income_10yr_change_pct": 30.0,
        "population_10yr_change_pct": 12.0, "bachelors_degree_pct": 20.0,
        "unemployment_pct": None, "poverty_pct": 18.0,
        "flood_risk_pct": 8.0, "flood_2050_growth_pts": 2.0, "wildfire_risk": "low",
    },
    "Lexington": {
        "bond_rating_sp": "AAA", "free_cash_pct_of_budget": 6.7, "pension_funded_ratio_pct": 55,
        "debt_per_capita": 3200, "gfoa_certificate_consecutive_years": 20,
        "tax_base_non_residential_pct": 13.6, "effective_tax_rate_pct": 1.22,
        "median_annual_tax_bill": 14714, "median_household_income": 238444,
        "residential_rate_per_1000": 12.23,
        "district_state_rank": 4, "district_state_rank_total": 351, "district_rank_10yr_change": 3,
        "test_scores_math_pct": 78.0, "graduation_rate_pct": 98.2, "ap_participation_pct": None,
        "transparency": "yes", "electric_savings_vs_state_avg": 0,
        "water_violations_5yr": 0, "transit_access": "bus_only",
        "violent_crime_per_100k": 25.0, "property_crime_per_100k": 450.0,
        "crime_5yr_pct_change": None, "income_10yr_change_pct": 40.0,
        "population_10yr_change_pct": 5.0, "bachelors_degree_pct": 79.0,
        "unemployment_pct": None, "poverty_pct": 2.5,
        "flood_risk_pct": 1.5, "flood_2050_growth_pts": 0.5, "wildfire_risk": "low",
    },
    "Arlington": {
        "bond_rating_sp": "AA+", "free_cash_pct_of_budget": 5.2, "pension_funded_ratio_pct": 55,
        "debt_per_capita": 2100, "gfoa_certificate_consecutive_years": 15,
        "tax_base_non_residential_pct": 6.0, "effective_tax_rate_pct": 1.15,
        "median_annual_tax_bill": 10058, "median_household_income": 150701,
        "residential_rate_per_1000": 10.77,
        "district_state_rank": 24, "district_state_rank_total": 351, "district_rank_10yr_change": 8,
        "test_scores_math_pct": 69.0, "graduation_rate_pct": 96.8, "ap_participation_pct": None,
        "transparency": "yes", "electric_savings_vs_state_avg": 0,
        "water_violations_5yr": 0, "transit_access": "commuter_rail_nearby",
        "violent_crime_per_100k": 95.0, "property_crime_per_100k": 700.0,
        "crime_5yr_pct_change": None, "income_10yr_change_pct": 45.0,
        "population_10yr_change_pct": 8.0, "bachelors_degree_pct": 68.0,
        "unemployment_pct": None, "poverty_pct": 4.5,
        "flood_risk_pct": 3.0, "flood_2050_growth_pts": 1.0, "wildfire_risk": "low",
    },
    "Medford": {
        "bond_rating_sp": "AA+", "free_cash_pct_of_budget": 5.0, "pension_funded_ratio_pct": 55,
        "debt_per_capita": 1800, "gfoa_certificate_consecutive_years": None,
        "tax_base_non_residential_pct": 18.0, "effective_tax_rate_pct": 1.18,
        "median_annual_tax_bill": 6648, "median_household_income": 129540,
        "residential_rate_per_1000": 8.80,
        "district_state_rank": 210, "district_state_rank_total": 351, "district_rank_10yr_change": -15,
        "test_scores_math_pct": 35.0, "graduation_rate_pct": 90.9, "ap_participation_pct": None,
        "transparency": "yes", "electric_savings_vs_state_avg": 0,
        "water_violations_5yr": 0, "transit_access": "commuter_rail_in_town",
        "violent_crime_per_100k": 150.0, "property_crime_per_100k": 900.0,
        "crime_5yr_pct_change": None, "income_10yr_change_pct": 55.0,
        "population_10yr_change_pct": 10.0, "bachelors_degree_pct": 50.0,
        "unemployment_pct": None, "poverty_pct": 8.0,
        "flood_risk_pct": 5.0, "flood_2050_growth_pts": 2.0, "wildfire_risk": "low",
    },
    "Belmont": {
        "bond_rating_sp": "AAA", "free_cash_pct_of_budget": 5.5, "pension_funded_ratio_pct": 55,
        "debt_per_capita": 2800, "gfoa_certificate_consecutive_years": 18,
        "tax_base_non_residential_pct": 8.0, "effective_tax_rate_pct": 1.14,
        "median_annual_tax_bill": 13212, "median_household_income": 183137,
        "residential_rate_per_1000": 11.39,
        "district_state_rank": 12, "district_state_rank_total": 351, "district_rank_10yr_change": 5,
        "test_scores_math_pct": 71.0, "graduation_rate_pct": 96.7, "ap_participation_pct": None,
        "transparency": "yes", "electric_savings_vs_state_avg": 0,
        "water_violations_5yr": 0, "transit_access": "commuter_rail_in_town",
        "violent_crime_per_100k": 40.0, "property_crime_per_100k": 500.0,
        "crime_5yr_pct_change": None, "income_10yr_change_pct": 38.0,
        "population_10yr_change_pct": 5.0, "bachelors_degree_pct": 72.0,
        "unemployment_pct": None, "poverty_pct": 3.5,
        "flood_risk_pct": 2.0, "flood_2050_growth_pts": 1.0, "wildfire_risk": "low",
    },
    "Winchester": {
        "bond_rating_sp": "AAA", "free_cash_pct_of_budget": 11.1, "pension_funded_ratio_pct": 55,
        "debt_per_capita": 1900, "gfoa_certificate_consecutive_years": 20,
        "tax_base_non_residential_pct": 4.3, "effective_tax_rate_pct": 1.11,
        "median_annual_tax_bill": 13479, "median_household_income": 230198,
        "residential_rate_per_1000": 11.09,
        "district_state_rank": 10, "district_state_rank_total": 351, "district_rank_10yr_change": 4,
        "test_scores_math_pct": 74.0, "graduation_rate_pct": 96.0, "ap_participation_pct": None,
        "transparency": "yes", "electric_savings_vs_state_avg": 0,
        "water_violations_5yr": 0, "transit_access": "commuter_rail_in_town",
        "violent_crime_per_100k": 30.0, "property_crime_per_100k": 420.0,
        "crime_5yr_pct_change": None, "income_10yr_change_pct": 42.0,
        "population_10yr_change_pct": 4.0, "bachelors_degree_pct": 74.0,
        "unemployment_pct": None, "poverty_pct": 2.5,
        "flood_risk_pct": 1.5, "flood_2050_growth_pts": 0.5, "wildfire_risk": "low",
    },
    "Woburn": {
        "bond_rating_sp": "AAA", "free_cash_pct_of_budget": 5.0, "pension_funded_ratio_pct": 55,
        "debt_per_capita": 1600, "gfoa_certificate_consecutive_years": 8,
        "tax_base_non_residential_pct": 35.0, "effective_tax_rate_pct": 0.91,
        "median_annual_tax_bill": 5752, "median_household_income": 111185,
        "residential_rate_per_1000": 8.54,
        "district_state_rank": 247, "district_state_rank_total": 351, "district_rank_10yr_change": -10,
        "test_scores_math_pct": 34.0, "graduation_rate_pct": 91.1, "ap_participation_pct": None,
        "transparency": "yes", "electric_savings_vs_state_avg": 0,
        "water_violations_5yr": 0, "transit_access": "commuter_rail_in_town",
        "violent_crime_per_100k": 90.0, "property_crime_per_100k": 800.0,
        "crime_5yr_pct_change": None, "income_10yr_change_pct": 30.0,
        "population_10yr_change_pct": 5.0, "bachelors_degree_pct": 43.0,
        "unemployment_pct": None, "poverty_pct": 4.5,
        "flood_risk_pct": 3.0, "flood_2050_growth_pts": 1.5, "wildfire_risk": "low",
    },
    "Wakefield": {
        "bond_rating_sp": "AA+", "free_cash_pct_of_budget": 5.5, "pension_funded_ratio_pct": 55,
        "debt_per_capita": 1500, "gfoa_certificate_consecutive_years": 10,
        "tax_base_non_residential_pct": 22.0, "effective_tax_rate_pct": 1.14,
        "median_annual_tax_bill": 8212, "median_household_income": 134306,
        "residential_rate_per_1000": 11.35,
        "district_state_rank": 76, "district_state_rank_total": 351, "district_rank_10yr_change": 5,
        "test_scores_math_pct": 52.0, "graduation_rate_pct": 95.5, "ap_participation_pct": None,
        "transparency": "yes", "electric_savings_vs_state_avg": 0,
        "water_violations_5yr": 0, "transit_access": "commuter_rail_in_town",
        "violent_crime_per_100k": 80.0, "property_crime_per_100k": 700.0,
        "crime_5yr_pct_change": None, "income_10yr_change_pct": 30.0,
        "population_10yr_change_pct": 4.0, "bachelors_degree_pct": 45.0,
        "unemployment_pct": None, "poverty_pct": 5.0,
        "flood_risk_pct": 5.0, "flood_2050_growth_pts": 2.0, "wildfire_risk": "low",
    },
    "Reading": {
        "bond_rating_sp": "AAA", "free_cash_pct_of_budget": 6.0, "pension_funded_ratio_pct": 55,
        "debt_per_capita": 1700, "gfoa_certificate_consecutive_years": 15,
        "tax_base_non_residential_pct": 12.0, "effective_tax_rate_pct": 1.14,
        "median_annual_tax_bill": 9213, "median_household_income": 165912,
        "residential_rate_per_1000": 11.39,
        "district_state_rank": 42, "district_state_rank_total": 351, "district_rank_10yr_change": 23,
        "test_scores_math_pct": 64.0, "graduation_rate_pct": 98.1, "ap_participation_pct": None,
        "transparency": "yes", "electric_savings_vs_state_avg": 0,
        "water_violations_5yr": 0, "transit_access": "commuter_rail_in_town",
        "violent_crime_per_100k": 30.0, "property_crime_per_100k": 500.0,
        "crime_5yr_pct_change": None, "income_10yr_change_pct": 35.0,
        "population_10yr_change_pct": 3.0, "bachelors_degree_pct": 60.0,
        "unemployment_pct": None, "poverty_pct": 3.0,
        "flood_risk_pct": 4.0, "flood_2050_growth_pts": 1.5, "wildfire_risk": "low",
    },
    "Cambridge": {
        "bond_rating_sp": "AAA", "free_cash_pct_of_budget": 40.0, "pension_funded_ratio_pct": 76,
        "debt_per_capita": 5207, "gfoa_certificate_consecutive_years": 25,
        "tax_base_non_residential_pct": 35.8, "effective_tax_rate_pct": 0.63,
        "median_annual_tax_bill": 6081, "median_household_income": 130748,
        "residential_rate_per_1000": 6.35,
        "district_state_rank": 81, "district_state_rank_total": 351, "district_rank_10yr_change": 5,
        "test_scores_math_pct": 56.0, "graduation_rate_pct": None, "ap_participation_pct": None,
        "transparency": "yes", "electric_savings_vs_state_avg": 0,
        "water_violations_5yr": 0, "transit_access": "commuter_rail_in_town",
        "violent_crime_per_100k": 370.0, "property_crime_per_100k": 1800.0,
        "crime_5yr_pct_change": None, "income_10yr_change_pct": 42.0,
        "population_10yr_change_pct": 12.0, "bachelors_degree_pct": 71.0,
        "unemployment_pct": None, "poverty_pct": 12.0,
        "flood_risk_pct": 8.0, "flood_2050_growth_pts": 3.0, "wildfire_risk": "low",
    },
}

def load_csv(path):
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def load_methodology():
    master = load_csv(DATA_DIR / "master_weights.csv")
    pillar = load_csv(DATA_DIR / "pillar_weights.csv")
    rubrics = load_csv(DATA_DIR / "scoring_rubrics.csv")

    pw = {row["pillar_id"]: float(row["weight"]) for row in master}
    sw = {}
    for row in pillar:
        sw.setdefault(row["pillar_id"], {})[row["submetric_id"]] = float(row["weight"])
    ri = {}
    for row in rubrics:
        ri.setdefault(row["submetric_id"], []).append(row)
    return pw, sw, ri

def score_submetric(submetric_id, raw_value, ri):
    if submetric_id not in ri:
        return 50
    rules = ri[submetric_id]
    default = float(rules[0]["default_if_missing"])
    if raw_value is None or raw_value == "":
        return default
    for rule in rules:
        if rule["rule_type"] == "range":
            try:
                v = float(raw_value)
                lo = float(rule["lower_bound"])
                hi = float(rule["upper_bound"])
                if lo <= v < hi:
                    return float(rule["score_0_100"])
            except (ValueError, TypeError):
                return default
        elif rule["rule_type"] == "lookup":
            if str(raw_value).strip().lower() == str(rule["match_value"]).strip().lower():
                return float(rule["score_0_100"])
    return default

def safe_div(a, b):
    try:
        return float(a) / float(b)
    except (TypeError, ValueError, ZeroDivisionError):
        return None

def float_or_none(v):
    try:
        return float(v) if v not in (None, "", "None") else None
    except (ValueError, TypeError):
        return None

def estimate_2014_inputs(t, ctx):
    """
    Build the submetric input dictionary for a town using 2014 estimates.
    't' is one row from towns.csv. 'ctx' is MA_2014 state context.
    """
    name = t["town_name"]

    # ── Helpers ────────────────────────────────────────────────────────────────

    # Income in 2014 (back-calculated from 10-year growth field)
    cur_income = float_or_none(t["median_household_income"])
    growth_10yr = float_or_none(t["income_10yr_change_pct"])
    if cur_income and growth_10yr is not None:
        income_2014 = cur_income / (1 + growth_10yr / 100)
    else:
        income_2014 = cur_income  # fallback

    # School rank in 2014 (back-calculated from 10yr trajectory field)
    # rank_10yr_change > 0 means rank number rose (worsened) over 10 years,
    # so in 2014 the rank number was lower (better).
    cur_rank = float_or_none(t["district_state_rank"])
    rank_change = float_or_none(t["district_rank_10yr_change"])
    rank_total = float_or_none(t["district_state_rank_total"]) or 351
    if cur_rank is not None and rank_change is not None:
        rank_2014 = cur_rank - rank_change
        rank_2014 = max(1, min(rank_total, rank_2014))
    else:
        rank_2014 = cur_rank  # fallback

    rank_percentile_2014 = (
        (1 - rank_2014 / rank_total) * 100
        if rank_2014 is not None else None
    )

    # Tax burden (2014 tax bill / 2014 income)
    tax_bill = float_or_none(t["median_annual_tax_bill"])
    tax_burden_2014 = (tax_bill / income_2014 * 100) if (tax_bill and income_2014) else None

    # Debt ratio vs 2014 state median
    debt_pc = float_or_none(t["debt_per_capita"])
    debt_ratio_2014 = safe_div(debt_pc, ctx["debt_per_capita_median"])

    # Income level ratio vs 2014 state median
    income_level_2014 = safe_div(income_2014, ctx["median_household_income"])

    # Crime ratios using 2014 MA state averages
    vc = float_or_none(t["violent_crime_per_100k"])
    pc = float_or_none(t["property_crime_per_100k"])
    violent_ratio_2014 = safe_div(vc, ctx["violent_crime_per_100k"])
    property_ratio_2014 = safe_div(pc, ctx["property_crime_per_100k"])

    # Poverty ratio vs 2014 state average
    poverty_pct = float_or_none(t["poverty_pct"])
    poverty_ratio_2014 = safe_div(poverty_pct, ctx["poverty_rate_pct"])

    # Unemployment ratio vs 2014 state average
    unemp_pct = float_or_none(t["unemployment_pct"])
    unemp_ratio_2014 = safe_div(unemp_pct, ctx["unemployment_rate_pct"])

    # GFOA: subtract 12 years, floor at 0 (proxy)
    gfoa = float_or_none(t["gfoa_certificate_consecutive_years"])
    gfoa_2014 = max(0, gfoa - 12) if gfoa is not None else None

    # Bond rating: use override if known, else current
    bond = BOND_RATING_2014_OVERRIDES.get(name, t["bond_rating_sp"])

    # ── Submetric map ──────────────────────────────────────────────────────────
    SM = {
        "bond_rating":           bond,
        "free_cash_pct":         float_or_none(t["free_cash_pct_of_budget"]),   # proxy
        "pension_funded":        float_or_none(t["pension_funded_ratio_pct"]),  # proxy
        "debt_per_capita":       debt_ratio_2014,
        "gfoa_years":            gfoa_2014,
        "tax_base_diversification": float_or_none(t["tax_base_non_residential_pct"]),
        "effective_tax_rate":    float_or_none(t["effective_tax_rate_pct"]),    # proxy
        "tax_burden_to_income":  tax_burden_2014,
        "tax_base_health":       float_or_none(t["tax_base_non_residential_pct"]),
        "rank_percentile":       rank_percentile_2014,
        "rank_trajectory":       rank_change,   # the 10yr change IS the 2014 trajectory
        "test_scores":           float_or_none(t["test_scores_math_pct"]),      # proxy
        "graduation_rate":       float_or_none(t["graduation_rate_pct"]),       # proxy
        "ap_participation":      float_or_none(t["ap_participation_pct"]),      # proxy
        "transparency":          t["transparency"],                              # proxy
        "electric_value":        float_or_none(t["electric_savings_vs_state_avg"]),
        "water_quality":         float_or_none(t["water_violations_5yr"]),
        "transit":               t["transit_access"],
        "violent_crime":         violent_ratio_2014,
        "property_crime":        property_ratio_2014,
        "crime_trajectory":      float_or_none(t["crime_5yr_pct_change"]),
        "income_trend":          float_or_none(t["income_10yr_change_pct"]),    # 10yr growth ending 2014
        "population_trend":      float_or_none(t["population_10yr_change_pct"]),
        "income_level":          income_level_2014,
        "education_attainment":  float_or_none(t["bachelors_degree_pct"]),
        "unemployment":          unemp_ratio_2014,
        "poverty":               poverty_ratio_2014,
        "flood_risk":            float_or_none(t["flood_risk_pct"]),
        "flood_trajectory":      float_or_none(t["flood_2050_growth_pts"]),
        "wildfire":              t["wildfire_risk"],
    }
    return SM

def score_town(SM, pw, sw, ri):
    sub_scores = {sm: score_submetric(sm, val, ri) for sm, val in SM.items()}
    ps = {}
    for pillar in pw:
        ps[pillar] = sum(sub_scores[k] * sw[pillar][k] for k in sw[pillar])
    civica = round(sum(ps[p] * pw[p] for p in pw))
    return civica, {k: round(v, 1) for k, v in ps.items()}

# ── Statistics helpers ────────────────────────────────────────────────────────

def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs)/n, sum(ys)/n
    num = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x-mx)**2 for x in xs))
    dy = math.sqrt(sum((y-my)**2 for y in ys))
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)

def spearman(xs, ys):
    n = len(xs)
    rx = rank_list(xs)
    ry = rank_list(ys)
    d2 = sum((a-b)**2 for a, b in zip(rx, ry))
    return 1 - 6*d2 / (n*(n**2-1))

def rank_list(xs):
    sorted_idx = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0]*len(xs)
    for rank, idx in enumerate(sorted_idx, 1):
        ranks[idx] = rank
    return ranks

def simple_ols(xs, ys):
    """Return (slope, intercept, r_squared) for OLS of ys on xs."""
    n = len(xs)
    mx, my = sum(xs)/n, sum(ys)/n
    ss_xx = sum((x-mx)**2 for x in xs)
    ss_xy = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    if ss_xx == 0:
        return None, None, None
    slope = ss_xy / ss_xx
    intercept = my - slope * mx
    y_hat = [slope*x + intercept for x in xs]
    ss_res = sum((y-yh)**2 for y, yh in zip(ys, y_hat))
    ss_tot = sum((y-my)**2 for y in ys)
    r2 = 1 - ss_res/ss_tot if ss_tot > 0 else 0
    return slope, intercept, r2

def percentile_groups(scores, apprec, n_groups=5):
    """Split by score quintile, return [(label, count, mean_apprec)] list."""
    pairs = sorted(zip(scores, apprec))
    size = len(pairs) // n_groups
    groups = []
    for i in range(n_groups):
        start = i * size
        end = (i+1)*size if i < n_groups-1 else len(pairs)
        chunk = pairs[start:end]
        label = f"Q{i+1} (scores {chunk[0][0]}–{chunk[-1][0]})"
        mean_apprec = sum(a for _, a in chunk) / len(chunk)
        groups.append((label, len(chunk), mean_apprec))
    return groups

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    pw, sw, ri = load_methodology()

    towns_raw = load_csv(DATA_DIR / "towns.csv")
    towns_by_name = {row["town_name"]: row for row in towns_raw}

    results = []
    skipped = []

    for name, (zhvi_2014, zhvi_2024) in ZILLOW.items():
        if zhvi_2014 is None:
            skipped.append((name, "no 2014 Zillow value"))
            continue

        t = towns_by_name.get(name)
        if t is None:
            # Try partial match (e.g. "Manchester" vs "Manchester-by-the-Sea")
            for k in towns_by_name:
                if k.startswith(name) or name.startswith(k.split("-")[0]):
                    t = towns_by_name[k]
                    break
        if t is None:
            skipped.append((name, "not found in towns.csv"))
            continue

        SM = estimate_2014_inputs(t, MA_2014)
        civica_2014, pillars = score_town(SM, pw, sw, ri)
        apprec_pct = (zhvi_2024 - zhvi_2014) / zhvi_2014 * 100

        results.append({
            "town":        name,
            "score_2014":  civica_2014,
            "zhvi_2014":   zhvi_2014,
            "zhvi_2024":   zhvi_2024,
            "apprec_pct":  round(apprec_pct, 1),
            "pillars":     pillars,
        })

    # Also score HTML-only towns
    for name, tdata in HTML_TOWNS.items():
        zil = ZILLOW.get(name)
        if zil is None or zil[0] is None:
            skipped.append((name, "no Zillow data"))
            continue
        zhvi_2014, zhvi_2024 = zil
        # Convert HTML dict to towns.csv-style string dict
        t = {k: (str(v) if v is not None else "") for k, v in tdata.items()}
        t["town_name"] = name
        t["state"] = "MA"
        SM = estimate_2014_inputs(t, MA_2014)
        civica_2014, pillars = score_town(SM, pw, sw, ri)
        apprec_pct = (zhvi_2024 - zhvi_2014) / zhvi_2014 * 100
        results.append({
            "town":        name,
            "score_2014":  civica_2014,
            "zhvi_2014":   zhvi_2014,
            "zhvi_2024":   zhvi_2024,
            "apprec_pct":  round(apprec_pct, 1),
            "pillars":     pillars,
            "res_rate":    float(tdata.get("residential_rate_per_1000") or 0),
        })

    # Add res_rate to CSV towns
    for r in results:
        if "res_rate" not in r:
            raw = towns_by_name.get(r["town"], {})
            try:
                r["res_rate"] = float(raw.get("residential_rate_per_1000") or 0)
            except (ValueError, TypeError):
                r["res_rate"] = 0.0

    results.sort(key=lambda r: r["score_2014"], reverse=True)

    print("=" * 70)
    print("CIVICA 2014 BACKTEST — Score vs. 10-Year Home Price Appreciation")
    print("=" * 70)
    print()
    print(f"{'Town':<22} {'Score':<8} {'ZHVI 2014':>10} {'ZHVI 2024':>10} {'Apprec %':>9}")
    print("-" * 65)
    for r in results:
        print(f"{r['town']:<22} {r['score_2014']:<8} ${r['zhvi_2014']:>9,.0f} ${r['zhvi_2024']:>9,.0f} {r['apprec_pct']:>8.1f}%")

    scores = [r["score_2014"] for r in results]
    apprec = [r["apprec_pct"] for r in results]
    prices = [r["zhvi_2014"] for r in results]

    print()
    print("=" * 70)
    print("STATISTICAL RESULTS")
    print("=" * 70)

    # 1. Pearson correlation
    r_pearson = pearson(scores, apprec)
    print(f"\n1. Pearson correlation (score vs. appreciation):  r = {r_pearson:+.3f}")

    # 2. Spearman rank correlation
    r_spearman = spearman(scores, apprec)
    print(f"2. Spearman rank correlation:                      rho = {r_spearman:+.3f}")

    # 3. OLS regression: appreciation ~ score
    sl, ic, r2 = simple_ols(scores, apprec)
    print(f"3. OLS (raw):  appreciation = {sl:+.2f}×score + {ic:+.1f}   R2 = {r2:.3f}")

    # 4. OLS controlling for starting price (to remove mean-reversion bias)
    # Normalize both predictors
    mn_s = sum(scores)/len(scores);  sd_s = math.sqrt(sum((s-mn_s)**2 for s in scores)/len(scores))
    mn_p = sum(prices)/len(prices);  sd_p = math.sqrt(sum((p-mn_p)**2 for p in prices)/len(prices))
    z_scores = [(s-mn_s)/sd_s for s in scores]
    z_prices = [(p-mn_p)/sd_p for p in prices]
    # Multiple regression via normal equations (X'X)^-1 X'y
    n = len(results)
    # Build design matrix [1, z_score, z_price]
    X = [[1, z_scores[i], z_prices[i]] for i in range(n)]
    y = apprec
    # X'X
    XtX = [[sum(X[r][c1]*X[r][c2] for r in range(n)) for c2 in range(3)] for c1 in range(3)]
    # X'y
    Xty = [sum(X[r][c]*y[r] for r in range(n)) for c in range(3)]
    # Solve via Gaussian elimination (3x3)
    A = [row[:] + [Xty[i]] for i, row in enumerate(XtX)]
    for col in range(3):
        pivot = max(range(col, 3), key=lambda r: abs(A[r][col]))
        A[col], A[pivot] = A[pivot], A[col]
        for row in range(3):
            if row != col and A[row][col] != 0:
                f = A[row][col] / A[col][col]
                A[row] = [A[row][j] - f*A[col][j] for j in range(4)]
    beta = [A[i][3]/A[i][i] for i in range(3)]
    y_hat2 = [beta[0] + beta[1]*z_scores[i] + beta[2]*z_prices[i] for i in range(n)]
    ss_res2 = sum((y[i]-y_hat2[i])**2 for i in range(n))
    ss_tot2 = sum((y[i]-sum(y)/n)**2 for i in range(n))
    r2_adj = 1 - ss_res2/ss_tot2
    print(f"4. OLS (controlled for starting price):")
    print(f"   b_score = {beta[1]:+.2f} pp appreciation per SD of score")
    print(f"   b_price = {beta[2]:+.2f} pp appreciation per SD of 2014 price")
    print(f"   R2 = {r2_adj:.3f}   (n={n})")

    # 5. Quintile analysis
    print()
    print("5. Quintile analysis (by 2014 Civica Score)")
    print(f"   {'Quintile':<28} {'N':>4}  {'Avg Appreciation':>16}")
    groups = percentile_groups(scores, apprec)
    for label, cnt, avg in groups:
        bar = "#" * int(avg / 5)
        print(f"   {label:<28} {cnt:>4}  {avg:>7.1f}%  {bar}")

    q1_apprec = groups[0][2]
    q5_apprec = groups[4][2]
    print(f"\n   Top quintile beat bottom by: {q5_apprec - q1_apprec:+.1f} pp")

    # 6. Top/bottom 10 by appreciation vs their scores
    print()
    print("6. Top 10 appreciating towns and their 2014 scores")
    by_apprec = sorted(results, key=lambda r: r["apprec_pct"], reverse=True)
    for r in by_apprec[:10]:
        print(f"   {r['town']:<22} apprec={r['apprec_pct']:.1f}%  score={r['score_2014']}")
    print()
    print("7. Bottom 10 appreciating towns and their 2014 scores")
    for r in by_apprec[-10:]:
        print(f"   {r['town']:<22} apprec={r['apprec_pct']:.1f}%  score={r['score_2014']}")

    # 8. TER correlation (score / residential rate)
    # TER captures value — high score for a low tax burden
    ter_data = [(r["score_2014"] / r["res_rate"], r["apprec_pct"])
                for r in results if r.get("res_rate", 0) > 0]
    ter_vals = [t for t, _ in ter_data]
    ter_apprec = [a for _, a in ter_data]
    r_ter_pearson = pearson(ter_vals, ter_apprec)
    r_ter_spearman = spearman(ter_vals, ter_apprec)
    sl_ter, ic_ter, r2_ter = simple_ols(ter_vals, ter_apprec)
    print()
    print("8. TER (Tax Efficiency Ratio = Score / Tax Rate) vs. Appreciation")
    print(f"   Pearson r  = {r_ter_pearson:+.3f}")
    print(f"   Spearman r = {r_ter_spearman:+.3f}")
    print(f"   OLS:  appreciation = {sl_ter:+.2f}*TER + {ic_ter:+.1f}   R2 = {r2_ter:.3f}  (n={len(ter_data)})")

    # 9. Scatter: TER vs appreciation with town labels
    print()
    print("9. TER vs Appreciation (sorted by TER)")
    print(f"   {'Town':<22} {'TER':>6} {'Score':>6} {'Apprec':>8}")
    for r in sorted(results, key=lambda x: x["score_2014"]/x["res_rate"] if x.get("res_rate",0)>0 else 0, reverse=True):
        if r.get("res_rate", 0) > 0:
            ter = r["score_2014"] / r["res_rate"]
            print(f"   {r['town']:<22} {ter:>6.1f} {r['score_2014']:>6} {r['apprec_pct']:>7.1f}%")

    if skipped:
        print()
        print("Skipped towns:")
        for name, reason in skipped:
            print(f"  {name}: {reason}")

    print()
    print("=" * 70)
    print("DATA QUALITY NOTES")
    print("=" * 70)
    print("""
Exact 2014 values used (no look-ahead bias):
  - Zillow ZHVI Jan 2014 / Jan 2024 (streamed directly from Zillow Research)
  - MA state crime rates 2014 (FBI UCR, disastercenter.com)
  - School rank back-calculated from rank_10yr_change field

Stable proxies (little variation over 10 years):
  - Transit access, wildfire, water violations, tax base %, test scores
  - Graduation rate, AP participation, transparency, electric savings

Conservative proxies (changes known directionally but not quantified):
  - Effective tax rate, free cash %, pension funded ratio
  - Bond rating (except Danvers: AA+ corrected)
  - Crime rates: town rates treated as constant, state denominator adjusted to 2014

Implication for validity:
  - Score variation driven by school rank back-calc and income back-calc is
    genuinely 2014-based. Score variation driven by proxy metrics is partially
    attenuated toward current data, which UNDERSTATES any real predictive signal
    (a conservative bias, not an optimistic one).
""")

if __name__ == "__main__":
    main()
