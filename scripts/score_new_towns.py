"""
Score the 5 new Essex County towns using the Civica methodology.
Outputs scored rows ready to append to towns.csv.
"""

import csv
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent

# MA electric avg rate from state_context.csv: 33.61 cents/kWh
# Electric savings formula: (state_avg_cents - town_rate_cents) / 100 * 10380
MA_ELECTRIC_CENTS = 33.61

# --- Reuse scoring logic from verify.py ---

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
    state = town_data["state"]
    ctx = si[state]

    def safe_div(a, b):
        try:
            return float(a) / float(b)
        except (TypeError, ValueError, ZeroDivisionError):
            return None

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
    park_s = score_submetric("park_score", town_data.get("park_acres_per_1000"), ri)
    lib_s = score_submetric("library_score", town_data.get("library_circ_per_capita"), ri)
    parks_libraries = (park_s + lib_s) / 2

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
        "sub_scores": sub_scores,
        "helpers": h,
    }


# --- Town data ---

MARBLEHEAD = {
    "town_name": "Marblehead", "state": "MA",
    "bond_rating_sp": "AAA", "free_cash_pct_of_budget": 7.4,
    "pension_funded_ratio_pct": None, "debt_per_capita": 6173,
    "gfoa_certificate_consecutive_years": 18, "tax_base_non_residential_pct": 4.4,
    "effective_tax_rate_pct": 0.905, "median_annual_tax_bill": 10181,
    "median_household_income": 182132, "residential_rate_per_1000": 9.05,
    "district_state_rank": 89, "district_state_rank_total": 351,
    "district_rank_10yr_change": None, "test_scores_math_pct": 59.0,
    "graduation_rate_pct": 99.0, "ap_participation_pct": 67.0, "per_pupil_spending": 21972,
    "response_311_days": None, "ems_response_minutes": None, "permits_per_1000": None,
    "iso_fire_rating": None, "transparency": "yes",
    # MMLD municipal electric: (33.61 - 15.0) / 100 * 10380 = $1,931
    "electric_savings_vs_state_avg": 1931, "water_violations_5yr": 0,
    "broadband_coverage_pct": None, "transit_access": "bus_only", "walk_score": 49,
    "park_acres_per_1000": 2.1, "library_circ_per_capita": 10.3,
    "violent_crime_per_100k": 14.6, "property_crime_per_100k": 57.8,
    "crime_5yr_pct_change": None,
    "income_10yr_change_pct": 28.3, "population_10yr_change_pct": 3.2,
    "bachelors_degree_pct": 78.3, "unemployment_pct": 1.9,
    "permits_3yr_per_1000": None, "poverty_pct": 4.4,
    "flood_risk_pct": 17.6, "flood_2050_growth_pts": 3.0,
    "wildfire_risk": "low", "heat_days_growth_2050": None,
    "air_quality_aqi": None, "tree_canopy_pct": None,
}

SALEM = {
    "town_name": "Salem", "state": "MA",
    "bond_rating_sp": "AA", "free_cash_pct_of_budget": 1.2,
    "pension_funded_ratio_pct": None, "debt_per_capita": None,
    "gfoa_certificate_consecutive_years": 10, "tax_base_non_residential_pct": None,
    "effective_tax_rate_pct": 1.13, "median_annual_tax_bill": None,
    "median_household_income": 85153, "residential_rate_per_1000": 11.34,
    "district_state_rank": 295, "district_state_rank_total": 351,
    "district_rank_10yr_change": None, "test_scores_math_pct": 42.0,
    "graduation_rate_pct": 81.6, "ap_participation_pct": 32.0, "per_pupil_spending": 25712,
    "response_311_days": None, "ems_response_minutes": None, "permits_per_1000": None,
    "iso_fire_rating": None, "transparency": "yes",
    "electric_savings_vs_state_avg": 0, "water_violations_5yr": 0,
    "broadband_coverage_pct": None, "transit_access": "commuter_rail_in_town", "walk_score": 70,
    "park_acres_per_1000": None, "library_circ_per_capita": 11.9,
    "violent_crime_per_100k": 152.0, "property_crime_per_100k": 1554.0,
    "crime_5yr_pct_change": None,
    "income_10yr_change_pct": None, "population_10yr_change_pct": 4.86,
    "bachelors_degree_pct": 47.8, "unemployment_pct": 3.3,
    "permits_3yr_per_1000": None, "poverty_pct": 12.1,
    "flood_risk_pct": 16.0, "flood_2050_growth_pts": 12.0,
    "wildfire_risk": "low", "heat_days_growth_2050": 11,
    "air_quality_aqi": None, "tree_canopy_pct": None,
}

