# Civica for Dummies
### The Complete Manual — How It Works, Why It Exists, and How to Run It

---

## Table of Contents

1. [What Is Civica?](#1-what-is-civica)
2. [The Problem Civica Solves](#2-the-problem-civica-solves)
3. [Who Uses Civica and Why](#3-who-uses-civica-and-why)
4. [How the Scoring Works](#4-how-the-scoring-works)
5. [The 7 Pillars — Deep Dive](#5-the-7-pillars--deep-dive)
6. [Special Scores: TER, Value Rating, and Momentum](#6-special-scores-ter-value-rating-and-momentum)
7. [Buyer Personas](#7-buyer-personas)
8. [How Civica Compares to the Competition](#8-how-civica-compares-to-the-competition)
9. [Data Sources](#9-data-sources)
10. [File Structure and Codebase](#10-file-structure-and-codebase)
11. [The Scoring Pipeline — How Data Becomes a Score](#11-the-scoring-pipeline--how-data-becomes-a-score)
12. [How to Add a New Town](#12-how-to-add-a-new-town)
13. [Deployment and Git Workflow](#13-deployment-and-git-workflow)
14. [Ads and Monetization](#14-ads-and-monetization)
15. [Frequently Asked Questions](#15-frequently-asked-questions)
16. [Citation Rules](#16-citation-rules)
17. [Data Collection Playbook](#17-data-collection-playbook)
18. [Approved Source Registry](#18-approved-source-registry)

---

## 1. What Is Civica?

Civica is a single-page web app that scores Massachusetts towns and cities on the things that actually matter when you're buying a home — fiscal health, schools, taxes, safety, and quality of life.

Every town gets a **Civica Score** from 0 to 100. Higher is better. You can browse all towns on a color-coded map, filter by what you care about (top schools, low crime, commuter rail access, etc.), and open any town's full profile to see every data point that went into its score.

**Live site:** bluepenguin1234.github.io/civica  
**Coverage:** 200 Massachusetts towns and cities (as of May 2026; count grows — `TOWNS.length` is authoritative)  
**Tech stack:** Single HTML file, vanilla JavaScript, Leaflet.js for maps, hosted on GitHub Pages (free)

---

## 2. The Problem Civica Solves

When you buy a home, you search Zillow for price and Redfin for comps. Maybe you Google the schools. But nobody tells you:

- Is this town fiscally solvent, or is it heading toward a tax crisis in 10 years?
- Are the schools actually getting better or slowly declining?
- Is the tax bill "high" because the town is well-run, or because it's mismanaged?
- Will my flood risk double by 2050?
- Does this town have municipal electric — and if so, how much does that save me per year?

Real estate agents don't know this. Zillow doesn't show it. Niche.com has it but buries it under ads and vague letter grades with no methodology. GreatSchools is static — it shows today's ranking but not whether the district is trending up or down.

**Civica's answer:** One composite score, 7 data pillars, 23 scoring submetrics, full source citations, and a 10-year trajectory view for schools and crime. Built for buyers who do their homework.

---

## 3. Who Uses Civica and Why

### Primary User: The Serious Homebuyer
Someone who is 3–12 months from buying, has a price range in mind, and is narrowing down towns. They've already done Zillow. They want to know which town is actually the better long-term bet — not just which house is prettier.

**What they do with Civica:**
- Open the map and scan colors to eliminate obvious low-scorers
- Filter by "Top Schools" or "Commuter Rail" to narrow the list
- Open 2–3 town profiles and compare them side by side
- Look at the Key Insight paragraph to understand the tradeoffs in plain English
- Check the TER (Tax Efficiency Ratio) to see which town gives more for the money

### Secondary User: The Real Estate Agent
An agent who wants to show clients data beyond the listing. Civica gives them a credible, cited source to point to when recommending a town.

### Tertiary User: The Town Researcher / Policy Wonk
Someone who just moved, is curious about their town's fiscal health, or is comparing commuter towns before choosing where to rent first.

---

## 4. How the Scoring Works

### The Big Picture

Every Civica Score is built in three layers:

```
Layer 1: Raw Data
  (bond rating, crime rate, school rank, etc.)
        ↓
Layer 2: Submetric Scores (0–100)
  (each raw data point converted to a 0–100 score)
        ↓
Layer 3: Pillar Scores (0–100)
  (weighted average of submetric scores within each pillar)
        ↓
Final Civica Score (0–100)
  (weighted average of the 7 pillar scores)
```

### Pillar Weights (v3)

| Pillar | Weight | Why |
|---|---|---|
| Schools | 25% | #1 stated homebuyer priority |
| Safety | 20% | #2 stated priority |
| Fiscal Health | 20% | Predicts future tax stability — Civica's biggest differentiator |
| Taxes | 15% | Direct out-of-pocket cost |
| Economic Vitality | 10% | Is the town growing? Property value implications |
| Quality of Life | 7% | Transit, utilities, water |
| Climate Risk | 3% | Long-term property value and insurance risk |

**Formula:**
```
Civica Score = (Schools × 0.25) + (Safety × 0.20) + (Fiscal × 0.20)
             + (Taxes × 0.15) + (Econ × 0.10) + (QoL × 0.07) + (Climate × 0.03)
```

### How Raw Data Becomes a 0–100 Score

There are two methods:

**1. Range-based scoring** (most metrics)  
Each metric has a table of bands. Your raw value falls into a band and gets that band's score.

Example — Effective Tax Rate:
| Tax Rate | Score |
|---|---|
| Under 0.6% | 100 |
| 0.6–0.9% | 92 |
| 0.9–1.1% | 80 |
| 1.1–1.3% | 70 |
| 1.3–1.5% | 55 |
| 1.5–1.8% | 40 |
| 1.8–2.2% | 25 |
| Over 2.2% | 10 |

**2. Lookup-based scoring** (categorical fields)  
Some fields are categories, not numbers. The lookup table maps each category to a score.

Example — Bond Rating:
| Rating | Score |
|---|---|
| AAA | 100 |
| AA+ | 92 |
| AA | 85 |
| AA- | 78 |
| A+ | 70 |
| Not rated | 50 (default) |

**Missing data:** If a field is missing, the scoring uses a pre-set default (usually 50 — neutral). Towns with more missing data get a lower `data_confidence` rating (high / medium / low).

### Absolute Scoring — Why Scores Don't Change When Towns Are Added

Civica uses **absolute scoring**, not percentile scoring. Every score is computed against fixed thresholds in `scoring_rubrics.csv`. An effective tax rate of 1.1% always scores 80. A graduation rate of 95% always scores 95. Adding 50 new towns doesn't move existing town scores at all.

**The exceptions — a few fields that compare to a fixed state baseline:**
- `violent_crime_ratio` — town crime rate ÷ MA state average
- `income_ratio` — town median income ÷ MA median income
- `debt_ratio` — town debt per capita ÷ MA average
- School district rank — already ranked among all 351 MA districts

These ratios are baked into the raw data, not the rubric — so they're fixed unless you re-pull state averages.

**What does change when you add towns:**
- The sort order and rankings in the directory
- The map pin distribution
- Which towns appear as top results in filtered views

**Why not percentile scoring?**

Percentile scores create three problems:
1. **Instability** — Needham scores 82 today, you add 50 Boston suburbs, Needham drops to 76. Nothing changed about Needham, only the dataset did. Confusing to users, erodes trust.
2. **Interpretability** — "73rd percentile" explains rank but not reality. "73 because taxes are high but schools are excellent" is actionable. Absolute scores let you explain *why*.
3. **Cross-state comparison breaks** — An 80th percentile MA town and an 80th percentile TX town mean completely different things. Absolute scores on a consistent 0–100 scale let you eventually compare across states.

**The right solution for state expansion:** When adding New Hampshire towns, create NH-calibrated rubric thresholds that reflect what's actually good or bad in that state (higher property taxes are normal there, different crime baselines, etc.). The 0–100 scale stays identical — only the band thresholds shift. The scoring engine already supports this: you'd add a `state` column to `scoring_rubrics.csv`.

### Score Color Bands

Every score is color-coded consistently across the map markers, profile score ring, directory cards, pillar bars, and compare table:

| Score | Color | Label |
|---|---|---|
| 80–100 | Green `#30d158` | Excellent |
| 70–79 | Yellow `#ffd60a` | Good |
| 60–69 | Orange `#ff9f0a` | Fair |
| Below 60 | Red `#ff3b30` | — |

In code: `scoreColor(s)` and `profBarColor(s)` both use these thresholds. Update both functions in `civica-v5.html` if the bands ever change.

### Map Score Filters

The map page has filter pills that narrow markers to specific score bands. The filter logic lives in two places — `filteredTowns()` (directory view) and `mapFilteredTowns()` (map markers) — and both must be kept in sync with the color bands above:

| Filter | Score range |
|---|---|
| 80+ Excellent | score ≥ 80 |
| 70–79 Good | score ≥ 70 and < 80 |
| 60–69 Fair | score ≥ 60 and < 70 |

Good and Fair are **range** filters (not cumulative) — selecting "Good" shows only 70–79 towns, not everything above 70.

---

## 5. The 7 Pillars — Deep Dive

### Pillar 1: Schools (25%)

| Submetric | Weight | What It Measures |
|---|---|---|
| School District State Rank | 35% | Where the district ranks out of 351 MA districts |
| MCAS Math Proficiency | 25% | % of students scoring Proficient or Advanced on state math test |
| Graduation Rate | 20% | % of students who graduate on time |
| 10-Year Rank Trend | 20% | Has the district improved or declined over 10 years? |

**Key insight:** The rank trajectory submetric is Civica's biggest competitive differentiator in schools. A district ranked #50 that was #120 ten years ago is a fundamentally different buy than one ranked #50 that was #20. No competitor tracks this.

**Data source:** MA DESE (Dept. of Elementary & Secondary Education) district profiles

---

### Pillar 2: Safety (20%)

| Submetric | Weight | What It Measures |
|---|---|---|
| Violent Crime Rate | 50% | Town's violent crimes per 100k vs. MA state average |
| Property Crime Rate | 35% | Town's property crimes per 100k vs. MA state average |
| Crime 5-Year Trend | 15% | Is crime going up or down? |

**Important:** Crime rates are expressed as a **ratio to the state average**, not raw numbers. A ratio of 0.5 means half the state average. A ratio of 2.0 means twice the state average. This lets the scoring work across towns of very different sizes.

**MA state averages (2023):**
- Violent crime: 314.7 per 100k
- Property crime: 1,112.1 per 100k

**Data source:** FBI UCR / MA EOPSS

---

### Pillar 3: Fiscal Health (20%)

| Submetric | Weight | What It Measures |
|---|---|---|
| Bond Rating | 30% | S&P credit rating — the financial world's opinion of the town |
| Free Cash Reserve | 25% | % of budget held as unrestricted cash (fiscal cushion) |
| Pension Funded Ratio | 25% | How funded is the town's pension obligation? |
| Debt Per Capita | 20% | Town's per-person debt vs. state median |

**Why this pillar matters so much:** A town with poor fiscal health will eventually raise taxes, cut services, or both. Bond ratings and pension funding are leading indicators of future tax pressure — things you won't see on a listing but will feel in 10 years.

**Pension note:** Most Essex County towns are covered by the Essex Regional Retirement System (53.8% funded as of latest PERAC data). Cities like Lynn, Haverhill, and Lawrence have their own systems with varying funded ratios.

**Data sources:** EMMA/MSRB (bond ratings), MA DOR DLS (free cash), MA PERAC (pension)

---

### Pillar 4: Taxes (15%)

| Submetric | Weight | What It Measures |
|---|---|---|
| Effective Tax Rate | 45% | Annual tax bill ÷ assessed home value (as %) |
| Tax Burden as % of Income | 35% | Annual tax bill ÷ median household income (as %) |
| Housing Affordability Ratio | 20% | Median home value ÷ median household income |

**Why two different tax metrics?** A $10,000 tax bill means something very different in a $200k income household vs. a $60k income household. Tax burden as % of income captures real affordability. The effective tax rate captures the raw rate.

**Housing Affordability Ratio:** Calculated as `median home value ÷ median household income`. A ratio of 5× means the typical home costs 5 years of the typical household's gross income. National guideline: under 3× is affordable, over 6× is stretched.

**Data source:** MA DOR DLS (residential tax rates), Census ACS 2023 (income), Zillow ZHVI (home values)

---

### Pillar 5: Economic Vitality (10%)

| Submetric | Weight | What It Measures |
|---|---|---|
| Median Income vs. State | 40% | Town's median income as a ratio to MA median ($103,960) |
| Median Income 10-Year Growth | 35% | How much has income grown over 10 years? |
| Population 10-Year Growth | 25% | Is the town gaining or losing residents? |

**Why this matters for homebuyers:** A growing, increasingly prosperous town has a strengthening tax base — which means less future pressure on your property taxes and stronger property value appreciation.

**Data source:** Census ACS 2023 and 2013 (for 10-year comparisons)

---

### Pillar 6: Quality of Life (7%)

| Submetric | Weight | What It Measures |
|---|---|---|
| Transit Access | 35% | Commuter rail in town / nearby / bus only / none |
| Electric Utility Savings | 35% | Annual savings vs. Eversource avg if on a Municipal Light Dept |
| Water Quality | 30% | EPA drinking water violations in the past 5 years |

**Municipal electric (MLD) towns:** Danvers, Ipswich, Georgetown, Middleton, Merrimac, Groveland, Rowley, Marblehead (MMLD), and Peabody (PMLP). These towns have their own electric utilities and historically charge significantly less than Eversource. The savings figure is calculated against the MA average electric rate (33.61¢/kWh as of 2024 EIA data).

**Transit categories:**
- `commuter_rail_in_town` — MBTA station within the town boundary
- `commuter_rail_nearby` — station within ~5 miles
- `bus_only` — MBTA bus service only
- `limited` — minimal transit
- `none` — no public transit

**Data sources:** MBTA, EPA SDWIS, EIA Form 861

---

### Pillar 7: Climate Risk (3%)

| Submetric | Weight | What It Measures |
|---|---|---|
| Flood Risk | 50% | % of town land area in FEMA flood zone today |
| Flood Risk Growth to 2050 | 30% | How much will flood risk expand by 2050? (percentage points) |
| Wildfire Risk | 20% | USFS/First Street wildfire risk classification |

**Why only 3%?** Climate risk is real but relatively uniform across Massachusetts coastal towns. The big spread in Civica scores comes from schools, fiscal health, and safety — not climate. Weighted too high, it would unfairly penalize coastal communities with excellent schools and fiscal health. Weighted at 3%, it still penalizes towns like Gloucester (20% flood zone) meaningfully without dominating the score.

**Data sources:** FEMA NFIP, First Street Foundation, USFS

---

## 6. Special Scores: TER, Value Rating, and Momentum

### Tax Efficiency Ratio (TER)

**What it answers:** "Am I getting a good deal for my tax dollar?"

```
TER = Civica Score ÷ (Town Residential Tax Rate ÷ MA Average Residential Rate)
```

A TER of 6.8 (like Needham) means you're getting 6.8 units of Civica quality per unit of relative tax cost. Higher is better.

**TER Ratings:**
| TER | Rating |
|---|---|
| 6.5+ | Exceptional |
| 5.5–6.4 | Strong |
| 4.0–5.4 | Average |
| 3.0–3.9 | Below Average |
| Under 3.0 | Poor |

**Example:** A town charging a low tax rate but with mediocre schools and poor fiscal health might have a lower TER than a town with a high tax rate but excellent schools and AAA bond rating. The TER cuts through sticker shock.

---

### Value Rating (Bang-for-Buck Tier)

**What it answers:** "Is this town expensive relative to what you get?"

```
Value Score = Civica Score ÷ (Town Median Home Price ÷ MA Median Home Price)
```

Uses Zillow ZHVI for home prices. MA median home price: $613,049.

**Rating bands:**
| Value Score | Rating |
|---|---|
| 60+ | Hidden Gem |
| 50–59 | Strong Value |
| 40–49 | Market Rate |
| 30–39 | Premium Town |
| Under 30 | Luxury Market |

**Example:** Wellesley scores 70 on Civica but costs nearly 3× the MA median. Value Score ≈ 24 → Luxury Market. A high-quality but affordable town might score 58 on Civica but cost 0.8× the median, giving a Value Score of 72 → Hidden Gem.

---

### Town Momentum Score (TMS)

**What it answers:** "Where is this town headed over the next 10 years?"

Shown as a badge on every town profile (e.g., "Rising Town ↑").

```
TMS = (School Trajectory × 0.30) + (Income Trend × 0.25)
    + (Home Appreciation × 0.20) + (Population Trend × 0.15)
    + (Crime Trajectory × 0.10)
```

All inputs are already-computed 0–100 pillar submetric scores.

**TMS Labels:**
| TMS | Label |
|---|---|
| 75–100 | Rising Town ↑ |
| 60–74 | Steady Growth |
| 45–59 | Hold Steady |
| 30–44 | Stagnating |
| 0–29 | Declining |

**Why this matters:** A town ranked #80 statewide but improving fast is a fundamentally different buy than a town ranked #30 but declining. The TMS is the only score of its kind among Civica's competitors.

---

## 7. Buyer Personas

Civica lets users select a **persona** that reweights the 7 pillars based on what matters most to them. The town list re-sorts by their personalized score.

| Persona | Schools | Safety | Fiscal | Taxes | Econ | QoL | Climate |
|---|---|---|---|---|---|---|---|
| Balanced Buyer (default) | 25% | 20% | 20% | 15% | 10% | 7% | 3% |
| Schools First | 40% | 20% | 15% | 12% | 8% | 3% | 2% |
| Tax Sensitive | 10% | 18% | 28% | 30% | 8% | 4% | 2% |
| Long-Term Investor | 20% | 15% | 20% | 10% | 25% | 5% | 5% |
| First-Time Buyer | 15% | 25% | 18% | 22% | 12% | 5% | 3% |

**No new data is needed** — it's just a recalculation using different weights on the same 7 pillar scores. Pure JavaScript, instant.

---

## 8. How Civica Compares to the Competition

| Feature | Civica | Zillow | GreatSchools | Niche | City-Data |
|---|---|---|---|---|---|
| Composite town score | ✅ | ❌ | ❌ | ✅ (letter grade) | ❌ |
| Fiscal health data | ✅ | ❌ | ❌ | ❌ | ❌ |
| School trajectory (trend) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Pension liability scored | ✅ | ❌ | ❌ | ❌ | ❌ |
| Tax efficiency ratio | ✅ | ❌ | ❌ | ❌ | ❌ |
| Municipal electric scored | ✅ | ❌ | ❌ | ❌ | ❌ |
| Town momentum score | ✅ | ❌ | ❌ | ❌ | ❌ |
| Buyer persona reweighting | ✅ | ❌ | ❌ | ❌ | ❌ |
| Scoring methodology public | ✅ | ❌ | Partial | ❌ | ❌ |
| Free | ✅ | ✅ | ✅ | ✅ | ✅ |

**Civica's moat:** No competitor combines fiscal health, school trajectory, and a personalized score in one place with a transparent, cited methodology.

---

## 9. Data Sources

| Data | Source | Update Frequency |
|---|---|---|
| School rank, test scores, graduation rate | MA DESE district profiles | Annual (fall) |
| Bond ratings | EMMA/MSRB | As rated/updated |
| Free cash % of budget | MA DOR DLS Gateway (`CFC_PerBudg.xlsx`) | Annual (after DLS certification) |
| Municipal debt per capita | MA DOR DLS (`municipaldebt2022.xlsx`) | Periodic |
| Pension funded ratio | MA PERAC annual report | Annual |
| Crime rates | FBI UCR / MA EOPSS | Annual |
| Census data (income, population, demographics) | Census ACS 5-year estimates | Annual (December) |
| Home values | Zillow ZHVI (Zillow Home Value Index) | Monthly |
| Flood risk | FEMA NFIP flood maps | Periodic |
| Flood 2050 projection | First Street Foundation | Periodic |
| Wildfire risk | USFS / First Street Foundation | Periodic |
| Electric savings | EIA Form 861 | Annual |
| Water quality violations | EPA SDWIS | As reported |
| Transit access | MBTA GTFS | As updated |

### Where Data Lives Locally

```
C:\Users\Brian\Desktop\Civica\data\
  towns.csv                    ← all towns (200+), all fields, master record
  master_weights.csv           ← pillar weights (7 rows)
  pillar_weights.csv           ← submetric weights (23 rows)
  scoring_rubrics.csv          ← range/lookup tables for all submetrics
  state_context.csv            ← MA state averages used in ratio calculations
  source_dictionary.csv        ← data source metadata

  bulk/
    census_acs_ma_towns.csv    ← Census ACS data for all 351 MA towns
    ma_schools_combined.csv    ← DESE school data for all 397 districts
    CFC_PerBudg.xlsx           ← MA DOR free cash data (all 351 municipalities)
    municipaldebt2022.xlsx     ← MA DOR municipal debt data
```

---

## 10. File Structure and Codebase

### The One File That Matters

```
C:\Users\Brian\Desktop\Civica\
  civica-v5.html          ← THE ACTIVE FILE. Everything lives here.

  archive/
    civica-v3.html        ← old, ignore
    civica-v4.html        ← old, ignore
    civica-landing.html   ← old, ignore
    civica-methodology.html ← old, ignore
```

**Rule:** Never overwrite v5. If a major rewrite is ever needed, create `civica-v6.html`.

### What's Inside civica-v5.html

The file is one large HTML file with three main sections:

**1. `<style>` block** — All CSS, minified, inline. Covers the full design system: nav, hero, map, directory, profiles, methodology page, responsive breakpoints.

**2. `const TOWNS = [...]`** — A JavaScript array of all town objects (200+ and growing). Each town is one long line with ~55 fields. This is the source of truth for what gets rendered. Example fields:

```javascript
{name:"Needham", score:72, ter:6.8, ter_r:"Exceptional", bond:"AAA",
 free_cash:7.02, pens:78, d_10yr:5, math:71, grad:97.9,
 p_schools:80, p_safety:74, p_taxes:62, p_fiscal:69,
 p_econ:88, p_qol:46, p_climate:79,
 value_score:38.5, value_rating:"Premium Town", ...}
```

**3. `<script>` block** — All application logic:
- `grade()` — converts raw data to 0–100 submetric scores
- `computeScore()` — weighted average of submetrics into pillar scores, then into Civica Score
- `computeTMS()` — calculates Town Momentum Score
- `renderMap()` — Leaflet.js map with color-coded score markers
- `renderGrid()` — directory list view with filtering and sorting
- `openProfile()` — renders full town profile
- `renderMethodology()` — the methodology page
- `setPersona()` — applies persona reweighting and re-sorts the grid

### Key JavaScript Functions

| Function | What It Does |
|---|---|
| `grade(metric, value, town)` | Returns a 0–100 score for a raw data value using the rubric tables |
| `computeScore(town)` | Returns all 7 pillar scores and the final Civica Score |
| `computeTMS(town)` | Returns the Town Momentum Score and label |
| `scoreColor(score)` | Returns a hex color: green (80+), yellow (70–79), orange (60–69), red (<60) |
| `renderGrid(towns, persona)` | Renders the directory list with current filters/sort |
| `openProfile(town)` | Renders the full profile page for a town |
| `setPersona(id)` | Switches active persona, re-renders grid |

### Scripts

```
C:\Users\Brian\Desktop\Civica\scripts\
  update_all.py    ← master scoring pipeline (run this when data changes)
```

---

## 11. The Scoring Pipeline — How Data Becomes a Score

When you update data and need to recompute all town scores, you run:

```
py scripts/update_all.py
```

Here's what it does, step by step:

**Phase 1 — Fill Data**
- Reads `towns.csv` (master record for all towns)
- Pulls Census ACS data from `bulk/census_acs_ma_towns.csv` → updates income, population, demographics
- Pulls DESE school data from `bulk/ma_schools_combined.csv` → updates test scores, grad rate
- Pulls free cash from `bulk/CFC_PerBudg.xlsx` → overrides existing values (authoritative)
- Pulls debt per capita from `bulk/municipaldebt2022.xlsx` → overrides existing values
- Applies hardcoded updates (bond ratings, pension ratios, crime corrections, etc.)
- Calculates derived fields: `housing_affordability_ratio` = ZHVI ÷ median income

**Phase 2 — Score All Towns**
- For each town, calls `score_town()` which:
  - Calculates all 23 submetric scores using **absolute rubric thresholds** from `scoring_rubrics.csv` (range and lookup rules only — no percentile comparisons)
  - Computes 7 pillar scores (weighted averages of submetrics)
  - Computes final Civica Score
  - Calculates TER and TER rating
  - Counts data gaps and sets confidence level
  - Calculates Value Score and Value Rating

**Phase 3 — Save**
- Writes updated scores back to `towns.csv`
- Opens `civica-v5.html`, finds the `TOWNS = [...]` array
- For each town object, patches in the new scores using regex
- Saves the HTML

**When to run the pipeline:**
- When you update any CSV in the `data/` or `data/bulk/` folders
- When you add a new town
- When you change weights in `master_weights.csv` or `pillar_weights.csv`
- When you change scoring bands in `scoring_rubrics.csv`
- After adding new hardcoded data updates in `update_all.py` itself

**Important:** Use `py` not `python3`. PowerShell does not have `python3` aliased.

---

## 12. How to Add a New Town

Use `add_town.py` — it handles the bulk of the work automatically.

### Step 1: Run add_town.py

```powershell
py scripts\add_town.py "TownName" ^
    --lat 42.XXXX --lng -71.XXXX ^
    --zip "0XXXX" --zhvi 500000 --county Essex ^
    --transit "none" --pension 54.54
```

This auto-fills from bulk files: Census ACS (income, pop, demographics), DESE schools (math%, grad%, AP%), free cash (Excel), debt/capita (Excel), and computed district rank. It also inserts the town into both `towns.csv` and `civica-v5.html`.

The script prints a list of fields still requiring manual web lookup.

### Step 2: Look up flagged fields

After `add_town.py` runs, collect the remaining fields:

| Field | Source |
|---|---|
| Bond rating | EMMA (emma.msrb.org) |
| Pension funded ratio | MA PERAC annual report |
| Tax rates (eff_rate, res_rate, med_tax) | MA DOR DLS Gateway |
| Crime stats (violent, property, 5yr trend) | city-data.com → cross-check FBI UCR |
| Flood risk (flood, flood50) | First Street Foundation (manual lookup — JS-rendered) |
| Wildfire risk | First Street Foundation — almost always `"low"` for MA |

**Wildfire values must be lowercase:** `"low"`, `"moderate"`, `"high"`, `"very high"`, `"extreme"`.

### Step 3: Patch the data

Create a patch script (copy `scripts/patch_batch2b.py` as a template) or add the fields directly to `towns.csv`. If the town shares a regional school district with a non-obvious name, add an entry to `DISTRICT_MAP` in `update_all.py`.

### Step 4: Run the pipeline

```
py scripts/update_all.py
```

Verify the new town appears in the output with a reasonable score (not stuck at 50 flat across all pillars — that usually means missing data).

### Step 5: Validate and deploy

```powershell
# Quick JS syntax check (catches missing commas that break the page)
node -e "const fs=require('fs');const h=fs.readFileSync('civica-v5.html','utf8');const s=h.slice(h.indexOf('const TOWNS = ['));eval(s.slice(0,s.indexOf('\n];')+3));console.log('OK:',TOWNS.length,'towns')"

git add civica-v5.html data/towns.csv
git commit -m "add: [Town Name]"
git checkout main && git merge dev && git push origin main
git checkout dev && git push origin dev
```

**Note:** The town count in the UI is dynamic — `class="js-town-count"` spans auto-populate from `TOWNS.length`. No manual count update needed.

---

## 13. Deployment and Git Workflow

### Live Site

The site is hosted on **GitHub Pages** — free, automatic, no server required. Every push to `main` triggers a deployment. The site typically updates within 2–3 minutes of a push.

**Live URL:** https://bluepenguin1234.github.io/civica  
**GitHub repo:** https://github.com/bluepenguin1234/civica

### Branch Structure

| Branch | Purpose |
|---|---|
| `main` | Production — what the live site serves |
| `dev` | Working branch — make all changes here |

### The Standard Workflow

Every change follows this sequence:

```bash
# 1. Make changes on dev (already on dev branch)
git add civica-v5.html
git commit -m "description of change"

# 2. Merge to main and push
git checkout main
git merge dev
git push origin main

# 3. Push dev too (keeps remote dev in sync)
git checkout dev
git push origin dev
```

**Rules:**
- Never force-push to main
- Never commit directly to main
- Never edit old version files (v1–v4)

### Local Preview

To preview the current local file without waiting for GitHub Pages:

```bash
py -m http.server 8765 --directory "C:\Users\Brian\Desktop\Civica"
```

Then open: `http://localhost:8765/civica-v5.html`

This is essential when making layout or JS changes — GitHub Pages can take 2–3 minutes to update, but the local server shows changes instantly on refresh.

---

## 14. Ads and Monetization

Civica has three ad unit types built into every town profile. Currently all are placeholder/demo data.

### Ad Unit 1: Featured Agent

A real estate agent card shown on every profile. Currently shows "Sarah Mitchell" as a placeholder.

**Object in JS:** `AD_AGENT`  
**Fields:** name, photo, phone, email, brokerage, tagline, specialty towns

### Ad Unit 2: Featured Listings

A small listings card showing 1–3 homes for sale in the town. Currently only Beverly has real listing data; all others use the default placeholder.

**Object in JS:** `AD_LISTINGS_MAP` (keyed by town name)

### Ad Unit 3: Vendor Strip

Four vendor slots across the bottom of each profile. Currently all placeholders.

**Array in JS:** `AD_VENDORS`  
**Slots:** Moving company, home inspection, mortgage, homeowners insurance

### Mortgage Calculator

An unsponsored, unsold mortgage calculator appears on every profile. Inputs: home price, down payment, interest rate. Outputs: monthly payment estimate. This is a UX feature, not an ad slot.

### Monetization Path

1. **Agent advertising** — sell the Featured Agent slot to buyer's agents by town/county
2. **Vendor sponsorship** — sell the 4 vendor strip slots to moving companies, inspectors, mortgage brokers, insurers
3. **Listings integration** — partner with an MLS or IDX feed to show live listings
4. **Premium tier** — export reports, saved comparisons, email alerts when a town's score changes

---

## 15. Frequently Asked Questions

**Q: Why is my town's score lower than I expected?**  
A: The most common reasons are: pension funding (many MA towns are significantly underfunded), high effective tax rate, or a school district that's declining in state rank. Open the town profile and look at which pillar scores are lowest — that tells you exactly why.

**Q: Why do so many towns score in the 40s–60s instead of 80s–90s?**  
A: Because the scoring is honest. Pension underfunding is a systemic problem across Massachusetts (and most of the US). Even well-run towns carry significant unfunded liability. A score of 70+ is genuinely excellent. Needham at 72 is the top of the current dataset.

**Q: Can I trust the data?**  
A: Every metric links to a cited source. The methodology page in the app lists every data source. The data is as current as the source allows — some fields (like municipal debt) use 2022 data because that's the latest MA DOR has published. Missing or stale data is flagged with the `data_confidence` field.

**Q: How often does the scoring change?**  
A: Scores can change when: (1) new source data is published (Census, DESE, FBI UCR are all annual), (2) pillar weights are updated, or (3) new metrics are added. The `last_updated` field on each town record shows the last time that town's data was refreshed.

**Q: Does the map work on mobile?**  
A: Yes. The map, directory, and all town profiles are mobile-responsive. Horizontal scrolling is disabled. The persona selector, filter chips, and sort dropdown all work on touch screens.

**Q: What does "Not rated" mean for bond rating?**  
A: Many smaller MA towns (especially rural ones) have never issued enough municipal debt to bother getting a bond rating. "Not rated" defaults to a score of 50 (neutral) — it doesn't penalize the town, but it also doesn't reward it.

**Q: Will a town's score change as Civica adds more towns and states?**  
A: No. Scores are absolute — built against fixed rubric thresholds, not relative to other towns in the dataset. Adding 50 new towns doesn't move any existing town's score. The only things that change with more towns are the sort order in the directory and which towns appear at the top of filtered views. When Civica expands to new states, each state will get its own rubric thresholds calibrated to that state's context (e.g., property tax norms in NH are different from MA). The 0–100 scale stays the same — only the band cutoffs shift per state.

**Q: What's the difference between TER and Value Rating?**  
A: TER measures quality vs. tax rate (annual cost to own). Value Rating measures quality vs. home price (purchase cost). A town can have a great TER (low taxes, high score) but a poor Value Rating (very expensive to buy in). Both matter depending on your situation.

**Q: How do I know if the live site is updated after a push?**  
A: Wait 2–3 minutes, then hard-refresh (Ctrl+Shift+R). If you need to verify instantly, use the local server on port 8765.

---

## 16. Citation Rules

> Single most important rule: **Never publish a number without a citation, even if you have to leave the cell blank.**

Civica is a public-trust data product. The brand value comes from being the only place where every town score traces back to a verifiable public source. Lose that, and you have a "trust me" website that competes with Niche.com on UX — a losing game.

- A town manager challenges your score → you show them the source
- A journalist asks how you computed something → you show them the source
- A researcher wants to validate your methodology → they can replicate it

Compromise the citation discipline once, and you've compromised the entire product.

### Source Tier Priority

Always prefer higher tiers. When sources disagree, higher tier wins; if same tier, more recent wins; if same recency, more specific wins. Never average disagreeing sources — pick one and document why.

| Tier | Sources |
|---|---|
| **1 — Government Primary** | US Census, BLS, FBI, EPA, FCC, EIA, NCES; MA DOE, DOR, pension oversight; town ACFRs; EMMA bond ratings |
| **2 — Authoritative Nonprofit** | First Street Foundation, Trust for Public Land, GFOA, Data USA |
| **3 — Commercial Aggregators** | SchoolDigger, Zillow ZHVI, City-Data, Ownwell, US News, TapWaterData |
| **4 — Press / News** | Last resort — always cross-reference with primary sources |

### Handling Data Gaps

When a field is genuinely unavailable:

1. **Leave the value column blank** — do not guess, do not interpolate
2. **Note it in `compiler_notes`**: `"flood_risk: not published — tried First Street 2026-05-14"`
3. **Increment `data_gaps_count`**

The rubric uses the documented default (typically 50–70). A blank cell with a tracked gap is far better than a guess.

### Confidence Thresholds for Publication

| Tier | Gaps | Use |
|---|---|---|
| **high** | ≤3 | Safe to publish externally |
| **medium** | 4–8 | Internal use only; not for press or public profile |
| **low** | >8 | Not yet ready for any external use |

**Only towns marked `high` confidence should be published externally.** Publishing a "medium" confidence score means defending estimates to a journalist or town manager — that conversation is unwinnable.

### Legal Defensibility

The product's legal defensibility rests on three pillars:
1. Every published number sourced from publicly available data
2. Methodology published openly (this document + the scoring CSVs)
3. Correction mechanism exists (town manager review, "report data issue" link)

Never publish numbers without verifiable sources, subjective characterizations presented as facts, or anything reasonably construable as defamation. When in doubt: downscope rather than overclaim.

### Rules for LLM-Assisted Contributors

These rules are absolute:

- **Never invent values to fill gaps** — leave blank, increment gap counter, document why
- **Never average sources** — pick the higher-tier source
- **Never publish a "medium" confidence town externally** — flag for human review
- **Always cite every value** in the appropriate `_src` column

If asked to do something that conflicts with these rules — like "just estimate it, it's probably close" — refuse and explain why.

---

## 17. Data Collection Playbook

> Field-by-field instructions for finding the raw input values that feed the Civica scoring system.

Work through fields pillar by pillar. For each field: try the primary source first, then fallback sources in order, validate against the expected range, document the citation, and if genuinely unavailable leave blank — do **not** estimate. Allow ~4 hours per town for a full collection pass.

**Do not collect any field not listed here.** Fields like broadband, walk score, parks, library circulation, 311 response, EMS response, permits, air quality, and tree canopy are no longer scored and must not be collected.

---

### PILLAR 1: FISCAL HEALTH

**Field: `bond` — S&P Bond Rating**

Primary: EMMA (MSRB) — search the town, find most recent GO bond issue, note S&P rating.  
Fallback: Town ACFR → "Long-Term Debt" notes.  
Values: AAA, AA+, AA, AA-, A+, A, A-, BBB+, BBB, or `null` if unrated.  
Gotcha: Use most recent rating, not highest historical.

---

**Field: `free_cash` — Free Cash % of Budget**

Primary: MA DOR DLS Gateway — annual free cash certifications.  
Fallback: Town ACFR → "Unassigned General Fund Balance" in MD&A section.  
Calculation: `(free_cash_dollars / GF_expenditures) × 100`  
Range: 0–25%. Gotcha: "Total fund balance" ≠ free cash. Use unassigned balance only, not restricted funds.

---

**Field: `pension` — Pension Funded Ratio %**

Primary: MA PERAC → Public Reports → most recent actuarial valuation → "Funded Ratio".  
Note: Most MA towns use a county-level retirement system. Identify the correct retirement board first.  
Range: 40–100%+. Under 70% = concerning; above 90% = excellent.  
Gotcha: Pension and OPEB are different — use pension specifically.

---

**Field: `debt_pc` — Debt Per Capita ($)**

Primary: Town ACFR → "Long-Term Debt" → total GO bonded debt ÷ population.  
Range: $500–$10,000 per capita.  
Gotcha: Use GO debt only. Do not include revenue bonds or enterprise fund debt unless general obligation.

---

**Field: `gfoa` — GFOA Certificate (consecutive years)**

Primary: Town ACFR cover page — usually states "X consecutive years".  
Fallback: `https://www.gfoa.org/award-programs`  
Range: 0–30+. Gotcha: Awarded retrospectively — record the stated number, do not add 1.

---

**Field: `transp` — Financial Transparency**

Primary: Town's official website → Finance / Treasurer / Town Clerk pages.  
Values: `"Yes"` (both ACFR and budget downloadable), `"Partial"` (one available), `"No"` (neither posted).  
Gotcha: Use exact casing — this drives the scoring lookup.

---

### PILLAR 2: SCHOOLS

**Field: `d_rank` — State District Rank**

Primary: SchoolDigger → search district name → record "State Rank (#X of Y districts)".  
Fallback: MA DESE district profiles.  
Gotcha: Districts ≠ towns. Two towns may share a regional district. Use the district serving the town's K–12 students.

**Field: `d_total`** — collect at the same time as `d_rank` (denominator shown on same SchoolDigger page). Expected value for MA: ~350.

---

**Field: `d_10yr` — 10-Year Rank Change**

Primary: SchoolDigger → "Historical Rankings" tab.  
Calculation: `current_rank − rank_10yr_ago`  
**Sign convention: positive = declining (rank got worse).** If rank was 145 in 2014 and 196 in 2024, record +51.  
Range: −100 to +100.

---

**Field: `math` — MCAS Math Proficiency %**

Primary: MA DESE → `profiles.doe.mass.edu` → district profile → Assessment → MCAS Math "Meeting or Exceeding" %, all grades, most recent year.  
Range: 15–75%.

---

**Field: `grad` — 4-Year Graduation Rate %**

Primary: MA DESE district profile → Graduation & Dropout.  
Range: 70–99%. Gotcha: Use 4-year rate only, not the 5-year extended rate.

---

**Field: `ap` — AP Participation Rate %**

Primary: US News Best High Schools or College Board state reports.  
Range: 10–80%.

---

**Field: `enrollment_trend` — Enrollment Trend (10yr)**

Primary: MA DESE → compare current enrollment vs. 10yr prior.  
Values: `"Growing"` (>5% increase) / `"Stable"` (within ±5%) / `"Declining"` (>5% decrease).

---

### PILLAR 3: TAXES

**Field: `eff_rate` — Effective Tax Rate %**

Calculation: `residential_rate_per_1000 / 10` (valid for MA towns where assessment ratio is 100%).  
Or: `(median_annual_tax_bill / median_home_value) × 100`  
Range: 0.5–2.5%.

---

**Field: `med_tax` — Median Annual Tax Bill ($)**

Primary: Census ACS5 → "Median Real Estate Taxes Paid".  
Fallback: Ownwell.com (verify — Ownwell sometimes has corrupted data for small towns; cross-check against `eff_rate × med_home_val`).  
Range: $1,000–$20,000. Validation: should ≈ `eff_rate × med_home_val`. Off by >50%? Re-check.

---

**Field: `med_inc` — Median Household Income ($)**

Primary: Census ACS5 → "Income" → "Median Household Income".  
Range: $30,000–$200,000+.  
Gotcha: Use median *household* income, not median *family* income (family is typically higher).

---

**Field: `res_rate` — Residential Rate (per $1,000 AV)**

Primary: MA DOR DLS Gateway → Tax Rates → most recent FY → residential rate column.  
Range: $5–$30. Gotcha: Some towns have split rates. Always use the residential rate, not the commercial rate.

---

**Field: `tax_non_res` — Non-Residential Tax Base %**

Primary: Town ACFR → Statistical Section → "Assessed Value by Property Class".  
Calculation: `(commercial + industrial + personal property) / total × 100`  
Range: 5–40%. Gotcha: Use assessed value mix, not tax revenue split.

---

**Field: `med_home_val` — Median Home Value ($)**

Primary: Census ACS5 → "Housing" → "Median Value (Dollars)".  
Range: $200,000–$2,000,000+.

---

### PILLAR 4: SAFETY

**Field: `violent` — Violent Crime per 100k**

Primary: FBI Crime Data Explorer → search the town's law enforcement agency → most recent year with full submission → calculate per-100k.  
Fallback: MA EOPSS crime statistics.  
Range: 50–1,500 per 100k.  
Gotcha: Check submission completeness. Some agencies have reporting gaps — use most recent fully-reported year.

---

**Field: `prop_crime` — Property Crime per 100k**

Primary: FBI Crime Data Explorer (same search as violent crime).  
Range: 500–4,000 per 100k.

---

**Field: `sex_off` — Registered Sex Offenders per 1,000 Residents**

Primary: MA Sex Offender Registry Board → search by town → count Level 2 + Level 3 registrants → divide by population × 1,000.  
Range: 0.1–5.0 per 1,000. Gotcha: Count only Level 2 + Level 3 (publicly listed). Level 1 is not public.

---

### PILLAR 5: ECONOMIC VITALITY

**Field: `inc10yr` — Income Growth (10yr) %**

Primary: Census ACS5 current + Census ACS5 ~10 years prior.  
Calculation: `((current_income − income_10yr_ago) / income_10yr_ago) × 100`  
Range: 10–80%.

---

**Field: `pop10yr` — Population Growth (10yr) %**

Primary: Census ACS5.  
Calculation: `((current_pop − pop_10yr_ago) / pop_10yr_ago) × 100`  
Range: −10 to +30%.

---

**Field: `unemp` — Unemployment Rate %**

Primary: BLS LAUS (Local Area Unemployment Statistics). For town-level: MA Executive Office of Labor and Workforce Development.  
Range: 2–10%.

---

**Field: `pov` — Poverty Rate %**

Primary: Census ACS5 → "Poverty Status in the Past 12 Months".  
Range: 2–25%.

---

**Field: `owner_occ` — Owner-Occupied Housing %**

Primary: Census ACS5 → "Housing Tenure". Range: 40–90%.

---

**Field: `vacancy` — Vacancy Rate %**

Primary: Census ACS5 → "Housing Occupancy". Range: 2–15%.

---

**Field: `med_age` — Median Age**

Primary: Census ACS5 → "Age and Sex". Range: 25–55 years.

---

### PILLAR 6: QUALITY OF LIFE

**Field: `elec_save` — Electric Savings vs State Avg ($/yr)**

Calculation: `(state_avg_rate_cents − town_rate_cents) / 100 × 10380` (typical 10,380 kWh/yr residential customer).  
Primary: EIA Form 861 (state averages) + town utility website if municipal electric.  
MA municipal electric towns (MLDs): Danvers, Ipswich, Georgetown, Middleton, Merrimac, Groveland, Rowley, Marblehead, Peabody.  
If investor-owned (Eversource): savings = $0.  
Range: −$500 to +$2,500.

---

**Field: `water_viol` — Water Quality Violations (5yr)**

Primary: EPA SDWIS → `enviro.epa.gov/envirofacts/sdwis/search` → search by town PWSID → filter to past 5 years → count violations.  
Range: 0–10. Gotcha: Some towns have multiple PWSIDs. Sum across all systems.

---

**Field: `transit` — Transit Access**

Primary: MBTA website + town website.  
Values: `"Commuter Rail (in town)"` / `"Commuter Rail (nearby)"` / `"Bus only"` / `"None"`.

---

### PILLAR 7: CLIMATE RISK

**Field: `flood` — Flood Risk — Current %**

Primary: First Street Foundation → search the town → record "% of properties at substantial risk".  
Range: 0–30%. Note: First Street uses property-level modeling; differs from FEMA flood map percentages.  
Gotcha: First Street pages are JavaScript-rendered — WebFetch tools cannot retrieve the data. Must be checked manually or via the First Street API.

---

**Field: `flood50` — Flood Risk Growth by 2050 (percentage points)**

Primary: First Street Foundation (same page as `flood`).  
Calculation: First Street 2050 projection − current value. Range: 0–10 pts.

---

**Field: `fire` — Wildfire Risk**

Primary: First Street Foundation.  
Values (lowercase): `"low"` / `"moderate"` / `"high"` / `"very high"` / `"extreme"`.  
Note: Virtually all inland and coastal MA towns score "Low".

---

### Identity Fields (Not Scored — Required for Display)

| Field | What it is | Source |
|---|---|---|
| `name` | Town name | Known |
| `county` | County name | Known |
| `state` | State abbreviation | `"MA"` |
| `zip` | Primary ZIP code | USPS |
| `pop` | Total population | Census ACS5 |

`ter` and `ter_r` are computed automatically — do not collect them.

---

### Field Count Summary

| Pillar | Fields |
|---|---|
| Fiscal Health | bond, free_cash, pension, debt_pc, gfoa, transp (6) |
| Schools | d_rank, d_total, d_10yr, math, grad, ap, enrollment_trend (7) |
| Taxes | eff_rate, med_tax, med_inc, res_rate, tax_non_res, med_home_val (6) |
| Safety | violent, prop_crime, sex_off (3) |
| Economic Vitality | inc10yr, pop10yr, unemp, pov, owner_occ, vacancy, med_age (7) |
| Infrastructure | elec_save, water_viol, transit (3) |
| Climate | flood, flood50, fire (3) |
| **Total** | **35 scored + d_total display = 36** |

---

### When You're Genuinely Stuck

If a value is truly unavailable after working through all sources:

1. Leave the field `null`
2. Document in `compiler_notes`: `"{field}: not published — {what was tried}, {date}"`
3. Increment `gaps`
4. Move on

**Do NOT estimate. Do NOT interpolate. Do NOT cite a number you cannot verify.**

---

---

## 18. Approved Source Registry

This is the canonical list of approved data sources for Civica. **Do not use a source not on this list without first adding it here.** If you're unsure whether a source is acceptable, check its tier below — Tier 1 is always safe, Tier 4 requires a note explaining why a primary source was unavailable.

The tiers match the priority rules in §16 Citation Rules: Tier 1 > Tier 2 > Tier 3 > Tier 4. When sources disagree, the higher tier wins.

---

### Tier 1 — Primary / Official Government Sources

These are authoritative. Use by default. No cross-checking required.

| Source ID | Name | Publisher | URL | What It Covers | Update Frequency |
|---|---|---|---|---|---|
| CENSUS_ACS5 | American Community Survey 5-Year Estimates | U.S. Census Bureau | https://data.census.gov | Population, income, demographics, housing, commute | Annual |
| CENSUS_BPS | Building Permits Survey | U.S. Census Bureau | https://www.census.gov/construction/bps/ | Building permits by jurisdiction | Monthly + annual |
| CENSUS_BFS | Business Formation Statistics | U.S. Census Bureau | https://www.census.gov/econ/bfs/ | Business application filings by geography | Quarterly |
| BLS_LAUS | Local Area Unemployment Statistics | U.S. Bureau of Labor Statistics | https://www.bls.gov/lau/ | Unemployment rates by city/town | Monthly |
| FBI_UCR | FBI Uniform Crime Reporting / NIBRS | U.S. FBI | https://cde.ucr.cjis.gov/ | Violent and property crime by agency | Annual (Sept prior year) |
| EPA_SDWIS | Safe Drinking Water Information System | U.S. EPA | https://enviro.epa.gov/envirofacts/sdwis/search | Water system violations and compliance | Quarterly |
| EPA_CCR | Consumer Confidence Reports | U.S. EPA / local utilities | https://www.epa.gov/ccr | Annual water quality report from each utility | Annual (by July 1) |
| EPA_AIRNOW | AirNow Air Quality Data | U.S. EPA | https://www.airnow.gov/ | AQI by location | Real-time + historical |
| EPA_RADON | Map of Radon Zones | U.S. EPA | https://www.epa.gov/radon/epa-map-radon-zones | Radon zone classification by county | Static (1993 base) |
| EPA_SUPERFUND | Superfund National Priorities List | U.S. EPA | https://www.epa.gov/superfund | Superfund sites and brownfields by location | Continuous |
| FCC_BROADBAND | National Broadband Map | U.S. FCC | https://broadbandmap.fcc.gov/ | Broadband availability by location | Biannual |
| EIA_F861 | Form EIA-861 | U.S. Energy Information Administration | https://www.eia.gov/electricity/data/eia861/ | Electric utility rates, customers, sales | Annual |
| NCES_CCD | Common Core of Data | U.S. Dept of Education | https://nces.ed.gov/ccd/ | Per-pupil spending, enrollment, graduation | Annual |
| MA_DESE | DESE District Profiles | Commonwealth of MA DESE | https://profiles.doe.mass.edu/ | MCAS scores, district profiles, accountability | Annual |
| MA_DOR_DLS | Division of Local Services | Commonwealth of MA DOR | https://dlsgateway.dor.state.ma.us/ | Tax rates, levy, free cash certifications | Annual |
| MA_PERAC | Public Employee Retirement Administration | Commonwealth of MA PERAC | https://www.mass.gov/orgs/public-employee-retirement-administration-commission | Pension funding ratios and valuations | Annual |
| EMMA | Electronic Municipal Market Access | MSRB | https://emma.msrb.org/ | Bond ratings, official statements, disclosures | Continuous |
| TOWN_ACFR | Town Annual Comprehensive Financial Report | Town finance/auditor | (town-specific URL) | Full audited financials | Annual |
| TOWN_BUDGET | Town Annual Budget | Town manager/select board | (town-specific URL) | Budget documents | Annual |
| TOWN_WEBSITE | Official town website | Town government | (town-specific URL) | Town form, contacts, services info | Continuous |
| TOWN_CLERK | Town Clerk election records | Town clerk | (town-specific URL) | Election turnout, voter registration | After each election |
| CDC_PLACES | PLACES Local Data for Better Health | U.S. CDC | https://www.cdc.gov/places/ | Health outcomes, prevention, social determinants | Annual |
| USDA_FOOD_ATLAS | Food Access Research Atlas | USDA Economic Research Service | https://www.ers.usda.gov/data-products/food-access-research-atlas/ | Food deserts and access by census tract | Periodic (~4–5 yrs) |
| DOE_AFDC | Alternative Fuels Data Center | U.S. DOE | https://afdc.energy.gov/ | EV charging stations and alt fuels | Continuous |
| USDA_FOREST | Forest Service Tree Canopy | U.S. Dept of Agriculture | https://data.fs.usda.gov/ | Tree canopy from satellite analysis | Periodic |
| IRS_SOI_MIGRATION | IRS Statistics of Income Migration Data | U.S. IRS | https://www.irs.gov/statistics/soi-tax-stats-migration-data | County-to-county migration from tax returns | Annual |
| IMLS_PLS | Public Libraries Survey | U.S. IMLS | https://www.imls.gov/research-evaluation/data-collection/public-libraries-survey | Library circulation, programs, visits | Annual |

---

### Tier 2 — Authoritative Non-Government Sources

High credibility but not official government data. Use when no Tier 1 equivalent exists. No additional cross-checking required, but note the source.

| Source ID | Name | Publisher | URL | What It Covers | Notes |
|---|---|---|---|---|---|
| FIRST_STREET | First Street Foundation Climate Risk | First Street Foundation (501c3) | https://firststreet.org/ | Property-level flood, fire, heat risk | Widely cited; JS-rendered — must look up manually |
| GFOA_CERT | GFOA Certificate of Achievement | Govt Finance Officers Association | https://www.gfoa.org/award-programs | Recognition for high-quality ACFRs | Annual award listing |
| TPL_PARKSCORE | ParkScore Index | Trust for Public Land (501c3) | https://www.tpl.org/parkscore | Park acreage, access, investment | Largest cities only |
| C2ER_COLI | Cost of Living Index | C2ER | https://www.c2er.org/ | Cost of living index (100 = US avg) | Commercial publication; widely cited |
| NU_LNI | Local News Initiative | Northwestern / Medill School | https://localnewsinitiative.northwestern.edu/ | Local news outlet inventory; news deserts | Academic |

---

### Tier 3 — Aggregators and Commercial Sources

Convenient but derived from primary sources. Always cross-check against a Tier 1 or Tier 2 source before publishing. Note both the aggregator and the underlying primary.

| Source ID | Name | Publisher | URL | What It Covers | Cross-Check With |
|---|---|---|---|---|---|
| ZILLOW_ZHVI | Zillow Home Value Index | Zillow | https://www.zillow.com/research/data/ | Smoothed home value index by geography | — (no direct substitute; document vintage) |
| WALK_SCORE | Walk Score | Redfin / Walk Score | https://www.walkscore.com/ | Walk/Transit/Bike scores by location | MBTA GTFS for transit |
| SCHOOLDIGGER | SchoolDigger.com | SchoolDigger | https://www.schooldigger.com/ | School rankings | MA_DESE preferred |
| USNEWS_HS | US News Best High Schools | US News & World Report | https://www.usnews.com/education/best-high-schools | National HS rankings | MA_DESE preferred |
| AGG_DATAUSA | Data USA | Deloitte / Datawheel | https://datausa.io/ | Aggregates Census + BLS | CENSUS_ACS5, BLS_LAUS |
| AGG_CITYDATA | City-Data.com | City-Data.com | https://www.city-data.com/ | Aggregates Census + crime | FBI_UCR, CENSUS_ACS5 |
| AGG_OWNWELL | Ownwell Property Tax | Ownwell | https://www.ownwell.com/ | Property tax rate aggregator | MA_DOR_DLS |
| AGG_NHSCOUT | NeighborhoodScout | Location, Inc. | https://www.neighborhoodscout.com/ | FBI UCR derivative crime data | FBI_UCR |
| AGG_TAPWATER | TapWaterData (EWG-derived) | TapWaterData | https://www.tapwaterdata.com/ | Water utility quality summaries | EPA_SDWIS |
| AGG_NICHE | Niche.com | Niche | https://www.niche.com/ | Place rankings | Do not use as primary; compare only |

---

### Tier 4 — Editorial / Press (Last Resort)

Use only when all higher tiers have been exhausted and the field would otherwise remain null. **Always document in `compiler_notes` that a primary source was unavailable and why.**

| Source ID | Name | Publisher | URL | Notes |
|---|---|---|---|---|
| PRESS_LOCAL | Local newspaper | Various | (specific publication) | Cite the specific article; always cross-reference |
| PRESS_PATCH | Patch.com Local News | Patch Media | https://patch.com/ | Hyperlocal news; verify with primary sources |

---

### Quick Rule: Is This Source Approved?

1. Check this list. If it's here, use it at its tier.
2. If it's not here and you want to use it, add it to this section first with tier, publisher, URL, and notes — then use it.
3. Never use a source you can't name. "I found it online" is not a citation.

*Last updated: May 2026*  
*Civica — Know Before You Buy*
