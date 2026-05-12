# Civica AI Implementation Specification v1.0

> Implementation-level details an AI assistant needs to correctly compute Civica Scores from the methodology CSVs.

This document is targeted at an AI implementing the Civica scorer from scratch. The conceptual methodology lives in `04-scoring-methodology.md`; the **mechanics that produce silently wrong scores if implemented naively** live here.

**Verification:** A correct implementation reproduces Danvers, MA = 72 / TER 5.4 and Beverly, MA = 73 / TER 6.5. Run `verify.py` to confirm.

---

## Why This Document Exists

While building the Civica reference workbook, two specific implementation bugs were discovered that produced silently wrong scores — no error message, just numbers that looked plausible but were incorrect:

1. The safety pillar referenced a sub-metric `fire_iso` that had no rubric rules, returning `#N/A` and breaking aggregation
2. Ratio helper calculations returned 0 (not blank) when raw inputs were missing, which silently matched the lowest range bucket and inflated scores

Both bugs are documented here so future implementations don't repeat them.

---

## 1. The Helper Calculation Checklist

Before any rubric lookup, **9 helper values must be computed** from raw inputs. These are inputs to specific sub-metrics.

| Helper | Formula | Used By |
|---|---|---|
| `tax_burden_pct` | `(median_annual_tax_bill / median_household_income) × 100` | tax_burden_to_income |
| `rank_percentile` | `(1 − district_state_rank / district_state_rank_total) × 100` | rank_percentile, spending_efficiency |
| `spending_efficiency_idx` | `(rank_pct/100) ÷ (per_pupil_spending / state_median_per_pupil)` | spending_efficiency |
| `debt_ratio` | `town_debt_per_capita / state_debt_per_capita_median` | debt_per_capita |
| `violent_crime_ratio` | `town_violent_per_100k / state_violent_avg` | violent_crime |
| `property_crime_ratio` | `town_property_per_100k / state_property_avg` | property_crime |
| `income_ratio` | `town_median_income / state_median_income` | income_level |
| `poverty_ratio` | `town_poverty_pct / state_poverty_pct` | poverty |
| `unemployment_ratio` | `town_unemployment / state_unemployment` | unemployment |

**Compute these BEFORE attempting any rubric lookup.** The sub-metrics that consume them expect the ratio/percentage value, not the raw values.

---

## 2. The Missing-Data Convention

**Critical rule:** When a raw input is missing, helper calculations must return `null`/`None`/blank — **never 0**.

### Why this matters

If `unemployment_ratio` returns 0 when input is missing, Excel/Sheets/Python treats 0 as a valid number that falls into the lowest range bucket (0 to 0.7 → score 100). This silently inflates the score by ~30 points.

### Correct pattern (Python)

```python
def safe_div(a, b):
    if a is None or a == "":
        return None
    try:
        return float(a) / float(b)
    except (TypeError, ValueError, ZeroDivisionError):
        return None
```

### Correct pattern (spreadsheet)

```
=IF(input_cell="","",input_cell / state_median)
```

**Wrong** (returns 0 when blank):
```
=IFERROR(input_cell / state_median, 0)
```

### What happens when a sub-metric receives null

The rubric returns the **documented default** for that sub-metric (typically 50–70). This is correct behavior — it represents genuine uncertainty without artificially inflating or deflating the score.

---

## 3. The fire_iso / iso_fire Aliasing

### The fact

The safety pillar uses sub-metric ID `iso_fire` (not `fire_iso`). The rubrics file only has rules for `iso_fire`. The same ISO fire rating contributes to **both** the operational pillar and the safety pillar — they reuse the same sub-metric.

### Why this matters

Earlier versions of `pillar_weights.csv` used `fire_iso` for the safety pillar. If you implement based on those weights without checking the rubrics, the safety pillar tries to look up `fire_iso` rules that don't exist and silently fails.

### Correct implementation

In the safety pillar weighted sum:

```python
safety_score = (
    sub_scores["violent_crime"] * 0.40 +
    sub_scores["property_crime"] * 0.25 +
    sub_scores["crime_trajectory"] * 0.20 +
    sub_scores["iso_fire"] * 0.15           # NOT fire_iso
)
```

