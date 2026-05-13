# Civica — Things to Come Back To

## 1. Set up Cloudflare
GitHub Pages can't set HTTP security headers. Cloudflare (free tier) fixes this.
**What you get:**
- HSTS (forces HTTPS at the network level)
- Real Content-Security-Policy headers (replaces the current meta tag workaround)
- WAF — blocks bad bots before they hit the site
- DDoS protection
- ~20 minutes to set up

## 2. Ad Structure Review
Before approaching real advertisers, do a full pass on the three ad units:
- **Featured Agent** — currently shows placeholder "Sarah Mitchell / Coldwell Banker"
- **Featured Listings** — only Beverly has real listing data, all others use defaults
- **Vendor Strip** — all 4 slots are placeholder businesses
Review: does each unit render well on all 36 towns? Are the placeholder names/prices professional-looking? Does the advertiser onboarding flow make sense?

## 4. Google Analytics 4 (GA4) — You need to do this
- Go to analytics.google.com → create a new property for bluepenguin1234.github.io/civica
- Copy the Measurement ID (looks like `G-XXXXXXXXXX`)
- Give the ID to Claude — code gets dropped into civica-v5.html in one edit
- Without this you have zero visibility into traffic, which towns get views, where users come from

## 5. OG Social Preview Image (`civica-og.png`) — You need to do this
- Open Graph / Twitter card tags are live but the image file doesn't exist yet
- Create a 1200×630 PNG: Civica logo + tagline on a clean background (even simple is fine)
- Drop it in `C:\Users\Brian\Desktop\Civica\` and tell Claude — it gets pushed with the next commit
- Without this, shared links on Twitter/Slack/iMessage show a blank card (no image)

## 6. Google Search Console — You need to do this
- Go to search.google.com/search-console → add property: `bluepenguin1234.github.io/civica`
- Choose HTML tag verification → give the tag to Claude → it gets added to the site and pushed
- This is how you see what Google search queries are bringing people to Civica

## 7. Formspree (Notify Me form) — You need to do this
- The email capture form currently uses a placeholder endpoint — signups are NOT being saved
- Go to formspree.io → create a free account → create a form → copy the form ID
- Give the ID to Claude — one edit to civica-v5.html wires it up

---

## 3. Move JS to External File (Security)
The biggest remaining CSP weakness is `'unsafe-inline'` — required because all JavaScript is inline in the HTML.
Moving JS to `civica-v5.js` would allow a fully strict Content Security Policy.
**Effort:** Large refactor. Low urgency, high payoff long-term.
