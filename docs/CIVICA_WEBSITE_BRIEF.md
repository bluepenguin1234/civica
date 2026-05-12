# Civica Website Build — Claude Code Project Brief

> Paste this entire document into Claude Code as your project brief. It contains everything needed to produce a production-quality website on the first pass.

---

## Project Context

You are building the marketing and methodology website for **Civica** — a municipal performance and tax-efficiency scoring system. Civica produces 0–100 scores for U.S. municipalities based on 8 pillars and 42 sub-metrics, with a signature Tax Efficiency Ratio (TER) metric.

The product strategy, methodology, and current data live in this repo's other files. **Read these before designing anything:**

- `04-scoring-methodology.md` — The scoring system
- `05-citation-sop.md` — The citation discipline that defines the brand
- `MASTER_TEMPLATE.md` — The product overview
- `towns.csv` — Current scored towns (Danvers, Beverly)
- `source_dictionary.csv` — The 43 cited sources

---

## What This Site Must Accomplish

Civica's defensibility is *transparency and methodology*. The site exists to do three things, in priority order:

1. **Establish methodological credibility** — visitors must believe Civica is the most rigorous source for municipal fiscal data. This is non-negotiable.
2. **Drive B2B inquiry** — insurance, mortgage, proptech, and relocation companies should be able to understand the API offering and request a demo within 30 seconds.
3. **Capture consumer interest** — homebuyers should be able to look up their target town, see its score with full citation, and join a waitlist for deeper features.

The site is **not** a real estate portal, **not** a Niche.com competitor, and **not** a general "best places to live" ranker. Don't design it like one.

---

## Design References — Read Carefully

### What to model after

These are the actual references for tone and execution:

- **stripe.com** — for editorial clarity around technical content; how to take complex rigor seriously without being dry
- **linear.app** — for minimal layouts with confident typography and restrained motion
- **fred.stlouisfed.org** — for data presentation that feels institutional and trustworthy
- **mercury.com** — for B2B financial product credibility paired with approachable copy
- **the-pudding.com** — for narrative-driven data journalism; how to make data feel like a story

### What NOT to copy

The user mentioned "Apple-like" and "Zillow-like" — these are intentionally **NOT** the references. Here's why:

- **Apple.com** is built to sell one premium consumer product through sequential storytelling. Civica is a data product evaluating thousands of towns. Apple's design language can't carry that information density.
- **Zillow.com** is built around map search of properties. Civica scores municipalities, not properties, and is methodology-first. A Zillow clone misrepresents what Civica is.

If the user pushes back on this, explain why and offer a hybrid: editorial clarity (Stripe/Linear) for the marketing pages, and dense-but-clean data layouts (FRED, Bloomberg Terminal sensibility) for the town profile pages.

---

## Anti-Patterns to Refuse

These are the visual tells that mark "AI-designed website" — actively avoid all of them:

1. **No gradient blobs** in hero sections. They're a 2022 trend, overused, and signal generic AI output.
2. **No glassmorphism** beyond one subtle use. Overuse is dated.
3. **No floating particles, animated backgrounds, or parallax for its own sake.**
4. **No purple-to-pink gradients.** Civica's brand needs to feel institutional, not crypto.
5. **No fake testimonials.** The product hasn't launched. Don't fabricate them.
6. **No fake metrics ("10,000+ users").** The user count is currently 0. Use waitlist/coverage metrics instead.
7. **No stock photos of generic suburban houses or smiling families.** They look like every real estate site.
8. **No "AI-powered" or "revolutionary" copy.** Civica's value is the opposite — boring rigor, not AI hype.
9. **No marquee scrolling logos** unless those companies have actually agreed to use Civica.
10. **No three-column "Features" section with icons.** Overdone. Replace with substantive content.
11. **No emoji icons inside the content** beyond the trajectory indicators (↑↑ ↑ → ↓ ↓↓), which are part of the methodology.
12. **No dark mode toggle** unless trivial — it doubles the design surface area for marginal benefit on a marketing site.
13. **No carousel sliders.** They hide content; engagement metrics show people don't interact with them.
14. **No "Get Started Free" CTAs on a product that's not yet live.** Use "Join Waitlist" honestly.