PEABODY = {
    "town_name": "Peabody", "state": "MA",
    "bond_rating_sp": None, "free_cash_pct_of_budget": 5.16,
    "pension_funded_ratio_pct": None, "debt_per_capita": None,
    "gfoa_certificate_consecutive_years": None, "tax_base_non_residential_pct": 16.5,
    "effective_tax_rate_pct": 0.926, "median_annual_tax_bill": 4572,
    "median_household_income": 96657, "residential_rate_per_1000": 9.26,
    "district_state_rank": 265, "district_state_rank_total": 351,
    "district_rank_10yr_change": None, "test_scores_math_pct": 33.0,
    "graduation_rate_pct": 90.7, "ap_participation_pct": 33.0, "per_pupil_spending": 19148,
    "response_311_days": None, "ems_response_minutes": None, "permits_per_1000": None,
    "iso_fire_rating": None, "transparency": "partial",
    # PMLP municipal electric: (33.61 - 15.78) / 100 * 10380 = $1,850
    "electric_savings_vs_state_avg": 1850, "water_violations_5yr": 0,
    "broadband_coverage_pct": None, "transit_access": "commuter_rail_nearby", "walk_score": 43,
    "park_acres_per_1000": None, "library_circ_per_capita": 4.6,
    "violent_crime_per_100k": 254.7, "property_crime_per_100k": 836.9,
    "crime_5yr_pct_change": None,
    "income_10yr_change_pct": None, "population_10yr_change_pct": 3.48,
    "bachelors_degree_pct": 35.0, "unemployment_pct": None,
    "permits_3yr_per_1000": None, "poverty_pct": 7.7,
    "flood_risk_pct": 10.5, "flood_2050_growth_pts": 0.4,
    "wildfire_risk": "low", "heat_days_growth_2050": None,
    "air_quality_aqi": None, "tree_canopy_pct": None,
}

GLOUCESTER = {
    "town_name": "Gloucester", "state": "MA",
    "bond_rating_sp": "AA", "free_cash_pct_of_budget": 3.2,
    "pension_funded_ratio_pct": None, "debt_per_capita": None,
    "gfoa_certificate_consecutive_years": 6, "tax_base_non_residential_pct": 8.26,
    "effective_tax_rate_pct": 0.97, "median_annual_tax_bill": 6056,
    "median_household_income": 83883, "residential_rate_per_1000": 9.72,
    "district_state_rank": 254, "district_state_rank_total": 351,
    "district_rank_10yr_change": None, "test_scores_math_pct": 29.0,
    "graduation_rate_pct": 89.1, "ap_participation_pct": 29.0, "per_pupil_spending": 22663,
    "response_311_days": None, "ems_response_minutes": None, "permits_per_1000": None,
    "iso_fire_rating": None, "transparency": "yes",
    "electric_savings_vs_state_avg": 0, "water_violations_5yr": 0,
    "broadband_coverage_pct": None, "transit_access": "commuter_rail_in_town", "walk_score": 42,
    "park_acres_per_1000": 212.0, "library_circ_per_capita": 5.1,
    "violent_crime_per_100k": None, "property_crime_per_100k": None,
    "crime_5yr_pct_change": None,
    "income_10yr_change_pct": None, "population_10yr_change_pct": 4.5,
    "bachelors_degree_pct": 40.3, "unemployment_pct": 4.3,
    "permits_3yr_per_1000": None, "poverty_pct": 9.6,
    "flood_risk_pct": None, "flood_2050_growth_pts": None,
    "wildfire_risk": "low", "heat_days_growth_2050": None,
    "air_quality_aqi": None, "tree_canopy_pct": None,
}

