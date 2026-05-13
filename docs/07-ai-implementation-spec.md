# Civica AI Implementation Specification v2.0

> Implementation-level details for correctly computing Civica Scores from the 36 data points.

This document is targeted at an AI computing Civica Scores from collected data. The conceptual methodology is in `04-scoring-methodology.md`; the **mechanics that produce silently wrong scores if implemented naively** live here.

**Authoritative source:** The `computeScore(t)` and `grade(k,v,t)` functions in `civica-v5.html` are the single source of truth. If this document conflicts with that code, the code wins.

---

## 1. The Scoring Formula

```
Civica Score = fiscal×0.28 + schools×0.25 + tax×0.15 + safety×0.15
             + momentum×0.08 + infra×0.06 + climate×0.03
```

Seven pillars. Weights sum to 1.00. Result is rounded to the nearest integer (0–100).

Each pillar score is the **unweighted average** of the green/yellow/red grades for its gradeable metrics:

```
green  = 100 points
yellow =  55 points
red    =  15 points
na     = excluded from average (not counted in denominator)
```

If all metrics in a pillar are `na`, the pillar defaults to 50.

---

## 2. The `grade(key, value, town)` Function

Every metric is graded as `"green"`, `"yellow"`, `"red"`, or `"na"`.

- `"na"` means data is missing or the metric is display-only (not scored)
- A `null` or missing value always returns `"na"` — **never 0, never red by default**

The grade thresholds for each key are defined in the `grade()` function in `civica-v5.html`. Below are the grading rules for each scored metric:

### Fiscal Health grades

| Key | Green | Yellow | Red |
|---|---|---|---|
| `bond` | AAA, AA+, AA | AA-, A+, A | below A or null |
| `free_cash` | ≥7% | ≥3% | <3% |
| `debt_pc` | <$2,000 | <$4,000 | ≥$4,000 |
| `eff_rate` | <1.2% | <1.7% | ≥1.7% |

`pension`, `gfoa`, `transp` are displayed but graded `na` (informational only, not scored directly — they feed the fiscal weighted blend).

### Fiscal Health — weighted blend

Fiscal Health uses a custom weighted blend rather than a simple average:

```javascript
const fiscalBase = avg(grade(bond), grade(free_cash), grade(debt_pc));  // weight 3
const pg = gradePension(pension);   // weight 1
const tg = gradeTransp(transp);     // weight 0.5
const gg = gradeGfoa(gfoa);         // weight 0.5

fiscal = weightedAvg([fiscalBase×3, pg×1, tg×0.5, gg×0.5])
```

Pension grading: ≥80% → green, ≥60% → yellow, <60% → red
Transparency grading: "Yes" → green, "Partial" → yellow, "No" → red
GFOA grading: ≥16 yrs → green, ≥10 yrs → yellow, <10 yrs → red

Only non-null components are included in the weighted average denominator.

### Schools grades

| Key | Green | Yellow | Red |
|---|---|---|---|
| `d_rank` | top 30% of districts | top 60% | bottom 40% |
| `math` | ≥55% | ≥35% | <35% |
| `grad` | ≥92% | ≥82% | <82% |

`d_10yr`, `ap`, `enrollment_trend` are display-only (`na`).

Schools pillar = average of `grade(d_rank)`, `grade(math)`, `grade(grad)`.

### Tax Efficiency grades

| Key | Green | Yellow | Red |
|---|---|---|---|
| `eff_rate` | <1.2% | <1.7% | ≥1.7% |
| `ter_r` | "Strong" | "Fair" | "Weak" |

`med_tax`, `med_inc`, `res_rate`, `tax_non_res`, `med_home_val` are display-only (`na`).

Tax pillar = average of `grade(eff_rate)`, `grade(ter_r)`.

### Safety grades

| Key | Green | Yellow | Red |
|---|---|---|---|
| `violent` | <60/100k | <150/100k | ≥150/100k |
| `prop_crime` | <800/100k | <2000/100k | ≥2000/100k |

`sex_off` is display-only (`na`).

Safety pillar = average of `grade(violent)`, `grade(prop_crime)`.

### Economic Momentum grades

| Key | Green | Yellow | Red |
|---|---|---|---|
| `unemp` | <4% | <7% | ≥7% |
| `pov` | <6% | <12% | ≥12% |

`inc10yr`, `pop10yr`, `owner_occ`, `vacancy`, `med_age` are display-only (`na`).

Momentum pillar = average of `grade(unemp)`, `grade(pov)`.

### Infrastructure grades

| Key | Green | Yellow | Red |
|---|---|---|---|
| `elec_save` | >$500/yr savings | ≥$0 | negative (costs more than state avg) |
| `water_viol` | 0 violations | ≤2 | >2 |

`transit` is display-only (`na`).

