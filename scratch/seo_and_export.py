import os
import json
import csv

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
products_json_path = os.path.join(base_dir, "products_full.json")
csv_output_path = os.path.join(base_dir, "products_sheet.csv")

# Load products database
with open(products_json_path, 'r', encoding='utf-8') as f:
    products = json.load(f)

# SEO Optimization Functions
def get_recommended_title(product_name):
    # Rule: Primary keyword first, followed by brand. Keep <= 60 chars.
    brand = "Santosh Polymers"
    option1 = f"{product_name} Manufacturer & Supplier | {brand}"
    option2 = f"{product_name} Manufacturer | {brand}"
    option3 = f"{product_name} Supplier | {brand}"
    option4 = f"{product_name} | {brand}"
    
    if len(option1) <= 60:
        return option1
    elif len(option2) <= 60:
        return option2
    elif len(option3) <= 60:
        return option3
    elif len(option4) <= 60:
        return option4
    else:
        # Fallback to option 4 even if slightly over 60
        return option4

def get_recommended_meta_desc(product_name, category):
    # Rule: Category specific template, 140-160 characters.
    cat_lower = category.lower()
    desc = ""
    
    if "oleo" in cat_lower:
        desc = f"Looking for high-quality {product_name}? Santosh Polymers is a leading manufacturer & supplier in India. Enquire today for bulk pricing & specs!"
        if len(desc) > 160:
            desc = f"Looking for high-quality {product_name}? Santosh Polymers is India's leading manufacturer & supplier. Enquire for bulk pricing!"
    elif "paper" in cat_lower:
        desc = f"Enhance production with premium {product_name}. Santosh Polymers is India's trusted manufacturer of paper sizing chemicals. Request a quote today!"
        if len(desc) > 160:
            desc = f"Enhance paper quality with premium {product_name}. Santosh Polymers is India's trusted manufacturer. Request a quote today!"
    elif "herbal" in cat_lower:
        desc = f"Get pure, high-grade {product_name} from Santosh Polymers, India's leading manufacturer & exporter of herbal extracts. Contact us for bulk pricing!"
        if len(desc) > 160:
            desc = f"Get pure, high-grade {product_name} from Santosh Polymers, India's leading manufacturer & exporter of extracts. Enquire now!"
    elif "packaging" in cat_lower:
        desc = f"Durable and customized {product_name} by Santosh Polymers. Premium quality packaging solutions for industrial use. Request a free quote today!"
        if len(desc) > 160:
            desc = f"Durable, customized {product_name} by Santosh Polymers. Premium quality packaging solutions. Request a quote today!"
    else:
        desc = f"Looking for high-quality {product_name}? Santosh Polymers is India's trusted manufacturer & supplier of industrial chemicals. Request a quote!"
        
    # Final length optimization
    if len(desc) > 160:
        desc = desc[:157] + "..."
    elif len(desc) < 120:
        # Pad with general quality message if too short
        desc += " High purity and reliable supply guaranteed."
        if len(desc) > 160:
            desc = desc[:160]
            
    return desc

def get_recommended_keywords(product_name, category):
    base_keywords = [
        product_name,
        f"{product_name} manufacturer",
        f"{product_name} supplier",
        f"buy {product_name} in bulk",
        f"{product_name} price India",
        "Santosh Polymers",
        "Haryana",
        "Kurukshetra",
        "Ladwa"
    ]
    return ", ".join(base_keywords)

# Process and optimize each product
rows = []
for p in products:
    p_name = p["product_name"]
    category = p["category"]
    filename = p["link"].split('/')[-1]
    
    # Save original meta values for comparison
    old_title = p.get("title", "")
    old_meta_desc = p.get("meta_description", "")
    old_meta_keywords = p.get("meta_keywords", "")
    
    # Apply optimizations to products_full.json fields
    rec_title = get_recommended_title(p_name)
    rec_desc = get_recommended_meta_desc(p_name, category)
    rec_keywords = get_recommended_keywords(p_name, category)
    
    p["title"] = rec_title
    p["meta_description"] = rec_desc
    p["meta_keywords"] = rec_keywords
    
    # Format list and dictionary fields for spreadsheet display
    features_str = "\n".join(p.get("features", []))
    
    specs_list = []
    for k, v in p.get("specs_table", {}).items():
        specs_list.append(f"{k}: {v}")
    specs_str = "\n".join(specs_list)
    
    detailed_specs_list = []
    for k, v in p.get("detailed_specs", {}).items():
        detailed_specs_list.append(f"{k}: {v}")
    detailed_specs_str = "\n".join(detailed_specs_list)
    
    # Prepare row for CSV
    rows.append({
        "Product Name": p_name,
        "Filename": filename,
        "Category": category,
        "Old Meta Title": old_title,
        "Meta Title (SEO)": rec_title,
        "Old Meta Description": old_meta_desc,
        "Meta Description (SEO)": rec_desc,
        "Meta Keywords": rec_keywords,
        "Description": p.get("description", ""),
        "Features": features_str,
        "Applications": p.get("applications", ""),
        "Specs Table": specs_str,
        "Detailed Specs": detailed_specs_str
    })

# Save updated JSON database
with open(products_json_path, 'w', encoding='utf-8') as f:
    json.dump(products, f, indent=4, ensure_ascii=False)
print("Updated products_full.json with optimized SEO meta tags.")

# Write to CSV
headers = [
    "Product Name", "Filename", "Category", 
    "Old Meta Title", "Meta Title (SEO)", 
    "Old Meta Description", "Meta Description (SEO)", 
    "Meta Keywords", "Description", "Features", 
    "Applications", "Specs Table", "Detailed Specs"
]

with open(csv_output_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)

print(f"Generated Excel-compatible CSV sheet at: {csv_output_path}")