The current `pillar_weights.csv` correctly uses `iso_fire` for the safety pillar's last sub-metric. Maintain this convention.

---

## 4. The Parks + Libraries Composite

The `parks_libraries` sub-metric is not directly looked up. It's a **composite of two separately-scored sub-metrics**:

```python
park_score = score_submetric("park_score", park_acres_per_1000, rubrics)
library_score = score_submetric("library_score", library_circ_per_capita, rubrics)
parks_libraries_score = (park_score + library_score) / 2
```

In the infrastructure pillar aggregation:

```python
infrastructure_score = (
    sub_scores["electric_value"] * 0.30 +
    sub_scores["water_quality"] * 0.20 +
    sub_scores["broadband"] * 0.15 +
    sub_scores["transit"] * 0.15 +
    sub_scores["walkability"] * 0.10 +
    parks_libraries_score * 0.10            # the composite, not a direct lookup
)
```

Both `park_score` and `library_score` have their own rubric rules in `scoring_rubrics.csv`. The composite is computed in code, not stored in the rubrics file.

---

## 5. Data Format Conventions

These look obvious but trip up implementations.

### ISO fire ratings are strings

In `scoring_rubrics.csv`, ISO ratings are stored as `"1"`, `"2"`, ... `"10"` (strings, not integers). The lookup is a string match. If your input is integer 4, convert to string `"4"` before matching.

### Categorical values are case-insensitive

`"AA+"` and `"aa+"` should both match the bond_rating row for `AA+`. Implement lookup as:

```python
str(raw_value).strip().lower() == str(rule["match_value"]).strip().lower()
```

### Range bounds are inclusive low, exclusive high

A rule with `lower_bound=0, upper_bound=2` matches values where `0 <= v < 2`. A value of exactly 2 matches the **next** row. Critical for boundary cases.

### Wildfire risk values are lowercase

Use `"low"`, `"moderate"`, `"high"`, `"very high"`, `"extreme"`. Capitalized inputs like `"Low"` will match (case-insensitive), but the canonical form is lowercase.

### Transparency is `yes`/`partial`/`no`

Lowercase only. The rubric matches case-insensitively but documents the canonical form as lowercase.

### Transit access has 8 valid values

`commuter_rail_in_town`, `commuter_rail_nearby`, `bus_only`, `limited`, `none`, `yes`, `no`, `nearby`. The first five are the canonical taxonomy; `yes`/`no`/`nearby` are aliases for backward compatibility.

---

## 6. State Context Is Required Before Scoring

Six sub-metrics require state-level baseline values from `state_context.csv`:

| Sub-metric | Requires | State Context Key |
|---|---|---|
| debt_per_capita | state debt median | `debt_per_capita_median` |
| violent_crime | state violent crime avg | `violent_crime_per_100k` |
| property_crime | state property crime avg | `property_crime_per_100k` |
| income_level | state median income | `median_household_income` |
| poverty | state poverty rate | `poverty_rate_pct` |
| unemployment | state unemployment | `unemployment_rate_pct` |

Plus `spending_efficiency` requires `per_pupil_spending_median`.

**Before scoring any town in a new state, populate `state_context.csv` for that state.** If you score a town in a state without context, the ratio calculations will fail (return null) and 6 sub-metrics will fall back to defaults — silently producing a less accurate score.

---

## 7. The Scoring Sequence

Strict order required. Skipping or reordering produces wrong results.

```
1. Load methodology files (master_weights, pillar_weights, scoring_rubrics, state_context)
2. Confirm state_context has rows for the town's state
3. Load the town's raw inputs (from towns.csv or directly from data sources)
4. Compute the 9 helper values (using state context where needed)
5. For each of 42 sub-metrics, look up the rubric and compute 0–100 score
6. For park_score and library_score, compute additionally; average for parks_libraries
7. For each pillar, compute weighted sum of sub-metric scores
8. Compute Civica Score as weighted sum of pillar scores; round to integer
9. Compute TER = Civica Score / residential_rate_per_1000; round to 1 decimal
10. Look up TER rating from band thresholds
11. Write output to towns.csv schema
12. Run verify.py to confirm methodology hasn't drifted
```

---

## 8. Verification Protocol

After ANY change that touches the methodology files or scoring code:

