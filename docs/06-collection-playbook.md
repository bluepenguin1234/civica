# Civica Data Collection Playbook v2.0

> Field-by-field instructions for finding the 36 raw input values that feed the Civica scoring system.

This document tells an AI assistant **exactly how to find each of the 36 raw input values** for any Massachusetts municipality. For each field it specifies the source, retrieval procedure, validation ranges, and common gotchas.

**Companion documents:**
- `04-scoring-methodology.md` — pillar weights and scoring logic
- `07-ai-implementation-spec.md` — how to compute scores from values
- `05-citation-sop.md` — citation discipline rules

**Do not collect any field not listed here.** Earlier versions of this playbook listed ~45 fields; 9 of those (broadband, walk score, parks, library circulation, 311 response, EMS response, permits, air quality, tree canopy) are no longer scored and must not be collected or stored.

---

## How to Use This Playbook

Work through fields pillar by pillar. For each field:

1. Try the **primary source** first
2. If unavailable, try **fallback sources** in order
3. Validate against **expected range** to catch errors
4. Document the citation in companion `_src`, `_url`, `_retrieved` columns per `05-citation-sop.md`
5. If genuinely unavailable, leave blank — do **not** estimate

Allow ~4 hours per town for a full collection pass.

---

## PILLAR 1: FISCAL HEALTH (28%)

---

### Field 1: `bond` — S&P Bond Rating

**What it is:** S&P general obligation bond rating for the town.

**Primary source:** EMMA (MSRB Electronic Municipal Market Access)
**URL:** `https://emma.msrb.org/`
**Steps:**
1. Search for the town
2. Find most recent GO bond issue
3. Note S&P credit rating

**Fallback:** Town ACFR — quoted in "Long-Term Debt" notes

**Expected values:** AAA, AA+, AA, AA-, A+, A, A-, BBB+, BBB, or "Not rated"
**Gotcha:** Use most recent rating, not highest historical. Some towns are unrated — record as `null`.

---

### Field 2: `free_cash` — Free Cash % of Budget

**What it is:** Certified free cash as a percentage of the annual general fund budget.

**Primary source (MA):** MA DOR DLS Gateway — annual free cash certifications
**URL:** `https://dlsgateway.dor.state.ma.us/`
**Steps:**
1. Find the town's most recent free cash certification (DLS publishes annually)
2. Find total General Fund expenditures in the ACFR or budget document
3. Calculate: `(free_cash_dollars / GF_expenditures) × 100`

**Fallback:** Town ACFR — "Unassigned General Fund Balance" in MD&A section

**Expected range:** 0–25% (negative = fiscal crisis; >15% = exceptional)
**Gotcha:** "Total fund balance" ≠ free cash. Free cash / unassigned balance only. Do not include restricted funds.

---

### Field 3: `pension` — Pension Funded Ratio %

**What it is:** Funding ratio of the town's primary pension obligation.

**Primary source (MA):** MA PERAC (Public Employee Retirement Administration Commission)
**URL:** `https://www.mass.gov/perac` → Public Reports
**Steps:**
1. Find the town's retirement system (most Essex County towns use Essex Regional Retirement)
2. Open most recent actuarial valuation
3. Record "Funded Ratio" percentage

**Expected range:** 40–100%+ (under 70% = concerning; above 90% = excellent)
**Gotcha:** Pension and OPEB are different. Use pension specifically. Most MA towns use a county-level retirement system, not a town-specific fund.

---

### Field 4: `debt_pc` — Debt Per Capita ($)

**What it is:** Total outstanding bonded debt divided by population.

**Primary source:** Town ACFR → "Long-Term Debt" or "Bonded Debt Outstanding"
**Steps:**
1. Take total general obligation bonded debt
2. Divide by town population

**Expected range:** $500–$10,000 per capita
**Gotcha:** Use GO debt only. Do not include revenue bonds or enterprise fund (water/sewer) debt unless they are general obligation.

---

### Field 5: `gfoa` — GFOA Certificate (consecutive years)

**What it is:** Number of consecutive years the town has earned GFOA Certificate of Achievement for Excellence in Financial Reporting.

**Primary source:** Town ACFR cover page or introductory letters — usually states "X consecutive years"
**Fallback:** `https://www.gfoa.org/award-programs`

**Expected range:** 0–30+
**Gotcha:** Awarded retrospectively for the prior fiscal year. Record the stated number; do not add 1.

---

### Field 6: `transp` — Financial Transparency (ACFR Published)

**What it is:** Whether the town publishes its ACFR and annual budget online.

**Primary source:** Town's official website → Finance / Treasurer / Town Clerk pages