Infra pillar = average of `grade(elec_save)`, `grade(water_viol)`.

### Climate grades

| Key | Green | Yellow | Red |
|---|---|---|---|
| `flood` | <5% properties | <15% | ≥15% |
| `flood50` | <2 pt growth | <5 pt | ≥5 pt |

`fire` is display-only (`na`).

Climate pillar = average of `grade(flood)`, `grade(flood50)`.

---

## 3. The Missing-Data Convention

**Critical rule:** When a raw input is `null` or missing, `grade()` returns `"na"` — never `"red"` and never `0`.

The `na` grade is excluded from pillar averages. A pillar with all `na` values defaults to 50 (neutral), not 0.

**Never** substitute 0 for a missing value before passing to the grader. That would silently score the town as if the value is 0, which hits the lowest bucket and artificially deflates the score.

---

## 4. The TER (Tax Efficiency Ratio)

TER is a derived metric — do not collect it, compute it:

```
TER = civica_score / res_rate
```

TER rating bands:
- `"Strong"` — TER ≥ 5.0
- `"Fair"` — TER ≥ 3.0
- `"Weak"` — TER < 3.0

TER is computed and stored in the town object. `ter_r` feeds back into the Tax pillar as a gradeable metric.

---

## 5. The Scoring Sequence

```
1. Collect all 36 data points per 06-collection-playbook.md
2. For each pillar, pass the relevant (key, value) pairs to grade()
3. Filter out 'na' grades, average the numeric scores (green=100, yellow=55, red=15)
4. Compute fiscal using the weighted blend (see Section 2)
5. Compute Civica Score using pillar weights (28/25/15/15/8/6/3)
6. Round Civica Score to nearest integer
7. Compute TER = score / res_rate, round to 1 decimal
8. Assign ter_r rating band
9. Count gaps (null fields among the 36)
10. Set conf: "high" <5 gaps, "medium" 5–15, "low" >15
```

---

## 6. Fields That Are Display-Only (Not Scored)

These fields appear in town profiles but do not affect the Civica Score:

`pension`, `gfoa`, `transp` — informational under Fiscal (but do feed the fiscal weighted blend — see Section 2)
`d_10yr`, `ap`, `enrollment_trend` — informational under Schools
`med_tax`, `med_inc`, `res_rate`, `tax_non_res`, `med_home_val` — informational under Tax
`sex_off` — informational under Safety
`inc10yr`, `pop10yr`, `owner_occ`, `vacancy`, `med_age` — informational under Economic Momentum
`transit` — informational under Infrastructure
`fire` — informational under Climate

**Do not skip collecting these.** They display in town profiles and are valuable to buyers even if they don't feed the score formula.

---

## 7. Fields Removed from Prior Versions

These fields appeared in v1 of the collection playbook and implementation spec but are **no longer used**. Do not collect them:

- `response_311_days` (311 response time)
- `ems_response_minutes` (EMS response time)
- `permits_per_1000` / `permits_3yr_per_1000` (building permits)
- `iso_fire_rating` (ISO fire rating)
- `broadband_coverage_pct` (broadband access)
- `walk_score` (Walk Score)
- `park_acres_per_1000` (park acreage)
- `library_circ_per_capita` (library circulation)
- `crime_5yr_pct_change` (crime trend)
- `bachelors_degree_pct` (education attainment)
- `per_pupil_spending` (school spending)
- `heat_days_growth_2050` (heat days projection)
- `air_quality_aqi` (air quality)
- `tree_canopy_pct` (tree canopy)

These were part of the original 8-pillar design that included an Operational Responsiveness pillar. That pillar has been removed. The operational and climate metrics listed above are no longer scored.

---

## 8. Common Implementation Mistakes

**"I'll estimate the missing value to be helpful"**
Wrong. Leave null. Let the grade default to `na` and be excluded from the average.

**"I'll collect the extra fields from v1 just in case"**
Wrong. The v1 fields are not displayed and not scored. Collecting them wastes time and clutters the data.

**"I'll use the old 8-pillar weights"**
Wrong. Current weights: Fiscal 28%, Schools 25%, Tax 15%, Safety 15%, Momentum 8%, Infrastructure 6%, Climate 3%.

**"I'll round intermediate pillar scores"**
Wrong. Round only the final Civica Score (integer) and TER (1 decimal). Rounding intermediate values accumulates error.

---

## 9. Output Fields Written to Town Object

| Field | Type | Notes |
|---|---|---|
| Identity (5) | string/int | name, county, state, zip, pop |
| Scored inputs (36) | varies | per collection playbook |
| `score` | integer | computed Civica Score |
| `ter` | decimal (1 place) | computed TER |
| `ter_r` | string | "Strong" / "Fair" / "Weak" |
| `gaps` | integer | count of null scored fields |
| `conf` | string | "high" / "medium" / "low" |