NEWBURYPORT = {
    "town_name": "Newburyport", "state": "MA",
    "bond_rating_sp": None, "free_cash_pct_of_budget": None,
    "pension_funded_ratio_pct": None, "debt_per_capita": None,
    "gfoa_certificate_consecutive_years": None, "tax_base_non_residential_pct": None,
    "effective_tax_rate_pct": 0.96, "median_annual_tax_bill": 7778,
    "median_household_income": 139625, "residential_rate_per_1000": 9.58,
    "district_state_rank": 87, "district_state_rank_total": 351,
    "district_rank_10yr_change": None, "test_scores_math_pct": 48.0,
    "graduation_rate_pct": 98.0, "ap_participation_pct": 64.0, "per_pupil_spending": 23233,
    "response_311_days": None, "ems_response_minutes": None, "permits_per_1000": None,
    "iso_fire_rating": None, "transparency": "yes",
    "electric_savings_vs_state_avg": None, "water_violations_5yr": 0,
    "broadband_coverage_pct": None, "transit_access": "commuter_rail_in_town", "walk_score": 52,
    "park_acres_per_1000": None, "library_circ_per_capita": 19.8,
    "violent_crime_per_100k": 47.0, "property_crime_per_100k": 395.0,
    "crime_5yr_pct_change": None,
    "income_10yr_change_pct": None, "population_10yr_change_pct": 5.3,
    "bachelors_degree_pct": 64.0, "unemployment_pct": 3.7,
    "permits_3yr_per_1000": None, "poverty_pct": 5.0,
    "flood_risk_pct": None, "flood_2050_growth_pts": None,
    "wildfire_risk": "low", "heat_days_growth_2050": None,
    "air_quality_aqi": None, "tree_canopy_pct": None,
}

NEW_TOWNS = [MARBLEHEAD, SALEM, PEABODY, GLOUCESTER, NEWBURYPORT]


def count_gaps(town_data):
    """Count blank required input fields (excluding identity/output fields)."""
    required_inputs = [
        "bond_rating_sp", "free_cash_pct_of_budget", "pension_funded_ratio_pct",
        "debt_per_capita", "gfoa_certificate_consecutive_years", "tax_base_non_residential_pct",
        "effective_tax_rate_pct", "median_annual_tax_bill", "median_household_income",
        "district_state_rank", "district_rank_10yr_change", "test_scores_math_pct",
        "graduation_rate_pct", "ap_participation_pct", "per_pupil_spending",
        "response_311_days", "ems_response_minutes", "permits_per_1000", "iso_fire_rating",
        "transparency", "electric_savings_vs_state_avg", "water_violations_5yr",
        "broadband_coverage_pct", "transit_access", "walk_score",
        "park_acres_per_1000", "library_circ_per_capita",
        "violent_crime_per_100k", "property_crime_per_100k", "crime_5yr_pct_change",
        "income_10yr_change_pct", "population_10yr_change_pct", "bachelors_degree_pct",
        "unemployment_pct", "permits_3yr_per_1000", "poverty_pct",
        "flood_risk_pct", "flood_2050_growth_pts", "wildfire_risk", "heat_days_growth_2050",
        "air_quality_aqi", "tree_canopy_pct",
    ]
    return sum(1 for f in required_inputs if town_data.get(f) is None or town_data.get(f) == "")


def main():
    pw, sw, ri, si = load_methodology()

    print("=" * 70)
    print("CIVICA — NEW TOWN SCORING")
    print("=" * 70)

    results = []
    for town_data in NEW_TOWNS:
        name = town_data["town_name"]
        result = score_town(town_data, pw, sw, ri, si)
        gaps = count_gaps(town_data)
        confidence = "high" if gaps < 5 else ("medium" if gaps <= 15 else "low")

        print(f"\n{name}, MA")
        print(f"  Pillar scores:")
        for p, s in result["pillar_scores"].items():
            print(f"    {p:25s} {s:5.1f}")
        print(f"  Civica Score: {result['civica_score']}")
        print(f"  TER: {result['ter']} ({result['ter_rating']})")
        print(f"  Data gaps: {gaps}  Confidence: {confidence}")

        results.append({
            "town_data": town_data,
            "result": result,
            "gaps": gaps,
            "confidence": confidence,
        })

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"{'Town':<15} {'Score':>6} {'TER':>6} {'Rating':<14} {'Gaps':>5} {'Confidence'}")
    print("-" * 70)
    for r in results:
        print(f"{r['town_data']['town_name']:<15} {r['result']['civica_score']:>6} "
              f"{r['result']['ter']:>6.1f} {r['result']['ter_rating']:<14} "
              f"{r['gaps']:>5} {r['confidence']}")

    return results


if __name__ == "__main__":
    main()
