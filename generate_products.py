import os
import json
import urllib.parse
import re

base_dir = os.path.dirname(os.path.abspath(__file__))
products_json_path = os.path.join(base_dir, "products_full.json")
layout_path = os.path.join(base_dir, "templates", "layout.html")
prod_detail_template_path = os.path.join(base_dir, "templates", "product_detail.html")

# Read database
with open(products_json_path, 'r', encoding='utf-8') as f:
    products = json.load(f)

# Read layout
with open(layout_path, 'r', encoding='utf-8') as f:
    layout_tpl = f.read()

# Read product detail template
with open(prod_detail_template_path, 'r', encoding='utf-8') as f:
    prod_detail_tpl = f.read()

def clean_weblink_boilerplate(text, product_name):
    if not text:
        return product_name
    # Strip common Weblink action texts
    text = text.replace("Call Now", "")
    text = text.replace("Get Latest Price", "")
    text = text.replace("Link Copied", "")
    
    # Strip MOQ phrases e.g. "50 Litre (MOQ)"
    text = re.sub(r'\d+\s+\w+\s+\(MOQ\)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'moq\s*:\s*\d+\s+\w+', '', text, flags=re.IGNORECASE)
    
    # Strip duplicate product name prefix if present
    double_title = f"{product_name} {product_name}"
    if text.startswith(double_title):
        text = text[len(double_title):].strip()
    elif text.startswith(product_name):
        text = text[len(product_name):].strip()
        
    # Clean up double spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Helper to render base layout
def render_page(content, title, desc, keywords, active_menu="home"):
    page = layout_tpl
    page = page.replace("{{title}}", title)
    page = page.replace("{{meta_description}}", desc)
    page = page.replace("{{meta_keywords}}", keywords)
    page = page.replace("{{content}}", content)
    
    # Active menu classes
    page = page.replace("{{active_home}}", "active" if active_menu == "home" else "")
    page = page.replace("{{active_about}}", "active" if active_menu == "about" else "")
    page = page.replace("{{active_industries}}", "active" if active_menu == "industries" else "")
    page = page.replace("{{active_products}}", "active" if active_menu == "products" else "")
    page = page.replace("{{active_contact}}", "active" if active_menu == "contact" else "")
    
    return page

# Helper to slugify category names
def get_cat_slug(cat):
    cat_lower = cat.lower()
    if "oleo" in cat_lower:
        return "oleo-chemicals"
    elif "paper" in cat_lower:
        return "paper-chemicals"
    elif "herbal" in cat_lower:
        return "herbal-extracts"
    elif "packaging" in cat_lower:
        return "packaging-solutions"
    return "oleo-chemicals"

# ==========================================
# 1. BUILD INDIVIDUAL PRODUCT PAGES
# ==========================================
print("Generating 30 product detail pages...")
for p in products:
    p_name = p["product_name"]
    category = p["category"]
    filename = p["link"].split('/')[-1] # e.g. akd-wax-emulsion.htm (matches live SEO exactly)
    
    # Format images
    img_list = p["images"]
    main_image = img_list[0] if img_list else "images/product/default.webp"
    
    # Thumbnails formatting
    has_thumbs = len(img_list) > 1
    thumbs_html = ""
    if has_thumbs:
        for idx, img in enumerate(img_list):
            active_class = "active" if idx == 0 else ""
            thumbs_html += f'<div class="gallery-thumb {active_class}" data-large="{img}"><img src="{img}" alt="{p_name} Thumb"></div>'
            
    # Specifications Table
    specs = p["specs_table"]
    has_specs = len(specs) > 0
    specs_rows = ""
    if has_specs:
        for k, v in specs.items():
            specs_rows += f'<tr><td class="label-col">{k}</td><td class="val-col">{v}</td></tr>'
            
    # Detailed Specifications Grid
    detailed_specs = p["detailed_specs"]
    has_detailed_specs = len(detailed_specs) > 0
    detailed_specs_rows = ""
    if has_detailed_specs:
        for k, v in detailed_specs.items():
            detailed_specs_rows += f'<div class="spec-detail-item"><span class="lbl">{k}</span><span class="val">{v}</span></div>'

    # Features formatting
    features_list = p["features"]
    features_html = ""
    if features_list:
        features_html += "<h3>Key Features & Benefits:</h3><ul style='list-style-type: disc; padding-left: 20px; margin-top: 10px; display: flex; flex-direction: column; gap: 8px;'>"
        for f in features_list:
            features_html += f"<li>{f}</li>"
        features_html += "</ul>"
    else:
        features_html = f"<p>{p['description']}</p>"

    # Applications formatting
    apps_text = p.get("applications", "")
    if not apps_text:
        # Fallback to specs_table "Application" value
        specs_table_dict = p.get("specs_table", {})
        if "Application" in specs_table_dict:
            apps_text = f"This product is widely used in the following applications: {specs_table_dict['Application']}."
            
    apps_html = ""
    if apps_text:
        # split by newline if present
        lines = [line.strip() for line in apps_text.split('\n') if line.strip()]
        if len(lines) > 1:
            apps_html += "<ul style='list-style-type: disc; padding-left: 20px; display: flex; flex-direction: column; gap: 8px;'>"
            for line in lines:
                apps_html += f"<li>{line}</li>"
            apps_html += "</ul>"
        else:
            apps_html = f"<p>{apps_text}</p>"
    else:
        apps_html = "<p>Standard industrial applications. Please consult our technical experts for formulation guidelines.</p>"

    # Render product details section
    detail_content = prod_detail_tpl
    detail_content = detail_content.replace("{{product_name}}", p_name)
    detail_content = detail_content.replace("{{product_name_url}}", urllib.parse.quote(p_name))
    detail_content = detail_content.replace("{{category}}", category)
    detail_content = detail_content.replace("{{description}}", clean_weblink_boilerplate(p["description"], p_name))
    detail_content = detail_content.replace("{{main_image}}", main_image)
    
    # Thumbnails hook
    if has_thumbs:
        detail_content = re.sub(r'{% if has_thumbs %}(.*?){% endif %}', r'\1', detail_content, flags=re.DOTALL)
        detail_content = re.sub(r'{% for thumb in thumbs %}.*?{% endfor %}', thumbs_html, detail_content, flags=re.DOTALL)
    else:
        detail_content = re.sub(r'{% if has_thumbs %}.*?{% endif %}', '', detail_content, flags=re.DOTALL)
        
    # Specs table hook
    if has_specs:
        detail_content = re.sub(r'{% if has_specs %}(.*?){% endif %}', r'\1', detail_content, flags=re.DOTALL)
        detail_content = re.sub(r'{% for spec_key, spec_val in specs.items\(\) %}.*?{% endfor %}', specs_rows, detail_content, flags=re.DOTALL)
    else:
        detail_content = re.sub(r'{% if has_specs %}.*?{% endif %}', '', detail_content, flags=re.DOTALL)
        
    # Detailed Specs grid hook
    if has_detailed_specs:
        detailed_specs_html = '<div class="specs-detail-grid">' + detailed_specs_rows + '</div>'
    else:
        detailed_specs_html = '<p style="color: var(--text-muted); font-style: italic;">Detailed specifications are available upon request. Please contact us.</p>'
        
    detail_content = detail_content.replace("{{detailed_specs_html}}", detailed_specs_html)

    detail_content = detail_content.replace("{{features_html}}", features_html)
    detail_content = detail_content.replace("{{applications_html}}", apps_html)

    # Wrap in master layout
    final_html = render_page(
        content=detail_content,
        title=p["title"],
        desc=p["meta_description"],
        keywords=p["meta_keywords"],
        active_menu="products"
    )
    
    # Save the file (e.g. oleic-fatty-acid.htm)
    # Ensure the file is saved directly into the base directory
    output_path = os.path.join(base_dir, filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
    print(f"Generated product file: {filename}")

# ==========================================
# 2. BUILD PRODUCTS CATALOG PAGE (products.htm)
# ==========================================
print("\nGenerating catalog page products.htm...")
# Build products catalog grid HTML
products_grid_html = ""
for p in products:
    p_name = p["product_name"]
    category = p["category"]
    filename = p["link"].split('/')[-1]
    cat_slug = get_cat_slug(category)
    img_list = p["images"]
    main_image = img_list[0] if img_list else "images/product/default.webp"
    
    # Check for best sellers or limited stock tags
    badge_html = ""
    p_name_lower = p_name.lower()
    if "soya lecithin" in p_name_lower or "oleic" in p_name_lower:
        badge_html = '<span class="product-badge">Bestseller</span>'
    elif "akd" in p_name_lower:
        badge_html = '<span class="product-badge">Popular</span>'
        
    products_grid_html += f'''
      <div class="product-card" data-category="{cat_slug}">
        <div class="product-image">
          {badge_html}
          <img src="{main_image}" alt="{p_name}" loading="lazy">
        </div>
        <div class="product-info">
          <div>
            <span class="product-cat">{category}</span>
            <h3 class="product-title"><a href="{filename}">{p_name}</a></h3>
            <p class="product-desc">{clean_weblink_boilerplate(p["description"], p_name)}</p>
          </div>
          <div class="product-actions">
            <a href="{filename}" class="btn btn-secondary btn-sm" style="flex: 1; font-size: 13px; padding: 8px 12px;">Details</a>
            <a href="https://wa.me/919215660695?text=Hi%20Santosh%20Polymers,%20I'm%20interested%20in%20buying%20{urllib.parse.quote(p_name)}." target="_blank" class="btn btn-primary btn-sm" style="flex: 1; font-size: 13px; padding: 8px 12px;">Enquire</a>
          </div>
        </div>
      </div>
    '''

# Read products source page
src_products_path = os.path.join(base_dir, "src", "products.html")
with open(src_products_path, 'r', encoding='utf-8') as f:
    src_products_content = f.read()

# Replace placeholder
products_content = src_products_content.replace("{{products_grid_html}}", products_grid_html)

# Wrap in master layout
products_html = render_page(
    content=products_content,
    title="Products Catalog | Oleochemicals, Paper Sizing, Packaging Trays",
    desc="Browse our extensive range of high-quality oleochemicals, distilled fatty acids, paper chemicals, essential oils, and packaging products manufactured in Haryana, India.",
    keywords="oleic fatty acid, distilled palm fatty acid, akd wax emulsion, corrugated boxes, pulp egg trays, soya lecithin",
    active_menu="products"
)

# Save products.htm
with open(os.path.join(base_dir, "products.htm"), 'w', encoding='utf-8') as f:
    f.write(products_html)
print("Generated core page: products.htm")

# ==========================================
# 3. BUILD OTHER CORE PAGES
# ==========================================
core_pages = [
    {
        "src": "index.html",
        "dest": "index.html",
        "title": "Santosh Polymers | Oleochemicals & Packaging Manufacturer India",
        "desc": "Leading manufacturer and supplier of Oleochemicals, Distilled Fatty Acids, Soya Lecithin, Paper Chemicals (AKD Emulsion, DSR), and eco-friendly Pulp Packaging Trays in Kurukshetra, Haryana.",
        "keywords": "oleic fatty acid, distilled palm fatty acid, liquid soya lecithin, corrugated boxes, pulp egg trays, haryana, india",
        "menu": "home"
    },
    {
        "src": "about-us.html",
        "dest": "about-us.htm",
        "title": "About Us | Santosh Polymers Kurukshetra Haryana",
        "desc": "Discover Santosh Polymers' history since 1997, our team leaders, state-of-the-art chemical manufacturing infrastructure, and our commitment to sustainable packaging and high-purity oleochemicals.",
        "keywords": "about company, founders, history, values, kurukshetra, haryana",
        "menu": "about"
    },
    {
        "src": "industries-we-serve.html",
        "dest": "industries-we-serve.htm",
        "title": "Industries We Serve | Santosh Polymers",
        "desc": "We supply specialty chemicals, distilled fatty acids, and eco-friendly packaging boxes to the Paint, Biodiesel fuel, Pharmaceutical, Petrochemical, and Plastic & Resin industries.",
        "keywords": "paint industry, biodiesel, pharmaceutical, petrochemical, resins, packaging",
        "menu": "industries"
    },
    {
        "src": "contact-us.html",
        "dest": "contact-us.htm",
        "title": "Contact Us | Santosh Polymers Ladwa Kurukshetra",
        "desc": "Contact Mr. Ankur Goel or our technical sales team for sample requests, chemical formulation assistance, or commercial wholesale pricing on oleochemicals and pulp packaging.",
        "keywords": "contact address, phone, email, google map, office location, ladwa",
        "menu": "contact"
    }
]

import re

for page in core_pages:
    src_path = os.path.join(base_dir, "src", page["src"])
    with open(src_path, 'r', encoding='utf-8') as f:
        src_content = f.read()
        
    final_html = render_page(
        content=src_content,
        title=page["title"],
        desc=page["desc"],
        keywords=page["keywords"],
        active_menu=page["menu"]
    )
    
    dest_path = os.path.join(base_dir, page["dest"])
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
    print(f"Generated core page: {page['dest']}")

print("\n--- ALL PAGES GENERATED SUCCESSFULLY ---")
