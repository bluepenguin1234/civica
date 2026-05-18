"""
Re-extract pension funded ratios from PERAC AR2024 PDF.

Each retirement system page has a data line with this layout:
  $ [Market Value]  [Returns%]  [Assumed Rate%]  $ [COLA Base]  [Funded Ratio%]

The funded ratio is the LAST percentage on that data line.
Previous extraction wrongly took the FIRST % (2024 investment returns ~9%).
"""

import re
import csv
import sys
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "pdfplumber"], check=True)
    import pdfplumber

PDF = Path(r"C:\Users\Brian\Downloads\AR24_WEB.pdf")
OUT = Path(r"C:\Users\Brian\Desktop\Civica\data\bulk\perac_funded_ratios_2024.csv")

# Known noise lines to skip when hunting for the system name
SKIP_WORDS = {
    'PERAC', 'Annual', 'Report', 'Massachusetts', 'Pension', 'Reserves',
    'Investment', 'Market', 'Value', 'Returns', 'Assumed', 'COLA',
    'Funded', 'Ratio', 'Rate', 'Assets', 'Liabilities', 'Page',
    'Table', 'Figure', 'Financial', 'Statements', 'Notes', 'Actuarial',
    'Valuation', 'Summary', 'System', 'Systems', 'Board', 'Members',
    'Contributions', 'Benefits', 'Expenses', 'Net', 'Total', 'Schedule',
}

# Regex that matches the full 5-column data line
# Groups: (returns_pct, assumed_pct, funded_pct)
FULL_LINE_RE = re.compile(
    r'\$\s*[\d,.\s]+[BMK]?\s+'    # market value (e.g. $ 2.3 B or $ 1,234,567,890)
    r'([\d.]+)\s*%\s+'             # 2024 returns %
    r'([\d.]+)\s*%\s+'             # assumed rate %
    r'\$\s*[\d,.\s]+\s+'           # COLA base (e.g. $ 16,000)
    r'([\d.]+)\s*%',               # funded ratio % — the one we want
    re.IGNORECASE
)


def find_system_name(lines):
    """Return the most likely retirement system name from page text lines."""
    for line in lines:
        line = line.strip()
        if not line or len(line) < 4:
            continue
        # Skip pure numbers / symbols
        if re.match(r'^[\d\s$%,.()\-]+$', line):
            continue
        # Skip lines that contain common noise words
        if any(w in line for w in SKIP_WORDS):
            continue
        # Must have at least one capitalized word
        if not re.search(r'[A-Z][a-z]', line) and not line.isupper():
            continue
        # Strip parenthetical suffixes
        clean = re.sub(r'\s*\(.*?\)\s*$', '', line).strip()
        if 3 < len(clean) < 80:
            return clean
    return None


def find_funded_ratio(text):
    """
    Find funded ratio from page text.
    Strategy 1: match full 5-column data line, take group(3).
    Strategy 2: find any line starting with $ that has >=2 pcts; take last.
    """
    # Strategy 1: structured match
    m = FULL_LINE_RE.search(text)
    if m:
        return float(m.group(3))

    # Strategy 2: any $ line with multiple percentages
    for line in text.split('\n'):
        stripped = line.strip()
        if not (stripped.startswith('$') or re.match(r'\$\s*[\d,.]', stripped)):
            continue
        pcts = re.findall(r'([\d]+\.?[\d]*)%', stripped)
        if len(pcts) >= 2:
            val = float(pcts[-1])
            if 1.0 <= val <= 200.0:   # sanity: funded ratios are 1%–200%
                return val

    return None


results = {}
debug_lines = []

with pdfplumber.open(PDF) as pdf:
    total = len(pdf.pages)
    print(f"PDF loaded: {total} pages")

    for i, page in enumerate(pdf.pages):
        text = page.extract_text() or ""
        if not text.strip():
            continue

        funded = find_funded_ratio(text)
        if funded is None:
            continue

        lines = [ln.strip() for ln in text.split('\n') if ln.strip()]
        name = find_system_name(lines)

        if name and name not in results:
            results[name] = funded
            debug_lines.append(f"  p{i+1:3d}  {name}: {funded}%")

print(f"\nExtracted {len(results)} systems:\n")
for dl in debug_lines:
    print(dl)

# Write CSV sorted by name
with open(OUT, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['system_name', 'funded_ratio_pct'])
    for name, ratio in sorted(results.items()):
        w.writerow([name, ratio])

print(f"\nWrote {len(results)} rows to {OUT}")
