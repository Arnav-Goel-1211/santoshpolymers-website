import os
import json
import csv
import urllib.request
import re
import html as html_lib
import shutil
import subprocess

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
products_json_path = os.path.join(base_dir, "products_full.json")
products_backup_path = os.path.join(base_dir, "products_full.json.bak")
csv_input_path = os.path.join(base_dir, "updated-products_sheet.csv")
generate_script_path = os.path.join(base_dir, "generate_products.py")

# Ensure files exist
if not os.path.exists(csv_input_path):
    print(f"Error: CSV sheet not found at {csv_input_path}")
    exit(1)

# Back up database
if os.path.exists(products_json_path):
    shutil.copy(products_json_path, products_backup_path)
    print(f"Backed up products_full.json to {products_backup_path}")

# Load original products database
with open(products_json_path, 'r', encoding='utf-8') as f:
    original_products = json.load(f)

# Map original products by their filename
original_products_by_file = {}
for p in original_products:
    fn = p.get("filename") or p["link"].split('/')[-1]
    original_products_by_file[fn] = p

# Rename map for CSV filenames to original JSON filenames
rename_map = {
    'oleic-acid.htm': 'oleic-fatty-acid.htm',
    'distilled-soya-fatty-acid.htm': 'distilled-soya-fatty-acid-oil.htm'
}

# Helper to crawl old site metadata
def fetch_meta_content(url):
    print(f"Crawling metadata from old website: {url}")
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            
        # Parse title
        title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else ""
        
        # Parse description
        desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html_content, re.IGNORECASE | re.DOTALL)
        if not desc_match:
            desc_match = re.search(r'<meta\s+content=["\'](.*?)["\']\s+name=["\']description["\']', html_content, re.IGNORECASE | re.DOTALL)
        desc = desc_match.group(1).strip() if desc_match else ""
        
        # Parse keywords
        keys_match = re.search(r'<meta\s+name=["\']keywords["\']\s+content=["\'](.*?)["\']', html_content, re.IGNORECASE | re.DOTALL)
        if not keys_match:
            keys_match = re.search(r'<meta\s+content=["\'](.*?)["\']\s+name=["\']keywords["\']', html_content, re.IGNORECASE | re.DOTALL)
        keywords = keys_match.group(1).strip() if keys_match else ""
        
        # Clean up HTML entities
        title = html_lib.unescape(title)
        desc = html_lib.unescape(desc)
        keywords = html_lib.unescape(keywords)
        
        return title, desc, keywords
    except Exception as e:
        print(f"  Warning: Failed to fetch/parse {url}: {e}")
        return None

# Helper to parse multi-line key-value specs cell
def parse_specs_cell(cell_value):
    specs = {}
    if not cell_value:
        return specs
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
            specs[line] = ""
    return specs

# Helper to parse multi-line features cell
def parse_list_cell(cell_value):
    if not cell_value:
        return []
    features = []
    for line in cell_value.split('\n'):
        line = line.strip()
        if line.startswith('-') or line.startswith('*'):
            line = line[1:].strip()
        if line:
            features.append(line)
    return features

# Process the updated CSV
new_products = []
old_directories_to_delete = set()
imported_filenames = set()

with open(csv_input_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        csv_filename = row.get("Filename")
        if not csv_filename:
            continue
            
        csv_filename = csv_filename.strip()
        imported_filenames.add(csv_filename)
        
        # Resolve original filename if renamed
        orig_filename = rename_map.get(csv_filename, csv_filename)
        
        if orig_filename in original_products_by_file:
            orig_p = original_products_by_file[orig_filename]
            
            # Create updated product entry
            updated_p = orig_p.copy()
            updated_p["product_name"] = row["Product Name"].strip()
            updated_p["category"] = row["Category"].strip()
            updated_p["description"] = row["Description"].strip()
            updated_p["applications"] = row["Applications"].strip()
            updated_p["features"] = parse_list_cell(row["Features"])
            updated_p["specs_table"] = parse_specs_cell(row["Specs Table"])
            updated_p["detailed_specs"] = parse_specs_cell(row["Detailed Specs"])
            
            # Update link and filename values to reflect new names
            if csv_filename != orig_filename:
                # Update link domain path
                old_link = orig_p["link"]
                new_link = old_link.replace(orig_filename, csv_filename)
                updated_p["link"] = new_link
                updated_p["filename"] = csv_filename
                
                # Flag old directory for deletion
                old_dir_name = orig_filename.replace(".htm", "")
                old_directories_to_delete.add(old_dir_name)
                print(f"Renamed file: {orig_filename} -> {csv_filename} (Old folder '{old_dir_name}' marked for deletion)")
            else:
                updated_p["filename"] = orig_filename
            
            # Fetch metadata from original live website
            meta = fetch_meta_content(orig_p["link"])
            if meta:
                fetched_title, fetched_desc, fetched_keywords = meta
                if fetched_title:
                    updated_p["title"] = fetched_title
                else:
                    updated_p["title"] = row["Meta Title (SEO)"].strip()
                    
                if fetched_desc:
                    updated_p["meta_description"] = fetched_desc
                else:
                    updated_p["meta_description"] = row["Meta Description (SEO)"].strip()
                    
                if fetched_keywords:
                    updated_p["meta_keywords"] = fetched_keywords
                else:
                    updated_p["meta_keywords"] = row["Meta Keywords"].strip()
            else:
                # Fallback to sheet metadata
                print(f"  Using spreadsheet metadata fallback for {updated_p['product_name']}")
                updated_p["title"] = row["Meta Title (SEO)"].strip()
                updated_p["meta_description"] = row["Meta Description (SEO)"].strip()
                updated_p["meta_keywords"] = row["Meta Keywords"].strip()
                
            new_products.append(updated_p)
        else:
            print(f"Warning: Product in CSV not found in JSON mapping: {csv_filename}")

# Identify deleted products
for orig_filename, orig_p in original_products_by_file.items():
    # If the original filename is not resolved to any imported filename, it was removed
    is_imported = False
    for csv_fn in imported_filenames:
        if rename_map.get(csv_fn, csv_fn) == orig_filename:
            is_imported = True
            break
            
    if not is_imported:
        old_dir_name = orig_filename.replace(".htm", "")
        old_directories_to_delete.add(old_dir_name)
        print(f"Removed product: {orig_p['product_name']} (Old folder '{old_dir_name}' marked for deletion)")

# Save new products list back to database
with open(products_json_path, 'w', encoding='utf-8') as f:
    json.dump(new_products, f, indent=4, ensure_ascii=False)

print(f"\nSaved {len(new_products)} products to products_full.json in the new order.")

# Delete old folders to keep workspace clean
for old_dir in old_directories_to_delete:
    old_dir_path = os.path.join(base_dir, old_dir)
    if os.path.exists(old_dir_path):
        print(f"Cleaning up orphaned directory: {old_dir_path}")
        shutil.rmtree(old_dir_path)

# Run site generation script
print("\nRunning generate_products.py to update HTML files...")
try:
    result = subprocess.run(
        ["python3", generate_script_path],
        cwd=base_dir,
        capture_output=True,
        text=True,
        check=True
    )
    print(result.stdout)
    print("Website generated successfully!")
except subprocess.CalledProcessError as e:
    print(f"Error running generate_products.py: {e}")
    print("Stdout:", e.stdout)
    print("Stderr:", e.stderr)
    exit(1)
