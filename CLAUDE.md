# Civica — Director's Brief

This file is the standing context for every Claude Code session on this project. Read it before doing anything. It tells you what Civica is, what success looks like, what's done, what's next, and what the rules are. With this context you should be able to pick up the next priority and execute without re-briefing.

**Also read `CIVICA_FOR_DUMMIES.md` before touching any scoring, data pipeline, or field logic.** It is the canonical deep reference: every submetric's source, formula, and gotchas; the full add-town workflow; transit canonical values; and the glance writing guide. CLAUDE.md is the quick-start; CIVICA_FOR_DUMMIES.md is the bible.

---

## 0. DATA INTEGRITY — NON-NEGOTIABLE

**Every single data field in every town object must come from a real, documented source. No estimates. No guesses. No placeholders dressed up as real values.**

The correct workflow for adding any town is:
1. Run `py scripts\add_town.py "TownName" --lat X --lng X --zip X --zhvi X --county X` — auto-fills census, schools, free cash, debt, district rank, median tax bill (DLS bulk), and residential rate (MMA bulk) from bulk files
2. Web-source the remaining flagged fields (bond rating, crime, pension, effective tax rate, flood risk) — see Section 12 for sources; enter them in `towns.csv` or pass as flags
3. Run `py scripts\update_all.py` to compute scores and patch civica-v5.html
4. Never hand-edit computed fields in the TOWNS array

If a field value is genuinely unknown, set it to `null` — the scoring engine handles nulls gracefully. **`null` is honest; a made-up number is a lie.**

Towns with fabricated data must be removed from the site and re-added only after real data is sourced.

---

## 1. Mission

Civica is a free municipal intelligence tool for Massachusetts homebuyers. It scores towns and cities on the factors that actually determine quality of life and long-term value — fiscal health, schools, taxes, safety, economic vitality, infrastructure, and climate risk — and synthesizes them into a single comparable score. The product solves a real, expensive problem: buyers spend $500k–$1.5M on a home without understanding whether the underlying city or town is fiscally healthy, well-run, or on a trajectory worth betting on. Civica gives them the intelligence layer their agent doesn't have.

**What winning looks like:** Civica becomes the default pre-purchase research tool that every Massachusetts homebuyer touches before they close. Short-term: dominate Essex County search results. Medium-term: cover all 351 MA municipalities. Long-term: license the model nationally.

---

## 2. Product at a Glance

- **~200 towns live** across MA (Essex, Middlesex, Norfolk, Plymouth, Suffolk, Worcester, Bristol, Hampshire, Barnstable counties) — count is dynamic, see `TOWNS.length`
- **Hosted at:** bluepenguin1234.github.io/civica (GitHub Pages, auto-deploys on push to main)
- **Architecture:** Single HTML file — `civica-v5.html` (380 KB) contains all HTML, CSS, JavaScript, and data inline. No build pipeline.
- **6 views:** landing, map, town profile, methodology, compare, advertise
- **7 scoring pillars:** Schools (25%), Safety (20%), Fiscal Health (20%), Taxes (15%), Economic Vitality (10%), Infrastructure & Utilities (7%), Climate Risk (3%)
- **3 special indices:** TER (Tax Efficiency Ratio), Value Rating (bang-for-buck), TMS (Town Momentum Score)
- **Revenue model:** Featured Agent ads, Featured Listings, Vendor Strip — all currently placeholder, not yet monetized

---

## 3. Current State (May 2026)

Know what's real and what's placeholder before assuming anything is wired.

**REAL and working:**
- Scoring engine (7 pillars, 23 submetrics, absolute rubric-based scoring)
- ~200 town profiles with full data (count is dynamic; `TOWNS.length` is authoritative)
- Interactive Leaflet.js map with color-coded markers and filters
- Multi-town compare view
- Methodology page (complete and accurate)
- PDF export (html2canvas + jsPDF)
- Mortgage calculator on every profile
- Similar towns recommendations
- Buyer persona reweighting (5 personas)

