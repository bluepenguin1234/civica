# Civica

Civic intelligence for MA home buyers. Scores 200 cities and towns on fiscal health, schools, taxes, safety, and infrastructure.

**Live site:** https://bluepenguin1234.github.io/civica/civica-v5.html
**GitHub:** https://github.com/bluepenguin1234/civica

---

## Quick Reference

### Root Files
| File | What it is |
|---|---|
| `civica-v5.html` | The live website — all 200 towns, map, profiles, scoring |
| `civica-privacy.html` | Privacy policy page |
| `index.html` | Redirects to civica-v5.html |
| `civica_value_scores.xlsx` | Private Excel — Civica Score + Value Score for all 200 towns |
| `CLAUDE.md` | Instructions for Claude AI assistant |

---

### `data/` — All Data
| File | What it is |
|---|---|
| `towns.csv` | **Single source of truth** — all 200 towns, every data field |
| `master_weights.csv` | The 7 pillar weights (Schools 25%, Safety 20%, Fiscal 20%, Taxes 15%, Econ 10%, QoL 7%, Climate 3%) |
| `pillar_weights.csv` | Submetric weights within each pillar |
| `scoring_rubrics.csv` | Rules that convert raw values → 0–100 scores |
| `state_context.csv` | MA state averages used as scoring benchmarks |
| `source_dictionary.csv` | Where each data field comes from |

#### `data/bulk/` — Bulk Source Data
| File | What it is |
|---|---|
| `census_acs_ma_towns.csv` | Census ACS demographics for all 351 MA towns |
| `ma_schools_combined.csv` | DESE school data (MCAS, grad rate, AP) for all districts |
| `CFC_PerBudg.xlsx` | MA DLS certified free cash % for all 351 municipalities |
| `municipaldebt2022.xlsx` | MA DLS total outstanding debt for all municipalities |

---

### `scripts/` — Pipeline
| Script | When to run it |
|---|---|
| `update_all.py` | **Run this for everything** — pulls bulk data, recomputes all scores, updates towns.csv and civica-v5.html |
| `fetch_census.py` | Refresh Census ACS bulk data (run yearly) |
| `fetch_dese.py` | Refresh DESE school bulk data (run yearly) |
| `add_town.py` | Add a single town — auto-fills census, schools, fiscal data from bulk files |
| `gen_excel.py` | Regenerate `civica_value_scores.xlsx` after scores change |
| `verify.py` | Spot-check a single town's score breakdown |
| `backtest_2014.py` | 2014 backtest — tests if high scores predicted home value growth |

**Normal workflow to add a town:**
1. `py scripts/add_town.py "TownName" --lat X --lng X --zip XXXXX --zhvi N --county Name`
2. Look up flagged fields (bond rating, pension, crime, tax rates, flood risk) and patch them in
3. Run `update_all.py`
4. Run `gen_excel.py`
5. `git add data/towns.csv civica-v5.html && git commit && git push`

---

### `docs/` — Reference Documents
| File | What it is |
|---|---|
| `CIVICA_MARKETING_PLAN.md` | Full go-to-market strategy and 90-day plan |
| `CIVICA_WEBSITE_BRIEF.md` | Website design brief |
| `civica-methodology.html` | Methodology page (web version) |
| `Civica Ads.html` | Ad copy and marketing materials |
| `REMINDERS.md` | Pending tasks and reminders |

---

### `archive/` — Old Versions
Previous HTML versions kept for reference. Do not edit.

---

## Scoring at a Glance

| Pillar | Weight |
|---|---|
| Schools | 25% |
| Safety | 20% |
| Fiscal Health | 20% |
| Taxes | 15% |
| Economic Vitality | 10% |
| Quality of Life | 7% |
| Climate Risk | 3% |

**Value Score** = Civica Score ÷ (Town ZHVI / MA State ZHVI $613,049) — private, Excel only.