When tempted to add visual flourish, ask: *does this make the methodology look more credible, or less?* If less, cut it.

---

## Tech Stack

Use this exact stack unless there's a specific blocking reason:

- **Framework:** Next.js 14+ with App Router
- **Styling:** Tailwind CSS, no component library
- **Fonts:** Inter (UI), Source Serif 4 (long-form prose, methodology content)
- **Hosting:** Vercel (free tier sufficient for launch)
- **Analytics:** Plausible (privacy-first, single script tag) — do not use Google Analytics
- **Email capture:** Formspree or Resend for waitlist; do not require user accounts
- **Data:** Static — read CSV files at build time, no database initially
- **Search:** Client-side fuzzy search (Fuse.js) for town lookup
- **Charts:** Recharts for any data viz; no D3 unless required

Reasons:
- Next.js App Router is current-best for SEO + fast page loads
- Tailwind keeps you out of CSS hell and produces small bundles
- No component library because every component-library default looks like every other startup site
- Static data is fine until 5,000+ towns; over-engineering hurts launch speed

---

## Information Architecture

Build these pages in this order:

### 1. `/` — Homepage

**Goal:** Establish what Civica is in 8 seconds. Drive scroll to methodology or B2B inquiry.

**Above the fold:**
- Civica wordmark (top left)
- Nav: Methodology, Towns, Data API, About (right)
- Hero: One sentence — "*Every town in America, scored on what your tax dollar actually buys.*"
- Sub-hero: 2 sentences explaining what makes Civica different (fiscal-first, open methodology, multi-year trend data)
- Primary CTA: "Look up your town" (links to `/towns`)
- Secondary CTA: "API for businesses" (links to `/api`)
- **No** stock hero image. Use a single, well-typeset live example: a real Civica score card for Danvers showing the 72 with the TER 5.4. Make it feel like a real product preview, not a mock.

**Below the fold:**
- Section 1: "What we measure" — the 8 pillars as a clean table or grid (not 8 icons in a row), each with its weight and a one-sentence description
- Section 2: "Why this exists" — explain the gap Civica fills. Acknowledge Niche/Zillow exist. Position as fiscal specialist.
- Section 3: "Open methodology" — short pitch for the rigor; CTA to read the methodology
- Section 4: "For businesses" — three sentences on API + enterprise; CTA to API page
- Section 5: Email waitlist signup with honest framing ("We're scoring 250 towns in 2026. Get notified when yours is added.")
- Footer with methodology link, GitHub repo (if public), legal links

### 2. `/towns` — Town Directory & Search

**Goal:** Let visitors find a specific town quickly. Show coverage progress honestly.

- Search bar at top with autocomplete
- Currently scored towns listed (Danvers, Beverly to start) — clickable cards
- Coverage map of Massachusetts highlighting scored towns
- Honest "Currently 2 towns scored. 250 by end of 2026." progress indicator
- Email capture: "Don't see your town? Get notified when it's added."

Do NOT fabricate scores for unscored towns. Do not show all of MA as "coming soon" with placeholder cards. Show only what's real.

### 3. `/towns/[slug]` — Individual Town Profile

**Goal:** Show a town's full Civica Score with complete transparency.

This is the page that has to do real work. Layout:

**Header section:**
- Town name (e.g., "Danvers, Massachusetts")
- The score: large display (e.g., "72") with rating context ("Above-average")
- TER: "$13.36/$1k → TER 5.4 (Average)"
- Confidence indicator ("High confidence — 76 of 99 fields verified")
- Last updated date

**Pillar breakdown:**
- 8 pillars laid out cleanly, each showing:
  - Pillar score (out of 100)
  - Top 2 sub-metrics that drove the score (e.g., "Bond Rating: AA+ (92/100)")
  - One-line context

**Sub-metric detail (collapsible):**
- All 42 sub-metrics with raw values, scores, and source citations
- Each citation links to the source URL
- Hover/click reveals retrieval date and source ID

**Standout factors:**
- 2-3 highlighted differentiators specific to this town (e.g., "Danvers Electric saves residents ~$2,036/year vs MA average")

**Data gaps:**
- Honestly list what's not yet sourced
- Show how it would change the score if filled

