import sys, re
sys.stdout.reconfigure(encoding='utf-8')

GUESSED = {
    "Attleborough", "Ayer", "Bellingham", "Bourne", "Dover",
    "East Longmeadow", "Groton", "Harvard", "Sherborn", "Stow", "West Boylston"
}

html_path = r"C:\Users\Brian\Desktop\Civica\civica-v5.html"

with open(html_path, encoding='utf-8') as f:
    content = f.read()

# Find TOWNS array boundaries
start_marker = 'const TOWNS = ['
end_marker = '\n];'
start_idx = content.index(start_marker) + len(start_marker)
end_idx = content.index(end_marker, start_idx)

towns_block = content[start_idx:end_idx]

# Split into individual town objects - each starts with '\n  {' and ends with '\n  }'
# Use a careful approach: find each {..} block at the top level
town_objects = []
depth = 0
current_start = None

for i, ch in enumerate(towns_block):
    if ch == '{' and depth == 0:
        depth = 1
        current_start = i
    elif ch == '{':
        depth += 1
    elif ch == '}':
        depth -= 1
        if depth == 0 and current_start is not None:
            town_objects.append(towns_block[current_start:i+1])
            current_start = None

print(f"Total towns found: {len(town_objects)}")

kept = []
removed = []
for obj in town_objects:
    m = re.search(r'\bname:\s*"([^"]+)"', obj)
    if m and m.group(1) in GUESSED:
        removed.append(m.group(1))
    else:
        kept.append(obj)

print(f"Removing {len(removed)} guessed towns: {removed}")
print(f"Keeping {len(kept)} towns")

# Reconstruct the TOWNS block
new_towns_block = ',\n  '.join(kept)
# Add proper leading/trailing whitespace to match original format
new_towns_block = '\n  ' + new_towns_block + '\n'

new_content = content[:start_idx] + new_towns_block + content[end_idx:]

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Done. civica-v5.html updated.")