**Values:**
- `"Yes"` — both ACFR and budget are downloadable PDFs
- `"Partial"` — one of the two is available
- `"No"` — neither is publicly posted

**Gotcha:** Use exact casing above. This drives the grading lookup.

---

## PILLAR 2: SCHOOLS (25%)

---

### Field 7: `d_rank` — State District Rank

**What it is:** State ranking of the school district by composite measure.

**Primary source:** SchoolDigger
**URL:** `https://www.schooldigger.com/`
**Steps:**
1. Search the district name
2. Record "State Rank" shown as "#X of Y districts"

**Fallback:** MA DESE district profiles

**Expected range:** 1 to ~350 (MA)
**Gotcha:** Districts ≠ towns. Two towns may share a regional district. Use the district that serves the town's K–12 students.

---

### Field 8: `d_total` — Total Districts in State

**What it is:** Total number of school districts in the state (denominator for rank display).

**Primary source:** Same SchoolDigger page — shown as "X of Y"

**Expected value (MA):** ~350
**Note:** This is a display companion to `d_rank`. Collect at the same time.

---

### Field 9: `d_10yr` — 10-Year Rank Change

**What it is:** Change in state district rank over 10 years. **Positive = declining (rank got worse).**

**Primary source:** SchoolDigger → "Historical Rankings" tab
**Steps:**
1. Note rank in current year and rank ~10 years prior
2. Calculate: `current_rank − rank_10yr_ago`

**Expected range:** −100 to +100
**Gotcha:** Sign convention is critical. If rank was 145 in 2014 and 196 in 2024, record +51 (got worse).

---

### Field 10: `math` — MCAS Math Proficiency %

**What it is:** Percentage of students meeting or exceeding standard on state math assessment.

**Primary source:** MA DESE
**URL:** `https://profiles.doe.mass.edu/`
**Steps:**
1. Navigate to district profile → Assessment results
2. Take MCAS Math "Meeting or Exceeding" percentage, all grades combined, most recent year

**Expected range:** 15–75%

---

### Field 11: `grad` — 4-Year Graduation Rate %

**What it is:** Four-year cohort high school graduation rate.

**Primary source:** MA DESE district profile → Graduation & Dropout
**Expected range:** 70–99%
**Gotcha:** Use 4-year rate only, not the 5-year extended rate.

---

### Field 12: `ap` — AP Participation Rate %

**What it is:** Percentage of high school students taking at least one AP exam.

**Primary source:** US News Best High Schools or College Board state reports
**URL:** `https://www.usnews.com/education/best-high-schools/`

**Expected range:** 10–80%

---

### Field 13: `enrollment_trend` — Enrollment Trend (10yr)

**What it is:** Categorical direction of student enrollment over the past 10 years.

**Primary source:** MA DESE district profiles → Enrollment data (compare current vs 10yr prior)

**Values:** `"Growing"` / `"Stable"` / `"Declining"`
- Growing: >5% increase
- Stable: within ±5%
- Declining: >5% decrease

---

## PILLAR 3: TAX EFFICIENCY (15%)

---

### Field 14: `eff_rate` — Effective Tax Rate %

**What it is:** Effective property tax rate as a percentage of home value.

**Calculation:** `(median_annual_tax_bill / median_home_value) × 100`
**Or:** `residential_rate_per_1000 / 10` for MA towns where assessment ratio is 100%

**Primary source:** MA DOR DLS Gateway or calculation from Fields 15 + 19

**Expected range:** 0.5–2.5%

---

### Field 15: `med_tax` — Median Annual Tax Bill ($)

**What it is:** Median annual property tax bill paid by homeowners.

**Primary source:** Census ACS5 → "Median Real Estate Taxes Paid"
**URL:** `https://data.census.gov/`

**Fallback:** AGG_OWNWELL

**Expected range:** $1,000–$20,000
**Validation:** Should ≈ `eff_rate × med_home_val`. Off by >50%? Re-check.

---

### Field 16: `med_inc` — Median Household Income ($)

**What it is:** Median household income per most recent ACS.

**Primary source:** Census ACS5 → "Income" → "Median Household Income"
**Expected range:** $30,000–$200,000+
**Gotcha:** Use median *household* income, not median *family* income (family is typically higher).

---

### Field 17: `res_rate` — Residential Rate (per $1,000 AV)

**What it is:** Residential property tax rate in dollars per $1,000 of assessed value.

**Primary source (MA):** MA DOR DLS Gateway → Tax Rates → most recent FY → residential rate column
**URL:** `https://dlsgateway.dor.state.ma.us/`

**Expected range:** $5–$30
**Gotcha:** Some towns have split rates (residential vs commercial differ). Always use the residential rate.

