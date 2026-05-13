# Civica Scoring Methodology v2.0

> Reproducible. Defensible. Open.

This document is the conceptual reference for the Civica scoring system. For implementation-level details (grading thresholds, edge cases, missing-data handling), see `07-ai-implementation-spec.md`. For data collection instructions, see `06-collection-playbook.md`.

**Authoritative source:** The `computeScore(t)` and `grade(k,v,t)` functions in `civica-v5.html` are the single source of truth. If this document conflicts with that code, the code wins.

---

## 1. The Core Formula

```
Civica Score = Σ (Pillar Score × Pillar Weight)
```

Each of **7 pillars** scores 0–100. Weights sum to 1.00. Result is a 0–100 composite rounded to the nearest integer.

Each pillar score is the **unweighted average** of the green/yellow/red point values for its gradeable metrics:

```
green  = 100 points
yellow =  55 points
red    =  15 points
na     = excluded from average (not in denominator)
```

If a metric is missing (`null`) it returns `na` — it does not count as red. If all metrics in a pillar are `na`, the pillar defaults to 50.

---

## 2. The 7 Pillars

| # | Pillar | Weight |
|---|---|---|
| 1 | Fiscal Health | 28% |
| 2 | Schools | 25% |
| 3 | Tax Efficiency | 15% |
| 4 | Safety | 15% |
| 5 | Economic Momentum | 8% |
| 6 | Infrastructure & Utilities | 6% |
| 7 | Climate Resilience | 3% |

Weights sum to 100%.

---

## 3. The 36 Data Points

36 raw inputs collected per town (see `06-collection-playbook.md` for sourcing):

- **Fiscal Health (6):** bond rating, free cash %, pension funded ratio, debt per capita, GFOA consecutive years, financial transparency (ACFR)
- **Schools (7):** state district rank, total districts (denominator), 10-year rank change, math proficiency %, graduation rate %, AP participation %, enrollment trend
- **Tax Efficiency (6):** effective tax rate %, median annual tax bill, median household income, residential rate per $1k AV, non-residential tax base %, median home value
- **Safety (3):** violent crime per 100k, property crime per 100k, registered sex offenders per 1k
- **Economic Momentum (7):** income growth (10yr), population growth (10yr), unemployment %, poverty %, owner-occupied housing %, vacancy rate %, median age
- **Infrastructure (3):** electric savings vs state avg, water quality violations (5yr), transit access
- **Climate (3):** flood risk current %, flood risk growth by 2050 (pts), wildfire risk

Not every data point is scored — some are display-only (informational context shown in town profiles but not feeding the score formula). See `07-ai-implementation-spec.md` for the full list.

---

## 4. Grading Philosophy

Each scored metric is graded green/yellow/red using thresholds defined in `civica-v5.html`. The key principles:

- **Missing data = `na`**, not red. A town isn't penalized for data we can't find.
- **Thresholds are fixed**, not relative to state medians. Danvers vs Beverly is an apples-to-apples comparison.
- **Pillar score = simple average** of its graded metrics (excluding `na`). No within-pillar weighting — all gradeable metrics in a pillar count equally.
- **Exception: Fiscal Health** uses a weighted blend — the core three metrics (bond, free cash, debt) carry 3× weight; pension carries 1×; transparency and GFOA carry 0.5× each. This reflects that bond ratings and cash reserves are the most direct measures of fiscal stress.

---

## 5. The TER (Tax Efficiency Ratio)

```
TER = Civica Score ÷ Residential Rate (per $1,000 AV)
```

| TER | Rating |
|---|---|
| ≥ 5.0 | Strong |
| ≥ 3.0 | Fair |
| < 3.0 | Weak |

TER answers: *given what this town charges in property taxes, how much civic quality does a resident get?* A high-tax town can still be Strong TER if it delivers outstanding schools, safety, and infrastructure. A low-tax town with poor services scores Weak TER.

