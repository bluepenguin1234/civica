"""
Civica Reproducibility Verification
====================================

Independently re-implements the Civica scoring methodology by loading the
methodology CSV files and applying them to Danvers and Beverly. Verifies
output matches the published scores.

Run after any methodology change to catch silent drift.

Required input files (in same directory):
- master_weights.csv
- pillar_weights.csv
- scoring_rubrics.csv
- state_context.csv

Expected outputs:
- Danvers, MA → Civica Score 72, TER 5.4 (Average)
- Beverly, MA → Civica Score 73, TER 6.5 (Average)

Usage:  python verify.py
Exit:   0 = passed, 1 = failed
"""

import csv
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent
EXPECTED = {
    "Danvers": {"score": 72, "ter": 5.4},
    "Beverly": {"score": 73, "ter": 6.5},
}


def load_csv(path):
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_methodology():
    master = load_csv(DATA_DIR / "master_weights.csv")
    pillar = load_csv(DATA_DIR / "pillar_weights.csv")
    rubrics = load_csv(DATA_DIR / "scoring_rubrics.csv")
    state = load_csv(DATA_DIR / "state_context.csv")

    pw = {row["pillar_id"]: float(row["weight"]) for row in master}

    sw = {}
    for row in pillar:
        sw.setdefault(row["pillar_id"], {})[row["submetric_id"]] = float(row["weight"])

    ri = {}
    for row in rubrics:
        ri.setdefault(row["submetric_id"], []).append(row)

    si = {}
    for row in state:
        si.setdefault(row["state"], {})[row["metric"]] = float(row["value"])

    return pw, sw, ri, si


def score_submetric(submetric_id, raw_value, rubric_index):
    """Apply a rubric to a raw value, returning a 0-100 score."""
    if submetric_id not in rubric_index:
        return 50

    rules = rubric_index[submetric_id]
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


