# Civica Scoring Methodology v1.0

> Reproducible. Defensible. Open.

This document is the conceptual reference for the Civica scoring system. For implementation-level details (helper formulas, edge cases, gotchas), see `07-ai-implementation-spec.md`. For authoritative machine-readable definitions, see the methodology CSVs.

**Verification status:** Independently re-implemented and verified to reproduce Danvers, MA = 72 and Beverly, MA = 73. Run `verify.py` to confirm.

---

## 1. The Core Formula

```
Civica Score = Σ (Pillar Score × Pillar Weight)
```

Each of 8 pillars scores 0–100. Weights sum to 1.00. Result is a 0–100 composite for any U.S. municipality.

Each pillar is itself:

```
Pillar Score = Σ (Sub-metric Score × Sub-metric Weight)
```

Each sub-metric is:

```
Sub-metric Score = lookup(raw_value, rubric)
```

If raw data is missing, the rubric returns a documented default (typically 50–70).

---

## 2. The 8 Pillars

| Pillar | Weight |
|---|---|
| Fiscal Health | 30% |
| Tax Efficiency | 15% |
| Schools | 15% |
| Operational Responsiveness | 10% |
| Infrastructure & Utilities | 10% |
| Economic Momentum | 10% |
| Safety | 5% |
| Climate Resilience | 5% |

Authoritative file: `master_weights.csv`

---

## 3. The 43 Sub-metrics

Full list with weights and source documentation in `pillar_weights.csv`. High-level inventory:

- **Fiscal Health (6)**: bond rating, free cash %, pension funded ratio, debt per capita ratio, GFOA years, tax base diversification
- **Tax Efficiency (3)**: effective tax rate, tax burden % income, non-residential tax base
- **Schools (6)**: rank percentile, rank trajectory, test scores, graduation, AP participation, spending efficiency
- **Operational (5)**: 311 response, EMS response, permits per 1000, ISO fire, transparency
- **Infrastructure (6)**: electric value, water quality, broadband, transit, walkability, parks+libraries
- **Safety (4)**: violent crime ratio, property crime ratio, crime trajectory, ISO fire (alias)
- **Economic (7)**: income trend, population trend, income level, education, unemployment, permits growth, poverty
- **Climate (6)**: flood risk, flood trajectory, wildfire, heat trajectory, air quality, tree canopy

---

## 4. Rubric Types

Authoritative file: `scoring_rubrics.csv` (276 rules)

### Range rubrics
Lower bound inclusive, upper bound exclusive. Maps a numeric value to a 0–100 score via thresholds.

### Lookup rubrics
Case-insensitive string match. Maps a categorical value (like "AA+" or "yes") to a 0–100 score.

### Ratio rubrics
For state-normalized metrics. Computes town-value / state-median first, then applies a range rubric to the ratio.

### Composite rubrics
Two sub-metrics use composite calculations:

**Spending Efficiency** = (1 − rank/total) ÷ (per_pupil_spending / state_median)

**Parks + Libraries** = average of park_score and library_score, each scored separately

### Default scores
Missing data returns documented default. A town with all defaults scores ~63 — by design, representing genuine uncertainty without inflation or deflation.

---

## 5. Worked Example — Danvers, MA

Pillar scores compute to:

| Pillar | Score | × Weight | Contribution |
|---|---|---|---|
| Fiscal Health | 80.3 | 0.30 | 24.09 |
| Tax Efficiency | 75.4 | 0.15 | 11.31 |
| Schools | 50.2 | 0.15 | 7.54 |
| Operational | 66.2 | 0.10 | 6.62 |
| Infrastructure | 76.6 | 0.10 | 7.66 |
| Safety | 69.8 | 0.05 | 3.49 |
| Economic | 81.3 | 0.10 | 8.13 |
| Climate | 68.7 | 0.05 | 3.44 |
| **CIVICA SCORE** | | | **72.3 → 72** |

**TER**: 72 / $13.36 = 5.4 (Average)

### Why Danvers Earns Its Score

**Strongest pillars:**
- Economic Momentum (81) — 65% income growth, 6% population growth, 48% bachelor's+
- Fiscal Health (80) — AA+ rating, 10.7% free cash, 16 GFOA years
- Infrastructure (77) — Danvers Electric saves residents ~$2,036/year (perfect 100 sub-score)

**Weakest pillar:**
- Schools (50) — Pulled down hard by 51-spot rank decline over decade and below-state-average MCAS Math

### Historical Note

An earlier "expert estimate" produced 81 for Danvers. The rubric-based methodology produces 72. The 9-point gap is the entire reason this rubric system exists — it correctly penalizes the school decline that the expert estimate had soft-pedaled. **The 72 is the official score under v1.0.**