**PLACEHOLDER / NOT WIRED:**
- Formspree email capture ("Notify Me" form) — placeholder endpoint, signups are NOT being saved
- Featured Agent ad unit — shows "Sarah Mitchell / Coldwell Banker" on all towns (not a real advertiser)
- Featured Listings — only Beverly has real listing data; all other towns show placeholder homes
- Vendor Strip — all 4 slots (moving, inspection, mortgage, insurance) are placeholder businesses
- GA4 — Google Analytics not integrated; zero visibility into traffic
- OG social preview image — `civica-og.png` referenced in meta tags but file does not exist; shared links show no image
- Google Search Console — not verified; can't see organic search keywords

---

## 4. Priority Queue

Work down this list in order. Pick the first unchecked item that isn't marked `[Brian]` and execute it. Items marked `[Brian]` require account access Claude doesn't have — flag them to Brian and move to the next executable item.

```
[ ] [Brian] Formspree — create account at formspree.io, get form ID, give it to Claude
[ ] Wire Formspree form ID into civica-v5.html (one-line edit to the action= attribute on the Notify Me form)
[ ] [Brian] GA4 — go to analytics.google.com, create property for bluepenguin1234.github.io/civica, get Measurement ID (G-XXXXXXXX)
[ ] Wire GA4 Measurement ID into civica-v5.html <head> (two-snippet insert after Brian provides ID)
[ ] [Brian] Create civica-og.png — 1200×630 PNG, Civica logo + tagline on clean background — drop in C:\Users\Brian\Desktop\Civica\
[ ] Push civica-og.png with next commit (after Brian creates it)
[ ] [Brian] Google Search Console — go to search.google.com/search-console, add property bluepenguin1234.github.io/civica, choose HTML tag verification, give tag to Claude
[ ] Wire Search Console verification meta tag into civica-v5.html <head>
[ ] Ad structure review — audit all 3 ad units across all towns; fix any render issues or unprofessional placeholder content
[ ] Cloudflare setup — document exact DNS steps for Brian (free tier: HSTS, real CSP headers, WAF, DDoS protection)
[ ] Blog post — write and publish "The 5 Essex County Towns with Strongest Fiscal Health in 2026" as a static HTML page in /blog/
[ ] Compare feature UX — add "share this comparison" link that encodes selected towns in the URL (so comparisons are linkable)
[ ] SEO — add per-town og:description meta tags to each profile (currently set globally; needs per-town override with town name + score + key stat)
```

---

## 5. What Only Brian Can Do

These tasks require Brian's accounts and logins. Claude cannot do them. Prompt Brian when they're blocking.

- Create Formspree account and form → get form ID
- Create GA4 property → get Measurement ID
- Create civica-og.png image file
- Add site to Google Search Console and verify domain
- Point DNS to Cloudflare (requires domain registrar access)

---

## 6. File Rules

**The one active file:**
- `C:\Users\Brian\Desktop\Civica\civica-v5.html` — edit only this file for all site changes

**Version history — never touch these:**
- `civica.html` = v1, locked forever
- `civica-v2.html` through `civica-v4.html` = old versions, in archive/, ignore
- If a major structural change requires a new version: create `civica-v6.html`, never overwrite v5

**Data file:**
- `C:\Users\Brian\Desktop\Civica\data\towns.csv` — master data for all towns (~55 fields per town; count is dynamic)
- After any data change, run `py scripts\update_all.py` to regenerate scores and patch the TOWNS array

**Edit tool limitation:**
The Edit tool sometimes fails with "file modified since read" on the large civica-v5.html. For TOWNS array changes, use a Python read+write script instead (atomic replacement). `py script.py` works; `python3` does not.

---

## 7. Architecture

**Data pipeline:**
```
towns.csv → scripts/update_all.py → patches TOWNS array in civica-v5.html → commit → push to main → live in ~2 min
```

**towns.csv → TOWNS array field map** — every towns.csv column that feeds a TOWNS field must have a corresponding `patch_any` / `patch_str` call in `update_all.py`. If you add a new field to towns.csv and it needs to appear in the TOWNS array, add a patch call. `update_all.py` runs a sync check at the end and will warn if any tracked field is out of sync.

