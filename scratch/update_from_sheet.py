import os
import json
import csv
import subprocess

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
products_json_path = os.path.join(base_dir, "products_full.json")
csv_input_path = os.path.join(base_dir, "products_sheet.csv")
generate_script_path = os.path.join(base_dir, "generate_products.py")

if not os.path.exists(csv_input_path):
    print(f"Error: CSV sheet not found at {csv_input_path}")
    print("Please make sure you have generated the sheet first by running scratch/seo_and_export.py.")
    exit(1)

# Load CSV data into a dictionary keyed by Filename
sheet_products = {}
with open(csv_input_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        filename = row.get("Filename")
        if filename:
            sheet_products[filename] = row

print(f"Read {len(sheet_products)} products from CSV sheet.")

# Load existing products database
with open(products_json_path, 'r', encoding='utf-8') as f:
    products = json.load(f)

# Helper to parse multi-line key-value specs cell
def parse_specs_cell(cell_value):
    specs = {}
    if not cell_value:
        return specs
    
    # Support lines like 'Color: Yellow' or 'Color : Yellow'
    for line in cell_value.split('\n'):
        line = line.strip()
        if not line:
            continue
        if ':' in line:
            parts = line.split(':', 1)
            k = parts[0].strip()
            v = parts[1].strip()
            if k:
                specs[k] = v
        else:
            # If the user put a line without a colon, keep it as key with empty value
            specs[line] = ""
    return specs

# Helper to parse multi-line features cell
def parse_list_cell(cell_value):
    if not cell_value:
        return []
    features = []
    for line in cell_value.split('\n'):
        line = line.strip()
        # Remove markdown bullet points if user added them, e.g. "- Excellent quality" or "* Excellent quality"
        if line.startswith('-') or line.startswith('*'):
            line = line[1:].strip()
        if line:
            features.append(line)
    return features

# Update JSON database
updated_count = 0
for p in products:
    # Identify product filename from its link
    filename = p["link"].split('/')[-1]
    
    if filename in sheet_products:
        row = sheet_products[filename]
        
        # Core info
        p["product_name"] = row["Product Name"].strip()
        p["category"] = row["Category"].strip()
        p["title"] = row["Meta Title (SEO)"].strip()
        p["meta_description"] = row["Meta Description (SEO)"].strip()
        p["meta_keywords"] = row["Meta Keywords"].strip()
        p["description"] = row["Description"].strip()
        p["applications"] = row["Applications"].strip()
        
        # Features and specs
        p["features"] = parse_list_cell(row["Features"])
        p["specs_table"] = parse_specs_cell(row["Specs Table"])
        p["detailed_specs"] = parse_specs_cell(row["Detailed Specs"])
        
        updated_count += 1
    else:
        print(f"Warning: Product in database not found in CSV sheet: {filename}")

# Save updated JSON database
with open(products_json_path, 'w', encoding='utf-8') as f:
    json.dump(products, f, indent=4, ensure_ascii=False)

print(f"Successfully updated {updated_count} products in products_full.json.")

# Run the page generation script to update all HTML files
print("Running generate_products.py to update HTML files...")
try:
    result = subprocess.run(
        ["python3", generate_script_path],
        cwd=base_dir,
        capture_output=True,
        text=True,
        check=True
    )
    print(result.stdout)
    print("Static HTML pages generated successfully!")
except subprocess.CalledProcessError as e:
    print(f"Error running generate_products.py: {e}")
    print("Stdout:", e.stdout)
    print("Stderr:", e.stderr)
    exit(1)