```bash
python verify.py
```

Expected output ends with `✓ VERIFICATION PASSED`. If it shows `✗ VERIFICATION FAILED`, the methodology has drifted and must be fixed before any new town scores are treated as authoritative.

`verify.py` independently re-implements the scoring logic and tests against the Danvers and Beverly datasets. It is the canonical reproducibility test.

---

## 9. Output Schema

When writing to `towns.csv`:

| Column Group | Notes |
|---|---|
| Identity (5 cols) | town_name, state, county, zip_codes, population |
| Raw inputs (~42 cols) | One per sub-metric input; left blank if data unavailable |
| Helper calcs (9 cols) | Computed; left blank if any input null |
| Pillar scores (8 cols) | Computed; rounded to 1 decimal |
| Final outputs (3 cols) | civica_score (integer), ter (1 decimal), ter_rating (string) |
| Metadata (4 cols) | data_gaps_count, data_confidence, last_updated, compiler_notes |

For each raw input column, also populate the `_src` and `_retrieved` companion columns per `05-citation-sop.md`. Town-specific document fields also populate `_url`.

---

## 10. Common Implementation Mistakes

### "I'll just estimate the missing values to be helpful"
**Wrong.** Leave blank, document the gap, let the rubric default fire. Estimating compromises the citation discipline that is the entire point of Civica.

### "I'll average two disagreeing sources"
**Wrong.** Pick the higher-tier source and document the discrepancy. Averaging hides the source disagreement.

### "I'll round at every intermediate step for cleanliness"
**Wrong.** Round only at the final Civica Score (integer) and TER (1 decimal). Intermediate rounding accumulates error.

### "The Danvers verification passes, so my code is correct"
**Necessary but not sufficient.** Danvers has many data gaps. A code bug affecting only well-populated fields might not show up in Danvers. Run verify.py against both Danvers and Beverly, and ideally a third town once you score one.

### "I'll add this new sub-metric without versioning"
**Wrong.** Any change to weights, rubrics, or sub-metric definitions requires a methodology version bump. Add to `methodology/archive/v1.0/` first.

### "The score came out as 87 not 72 — must be a calculation issue, let me adjust"
**Wrong.** If verify.py passes (Danvers = 72), the methodology is correct. If a new town scores 87, that's the methodology's honest output. Don't tune to taste; document and publish.

---

## 11. Performance Notes

For one town, scoring takes <1 second (mostly file I/O). For 100 towns, scoring takes <10 seconds. Don't optimize prematurely.

If scoring 1000+ towns, consider:
- Loading methodology files once and reusing
- Pandas vectorization for the rubric lookups
- Parallel scoring (each town is independent)

But first, get correctness right. The verification protocol matters more than performance.

---

## 12. When You're Stuck

If your implementation produces a score that doesn't match `verify.py`:

1. Compare your pillar scores to the documented Danvers values:
   - Fiscal Health 80.3, Tax Efficiency 75.4, Schools 50.2, Operational 66.2, Infrastructure 76.6, Safety 69.8, Economic 81.3, Climate 68.7
2. Find which pillar diverges
3. Compare your sub-metric scores within that pillar
4. Find which sub-metric diverges
5. Check the rubric application for that sub-metric:
   - Is the input the right one? (raw value vs helper calc?)
   - Is the rubric type right? (range vs lookup?)
   - For range: are bounds inclusive low / exclusive high?
   - For lookup: is the comparison case-insensitive?
   - Is missing-data handling returning the documented default?

Most divergences come from: helper calc returning 0 instead of blank, ISO ratings as int not string, or fire_iso vs iso_fire.

---

## Files Referenced

| File | Role |
|---|---|
| `master_weights.csv` | Pillar weights |
| `pillar_weights.csv` | Sub-metric weights |
| `scoring_rubrics.csv` | 276 rubric rules |
| `state_context.csv` | State medians |
| `verify.py` | Reproducibility test (run after any change) |
| `04-scoring-methodology.md` | Conceptual reference |
| `05-citation-sop.md` | Citation rules |
| `06-collection-playbook.md` | Field-by-field data sourcing |

**When this spec conflicts with `verify.py` output, `verify.py` is authoritative.** It is the single source of truth for "is the methodology working correctly."