---

## 6. Tax Efficiency Ratio (TER)

```
TER = Civica Score ÷ Effective Tax Rate per $1,000
```

| TER | Rating |
|---|---|
| ≥ 9.0 | Exceptional |
| 7.0–8.99 | Strong |
| 5.0–6.99 | Average |
| 3.0–4.99 | Below Average |
| < 3.0 | Poor |

**Beverly vs Danvers comparison illustrates why TER matters:**
- Danvers: 72 / $13.36 = TER 5.4 (Average)
- Beverly: 73 / $11.23 = TER 6.5 (Average, near Strong)

Towns are nearly identical at headline score, but Beverly delivers meaningfully better value per tax dollar because its rate is $2.13/$1,000 lower.

---

## 7. Trajectory Indicator (Year 4+ only)

| Indicator | Criterion |
|---|---|
| ↑↑ Strongly Improving | Score up 5+ over 3 years |
| ↑ Improving | Score up 2–4 |
| → Steady | Within ±2 |
| ↓ Declining | Down 2–4 |
| ↓↓ Strongly Declining | Down 5+ |

Trajectory requires 3+ years of historical Civica Scores using the same methodology version. Year 1–3 will leave this blank.

For long-horizon decisions, trajectory is arguably more valuable than absolute score. Year 5 Civica is dramatically more valuable than Year 1 because of this.

---

## 8. How to Apply This Methodology to a New Town

### Step 1 — Pull the data
Use `source_dictionary.csv` and the field-by-field instructions in `06-collection-playbook.md` to populate every input from authoritative sources. Document each citation.

### Step 2 — Score each sub-metric
Using `scoring_rubrics.csv` and the implementation rules in `07-ai-implementation-spec.md`, look up each town's value in the right rubric and read off the 0–100 score.

### Step 3 — Compute pillar scores
For each pillar, sum (sub_score × sub_weight) using `pillar_weights.csv`.

### Step 4 — Compute the Civica Score
Sum (pillar_score × master_weight) using `master_weights.csv`. Round to nearest integer.

### Step 5 — Compute the TER
TER = Civica Score / residential_rate_per_1000. Round to one decimal. Match against bands.

### Step 6 — Document everything
Write to `towns.csv` schema. Cite every value. Mark data confidence based on gaps count (<5 = high, 5–15 = medium, >15 = low).

### Step 7 — Verify
Run `verify.py` to confirm the methodology still reproduces Danvers = 72 and Beverly = 73 before treating any new score as authoritative.

---

## 9. Defending the Methodology

1. **Every input is publicly sourced** — no proprietary data
2. **Every transformation is explicit** — reproducible by anyone
3. **All weights are published** — no black-box weighting
4. **Defaults are conservative** — gaps regress toward 50–70
5. **The methodology is versioned** — prior scores preserved when methodology changes
6. **Ratios are state-normalized** — fair across regions

If a town manager challenges Danvers's 72:
> "Here are your inputs from your own ACFR, your DESE data, and FBI UCR. Here's the rubric we applied. Here's the math. If any input is wrong, show us the corrected source and we'll update."

That conversation is winnable.

---

## 10. Methodology Versioning

Current: **v1.0**

Rules:
1. Any change to weights, rubrics, definitions = version bump
2. Prior version archived before change committed
3. Previously published scores remain valid under their original version

Planned:
- **v1.1** — Add ELA test scores, refine spending efficiency, add 5-year crime trend
- **v1.2** — Replace remaining placeholder logic, expand beyond MA
- **v2.0** — First major revision after a year of operation; validate against outcome data

---

## 11. Honest Limitations

- Default scores are necessarily approximate
- Trajectory requires 3 years of history
- Climate leans heavily on First Street
- Currently MA-only
- Some sub-metrics hard to source at scale (ISO ratings, 311 data, pension funding)
- Methodology not yet validated against outcomes
- Score precision matters less than 5-point bands
- Competitive landscape is crowded (Niche has 70M users; Civica is a fiscal specialist)

---

## Files Referenced

| File | Role |
|---|---|
| `master_weights.csv` | 8 pillar weights |
| `pillar_weights.csv` | 43 sub-metric weights |
| `scoring_rubrics.csv` | 276 rubric rules |
| `state_context.csv` | State median values |
| `source_dictionary.csv` | 43 cited sources |
| `verify.py` | Reproducibility test |
| `06-collection-playbook.md` | Field-by-field data collection |
| `07-ai-implementation-spec.md` | Implementation gotchas |

**When prose in this document conflicts with the CSVs, the CSVs are authoritative.**
