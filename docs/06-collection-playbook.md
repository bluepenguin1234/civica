# Civica Data Collection Playbook v1.0

> Field-by-field instructions for finding the raw values that feed the Civica scoring system.

This document tells an AI assistant **exactly how to find each of the ~42 raw input values** for any U.S. municipality. For each field, it specifies the source, retrieval procedure, identification heuristics, validation ranges, and common gotchas.

**Companion documents:**
- `source_dictionary.csv` — full list of 43 cited sources with URLs
- `04-scoring-methodology.md` — what the values feed into
- `07-ai-implementation-spec.md` — how to compute scores from values
- `05-citation-sop.md` — citation discipline rules

---

## How to Use This Playbook

For each town, work through fields in the order listed. Some fields are easy 5-minute pulls (Census ACS demographics); some require ACFR PDF parsing (free cash, debt). Allow ~6 hours per town for a full data collection pass.

For each field:

1. Try the **primary source** first
2. If not available, try **fallback sources** in tier order
3. Validate against the **expected range** to catch errors
4. Document the citation in `_src`, `_url`, `_retrieved` columns
5. If genuinely unavailable, leave blank and document in `compiler_notes`

---

## Field 1: population

**What it is:** Total town population per most recent 5-year ACS estimate.

**Primary source:** CENSUS_ACS5
**URL pattern:** `https://data.census.gov/profile?q={town},{state}`
**Retrieval steps:**
1. Visit Census Reporter or data.census.gov
2. Search "{town}, {state}"
3. Find the "Total Population" headline figure
4. Note the vintage (e.g., "2024 5-year")

**Fallback sources:** AGG_DATAUSA, AGG_CITYDATA (verify upstream)

**Expected range:** 100 – 500,000 for typical municipalities
**Common gotcha:** Some sources report city-vs-CDP populations differently. Use the incorporated municipality figure.

---

## Field 2: residential_rate_per_1000

**What it is:** Residential property tax rate, expressed as dollars per $1,000 of assessed value.

**Primary source:** State DOR (e.g., MA_DOR_DLS for Massachusetts)
**URL pattern (MA):** `https://dlsgateway.dor.state.ma.us/`
**Retrieval steps (MA-specific):**
1. Go to MA DOR DLS Gateway
2. Navigate to "Tax Rates" → most recent FY
3. Find the town's row
4. Take the residential rate column

**For other states:** Each state's DOR publishes equivalent data; URL patterns vary. Search "{state} property tax rates by municipality {year}".

**Fallback sources:** AGG_OWNWELL, AGG_CITYDATA

**Expected range:** $5 – $30 per $1,000 in most U.S. towns
**Common gotcha:** Some towns use split rates (different residential vs commercial). Always use the residential rate. Some sources report "effective rate" as a percentage; convert by multiplying by 10.

---

## Field 3: effective_tax_rate_pct

**What it is:** Effective property tax rate as a percentage of home value.

**Calculation:** Often `residential_rate_per_1000 / 10` for towns where assessment ratio is 100% (most MA towns). Otherwise: `(median_annual_tax_bill / median_home_value) × 100`.

**Primary source:** AGG_OWNWELL or state DOR
**Fallback:** Calculate from rate × assessment ratio

**Expected range:** 0.5% – 2.5%
**Common gotcha:** Some states have low statutory rates but high assessment ratios; effective rate is what matters for the rubric.

---

## Field 4: median_annual_tax_bill

**What it is:** Median annual property tax bill paid by homeowners.

**Primary source:** CENSUS_ACS5 (Real Estate Taxes Paid)
**URL pattern:** Same Census profile page
**Retrieval steps:**
1. Census town profile → "Housing" section
2. "Median Real Estate Taxes Paid"

**Fallback:** AGG_OWNWELL

**Expected range:** $1,000 – $20,000
**Validation:** Should approximately equal `effective_tax_rate × median_home_value`. Off by >50%? Re-check.

---

## Field 5: median_household_income

**What it is:** Median household income per most recent ACS.

