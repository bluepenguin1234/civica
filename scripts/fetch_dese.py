"""
Fetch MA DESE school data for all districts.
Saves: bulk/ma_ap_participation_2024.csv
       bulk/ma_graduation_rates_2025.csv
       bulk/ma_mcas_math_2024.csv
       bulk/ma_enrollment_by_grade_2024.csv
       bulk/ma_schools_combined.csv  (joined, ready to use)
"""

import urllib.request, csv, re
from pathlib import Path

BULK = Path(__file__).parent.parent / "data" / "bulk"
BULK.mkdir(parents=True, exist_ok=True)

BASE = "https://profiles.doe.mass.edu/statereport"

def fetch_html(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")

def parse_table(html):
    """Extract the main HTML table as list of dicts."""
    # Find table
    m = re.search(r'<table[^>]*>(.*?)</table>', html, re.DOTALL | re.IGNORECASE)
    if not m:
        return []
    table = m.group(1)
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table, re.DOTALL | re.IGNORECASE)
    if not rows:
        return []

    def strip_tags(s):
        s = re.sub(r'<[^>]+>', '', s)
        return re.sub(r'\s+', ' ', s).strip().replace('&amp;', '&').replace('&#39;', "'").replace('&nbsp;', ' ')

    headers = [strip_tags(th) for th in re.findall(r'<th[^>]*>(.*?)</th>', rows[0], re.DOTALL | re.IGNORECASE)]
    if not headers:
        return []

    result = []
    for row in rows[1:]:
        cells = [strip_tags(td) for td in re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)]
        if len(cells) >= len(headers):
            result.append(dict(zip(headers, cells)))
    return result

def save_csv(path, rows):
    if not rows:
        print(f"  No data for {path.name}")
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"  Saved {len(rows)} rows -> {path.name}")

def safe_float(s):
    try:
        return float(str(s).replace('%','').replace(',','').strip())
    except:
        return None

# ── AP Participation ──────────────────────────────────────────────────────────
print("Fetching AP Participation...")
html = fetch_html(f"{BASE}/ap_part.aspx?mode=district&orderBy=&year=2024")
ap_rows = parse_table(html)
save_csv(BULK / "ma_ap_participation_2024.csv", ap_rows)

# ── Graduation Rates ──────────────────────────────────────────────────────────
print("Fetching Graduation Rates...")
html = fetch_html(f"{BASE}/gradrates.aspx?mode=district&year=2024&grade=&reportType=grads")
grad_rows = parse_table(html)
save_csv(BULK / "ma_graduation_rates_2025.csv", grad_rows)

# ── MCAS Math ─────────────────────────────────────────────────────────────────
print("Fetching MCAS Math (All Grades)...")
html = fetch_html(f"{BASE}/mcas.aspx?mode=district&subject=MTH&grade=All&year=2024&orderBy=")
mcas_rows = parse_table(html)
save_csv(BULK / "ma_mcas_math_2024.csv", mcas_rows)

# ── Enrollment by Grade (for AP rate denominator) ─────────────────────────────
print("Fetching Enrollment by Grade...")
html = fetch_html(f"{BASE}/enrollmentbygrade.aspx?mode=district&year=2024&grade=&orderBy=")
enroll_rows = parse_table(html)
save_csv(BULK / "ma_enrollment_by_grade_2024.csv", enroll_rows)

# ── Build combined lookup: district_name → school metrics ─────────────────────
print("\nBuilding combined schools lookup...")

# Index AP by district name
ap_idx = {}
for r in ap_rows:
    name = r.get("District Name","").strip()
    takers = safe_float(r.get("Test Takers","0") or "0")
    ap_idx[name.lower()] = takers

# Index enrollment: sum grades 9-12
enroll_idx = {}
grade_cols = ["09", "10", "11", "12", "9", "10", "11", "12", "Gr 9", "Gr 10", "Gr 11", "Gr 12"]
for r in enroll_rows:
    name = r.get("District Name","").strip()
    total = 0
    for k, v in r.items():
        if any(g in k for g in ["9","10","11","12"]) and k not in ["District Name","District Code"]:
            v_f = safe_float(v)
            if v_f:
                total += v_f
    if name:
        enroll_idx[name.lower()] = total

# Index grad rates
grad_idx = {}
for r in grad_rows:
    name = r.get("District Name","").strip()
    pct = safe_float(r.get("% Graduated","") or r.get("% Grad",""))
    grad_idx[name.lower()] = pct

# Index MCAS
mcas_idx = {}
for r in mcas_rows:
    name = r.get("District Name","").strip()
    me = safe_float(r.get("M+E %","") or r.get("% M+E","") or r.get("Meeting or Exceeding",""))
    mcas_idx[name.lower()] = me

# Combine using AP as base (most districts)
all_districts = sorted(set(list(ap_idx.keys()) + list(grad_idx.keys()) + list(mcas_idx.keys())))
combined = []
for d in all_districts:
    takers   = ap_idx.get(d)
    hs_enroll = enroll_idx.get(d)
    ap_rate  = round(takers / hs_enroll * 100, 1) if takers and hs_enroll and hs_enroll > 0 else None
    combined.append({
        "district_name":     d,
        "ap_test_takers":    takers,
        "hs_enrollment_9_12":hs_enroll,
        "ap_participation_pct": ap_rate,
        "graduation_rate_pct":  grad_idx.get(d),
        "mcas_math_pct":         mcas_idx.get(d),
    })

save_csv(BULK / "ma_schools_combined.csv", combined)

# ── Spot-check our towns ──────────────────────────────────────────────────────
print("\nSpot check — our towns:")
targets = ["danvers","beverly","cambridge","lexington","arlington","lynn","lawrence","somerville","reading","winchester"]
for t in targets:
    row = next((r for r in combined if t in r["district_name"]), None)
    if row:
        print(f"  {row['district_name']:<30} AP={row['ap_participation_pct']}%  grad={row['graduation_rate_pct']}%  mcas={row['mcas_math_pct']}%")
    else:
        print(f"  {t} — NOT FOUND")