**Comparison tool:**
- "Compare Danvers to:" dropdown (Beverly, etc.)

This is where you can be most data-dense. Use small type, generous use of fixed-width fonts for numbers, and clear hierarchy. Reference: how the FRED website displays economic data series.

### 4. `/methodology` — How Civica Works

**Goal:** Establish credibility through detail. This is the page B2B buyers will scrutinize.

- Render the contents of `04-scoring-methodology.md` as polished long-form content
- Use Source Serif 4 for prose, Inter for tables and code
- Embedded interactive elements: clickable pillar weights, collapsible sub-metric definitions
- Link to GitHub for the actual methodology files
- Footer: "Have questions about the methodology? Email methodology@civica.example"

### 5. `/api` — Data API for Businesses

**Goal:** Make B2B prospects feel they're dealing with a serious data vendor. Capture qualified inquiries.

- Hero: "Civica API for proptech, insurance, mortgage, and relocation"
- Use cases (3-4): each with a specific scenario and what data they'd consume
- Pricing tiers (be honest about what you offer):
  - Developer: $99/mo, 1K calls/day, methodology score lookup
  - Business: $499/mo, 10K calls/day, full sub-metric breakdown
  - Enterprise: Custom, dedicated, includes historical data
- "Request API access" form — collect company, role, use case
- Sample response payload (JSON) for credibility
- Do not show "Sign Up" / "Get Started" CTAs — this is enterprise sales, lead capture only

### 6. `/about` — Who's Behind This

**Goal:** Establish the team's credibility honestly.

- One-paragraph mission statement
- Founder/team section (only real people, real bios)
- "Why Civica?" — the founder's reason for building this
- Press / mentions if any (only real ones)
- Contact information

### 7. `/legal/*` — Standard pages