---

### Field 18: `tax_non_res` — Non-Residential Tax Base %

**What it is:** Percentage of total assessed value that is commercial + industrial (not residential).

**Primary source:** Town ACFR → Statistical Section → "Assessed Value by Property Class"
**Steps:**
1. Find table showing assessed value by class
2. Calculate: `(commercial + industrial + personal property) / total × 100`

**Expected range:** 5–40%
**Gotcha:** Use assessed value mix, not tax revenue split (revenue varies with split rates).

---

### Field 19: `med_home_val` — Median Home Value ($)

**What it is:** Median owner-occupied home value.

**Primary source:** Census ACS5 → "Housing" → "Median Value (Dollars)"
**Expected range:** $200,000–$2,000,000+

---

## PILLAR 4: SAFETY (15%)

---

### Field 20: `violent` — Violent Crime per 100k

**What it is:** Violent crimes (murder, rape, robbery, aggravated assault) per 100,000 residents.

**Primary source:** FBI Crime Data Explorer
**URL:** `https://cde.ucr.cjis.gov/`
**Steps:**
1. Search the town's law enforcement agency
2. Most recent year with full submission
3. Calculate per-100k if reported as raw counts

**Fallback:** MA EOPSS crime statistics

**Expected range:** 50–1,500 per 100k
**Gotcha:** Check submission completeness. Some agencies have reporting gaps — use most recent fully-reported year.

---

### Field 21: `prop_crime` — Property Crime per 100k

**What it is:** Property crimes (burglary, larceny-theft, motor vehicle theft) per 100,000 residents.

**Primary source:** FBI Crime Data Explorer (same search as violent crime)
**Expected range:** 500–4,000 per 100k

---

### Field 22: `sex_off` — Registered Sex Offenders per 1,000 Residents

**What it is:** Number of registered sex offenders divided by population, expressed per 1,000 residents.

**Primary source (MA):** MA Sex Offender Registry Board
**URL:** `https://www.mass.gov/sex-offender-registry`
**Steps:**
1. Search by town to count Level 2 and Level 3 registrants
2. Divide by town population × 1,000

**Expected range:** 0.1–5.0 per 1,000
**Gotcha:** Count only registered (Level 2 + Level 3) offenders, not Level 1 (not publicly listed).

---

## PILLAR 5: ECONOMIC MOMENTUM (8%)

---

### Field 23: `inc10yr` — Income Growth (10yr) %

**What it is:** Percentage change in median household income over 10 years.

**Primary source:** Census ACS5 (current) and Census ACS5 ~10 years prior
**Calculation:** `((current_income − income_10yr_ago) / income_10yr_ago) × 100`
**Expected range:** 10–80%

---

### Field 24: `pop10yr` — Population Growth (10yr) %

**What it is:** Percentage change in population over 10 years.

**Primary source:** Census ACS5
**Calculation:** `((current_pop − pop_10yr_ago) / pop_10yr_ago) × 100`
**Expected range:** −10 to +30%

---

### Field 25: `unemp` — Unemployment Rate %

**What it is:** Most recent published unemployment rate.

**Primary source:** BLS LAUS (Local Area Unemployment Statistics)
**URL:** `https://www.bls.gov/lau/`
**Note:** BLS may publish county-level; for town-level, check MA Executive Office of Labor and Workforce Development
**Expected range:** 2–10%

---

### Field 26: `pov` — Poverty Rate %

**What it is:** Percentage of residents below the federal poverty line.

**Primary source:** Census ACS5 → "Poverty Status in the Past 12 Months"
**Expected range:** 2–25%

---

### Field 27: `owner_occ` — Owner-Occupied Housing %

**What it is:** Percentage of occupied housing units that are owner-occupied.

**Primary source:** Census ACS5 → "Housing Tenure"
**Expected range:** 40–90%

---

### Field 28: `vacancy` — Vacancy Rate %

**What it is:** Percentage of housing units that are vacant.

**Primary source:** Census ACS5 → "Housing Occupancy"
**Expected range:** 2–15%

---

### Field 29: `med_age` — Median Age (years)

**What it is:** Median age of residents.

**Primary source:** Census ACS5 → "Age and Sex"
**Expected range:** 25–55 years

---

## PILLAR 6: INFRASTRUCTURE & UTILITIES (6%)

---

### Field 30: `elec_save` — Electric Savings vs State Avg ($/yr)

**What it is:** Annual savings (or extra cost if negative) vs state average electric rate for a typical 10,380 kWh/year residential customer.

**Calculation:** `(state_avg_rate_cents − town_rate_cents) / 100 × 10380`