| towns.csv column | TOWNS field | towns.csv column | TOWNS field |
|---|---|---|---|
| `bond_rating_sp` | `bond` | `violent_crime_per_100k` | `violent` |
| `free_cash_pct_of_budget` | `free_cash` | `property_crime_per_100k` | `prop_crime` |
| `pension_funded_ratio_pct` | `pension` | `crime_5yr_pct_change` | `crime5yr` |
| `debt_per_capita` | `debt_pc` | `income_10yr_change_pct` | `inc10yr` |
| `effective_tax_rate_pct` | `eff_rate` | `population_10yr_change_pct` | `pop10yr` |
| `median_annual_tax_bill` | `med_tax` | `flood_risk_pct` | `flood` |
| `median_household_income` | `med_inc` | `flood_2050_growth_pts` | `flood50` |
| `residential_rate_per_1000` | `res_rate` | `wildfire_risk` | `fire` |
| `test_scores_math_pct` | `math` | `transit_access` | `transit` |
| `graduation_rate_pct` | `grad` | `electric_savings_vs_state_avg` | `elec_save` |
| `district_rank_10yr_change` | `d_10yr` | `water_violations_5yr` | `water_viol` |

**To add a new town — use `add_town.py`:**

```powershell
py scripts\add_town.py "TownName" `
    --lat 42.XXXX --lng -71.XXXX `
    --zip "0XXXX" --zhvi 500000 --county Essex `
    --transit "none"