- Privacy policy
- Terms of service
- Cookie policy (Plausible doesn't require one but include for B2B trust)

---

## Visual System

### Color Palette

Pick one of these palettes. Don't use a "vibrant gradient" or "modern startup" palette.

**Option A — Institutional (recommended):**
- Background: `#FFFFFF` / `#FAFAF9` (warm white)
- Primary text: `#1A1A1A`
- Secondary text: `#525252`
- Accent: `#1E40AF` (deep institutional blue) — used sparingly for CTAs and links
- Score colors: 
  - 80+: `#15803D` (deep green)
  - 60-79: `#1E40AF` (blue)
  - 40-59: `#A16207` (amber)
  - <40: `#991B1B` (red)
- Borders: `#E5E5E5`

**Option B — Editorial Warm:**
- Background: `#FFFBF5`
- Primary text: `#1F1611`
- Accent: `#7C2D12` (deep terracotta)
- Use serifs more aggressively

Pick A unless the user specifies otherwise. It's safer, B2B-friendly, and ages well.

### Typography Scale

```
Display (hero):    Inter 600, 56px / 1.05
H1:                Inter 600, 40px / 1.15
H2:                Inter 600, 28px / 1.25
H3:                Inter 500, 20px / 1.3
Body:              Inter 400, 16px / 1.6
Small:             Inter 400, 14px / 1.5
Caption:           Inter 400, 13px / 1.4

Long-form prose:   Source Serif 4 400, 18px / 1.7
Numbers/data:      JetBrains Mono 400 (tabular figures)
```

Do not use more than 2 typefaces total. Don't add Poppins. Don't add Montserrat.

### Spacing

- Section vertical padding: 96px desktop / 64px mobile
- Container max-width: 1200px (1100px feels right for editorial content)
- Use Tailwind's spacing scale; don't introduce custom values

### Motion

Keep it minimal:
- Subtle fade-in on scroll for major sections (200ms ease-out, 8px translate)
- No more than that

Do NOT animate every element on the page. Do not use AOS-style "animate everything" libraries.

---

## Content Sourcing

Pull real content from this repo:

- The 8 pillars and weights → from `master_weights.csv`
- The 42 sub-metrics → from `pillar_weights.csv`
- The 43 sources → from `source_dictionary.csv`
- The Danvers and Beverly scores → from `towns.csv`
- The methodology prose → from `04-scoring-methodology.md`

Do NOT make up additional content. Do NOT invent additional towns, sources, or features.

---

## Honest Copy Guidelines

This is a pre-launch product. Copy must be honest about that. Some specific framings:

**Do say:**
- "Currently scoring 2 North Shore Massachusetts towns. 250 by end of 2026."
- "Methodology v1.0 — open and reproducible"
- "Join the waitlist"
- "Request API access"

**Do NOT say:**
- "Trusted by thousands" (no thousands yet)
- "Industry-leading" (industry is barely defined)
- "AI-powered scoring" (it's a rule-based system, not AI)
- "Real-time data" (data is updated periodically, not real-time)
- "Comprehensive coverage" (currently 2 towns)

The honesty is a feature, not a bug. Civica's brand is rigor and transparency. Pre-launch hype contradicts that.

---

## Development Approach

### Phase 1: Static skeleton (build first)

- All 7 page routes with placeholder content
- Layout, navigation, footer
- Responsive breakpoints

### Phase 2: Real content (build second)

- Wire CSV data to town profile pages
- Render full methodology page from markdown
- Implement search

### Phase 3: Conversion optimization (build third)

- Email capture forms
- API request form  
- Analytics

### Phase 4: Polish (build last)

- Subtle motion
- Performance optimization
- Open Graph / metadata
- Sitemap, robots.txt

Don't try to build everything at once. Ship the skeleton, then iterate.

---

## Deliverables

When complete, the project should have:

- All 7 page types implemented
- Real Danvers and Beverly profiles rendering from `towns.csv`
- Methodology page rendering from `04-scoring-methodology.md`
- Working email waitlist (Resend or Formspree)
- Working API request form
- Lighthouse scores: 95+ Performance, 100 Accessibility, 100 Best Practices, 100 SEO
- Mobile-responsive (test 375px, 768px, 1280px, 1920px)
- Build deployed to Vercel
- README explaining how to add new towns (just edit `towns.csv` and rebuild)

---

## Common Mistakes to Avoid

Specific things you (Claude Code) are likely to do that the user doesn't want:

1. **Don't add a "Features" section with three columns of icons.** It's the most overdone marketing section pattern.
2. **Don't use lorem ipsum.** All copy is in the existing files; pull from there.
3. **Don't add a chatbot or AI assistant widget.** Civica's credibility comes from rigor, not chatbots.
4. **Don't fabricate "as seen in" press logos** unless the user provides real ones.
5. **Don't add cryptocurrency-style visualizations.** No glowing nodes, no abstract data art. Use clean tables, charts, and typography.
6. **Don't use the word "platform."** Civica is a data product and methodology, not a "platform."
7. **Don't use generic SaaS marketing copy.** Read Stripe's docs and Linear's marketing copy for tone.
8. **Don't make the methodology page a wall of text.** Use generous whitespace, clear section headers, and inline data examples.
9. **Don't add live chat / Intercom / similar.** Pre-launch products don't need them.
10. **Don't add social media share buttons** on every page. Only on town profile pages, where they're useful.

---

## Final Note

The user has been told this product is more crowded territory than initially framed. Civica's defensibility comes from being the deepest fiscal-first source, not from being prettier than Niche.com. Build accordingly — credibility before aesthetics, methodology before flourish, honest framing before marketing hype.

If at any point you (Claude Code) are tempted to add something that feels "modern" or "engaging" but doesn't serve the methodology credibility goal, cut it.

When in doubt, ask the user. Don't make brand-defining decisions unilaterally.

---

## After Building

Once the site is live, the user should:

1. Trademark search for "Civica" via USPTO
2. Set up the email forwarding for the contact addresses
3. Add Plausible analytics
4. Test the email capture and API request flows end-to-end
5. Submit sitemap to Google Search Console
6. Set up Vercel preview deployments for future content updates

---

## Approval Checkpoint

Before writing any code, confirm with the user:

1. Color palette (A or B)
2. Domain name (civica.com? civica.app? civica.us?)
3. Whether the GitHub repo will be public (affects whether to link to it)
4. Founder name(s) and bio for the About page
5. Email addresses for waitlist, API requests, methodology questions

Don't proceed past the static skeleton without these. Building generic content and replacing later wastes more time than asking now.