**Primary source:** EIA Form 861 (state averages) and town utility website (if municipal electric)
**Steps:**
1. Determine if town has municipal electric (MLDs in Essex County: Danvers, Ipswich, Georgetown, Middleton, Merrimac, Groveland, Rowley, Marblehead, Peabody)
2. If municipal: find current residential rate from town electric department website
3. If investor-owned: savings = $0 (town pays state average)
4. Calculate annual savings vs MA state average

**Expected range:** −$500 to +$2,500 (municipal utilities often save $500–$2,000/yr)
**Gotcha:** Most towns use investor-owned utilities (NStar/Eversource). Only municipal electric towns have meaningful savings.

---

### Field 31: `water_viol` — Water Quality Violations (5yr)

**What it is:** Number of EPA Safe Drinking Water Act violations in the past 5 years.

**Primary source:** EPA SDWIS
**URL:** `https://enviro.epa.gov/envirofacts/sdwis/search`
**Steps:**
1. Search for the town's water system (by PWSID)
2. Filter to past 5 years
3. Count violations (any type)

**Expected range:** 0–10
**Gotcha:** Some towns have multiple water systems (multiple PWSIDs). Sum across all systems serving the town.

---

### Field 32: `transit` — Transit Access

**What it is:** Categorical assessment of transit access.

**Primary source:** MBTA website + town website
**Values:**
- `"Commuter Rail"` — town has commuter rail station(s)
- `"Bus Only"` — MBTA or regional bus service, no rail
- `"None"` — no meaningful transit service

**Steps:**
1. Check if town has MBTA commuter rail station
2. If not, check for MBTA bus routes or CATA/MVRTA regional bus
3. Assign category

---

## PILLAR 7: CLIMATE RESILIENCE (3%)

---

### Field 33: `flood` — Flood Risk — Current %

**What it is:** Percentage of properties at substantial flood risk (current conditions).

**Primary source:** First Street Foundation
**URL:** `https://firststreet.org/`
**Steps:**
1. Search for the town
2. Record "% of properties at substantial risk"

**Expected range:** 0–30%
**Gotcha:** First Street uses property-level modeling; differs from FEMA flood map percentages.

---

### Field 34: `flood50` — Flood Risk Growth by 2050 (percentage points)

**What it is:** Projected percentage-point increase in flood risk by 2050.

**Calculation:** First Street 2050 projection − current value
**Primary source:** First Street Foundation (same page as `flood`)
**Expected range:** 0–10 percentage points

---

### Field 35: `fire` — Wildfire Risk

**What it is:** Categorical wildfire risk level.

**Primary source:** First Street Foundation
**Expected values (lowercase):** `"low"` / `"moderate"` / `"high"` / `"very high"` / `"extreme"`

---

## IDENTITY FIELDS (Not Scored — Required for Display)

Collect these for every town:

| Field | What it is | Source |
|---|---|---|
| `name` | Town name | Known |
| `county` | County name | Known |
| `state` | State abbreviation | `"MA"` |
| `zip` | Primary ZIP code | USPS |
| `pop` | Total population | Census ACS5 |

**Note:** `ter` (Tax Efficiency Ratio) and `ter_r` (TER rating) are computed automatically — do not collect them.

---

## Field Count Summary

| Pillar | Fields |
|---|---|
| Fiscal Health | bond, free_cash, pension, debt_pc, gfoa, transp (6) |
| Schools | d_rank, d_total, d_10yr, math, grad, ap, enrollment_trend (7) |
| Tax Efficiency | eff_rate, med_tax, med_inc, res_rate, tax_non_res, med_home_val (6) |
| Safety | violent, prop_crime, sex_off (3) |
| Economic Momentum | inc10yr, pop10yr, unemp, pov, owner_occ, vacancy, med_age (7) |
| Infrastructure | elec_save, water_viol, transit (3) |
| Climate | flood, flood50, fire (3) |
| **Total scored fields** | **35 + d_total = 36** |

---

## Confidence Marking

After collection, set `conf`:

- `"high"` — All fields populated except documented gaps; <5 gaps → ready to publish
- `"medium"` — 5–15 gaps OR significant Tier-3 reliance → review before publishing
- `"low"` — >15 gaps → not yet ready

Set `gaps` to the count of blank required fields.

---

## When You're Genuinely Stuck

If after working through all sources a value is truly unavailable:

1. Leave the field `null`
2. Document in `compiler_notes`: `"{field}: not published — {what was tried}, {date}"`
3. Increment `gaps`
4. Move on

**Do NOT estimate. Do NOT interpolate. Do NOT cite a number you cannot verify.**

This is the citation discipline that makes Civica defensible.
