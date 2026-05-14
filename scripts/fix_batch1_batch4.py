#!/usr/bin/env python3
"""Apply confirmed bond ratings and school district rank corrections for batch 1 and batch 4 towns."""
import csv, io

CSV_PATH = r"C:\Users\Brian\Desktop\Civica\data\towns.csv"

# Confirmed S&P bond ratings (from EMMA/MSRB research, May 2026)
BOND_CORRECTIONS = {
    # Batch 1
    "Shrewsbury":         "AAA",        # S&P Jul 2024
    "Northborough":       "Not rated",  # Moody's Aa1 only; no S&P
    "Milford":            "AAA",        # S&P Oct 2021
    "Mansfield":          "AA+",        # S&P 2024
    "Easton":             "Not rated",  # Moody's Aa3 only; no S&P
    "North Attleborough": "AA+",        # S&P 2026
    "Medway":             "AAA",        # S&P Aug 2025
    # Batch 4
    "Sharon":             "AA",         # S&P Feb 2026 (downgrade from AAA estimate)
    "Medfield":           "Not rated",  # Moody's Aa1 only; no S&P
}

# Confirmed school district ranks — SchoolDigger 2024-25, out of 351 MA districts
RANK_CORRECTIONS = {
    # Batch 1
    "Shrewsbury":         (43,  351),
    "Westborough":        (29,  351),
    "Northborough":       (83,  351),   # K-8 Northborough district
    "Grafton":            (85,  351),
    "Milford":            (294, 351),
    "Mansfield":          (88,  351),
    "Easton":             (68,  351),
    "North Attleborough": (151, 351),
    "Medway":             (47,  351),
    "Millis":             (93,  351),
    # Batch 4
    "Walpole":            (47,  351),
    "Sharon":             (23,  351),
    "Franklin":           (58,  351),
    "Foxborough":         (72,  351),
    "Medfield":           (17,  351),
    "Westford":           (33,  351),
    "Weston":             (6,   351),
    "Littleton":          (41,  351),
    "Stoughton":          (197, 351),
}

with open(CSV_PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

changes = []
for row in rows:
    town = row["town_name"]

    if town in BOND_CORRECTIONS:
        old = row.get("bond_rating_sp", "")
        new = BOND_CORRECTIONS[town]
        if old != new:
            row["bond_rating_sp"] = new
            changes.append(f"  {town}: bond {old!r} -> {new!r}")

    if town in RANK_CORRECTIONS:
        rank, total = RANK_CORRECTIONS[town]
        old_rank  = row.get("district_state_rank", "")
        old_total = row.get("district_state_rank_total", "")
        if str(old_rank) != str(rank) or str(old_total) != str(total):
            row["district_state_rank"]       = str(rank)
            row["district_state_rank_total"] = str(total)
            changes.append(f"  {town}: rank {old_rank}/{old_total} -> {rank}/{total}")

buf = io.StringIO()
writer = csv.DictWriter(buf, fieldnames=fieldnames, lineterminator="\n")
writer.writeheader()
writer.writerows(rows)

with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
    f.write(buf.getvalue())

print(f"Applied {len(changes)} corrections to towns.csv:")
for c in changes:
    print(c)