```

`add_town.py` auto-fills from bulk files: census (income, pop, education trends), schools (math%, grad%, AP%), free cash (Excel), debt/capita (Excel), **computed district rank** (derived from bulk composite — no manual lookup needed), **median tax bill** (`med_tax` from DLS community comparison file), **residential rate** (`res_rate` from MMA municipal directory), and **effective tax rate** (`eff_rate` = `res_rate / 10`, computed automatically). It prints a list of which fields still require manual web lookup, then inserts the town into both `towns.csv` and `civica-v5.html`.

**After running `add_town.py`:**
1. Look up the flagged manual fields (bond rating, pension, crime stats, flood risk)
2. Add them to `towns.csv` or pass them as flags to the script (see `--bond`, `--violent`, etc.)
3. Run `py scripts\update_all.py` to score and patch HTML
4. Validate: run the Node.js syntax check (Section 15, Rule 6)

**What still needs manual lookup** for each new town:
- Bond rating → EMMA (emma.msrb.org) or MA MFOB
- Pension funded ratio → MA PERAC annual report
- Crime stats → ma.beyond2020.com (browser download)
- Flood risk → RiskFactor.com or First Street Foundation
- Effective tax rate (`eff_rate`) → only needed if MMA bulk missing for the town (rare)

**Town count:** Fully dynamic — `class="js-town-count"` spans auto-populate from `TOWNS.length`. No manual update ever needed.

**WARNING:** Never add a town to the HTML without a matching row in `towns.csv` first. Bulk-file lookups are automatic; the manual fields above can be `null` initially and filled later.

**Supporting scripts:**
- `scripts/verify.py` — spot-check a town's score breakdown
- `scripts/gen_excel.py` — generate civica_value_scores.xlsx after score changes
- `scripts/fetch_census.py` / `fetch_dese.py` — refresh bulk data (annual)

---

## 8. Git Workflow

```
1. Work on dev branch
2. git add <files> && git commit -m "description"
3. git checkout main && git merge dev && git push origin main
4. git checkout dev && git push origin dev
```

- Live site: bluepenguin1234.github.io/civica
- Never force-push to main
- One logical change per commit (keeps diffs reviewable)

**Local preview:**
```
py -m http.server 8765 --directory "C:\Users\Brian\Desktop\Civica"
Open: http://localhost:8765/civica-v5.html
```

---

## 9. Scoring System

**7 pillars and weights:**
| Pillar | Weight | Key submetrics |
|---|---|---|
| Schools | 25% | District rank (35%), MCAS math % (25%), grad rate (20%), 10-yr rank trend (20%) |
| Safety | 20% | Violent crime /100k (50%), property crime /100k (35%), 5-yr crime trend (15%) |
| Fiscal Health | 20% | S&P bond rating (30%), free cash % of budget (25%), pension funded % (25%), debt per capita (20%) |
| Taxes | 15% | Effective tax rate (45%), tax burden % of income (35%), housing affordability ratio (20%) |
| Economic Vitality | 10% | Median income vs. MA (40%), 10-yr income growth (35%), 10-yr population growth (25%) |
| Infrastructure & Utilities | 7% | Transit access (35%), municipal electric savings $/yr (35%), water quality violations (30%) |
| Climate Risk | 3% | Current flood risk % (50%), 2050 flood projection (30%), wildfire rating (20%) |

**Scoring method:** Absolute rubric-based (fixed thresholds per metric). Adding new towns does not change existing town scores.

**Special indices:**
- **TER (Tax Efficiency Ratio)** = Civica Score ÷ (town tax rate ÷ MA average). Answers: "Am I getting value for my tax dollar?"
- **Value Rating** = Civica Score ÷ (median home price ÷ MA median). Answers: "Is this town expensive relative to what it offers?"
- **TMS (Town Momentum Score)** = weighted trajectory across schools, income, home appreciation, population, crime. Labels: Rising Town / Steady Growth / Hold Steady / Stagnating / Declining

Full methodology: `CIVICA_FOR_DUMMIES.md`

---

## 10. Ad Structure & Monetization

**3 ad units on every town profile:**
1. **Featured Agent** — `AD_AGENT` object in JS. Currently: Sarah Mitchell / Coldwell Banker (placeholder). Target: $800/month per market zone.
2. **Featured Listings** — `AD_LISTINGS_MAP` in JS. Currently: only Beverly has real data; all others use defaults. Target: $200–400/month per town.
3. **Vendor Strip** — `AD_VENDORS` array. 4 slots: moving company, home inspector, mortgage broker, insurance agent. All placeholder. Target: $1,200–$2,100/month total.

**Revenue targets (near-term):**
- 5 paying Featured Agents × $800/month = $4,000 MRR
- Vendor Strip filled = $1,200–$2,100 MRR
- 10 Featured Listing towns = $2,000–$4,000 MRR

**Medium-term:**
- Civica Pro for Agents: $49–99/month subscription for white-labeled reports (target: 50 agents)
- Sponsored research reports: $5,000–$15,000 per report (e.g., "2026 Essex County Fiscal Health Report" sponsored by a mortgage company)

**When building features:** Ask whether it helps convert ad clients or agent subscribers. The compare feature, for example, is a natural agent tool — agents use it with clients to justify recommendations.

---

## 11. Buyer Personas

Use these to make good UX and feature prioritization decisions.

1. **The Researcher** — 32–45, dual income, data-driven, first or second home. Uses Zillow, Redfin, Reddit (r/FirstTimeHomeBuyer, r/personalfinance). Needs comparable objective data across towns they're considering.

2. **The Mover** — Relocating from out of state or out of county. No local knowledge. High anxiety, high stakes. Needs a fast way to compare towns they've never heard of. Completely dependent on whatever tool they find first.

3. **The Advisor** (real estate agent) — Wants to be a trusted advisor, not just a door-opener. Lacks data to back up recommendations. Becomes a Civica champion if they use it as a client tool. The compare view is built for them.

4. **The Civic Wonk** — Town meeting regulars, local journalists, municipal finance nerds. Will share Civica organically if they find the data interesting. Source of earned media and local credibility.

---

## 12. Data Sources

**RULE: Every field must have a real source. If you cannot verify a value, use `null`. Never estimate, round, or infer. See Section 0.**

**Always check local bulk files before going to the web.** The six files in `data/bulk/` cover the majority of fields for every MA town. Only use web sources for the fields that aren't in the bulk files.

### Already downloaded — use these first

| File | Fields covered |
|---|---|
| `data/bulk/census_acs_ma_towns.csv` | `pop`, `med_inc`, `inc10yr`, `pop10yr`, `bach`, `unemp`, `pov`, `owner_occ`, `vacancy`, `med_age`, `commute` |
| `data/bulk/ma_schools_combined.csv` | `math`, `grad`, `ap` (via district name — check `DISTRICT_MAP` in update_all.py) |
| `data/bulk/CFC_PerBudg.xlsx` | `free_cash` |
| `data/bulk/municipaldebt2022.xlsx` | `debt_pc` |
| `data/bulk/dls-community-comparison-fy2025.xlsx.xlsx` | `med_tax` (FY 2025 single-family tax bill) |
| `data/bulk/mma-municipal-directory-2026.csv.csv` | `res_rate` (residential tax rate per $1,000) |

### Web lookups — only for fields not in bulk files

| Data | Source | Refresh cadence |
|---|---|---|
| School district rank (`d_rank`) | **Auto-computed** by `update_all.py` from bulk schools data (composite: math 50%/grad 30%/AP 20%). No manual lookup needed. `d_10yr` (rank change) still requires SchoolDigger or DESE. | Annual (Aug–Sep) |
| Bond ratings (`bond`) | EMMA / MSRB (emma.msrb.org) | As published |
| Pension funded % (`pension`) | MA PERAC annual report | Annual |
| Crime rates (`violent`, `prop_crime`) | FBI UCR / MA EOPSS | Annual |
| Home values (`med_home_val`) | Zillow ZHVI preferred; Census ACS as fallback. **Not in towns.csv** — update the `ZHVI` dict in `update_all.py` directly. | As needed |
| Flood risk (`flood`, `flood50`) | First Street Foundation | Periodic |
| Wildfire rating (`fire`) | First Street Foundation | Periodic |
| Municipal electric savings (`elec_save`) | Confirmed MLDs only (see below) | Periodic |
| Sex offender density (`sex_off`) | MA Sex Offender Registry Board | Periodic |
| Effective tax rate (`eff_rate`) | **Auto-computed** as `res_rate / 10` by `add_town.py`. Manual lookup (MA DLS / town assessor) only if MMA bulk file missing for the town. | Annual |
| GFOA years (`gfoa`) | GFOA website | Annual |

Field-level source metadata: `data/source_dictionary.csv`

---

## 13. Constraints — Never Change

These are locked. Do not modify without an explicit override from Brian.

- **Logo:** 30×30 blue SVG icon + logotype `civi` (dark) + `ca` (blue #0071e3). Every page. Never change.
- **Versioning:** civica.html (v1) through civica-v5.html are frozen. Next version = civica-v6.html. Never overwrite.
- **Git:** Never force-push to main.
- **CSP meta tag:** Must stay in the `<head>`. It's imperfect (uses `unsafe-inline`) but it's the only security layer until Cloudflare is set up. Do not remove it.
- **Contact email in UI:** hello@civica.com
- **GitHub repo:** bluepenguin1234/civica

---

## 16. Town Data Fields — Complete Spec

Every town in the TOWNS array in `civica-v5.html` is one JavaScript object. These are all the fields, grouped by category. Fields marked **[auto]** are computed by `update_all.py` — do not set them manually. Fields marked **[required]** must have a real value; others can be `null` if genuinely unknown.

### Identity
| Field | Type | Notes |
|---|---|---|
| `name` | string | Official town/city name |
| `lat` / `lng` | float | Decimal degrees. Look up via Google Maps or Census geocoder |
| `state` | string | Always `"MA"` |
| `county` | string | e.g., `"Essex"`, `"Middlesex"`, `"Norfolk"`, `"Plymouth"`, `"Worcester"`, `"Suffolk"` |
| `zip` | string | One or more ZIP codes, slash-separated: `"01923 / 01937"` |
| `pop` | integer | [required] Census ACS 2023 total population |

### Fiscal Health
| Field | Type | Notes |
|---|---|---|
| `bond` | string or null | S&P rating: `"AAA"`, `"AA+"`, `"AA"`, `"AA-"`, `"A+"`, `"A"`, `"A-"`, `"BBB+"`. Use `null` if unconfirmed — scores as 50. Verify via EMMA (emma.msrb.org). |
| `free_cash` | float | Free cash as % of operating budget. Source: MA DLS certified free cash. Healthy = 5–10%. |
| `pension` | float | Pension funded ratio %. Source: MA PERAC. Essex County towns on Essex Regional = 53.8%. |
| `debt_pc` | float | Net debt per capita $. Source: town ACFR or MA DLS. |
| `gfoa` | integer or null | Consecutive years with GFOA Certificate of Achievement. Source: GFOA website. |
| `tax_non_res` | float or null | Non-residential % of tax base. Source: MA DLS valuation report. High % = commercial subsidy for residents. |
| `transp` | string | Financial transparency: `"yes"` (posts ACFR online), `"partial"`, `"no"` — **must be lowercase**; scoring rubric matches on lowercase |

### Taxes
| Field | Type | Notes |
|---|---|---|
| `eff_rate` | float | [required] Effective residential tax rate (%). Source: MA DLS. |
| `med_tax` | integer or null | Median annual residential tax bill $. Source: MA DLS or Census ACS. |
| `res_rate` | float | Residential rate per $1,000 assessed value. Source: MA DLS. |

### Schools
| Field | Type | Notes |
|---|---|---|
| `d_rank` | integer | [required] DESE district rank out of ~396. Auto-computed from bulk schools file by `update_all.py`; no manual lookup needed. |
| `d_total` | integer | Total rankable MA school districts. **Always auto-set to current RANK_TOTAL by `update_all.py` — never hardcode.** Currently 396. Higher than 351 (municipalities) because regional districts count separately. |
| `d_10yr` | float or null | District rank change over 10 years. **Negative = improved** (rank number decreased = better position). **Positive = declined** (rank number increased = worse position). Source: SchoolDigger historical. |
| `math` | float | [required] MCAS math % proficient/advanced. Source: DESE. |
| `grad` | float | [required] Graduation rate %. Source: DESE. |
| `ap` | float | AP exam participation rate %. Source: DESE. |
| `enrollment_trend` | float or null | Leave `null` — not yet in scoring pipeline. |

### Safety
| Field | Type | Notes |
|---|---|---|
| `violent` | float or null | Violent crime per 100,000 residents. Source: FBI UCR / MA EOPSS. |
| `prop_crime` | float or null | Property crime per 100,000 residents. Source: FBI UCR / MA EOPSS. |
| `crime_5yr_pct_change` | float or null | 5-year % change in total crime index. Negative = crime fell; positive = crime rose. Leave `null` if unavailable — not heavily weighted. |
| `sex_off` | float | Sex offender density per 1,000 residents. Source: MA Sex Offender Registry Board. |

### Economic Vitality
| Field | Type | Notes |
|---|---|---|
| `med_inc` | float | [required] Median household income $. Source: Census ACS 2023. |
| `inc10yr` | float | 10-year income growth %. Source: Census ACS (compare 2013 vs 2023). |
| `pop10yr` | float | 10-year population growth %. Source: Census. |
| `bach` | float | Bachelor's degree attainment % (25+). Source: Census ACS. **Display only — not a scored submetric.** |
| `unemp` | float | Unemployment %. Source: Census ACS or MA DLT. **Display only — not a scored submetric.** |
| `pov` | float | Poverty rate %. Source: Census ACS. **Display only — not a scored submetric.** |

### Infrastructure & Utilities
| Field | Type | Notes |
|---|---|---|
| `transit` | string | Accepted values: `"Commuter Rail (in town)"`, `"Commuter Rail (nearby)"`, `"Bus only"`, `"None"` (or descriptive note like `"None (Beverly / Salem nearest)"`). |
| `elec_save` | integer | Annual $ savings vs MA average rate (33.61¢/kWh). Municipal light dept towns: Danvers (~$2,036), Ipswich, Georgetown, Middleton, Merrimac, Groveland, Rowley, Marblehead (~$1,931), Peabody (~$1,850). Non-MLD towns = `0`. Negative if MLD rate is worse than state avg. |
| `water_viol` | integer | Water quality violations in past 5 years. Source: EPA SDWIS. Most towns = 0. |
| `commute` | integer | Average commute time (minutes). Source: Census ACS. |

### Climate Risk
| Field | Type | Notes |
|---|---|---|
| `flood` | float or null | Current flood risk % of properties. Source: First Street Foundation. |
| `flood50` | float or null | Additional flood risk growth by 2050 (percentage points). Source: First Street Foundation. |
| `fire` | string | Wildfire risk: `"low"`, `"moderate"`, `"high"`, `"very high"`, `"extreme"`. **Must be lowercase** — the scoring rubric matches on lowercase. Source: First Street Foundation. Almost all MA towns = `"low"`. |

### Demographics & Housing
| Field | Type | Notes |
|---|---|---|
| `med_home_val` | integer | Median home value $. **Not in towns.csv** — lives in the `ZHVI` dict in `update_all.py`. To update a town's value, edit that dict and re-run the pipeline. Source: Zillow ZHVI preferred; Census ACS as fallback. |
| `owner_occ` | float | Owner-occupancy rate %. Source: Census ACS. |
| `vacancy` | float | Vacancy rate %. Source: Census ACS. |
| `med_age` | float | Median resident age. Source: Census ACS. |
| `low_income_pct` | float | % of students from low-income households. Source: DESE. |
| `ell_pct` | float | English Language Learner % of school enrollment. Source: DESE. |

### Computed by update_all.py — Do Not Set Manually
These are calculated from the raw fields above. Set them to `null` when first adding a town; `update_all.py` will fill them in.

`score`, `ter`, `ter_r`, `p_schools`, `p_safety`, `p_taxes`, `p_fiscal`, `p_econ`, `p_qol`, `p_climate`, `value_score`, `value_rating`

**WARNING — `p_qol` naming:** `p_qol` is the Infrastructure & Utilities pillar score. The internal key throughout `update_all.py` and `master_weights.csv` is `quality_of_life` (historical name). The display label was later changed to "Infrastructure & Utilities" but the code key was not renamed. **Do not rename `p_qol` to `p_infra` or change the key in any config file — it will break the scoring pipeline.**

### Editorial Fields
| Field | Type | Notes |
|---|---|---|
| `standout` | string | 1–2 sentences: the single most important thing to know about this town. Used in map side panel only — not shown on profiles. Lead with the concrete stat. **Auto-generated** by `update_all.py` if missing; refine manually for quality. |
| `glance` | string | 2–3 sentences: the honest buyer take. Shown in the "At a Glance" box on every profile. See Section 17 for the full writing guide. **Auto-generated** by `update_all.py` if missing; always refine manually — auto text is a starting point, not the final copy. |
| `notes` | string | Internal compiler notes: data confidence flags, verification reminders, source citations. Not shown to users. |
| `data_gaps_count` | integer | Count of missing/estimated fields. Honest self-assessment. |
| `data_confidence` | string | `"high"` (≤3 gaps), `"medium"` (4–8 gaps), `"low"` (>8 gaps). Computed by `update_all.py` — do not set manually. |
| `last_updated` | string | ISO date: `"2026-05-13"` |

---

## 17. At a Glance Writing Guide

The `glance` field is the 2–3 sentence "Honest Buyer Take" shown on every town profile. It's the most editorial part of Civica — it's what a smart local would tell you over coffee, not what a real estate brochure would say.

### The Pattern (from real profiles)

**Sentence 1 — Identity + defining characteristics**
Open with: `"[Town] is a [size/character descriptor] [town/city] [location anchor] with [2–3 concrete defining traits]."`
- Always include a location anchor (north of Boston, South Shore, etc.)
- Name 2–3 defining traits backed by actual data
- If commuter rail is in town, say so here — it's always relevant to buyers

**Sentence 2 — The honest caveat**
The thing that explains the score, limits the upside, or is the key tradeoff. Lead with "The key caveat:", "The main tradeoff:", or just state it directly.
- If schools are declining, say the rank and direction
- If flood risk is elevated, say it
- If the score is suppressed by data gaps, say so explicitly ("Score is suppressed by X data gaps — true fundamentals are likely stronger")
- If the tax bill is high, frame it: "The high median tax bill ($X) reflects premium property values and top-tier services"

**Sentence 3 (optional) — Transit note or differentiator**
Only include if transit is notable and wasn't covered in sentence 1, or if there's a third important dimension.

### Real Examples

**Andover (score 65) — Premium town, strong across the board:**
> "Andover is one of Essex County's most coveted communities — excellent schools, strong fiscal reserves, MBTA commuter rail, and very low crime. The high median tax bill ($10,542) reflects premium property values and top-tier municipal services."

**Burlington (score 62) — Fiscal standout, no rail:**
> "Burlington is one of Middlesex County's strongest fiscal stories. A massive commercial tax base funds solid schools and low-crime safety while keeping residential taxes unusually low. No MBTA station in town; nearest is Mishawum (Lowell line) in Woburn."

**Danvers (score 46) — Value story with school caveat:**
> "Danvers is an 18-mile-north-of-Boston town with a long fiscal track record, a municipal electric utility that shaves ~$2,000/year off the typical electric bill, and very low violent crime. The key caveat: the school district has slipped roughly 50 spots over the past decade and sits mid-table statewide."

**Newburyport (score 60) — Score suppressed by data gaps:**
> "Newburyport is one of the most desirable small cities on the North Shore — top schools, very low crime, commuter rail, and a celebrated downtown. Score is suppressed by data gaps — true fundamentals are likely stronger."

**Salem (score 40) — Urban, walkable, trade-offs explicit:**
> "Salem is the most urban and walkable town in the cohort — commuter rail, walkability, and a distinct cultural identity as a tourism destination. High crime rates and a high flood risk trajectory are the main trade-offs."

### Rules

1. **Use real numbers.** School rank X of 396, tax bill $X, crime X/100k, electric savings $X/yr. Never vague ("strong schools" → "schools ranked #75 of 396 statewide").
2. **One town, one voice.** Don't compare to other towns by name. Anchor to statewide ("top quartile"), not to peers.
3. **The caveat is mandatory.** Every glance must have one honest limitation or trade-off. No town gets a pure sell job.
4. **No marketing language.** Never: "great place to live," "vibrant community," "something for everyone," "hidden gem" (that's the Value Rating's job). State facts.
5. **No score in the glance.** The score is displayed separately. Don't repeat it.
6. **Transit is always worth noting.** Commuter rail in town = mention in sentence 1. Nearby = mention if transit-accessible buyers are a likely persona. No transit = mention if it's a notable limitation for the market.
7. **MLD electric savings ≥$500/yr = mention it.** It's one of Civica's most differentiated data points and buyers consistently undervalue it.
8. **Flood risk ≥15% or flood50 ≥5 = mention it.** Coastal towns especially.
9. **Length: 2 sentences is the target. 3 is the max. Never 1. Never 4.**

### What Bad Looks Like

- "Weston is a beautiful town with excellent schools and strong property values." → No numbers, pure marketing, no caveat.
- "A great community for families looking for top schools and low crime." → No town identity, no specificity, sounds like Niche.com copy.
- "Weston ranks #12 of 396 in schools, has an AA+ bond rating, a 92% graduation rate, a median tax bill of $18,400, low crime at 45/100k violent..." → Listing raw data instead of synthesizing it. That's what the data table is for.

---

## 15. How to Work on This Project (Agent Orchestration)

Whenever a task has independent sub-parts, deploy parallel agents rather than working sequentially. The goal is maximum throughput per session.

**Orchestration examples:**
- **"Audit all ad units"** → Spawn 3 agents in parallel: one audits Featured Agent rendering, one audits Featured Listings, one audits Vendor Strip. Synthesize results.
- **"Add 10 new towns"** → One agent researches raw data for all 10 towns. A second agent runs the scoring pipeline. A third verifies output against towns.csv. All overlap where possible.
- **"SEO pass"** → One agent writes per-town meta descriptions. A second audits `<head>` tags and schema markup. Both run in parallel.
- **"Blog post + push"** → One agent drafts the HTML. Another pre-checks git status. Merge outputs, then push.

**Rules:**
1. **Explore first, in parallel.** Before writing code on any unfamiliar task, spawn Explore agents to read relevant sections of civica-v5.html and towns.csv simultaneously.
2. **Never let sequential tasks block parallel ones.** If step A must precede step B, run step C (unrelated) in parallel with step A.
3. **Auditable outputs required.** After any modification to civica-v5.html, verify: (a) `TOWNS.length` is correct, (b) the modified town renders at localhost:8765, (c) `git diff` shows only the intended change.
4. **Data changes go through update_all.py.** Never hand-edit the TOWNS array for data changes — run the pipeline. Verify the script succeeded before committing.
5. **Commit scope = one logical change.** Parallel agents can work simultaneously but their outputs get committed separately.
6. **Always validate JS syntax before committing.** After any change that touches the TOWNS array, run `node _test_towns.js` (or extract the array inline) to catch syntax errors before they break the site. A single missing comma will prevent the entire page from loading. If the map or page isn't working after a change, run Node first — it will point directly to the broken line.

   Quick syntax check:
   ```powershell
   py -c "
   with open('civica-v5.html', encoding='utf-8') as f: c = f.read()
   s = c[c.index('const TOWNS = ['):c.index('\n];\ndocument.querySelectorAll')+3]
   open('_t.js','w').write(s+'\nconsole.log(TOWNS.length)')
   " && node _t.js && del _t.js
   ```
   If Node prints a line number and `SyntaxError`, that's the broken town. Fix the issue in civica-v5.html, re-run the check, then commit.