def score_town(town_data, pw, sw, ri, si):
    """Compute Civica Score for a town."""
    state = town_data["state"]
    ctx = si[state]

    def safe_div(a, b):
        try:
            return float(a) / float(b)
        except (TypeError, ValueError, ZeroDivisionError):
            return None

    # 9 helper calculations
    h = {
        "tax_burden_pct": (
            (float(town_data["median_annual_tax_bill"]) / float(town_data["median_household_income"])) * 100
            if town_data.get("median_annual_tax_bill") and town_data.get("median_household_income") else None
        ),
        "rank_percentile": (
            (1 - float(town_data["district_state_rank"]) / float(town_data["district_state_rank_total"])) * 100
            if town_data.get("district_state_rank") and town_data.get("district_state_rank_total") else None
        ),
        "debt_ratio": safe_div(town_data.get("debt_per_capita"), ctx["debt_per_capita_median"]),
        "violent_crime_ratio": safe_div(town_data.get("violent_crime_per_100k"), ctx["violent_crime_per_100k"]),
        "property_crime_ratio": safe_div(town_data.get("property_crime_per_100k"), ctx["property_crime_per_100k"]),
        "income_ratio": safe_div(town_data.get("median_household_income"), ctx["median_household_income"]),
        "poverty_ratio": safe_div(town_data.get("poverty_pct"), ctx["poverty_rate_pct"]),
        "unemployment_ratio": safe_div(town_data.get("unemployment_pct"), ctx["unemployment_rate_pct"]),
    }
    if h["rank_percentile"] is not None and town_data.get("per_pupil_spending"):
        h["spending_efficiency_idx"] = (
            (h["rank_percentile"] / 100) /
            (float(town_data["per_pupil_spending"]) / ctx["per_pupil_spending_median"])
        )
    else:
        h["spending_efficiency_idx"] = None

    # Map sub-metric → input value (raw or helper)
    SM = {
        "bond_rating": town_data.get("bond_rating_sp"),
        "free_cash_pct": town_data.get("free_cash_pct_of_budget"),
        "pension_funded": town_data.get("pension_funded_ratio_pct"),
        "debt_per_capita": h["debt_ratio"],
        "gfoa_years": town_data.get("gfoa_certificate_consecutive_years"),
        "tax_base_diversification": town_data.get("tax_base_non_residential_pct"),
        "effective_tax_rate": town_data.get("effective_tax_rate_pct"),
        "tax_burden_to_income": h["tax_burden_pct"],
        "tax_base_health": town_data.get("tax_base_non_residential_pct"),
        "rank_percentile": h["rank_percentile"],
        "rank_trajectory": town_data.get("district_rank_10yr_change"),
        "test_scores": town_data.get("test_scores_math_pct"),
        "graduation_rate": town_data.get("graduation_rate_pct"),
        "ap_participation": town_data.get("ap_participation_pct"),
        "spending_efficiency": h["spending_efficiency_idx"],
        "response_311": town_data.get("response_311_days"),
        "ems_response": town_data.get("ems_response_minutes"),
        "permits_efficiency": town_data.get("permits_per_1000"),
        "iso_fire": town_data.get("iso_fire_rating"),
        "transparency": town_data.get("transparency"),
        "electric_value": town_data.get("electric_savings_vs_state_avg"),
        "water_quality": town_data.get("water_violations_5yr"),
        "broadband": town_data.get("broadband_coverage_pct"),
        "transit": town_data.get("transit_access"),
        "walkability": town_data.get("walk_score"),
        "violent_crime": h["violent_crime_ratio"],
        "property_crime": h["property_crime_ratio"],
        "crime_trajectory": town_data.get("crime_5yr_pct_change"),
        "income_trend": town_data.get("income_10yr_change_pct"),
        "population_trend": town_data.get("population_10yr_change_pct"),
        "income_level": h["income_ratio"],
        "education_attainment": town_data.get("bachelors_degree_pct"),
        "unemployment": h["unemployment_ratio"],
        "permits_growth": town_data.get("permits_3yr_per_1000"),
        "poverty": h["poverty_ratio"],
        "flood_risk": town_data.get("flood_risk_pct"),
        "flood_trajectory": town_data.get("flood_2050_growth_pts"),
        "wildfire": town_data.get("wildfire_risk"),
        "heat_trajectory": town_data.get("heat_days_growth_2050"),
        "air_quality": town_data.get("air_quality_aqi"),
        "tree_canopy": town_data.get("tree_canopy_pct"),
    }

    sub_scores = {sm: score_submetric(sm, val, ri) for sm, val in SM.items()}

    # parks_libraries composite
    park_s = score_submetric("park_score", town_data.get("park_acres_per_1000"), ri)
    lib_s = score_submetric("library_score", town_data.get("library_circ_per_capita"), ri)
    parks_libraries = (park_s + lib_s) / 2

    # Aggregate to pillars
    ps = {}
    fh = sw["fiscal_health"]
    ps["fiscal_health"] = sum(sub_scores[k] * fh[k] for k in fh)
    te = sw["tax_efficiency"]
    ps["tax_efficiency"] = sum(sub_scores[k] * te[k] for k in te)
    sc = sw["schools"]
    ps["schools"] = sum(sub_scores[k] * sc[k] for k in sc)
    op = sw["operational"]
    ps["operational"] = sum(sub_scores[k] * op[k] for k in op)
    inf = sw["infrastructure"]
    ps["infrastructure"] = (
        sub_scores["electric_value"] * inf["electric_value"] +
        sub_scores["water_quality"] * inf["water_quality"] +
        sub_scores["broadband"] * inf["broadband"] +
        sub_scores["transit"] * inf["transit"] +
        sub_scores["walkability"] * inf["walkability"] +
        parks_libraries * inf["parks_libraries"]
    )
    sa = sw["safety"]
    ps["safety"] = sum(sub_scores[k] * sa[k] for k in sa)
    ec = sw["economic"]
    ps["economic"] = sum(sub_scores[k] * ec[k] for k in ec)
    cl = sw["climate"]
    ps["climate"] = sum(sub_scores[k] * cl[k] for k in cl)

    civica = round(sum(ps[p] * pw[p] for p in pw))
    ter = round(civica / float(town_data["residential_rate_per_1000"]), 1)

    if ter >= 9.0: rating = "Exceptional"
    elif ter >= 7.0: rating = "Strong"
    elif ter >= 5.0: rating = "Average"
    elif ter >= 3.0: rating = "Below Average"
    else: rating = "Poor"

    return {
        "civica_score": civica, "ter": ter, "ter_rating": rating,
        "pillar_scores": {k: round(v, 1) for k, v in ps.items()},
    }