TER feeds back into the Tax Efficiency pillar as a gradeable metric alongside effective tax rate.

---

## 6. What Changed From v1.0

**Removed:** Operational Responsiveness pillar (311 response, EMS response, permits, ISO fire rating). These metrics were rarely available for small towns, defaulted almost universally, and provided little signal.

**Weight rebalance:** The freed 10% was allocated to Safety (+10%, from 5%→15%) and Schools (+10%, from 15%→25%), reflecting homebuyer research showing schools and safety are the two highest-weighted factors in residential location decisions. Fiscal was trimmed by 2%, Economic by 2%, Infrastructure by 4%, Climate by 2%.

**Removed data points:** broadband, walk score, parks acreage, library circulation, crime 5-year trend, bachelor's degree %, per-pupil spending, heat days projection, air quality AQI, tree canopy %, ISO fire rating, 311 response time, EMS response time, permits per 1,000.

**Added data points:** sex offenders per 1k (Safety), enrollment trend (Schools), owner-occupied %, vacancy rate, median age (all Economic Momentum), median home value (Tax Efficiency).

---

## 7. How to Score a New Town

**Step 1 — Collect the 36 data points**
Use `06-collection-playbook.md`. Document every citation. Do not estimate.

**Step 2 — Grade each scored metric**
Using thresholds in `civica-v5.html grade()`. Missing = `na`, excluded from average.

**Step 3 — Compute pillar scores**
Average the non-`na` grade values within each pillar. Use fiscal weighted blend for Pillar 1.

**Step 4 — Compute the Civica Score**
`fiscal×0.28 + schools×0.25 + tax×0.15 + safety×0.15 + momentum×0.08 + infra×0.06 + climate×0.03`
Round to nearest integer.

**Step 5 — Compute TER**
`score / res_rate`, round to 1 decimal, assign rating band.

**Step 6 — Set confidence**
Count `null` fields among the 36. `conf = "high"` if gaps <5, `"medium"` if 5–15, `"low"` if >15.

**Step 7 — Add to TOWNS array in civica-v5.html**
One town object per line, all fields on that line. Commit to dev branch, merge to main, push both.

---

## 8. Honest Limitations

- Some display metrics are not scored (informational only); score reflects only the gradeable subset
- Missing data defaults to `na` exclusion — a town with many gaps may appear better than warranted
- Climate relies heavily on First Street Foundation modeling
- Currently Massachusetts-only
- Trajectory indicator requires 3+ years of historical scores; not yet available
- Score precision: treat 5-point bands as meaningful, not individual points

---

## 9. Defending the Methodology

1. **Every input is publicly sourced** — no proprietary data
2. **Every transformation is explicit** — reproducible by anyone
3. **All weights are published** — no black-box weighting
4. **Missing data is excluded, not penalized** — gaps don't inflate or deflate scores
5. **The methodology is versioned** — prior scores preserved when methodology changes

If a town manager challenges a score:
> "Here are your inputs from your own ACFR, your DESE data, and FBI UCR. Here's the threshold we applied. Here's the math. If any input is wrong, show us the corrected source and we'll update."

That conversation is winnable.

---

## 10. Methodology Versioning

Current: **v2.0** (7 pillars, 36 data points)
Previous: **v1.0** (8 pillars, ~43 sub-metrics) — archived

Rules:
1. Any change to weights, thresholds, or definitions = version bump
2. Previously published scores remain valid under their original version

---

## Files Referenced

| File | Role |
|---|---|
| `civica-v5.html` | Authoritative `computeScore()` and `grade()` implementation |
| `06-collection-playbook.md` | Field-by-field data collection (36 fields) |
| `07-ai-implementation-spec.md` | Grading thresholds, missing-data rules, implementation gotchas |
| `data/towns.csv` | Town data — 1 header row + 1 row per town |
| `data/state_context.csv` | State-level baseline values |