**Primary source:** CENSUS_ACS5
**Retrieval steps:**
1. Census town profile → "Income" section
2. "Median Household Income"

**Expected range:** $30,000 – $200,000+
**Common gotcha:** Median *family* income is different and typically higher. Use median *household*.

---

## Field 6: bond_rating_sp

**What it is:** S&P bond rating for the town's general obligation debt.

**Primary source:** EMMA (MSRB Electronic Municipal Market Access)
**URL pattern:** `https://emma.msrb.org/Search/Search.aspx?searchtype=I&issuer={town}`
**Retrieval steps:**
1. Search EMMA for the town
2. Find most recent GO bond issue
3. Look for "Credit Ratings" section
4. Note the S&P rating (also note Moody's and Fitch if present)

**Fallback:** Town ACFR — usually quoted in the "Long-Term Debt" notes
**Tier 4 fallback:** Press releases when town is upgraded/downgraded

**Expected range:** AAA, AA+, AA, AA-, A+, A, A-, BBB+, BBB, BBB-, BB+ and below
**Common gotcha:** Bond ratings expire. Use most recent rating, not the highest historical. Some towns are unrated — record as "Not rated".

---

## Field 7: free_cash_pct_of_budget

**What it is:** Town's certified free cash as a percentage of annual general fund budget.

**Primary source:** TOWN_ACFR or state-specific free cash certification
**For MA:** MA DOR DLS publishes annual free cash certifications
**URL pattern (MA):** Search "{town} free cash certification {year}" → MA DLS document
**Retrieval steps:**
1. Find town's most recent ACFR or budget document
2. Look for "Free Cash" or "Unassigned General Fund Balance" in the MD&A section
3. Find total General Fund expenditures in the same document
4. Calculate: (free cash / GF expenditures) × 100

**Expected range:** 0% – 25% (negative = fiscal crisis; >15% is exceptional)
**Common gotcha:** "Total fund balance" is NOT the same as free cash; it includes restricted funds. Use unassigned/free cash specifically. Some towns use different terminology — verify the definition matches.

---

## Field 8: pension_funded_ratio_pct

**What it is:** Funding ratio of the town's primary pension obligation.

**Primary source:** State pension oversight body
**For MA:** MA_PERAC (Public Employee Retirement Administration Commission)
**URL pattern (MA):** `https://www.mass.gov/perac` → Public Reports → individual system reports
**Retrieval steps (MA):**
1. Navigate to PERAC public reports
2. Find the town's retirement system (often county-level: "Essex Regional Retirement")
3. Open most recent actuarial valuation
4. Look for "Funded Ratio" — typically a percentage

**For other states:** Each state has equivalent oversight (CalPERS for California municipalities, etc.)

**Expected range:** 40% – 100%+ (under 70% is concerning; over 90% is excellent)
**Common gotcha:** Pension and OPEB are different obligations; use pension specifically. Many MA towns participate in regional retirement systems (county-level), not town-specific funds.

---

## Field 9: debt_per_capita

**What it is:** Total outstanding bonded debt divided by population.

**Primary source:** TOWN_ACFR
**URL pattern:** `{town}.gov` → Finance → Annual Report or ACFR
**Retrieval steps:**
1. Open town's most recent ACFR (PDF)
2. Find "Long-Term Debt" or "Bonded Debt Outstanding" section
3. Take total general obligation bonded debt
4. Divide by population

**Expected range:** $500 – $10,000 per capita
**Common gotcha:** Don't include non-GO debt (revenue bonds, etc.). Don't include enterprise fund debt (water/sewer) unless they're general obligation. Stay consistent: GO debt only.

---

## Field 10: gfoa_certificate_consecutive_years

**What it is:** Number of consecutive years the town has earned GFOA Certificate of Achievement for Excellence in Financial Reporting.

**Primary source:** GFOA_CERT
**URL pattern:** `https://www.gfoa.org/award-programs` (search by town)
**Alternative:** Most ACFRs proudly note this on the cover or in the introductory section.

**Retrieval steps:**
1. Open most recent ACFR
2. Look at cover page and introductory letters for "GFOA Certificate of Achievement"
3. Note "X consecutive years" if stated

**Expected range:** 0 – 30+ years
**Common gotcha:** This is awarded retrospectively for the prior fiscal year. The town earning it for "16 consecutive years" in 2024 has FY23 as the 16th certified year.

---

## Field 11: tax_base_non_residential_pct

**What it is:** Percentage of the property tax base that is commercial + industrial (non-residential).

**Primary source:** TOWN_ACFR (Statistical Section, "Assessed Value by Property Class") or local assessor's annual report
**Retrieval steps:**
1. ACFR Statistical Section, usually in last third of document
2. Find table showing assessed value by class (residential / commercial / industrial / personal property)
3. Calculate: (commercial + industrial + personal property) / total × 100

**Expected range:** 5% – 40% (most residential suburbs are 10–25%)
**Common gotcha:** Don't confuse with "tax revenue split" — that varies due to split-rate jurisdictions. Use assessed value mix.

---

## Field 12: district_state_rank

**What it is:** State ranking of the school district by composite measure.

**Primary source:** State DOE district profiles (preferred) or SCHOOLDIGGER (Tier 3, widely cited)
**URL pattern:** `https://www.schooldigger.com/go/MA/district/{district_id}/search.aspx`
**Retrieval steps:**
1. Navigate to SchoolDigger
2. Search the district
3. Note "State Rank" — typically displayed as "#X of Y districts"

**Expected range:** 1 to total districts in state
**Common gotcha:** Districts are not towns. Two towns may share a regional district. Use the actual district that serves the town's K-12 students.

---

## Field 13: district_state_rank_total

**What it is:** Total number of school districts in the state, used for percentile calculation.

**Primary source:** Same as district_state_rank — SchoolDigger displays "X of Y"
**Expected:** ~350 for MA, varies significantly by state

---

## Field 14: district_rank_10yr_change

**What it is:** Change in state rank over 10 years. **Positive = declining (rank got worse)**, negative = improving.

**Primary source:** SCHOOLDIGGER historical rankings
**Retrieval steps:**
1. SchoolDigger district page → click "Historical Rankings"
2. Note rank in current year and rank ~10 years prior
3. Calculate: current_rank − rank_10yr_ago

**Expected range:** −100 to +100 typical
**Common gotcha:** Sign convention is critical. If district was rank 145 in 2014 and rank 196 in 2024, the change is +51 (got worse by 51 spots). Document this convention in compiler_notes.

---

## Field 15: test_scores_math_pct

**What it is:** Percentage of students proficient or above on state math test (most recent year).

**Primary source:** State DOE (e.g., MA_DESE)
**URL pattern (MA):** `https://profiles.doe.mass.edu/` → district profile → Assessment results
**Retrieval steps:**
1. Navigate to district profile
2. Find "MCAS Achievement Results" (MA) or equivalent
3. Take Math proficiency percentage (combined 3-8 + 10)

**Expected range:** 15% – 75% in MA
**Common gotcha:** Some sources report "meets or exceeds standard" vs "proficient or above" — these are different definitions. Use the methodology's documented metric (state proficiency standard, all grades combined).

---

## Field 16: graduation_rate_pct

**What it is:** Four-year cohort high school graduation rate.

**Primary source:** State DOE or NCES
**URL:** Same district profile page
**Expected range:** 70% – 99%
**Common gotcha:** Use 4-year rate, not 5-year extended rate.

---

## Field 17: ap_participation_pct

**What it is:** Percentage of high school students taking at least one AP exam.

**Primary source:** USNEWS_HS or College Board state reports
**URL pattern:** `https://www.usnews.com/education/best-high-schools/{state}/districts/{district}`
**Expected range:** 10% – 80%

---

## Field 18: per_pupil_spending

**What it is:** Annual per-pupil expenditure (high school or district average).

**Primary source:** NCES_CCD or state DOE
**Expected range:** $10,000 – $30,000 in most U.S. districts; higher in MA
**Common gotcha:** "Total spending" varies by what's included. Use the standard per-pupil expenditure metric.

---

## Field 19: response_311_days

**What it is:** Average response time (in days) for non-emergency town service requests.

**Primary source:** Town's 311 portal or open data dashboard
**Reality:** Most towns under 50,000 don't publish this. Often unavailable.
**If unavailable:** Leave blank; rubric uses default 60.
**Expected range:** 1 – 30 days

---

## Field 20: ems_response_minutes

**What it is:** Average emergency medical services response time in minutes.

**Primary source:** Town annual report or fire/EMS department report
**Reality:** Some towns publish in their annual report; many don't.
**If unavailable:** Leave blank; rubric uses default 70.
**Expected range:** 4 – 12 minutes

---

## Field 21: permits_per_1000

**What it is:** Building permits issued per 1,000 residents per year (operational measure of permit throughput).

**Primary source:** CENSUS_BPS
**URL pattern:** `https://www.census.gov/construction/bps/`
**Reality:** Census BPS data is jurisdiction-level. Some smaller towns aren't separately reported.
**Expected range:** 1 – 20 permits per 1,000 residents

---

## Field 22: iso_fire_rating

**What it is:** ISO Public Protection Classification (1 = best, 10 = no fire protection).

**Primary source:** ISO Mitigation (proprietary, not publicly listed) or town fire department
**Reality:** Most towns don't publish this externally. Often requires direct contact with fire department.
**If unavailable:** Leave blank; rubric uses default 65 (corresponds to roughly Class 5).
**Expected range:** 1 – 10 (most suburbs are 3–5)
**Format note:** Store as STRING ("1", "2", ... "10") not integer. Critical for rubric matching.

---

## Field 23: transparency

**What it is:** Whether the town publishes its annual budget AND ACFR online.

**Primary source:** TOWN_WEBSITE
**Retrieval steps:**
1. Visit town's official website
2. Check Finance/Treasurer/Town Clerk pages
3. Look for downloadable PDFs of: most recent ACFR, most recent annual budget
4. Both available = "yes"; one available = "partial"; neither = "no"

**Expected values:** "yes" / "partial" / "no" (lowercase)

---

## Field 24: electric_savings_vs_state_avg

**What it is:** Annual savings (or extra cost, if negative) vs state average electric rate, for a typical 10,380 kWh/year residential customer.

**Calculation:** `(state_avg_rate_cents - town_rate_cents) / 100 × 10380`

**Primary source:** EIA_F861 (state averages) and town utility website (town rate)
**For municipal utilities:** Town electric department posts current residential rates
**For investor-owned utilities:** Use state IOU average rate

**Expected range:** −$1,000 to +$2,500
**Common gotcha:** Some municipalities have municipal electric (often dramatic savings); most have investor-owned. Check town website to identify provider type.

---

## Field 25: water_violations_5yr

**What it is:** Number of EPA SDWIS violations in the past 5 years.

**Primary source:** EPA_SDWIS
**URL pattern:** `https://enviro.epa.gov/envirofacts/sdwis/search`
**Retrieval steps:**
1. Search for the town's water system
2. Filter to past 5 years
3. Count violations (any type)

**Expected range:** 0 – 10
**Common gotcha:** Some towns have multiple water systems (multiple PWSIDs). Sum across all systems serving the town.

---

## Field 26: broadband_coverage_pct

**What it is:** Percentage of households with access to ≥100/20 Mbps broadband.

**Primary source:** FCC_BROADBAND
**URL pattern:** `https://broadbandmap.fcc.gov/`
**Retrieval steps:**
1. Enter town address or boundaries
2. Note coverage at 100/20 Mbps tier
3. Convert to percentage if reported as fraction

**Expected range:** 60% – 100%

---

## Field 27: transit_access

**What it is:** Categorical assessment of transit access.

**Primary source:** TOWN_WEBSITE + state/regional transit authority
**Retrieval steps:**
1. Check if town has commuter rail station: search "{town} commuter rail" or relevant transit authority site
2. If yes → "commuter_rail_in_town"
3. If station within 5 miles → "commuter_rail_nearby"
4. If only buses → "bus_only"
5. If limited service → "limited"
6. If no transit → "none"

**Expected values:** Use categorical taxonomy above (lowercase)

---

## Field 28: walk_score

**What it is:** Walk Score from 0–100 (Walk Score by Redfin).

**Primary source:** WALK_SCORE
**URL pattern:** `https://www.walkscore.com/{state}/{town}`
**Reality:** Free version shows score; commercial API provides bulk access.
**Expected range:** 0 – 100 (most suburbs 20–50)

---

## Field 29: park_acres_per_1000

**What it is:** Park acreage per 1,000 residents.

**Primary source:** TOWN_WEBSITE (parks department) or TPL_PARKSCORE for major cities
**Calculation:** total park acreage / population × 1000
**Expected range:** 2 – 50 acres per 1,000

---

## Field 30: library_circ_per_capita

**What it is:** Annual library items circulated per resident.

**Primary source:** IMLS_PLS (Public Libraries Survey)
**URL pattern:** `https://www.imls.gov/research-evaluation/data-collection/public-libraries-survey`
**Calculation:** total annual circulation / service population
**Expected range:** 2 – 15

---

## Field 31: violent_crime_per_100k

**What it is:** Violent crimes (murder, rape, robbery, aggravated assault) per 100,000 residents.

**Primary source:** FBI_UCR
**URL pattern:** `https://cde.ucr.cjis.gov/`
**Retrieval steps:**
1. FBI Crime Data Explorer
2. Search the town's law enforcement agency
3. Most recent year published (2023 as of 2026)
4. Calculate per-100k if reported as raw counts

**Fallback:** AGG_NHSCOUT, CrimeGrade (verify upstream)

**Expected range:** 50 – 1,500 per 100k
**Common gotcha:** Some agencies have reporting gaps. Check completeness of submission. Use most recent fully-reported year.

---

## Field 32: property_crime_per_100k

**What it is:** Property crimes (burglary, larceny-theft, motor vehicle theft) per 100,000 residents.

**Primary source:** FBI_UCR (same source as violent crime)
**Expected range:** 500 – 4,000 per 100k

---

## Field 33: crime_5yr_pct_change

**What it is:** Percentage change in total crime rate over 5 years (negative = improving).

**Primary source:** FBI UCR historical data
**Calculation:** ((current_year - 5_years_ago) / 5_years_ago) × 100
**Expected range:** −50% to +50%
**Reality:** Often unavailable for smaller agencies. If unavailable, leave blank; rubric uses default 60.

---

## Field 34: income_10yr_change_pct

**What it is:** Percentage change in median household income over 10 years.

**Primary source:** CENSUS_ACS5 (current and historical)
**Retrieval steps:**
1. Current median income from ACS 2024 5-year
2. Historical from ACS 2014 5-year
3. Calculate percentage change

**Expected range:** 10% – 80%

---

## Field 35: population_10yr_change_pct

**What it is:** Percentage change in population over 10 years.

**Primary source:** CENSUS_ACS5
**Calculation:** ((current_pop - pop_10yr_ago) / pop_10yr_ago) × 100
**Expected range:** −10% to +30%

---

## Field 36: bachelors_degree_pct

**What it is:** Percentage of adults age 25+ with a bachelor's degree or higher.

**Primary source:** CENSUS_ACS5
**Census table:** "Educational Attainment"
**Expected range:** 15% – 70%

---

## Field 37: unemployment_pct

**What it is:** Most recent published unemployment rate.

**Primary source:** BLS_LAUS
**URL pattern:** `https://www.bls.gov/lau/`
**Reality:** BLS publishes county-level data; town-level may require state Labor department source
**Expected range:** 2% – 10%

---

## Field 38: permits_3yr_per_1000

**What it is:** Average annual building permits per 1,000 residents over the last 3 years.

**Primary source:** CENSUS_BPS
**Expected range:** 1 – 15

---

## Field 39: poverty_pct

**What it is:** Percentage of residents below the federal poverty line.

**Primary source:** CENSUS_ACS5
**Census table:** "Poverty Status in the Past 12 Months"
**Expected range:** 2% – 25%

---

## Field 40: flood_risk_pct

**What it is:** Percentage of properties at substantial flood risk per First Street modeling.

**Primary source:** FIRST_STREET
**URL pattern:** `https://firststreet.org/city/{town}-{state}/{fsid}/flood`
**Retrieval steps:**
1. Search First Street for the town
2. Note "% of properties at substantial risk"
3. Free preview pages typically show this

**Expected range:** 0% – 30%
**Common gotcha:** First Street uses property-level modeling; aggregated town % may differ from FEMA flood map percentages.

---

## Field 41: flood_2050_growth_pts

**What it is:** Projected percentage-point increase in flood risk by 2050.

**Calculation:** First Street 2050 projection − current value
**Expected range:** 0 – 10 percentage points

---

## Field 42: wildfire_risk

**What it is:** Categorical wildfire risk level.

**Primary source:** FIRST_STREET
**Expected values (lowercase):** "low" / "moderate" / "medium" / "high" / "very high" / "extreme"

---

## Field 43: heat_days_growth_2050

**What it is:** Projected increase in number of days above 90°F by 2050.

**Primary source:** FIRST_STREET
**Calculation:** Days above 90°F in 2050 model − historical baseline
**Expected range:** 5 – 50 days

---

## Field 44: air_quality_aqi

**What it is:** Annual average AQI (Air Quality Index).

**Primary source:** EPA_AIRNOW
**URL pattern:** `https://www.airnow.gov/`
**Expected range:** 20 – 100 (lower is better)

---

## Field 45: tree_canopy_pct

**What it is:** Percentage of land area covered by tree canopy.

**Primary source:** USDA_FOREST or municipal urban forestry assessment
**Expected range:** 10% – 60%
**Reality:** Often unavailable. Leave blank if so; default 60 fires.

---

## State Context Fields (Required Before Scoring)

Before scoring any town in a state not yet in `state_context.csv`, populate these state-level values:

| Metric | Source |
|---|---|
| violent_crime_per_100k (state avg) | FBI_UCR state aggregate |
| property_crime_per_100k (state avg) | FBI_UCR state aggregate |
| median_household_income (state) | CENSUS_ACS5 state level |
| poverty_rate_pct (state) | CENSUS_ACS5 state level |
| unemployment_rate_pct (state) | BLS_LAUS state level |
| debt_per_capita_median (state) | State municipal finance office |
| per_pupil_spending_median (state) | NCES_CCD or state DOE |
| electric_avg_rate_cents_kwh (state) | EIA_F861 state residential rate |

---

## Time Estimates

| Field Category | Time per town |
|---|---|
| Census ACS demographics (5 fields) | 15 min |
| Property tax basics (4 fields) | 30 min |
| Schools (5 fields) | 45 min |
| Crime (3 fields) | 30 min |
| Climate (4 fields) | 30 min |
| Operational/Infrastructure (8 fields) | 90 min |
| Fiscal Health (6 fields, requires ACFR PDF) | 90 min |
| Other (~5 fields) | 30 min |
| **Total per town** | **~6 hours** |

---

## Confidence Marking

After collection, set `data_confidence_overall`:

- **high** — All fields populated except documented gaps; <5 gaps total → safe to publish
- **medium** — 5–15 gaps OR significant Tier-3 reliance → internal use only
- **low** — >15 gaps OR significant estimates → not yet ready

Update `data_gaps_count` to count blank required fields.

---

## When You're Genuinely Stuck

For each field, the playbook above lists primary, fallback, and last-resort sources. If after working through all of them a value is genuinely unavailable:

1. Leave the field blank
2. Document in `compiler_notes`: "{Field}: not published — {what was tried}, {date}"
3. Increment `data_gaps_count`
4. Move on

Do NOT estimate. Do NOT interpolate. Do NOT cite a number you can't verify.

This is the citation discipline that makes Civica defensible. It is the entire foundation of the product.
