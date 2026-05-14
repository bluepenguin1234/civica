import sys, re, csv
sys.stdout.reconfigure(encoding='utf-8')

html_path = r"C:\Users\Brian\Desktop\Civica\civica-v5.html"
csv_path = r"C:\Users\Brian\Desktop\Civica\data\towns.csv"

with open(html_path, encoding='utf-8') as f:
    content = f.read()

html_towns = set(re.findall(r'\bname:\s*"([^"]+)"', content))

csv_towns = set()
with open(csv_path, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        csv_towns.add(row['town_name'])

in_html_not_csv = sorted(html_towns - csv_towns)
in_csv_not_html = sorted(csv_towns - html_towns)

print(f"HTML towns: {len(html_towns)}")
print(f"CSV towns: {len(csv_towns)}")
print(f"\nIn HTML but NOT in CSV (guessed data — must be removed):")
for t in in_html_not_csv:
    print(f"  {t}")
print(f"\nIn CSV but NOT in HTML (ready to add via pipeline):")
for t in in_csv_not_html:
    print(f"  {t}")