# Test data
DANVERS = {
    "town_name": "Danvers", "state": "MA",
    "bond_rating_sp": "AA+", "free_cash_pct_of_budget": 10.7,
    "pension_funded_ratio_pct": None, "debt_per_capita": 3079,
    "gfoa_certificate_consecutive_years": 16, "tax_base_non_residential_pct": 21.5,
    "effective_tax_rate_pct": 1.18, "median_annual_tax_bill": 6371,
    "median_household_income": 125395, "residential_rate_per_1000": 13.36,
    "district_state_rank": 196, "district_state_rank_total": 351,
    "district_rank_10yr_change": 51, "test_scores_math_pct": 32.29,
    "graduation_rate_pct": 95.0, "ap_participation_pct": 54.0, "per_pupil_spending": 20883,
    "response_311_days": None, "ems_response_minutes": None, "permits_per_1000": None,
    "iso_fire_rating": None, "transparency": "yes",
    "electric_savings_vs_state_avg": 2036, "water_violations_5yr": 0,
    "broadband_coverage_pct": None, "transit_access": "no", "walk_score": None,
    "park_acres_per_1000": 9.0, "library_circ_per_capita": 7.0,
    "violent_crime_per_100k": 137.4, "property_crime_per_100k": 1480.2,
    "crime_5yr_pct_change": None,
    "income_10yr_change_pct": 65.0, "population_10yr_change_pct": 6.1,
    "bachelors_degree_pct": 48.4, "unemployment_pct": None,
    "permits_3yr_per_1000": None, "poverty_pct": 4.8,
    "flood_risk_pct": 9.8, "flood_2050_growth_pts": 2.8,
    "wildfire_risk": "low", "heat_days_growth_2050": 21,
    "air_quality_aqi": None, "tree_canopy_pct": None,
}

BEVERLY = {
    "town_name": "Beverly", "state": "MA",
    "bond_rating_sp": "AA+", "free_cash_pct_of_budget": 6.0,
    "pension_funded_ratio_pct": None, "debt_per_capita": 1900,
    "gfoa_certificate_consecutive_years": None, "tax_base_non_residential_pct": 18.0,
    "effective_tax_rate_pct": 1.0, "median_annual_tax_bill": 6605,
    "median_household_income": 106044, "residential_rate_per_1000": 11.23,
    "district_state_rank": 109, "district_state_rank_total": 351,
    "district_rank_10yr_change": -10, "test_scores_math_pct": 48.68,
    "graduation_rate_pct": 94.4, "ap_participation_pct": 37.0, "per_pupil_spending": 15302,
    "response_311_days": None, "ems_response_minutes": None, "permits_per_1000": None,
    "iso_fire_rating": None, "transparency": "yes",
    "electric_savings_vs_state_avg": -300, "water_violations_5yr": 0,
    "broadband_coverage_pct": None, "transit_access": "commuter_rail_in_town", "walk_score": None,
    "park_acres_per_1000": 8.0, "library_circ_per_capita": 8.0,
    "violent_crime_per_100k": 195, "property_crime_per_100k": 1450,
    "crime_5yr_pct_change": None,
    "income_10yr_change_pct": 32.0, "population_10yr_change_pct": 8.4,
    "bachelors_degree_pct": 31.3, "unemployment_pct": None,
    "permits_3yr_per_1000": None, "poverty_pct": 9.36,
    "flood_risk_pct": 14.0, "flood_2050_growth_pts": 4.0,
    "wildfire_risk": "low", "heat_days_growth_2050": 21,
    "air_quality_aqi": None, "tree_canopy_pct": None,
}


def main():
    print("=" * 60)
    print("CIVICA METHODOLOGY REPRODUCIBILITY VERIFICATION")
    print("=" * 60)
    print()

    pw, sw, ri, si = load_methodology()
    print("Loaded methodology:")
    print(f"  {len(pw)} pillars")
    print(f"  {sum(len(s) for s in sw.values())} sub-metric weights")
    print(f"  {sum(len(rules) for rules in ri.values())} rubric rules")
    print(f"  {len(si)} states in context")
    print()

    all_pass = True
    for town_data in [DANVERS, BEVERLY]:
        name = town_data["town_name"]
        result = score_town(town_data, pw, sw, ri, si)
        expected = EXPECTED[name]

        score_ok = result["civica_score"] == expected["score"]
        ter_ok = abs(result["ter"] - expected["ter"]) < 0.1

        print(f"{name}, MA")
        print(f"  Pillar scores:")
        for p, s in result["pillar_scores"].items():
            print(f"    {p:25s} {s:5.1f}")
        print(f"  Civica Score: {result['civica_score']} (expected {expected['score']}) {'✓' if score_ok else '✗'}")
        print(f"  TER: {result['ter']} (expected {expected['ter']}) {'✓' if ter_ok else '✗'}")
        print(f"  TER Rating: {result['ter_rating']}")
        print()

        if not (score_ok and ter_ok):
            all_pass = False

    print("=" * 60)
    if all_pass:
        print("✓ VERIFICATION PASSED")
        sys.exit(0)
    else:
        print("✗ VERIFICATION FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
