# Civica Citation Standard Operating Procedure

> Single most important rule: **Never publish a number without a citation, even if you have to leave the cell blank.**

This document defines how every data point in the Civica system gets sourced, cited, and tracked. The product's defensibility depends entirely on this discipline.

---

## Why Citations Matter

Civica is a public-trust data product. The brand value comes from being the only place where every town score traces back to a verifiable public source. Lose that, and you have a "trust me" website that competes with Niche.com on UX — a losing game.

The citation discipline is what makes this defensible:

- A town manager challenges your score → you show them the source
- A journalist asks how you computed something → you show them the source
- A researcher wants to validate your methodology → they can replicate it

Compromise the citation discipline once, and you've compromised the entire product.

---

## The Citation Convention

For every data column in `towns.csv`, there are companion columns:

| Column | Contents |
|---|---|
| `<column>_src` | Source ID from `source_dictionary.csv` |
| `<column>_url` | Town-specific document URL (when applicable) |
| `<column>_retrieved` | Date in YYYY-MM-DD format |

**Example:**

```
median_household_income           = 125395
median_household_income_src       = CENSUS_ACS5
median_household_income_url       = https://data.census.gov/profile/Danvers...
median_household_income_retrieved = 2026-05-08
```

---

## Source Tier Priority

Sources are ranked by reliability tier. Always prefer higher tiers.

### Tier 1 — Government Primary
**Use these first.** U.S. Census, BLS, FBI, EPA, FCC, EIA, NCES, IRS, IMLS, USDA, DOE; state agencies (DOE, DOR, pension oversight); town ACFRs and budgets; EMMA bond ratings.

### Tier 2 — Authoritative Nonprofit / Academic
Use when Tier 1 not available. First Street, Trust for Public Land, Northwestern Local News Initiative, C2ER, GFOA, Data USA.

### Tier 3 — Commercial Aggregators
Use only when primary unavailable, and verify upstream. SchoolDigger, US News, Walk Score, Zillow ZHVI, City-Data, Ownwell, NeighborhoodScout, TapWaterData, Niche.

### Tier 4 — Press / News
Last resort, with article URL. Always cross-reference with primary sources where possible.

---

## Handling Data Gaps

When a field is genuinely unavailable for a specific town:

1. **Leave the value column blank** (do not guess, do not interpolate)
2. **Add a note in `compiler_notes`**: "ISO fire rating not published — contacted Danvers FD on YYYY-MM-DD"
3. **Increment `data_gaps_count`**
4. **Do not increment beyond confidence tier** until gap is resolved

The rubric will use the documented default (typically 50–70). This is correct behavior — it represents genuine uncertainty without artificially inflating or deflating the score.

A blank cell with a tracked gap is far better than a guess.

---

## Confidence Thresholds for Publication

Every town has a `data_confidence_overall` value:

| Tier | Gaps | Use |
|---|---|---|
| **high** | <5 | Safe to publish externally |
| **medium** | 5–15 | Internal use only; not for press or public profile |
| **low** | >15 | Not yet ready for any external use |
| **pending** | (default) | New town before data collection begins |

**Only towns marked `high` confidence should be published externally.**

This is not optional. Publishing a "medium" confidence score externally means defending estimates to a journalist or town manager. That conversation is unwinnable.

---

## When Sources Disagree

Inevitable. Standard resolution:

1. **Higher tier wins** — Tier 1 always beats Tier 3
2. **More recent wins** — newer source beats older
3. **More specific wins** — town source beats county source beats state aggregate
4. **Document the discrepancy** — note in `compiler_notes`: "Census ACS shows $X; Ownwell shows $Y; using Census."

Never average disagreeing sources. Pick one and document why.

---

## Adding a New Source

If a new source is needed, add it to `source_dictionary.csv` with:

| Field | Required |
|---|---|
| `source_id` | UPPERCASE_WITH_UNDERSCORES, descriptive |
| `tier` | 1, 2, 3, or 4 |
| `full_name` | Official organization + dataset name |
| `publisher` | Organization that maintains it |
| `base_url` | Public landing page |
| `api_url` | If programmatic access exists |
| `license` | Public domain / CC / commercial / etc. |
| `update_frequency` | How often the source updates |
| `vintage_used` | Which version Civica is pulling |
| `notes` | Anything quirky about using it |

Adding a source does NOT require methodology version bump. **Editing existing entries does.**

---

## Town Manager Review Workflow

Before publishing a town's profile externally:

1. Set `town_manager_review_status` to `pending`
2. Send the draft profile to the town manager via email
3. Wait 14 days for response
4. If no response → publish, mark status `no_response`
5. If response with corrections → verify corrections against primary sources, update if confirmed, then publish, mark status `reviewed`

This is best practice, not legally required, but dramatically reduces risk of disputes.

---

## Legal Considerations

The product's legal defensibility rests on three pillars:

1. **Every published number sourced from publicly available data**
2. **Methodology published openly** (`04-scoring-methodology.md` + CSVs)
3. **Correction mechanism exists** (town manager review, "report data issue" link)

### Never publish:
- Numbers without verifiable source
- Subjective characterizations of towns presented as facts
- Comparisons relying on inconsistent methodology between towns
- Anything reasonably construable as defamation

### When in doubt:
**Downscope rather than overclaim.** A town profile that says "data confidence: medium, see notes for gaps" is far stronger than one that quietly fills gaps with estimates.

---

## For LLM-Assisted Contributors

If you are an LLM working on this project (Claude Code, Claude Projects, or another assistant), these rules are absolute:

- **Never invent values to fill gaps** — leave blank, increment gap counter, document why
- **Never average sources** — pick the higher-tier source
- **Never publish a "medium" confidence town externally** — flag for human review
- **Always run `verify.py`** after any methodology-touching change
- **Always cite every value** in the appropriate `_src` column

If asked to do something that conflicts with these rules — like "just estimate it, it's probably close" — refuse and explain why. The citation discipline is the entire foundation of the product.
