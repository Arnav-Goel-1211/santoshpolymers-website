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
    filename = p["link"].split('/')[-1] # e.g. akd-wax-emulsion.htm
    dir_name = filename.replace('.htm', '') # e.g. akd-wax-emulsion
    
    # Format images with root-relative paths
    img_list = p["images"]
    main_image = "/" + img_list[0] if img_list else "/images/product/default.webp"
    
    # Thumbnails formatting
    has_thumbs = len(img_list) > 1
    thumbs_html = ""
    if has_thumbs:
        for idx, img in enumerate(img_list):
            active_class = "active" if idx == 0 else ""
            thumbs_html += f'<div class="gallery-thumb {active_class}" data-large="/{img}"><img src="/{img}" alt="{p_name} Thumb"></div>'
            
    # Build Unified Spec Card
    unified_fields = [
        "Business Type", "Form", "Color", "Purity", "Shelf Life", 
        "Country of Origin", "Type", "Material"
    ]
    
    all_specs = {}
    if "specs_table" in p:
        for k, v in p["specs_table"].items():
            all_specs[k.lower().strip()] = (k, v)
    if "detailed_specs" in p:
        for k, v in p["detailed_specs"].items():
            all_specs[k.lower().strip()] = (k, v)
            
    unified_spec_rows = ""
    used_keys = set()
    for field in unified_fields:
        field_key = field.lower()
        matching_key = None
        if field_key == "form" and "form" in all_specs:
            matching_key = "form"
        elif field_key == "form" and "physical form" in all_specs:
            matching_key = "physical form"
        else:
            for k in all_specs:
                if field_key in k:
                    matching_key = k
                    break
        
        if matching_key and matching_key in all_specs:
            k_orig, v = all_specs[matching_key]
            # Exclude Application field
            if "application" not in k_orig.lower():
                unified_spec_rows += f'<div class="pdp-spec-item"><span class="pdp-spec-lbl">{k_orig}</span><span class="pdp-spec-val">{v}</span></div>'
                used_keys.add(matching_key)
            
    if not unified_spec_rows:
        unified_spec_rows = '<div class="pdp-spec-item"><span class="pdp-spec-lbl">Business Type</span><span class="pdp-spec-val">Manufacturer &amp; Supplier</span></div>'
        
    # Detailed Specifications Grid (Deduplicated - only show unused fields)
    detailed_spec_rows = ""
    for k in all_specs:
        if k in used_keys:
            continue
        if "application" in k:
            continue
        k_orig, v = all_specs[k]
        detailed_spec_rows += f'<div class="spec-detail-item"><span class="lbl">{k_orig}</span><span class="val">{v}</span></div>'
        
    if detailed_spec_rows:
        detailed_specs_html = '<div class="specs-detail-grid">' + detailed_spec_rows + '</div>'
    else:
        detailed_specs_html = '<p style="color: var(--text-muted); font-style: italic;">Detailed specifications are available upon request. Please contact our technical team.</p>'

    # Features formatting with icon bullets
    features_list = p["features"]
    features_html = ""
    if features_list:
        features_html += '<ul class="pdp-features-list">'
        for f in features_list:
            features_html += f'''
          <li>
            <svg class="feature-bullet-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
            <span>{f}</span>
          </li>
            '''
        features_html += "</ul>"
    else:
        features_html = f"<p>{clean_weblink_boilerplate(p['description'], p_name)}</p>"

    # Applications formatting
    apps_text = p.get("applications", "")
    if not apps_text:
        # Fallback to specs_table "Application" value
        specs_table_dict = p.get("specs_table", {})
        if "Application" in specs_table_dict:
            apps_text = f"This product is widely used in the following applications: {specs_table_dict['Application']}."
            
    apps_html = ""
    if apps_text:
        lines = [line.strip() for line in apps_text.split('\n') if line.strip()]
        if len(lines) > 1:
            apps_html += '<ul class="pdp-features-list">'
            for line in lines:
                apps_html += f'''
              <li>
                <svg class="feature-bullet-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 22 8.5 22 15.5 12 22 2 15.5 2 8.5 12 2"></polygon><polyline points="2 8.5 12 15 22 8.5"></polyline><polyline points="12 22 12 15"></polyline></svg>
                <span>{line}</span>
              </li>
                '''
            apps_html += "</ul>"
        else:
            apps_html = f"<p>{apps_text}</p>"
    else:
        apps_html = "<p>Standard industrial applications. Please consult our technical experts for formulation guidelines.</p>"

    # Contextual Related Products (3 items from same category)
    related_list = []
    for other in products:
        if other["product_name"] != p_name and other["category"] == category:
            related_list.append(other)
    if len(related_list) < 3:
        for other in products:
            if other["product_name"] != p_name and other not in related_list:
                related_list.append(other)
    related_list = related_list[:3]
    
    related_products_html = ""
    for r in related_list:
        r_name = r["product_name"]
        r_filename = r["link"].split('/')[-1]
        r_dir_name = r_filename.replace('.htm', '')
        r_url = f"/{r_dir_name}/"
        r_img = r["images"][0] if r["images"] else "images/product/default.webp"
        
        related_products_html += f'''
      <div class="related-product-card">
        <div class="related-product-img">
          <img src="/{r_img}" alt="{r_name}" loading="lazy">
        </div>
        <div class="related-product-info">
          <h4>{r_name}</h4>
          <a href="{r_url}" class="btn btn-secondary btn-xs">View Product</a>
        </div>
      </div>
        '''

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
        
    detail_content = detail_content.replace("{{unified_spec_card_html}}", unified_spec_rows)
    detail_content = detail_content.replace("{{detailed_specs_html}}", detailed_specs_html)
    detail_content = detail_content.replace("{{features_html}}", features_html)
    detail_content = detail_content.replace("{{applications_html}}", apps_html)
    detail_content = detail_content.replace("{{related_products_html}}", related_products_html)

    # Wrap in master layout
    final_html = render_page(
        content=detail_content,
        title=p["title"],
        desc=p["meta_description"],
        keywords=p["meta_keywords"],
        active_menu="products"
    )
    
    # Save as directory/index.html for clean URLs (e.g. /oleic-fatty-acid/)
    output_dir = os.path.join(base_dir, dir_name)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "index.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
    print(f"Generated product: {dir_name}/")

# ==========================================
# 2. BUILD PRODUCTS CATALOG PAGE (products.htm)
# ==========================================
print("\nGenerating catalog page products.htm...")

def make_segment_badges(segments):
    seg_map = {
        "personal-care": "Personal Care & Cosmetics",
        "paints-coatings": "Paints Coatings & Inks",
        "paper-pulp": "Paper & Pulp",
        "agri-food": "Agri & Food",
        "rubber-plastics": "Rubber & Plastics"
    }
    badges = []
    for s in segments:
        if s in seg_map:
            badges.append(f'<span class="tag-segment tag-{s}">{seg_map[s]}</span>')
    return "".join(badges)

# Build Featured Products Row HTML (from featured flag)
featured_products_html = ""
featured_products_no_labels_html = ""
for p in products:
    if p.get("featured", False):
        p_name = p["product_name"]
        filename = p["link"].split('/')[-1]
        dir_name = filename.replace('.htm', '')
        clean_url = f"/{dir_name}"
        img_list = p["images"]
        main_image = img_list[0] if img_list else "images/product/default.webp"
        
        segments_html = make_segment_badges(p.get("market_segments", []))
        sub_type = p.get("sub_type", "Specialty")
        form_label = p.get("physical_form", "N/A")
        
        # Determine featured badge (Bestseller vs Popular)
        f_badge = "Bestseller"
        if "akd" in p_name.lower():
            f_badge = "Popular"
            
        featured_products_html += f'''
      <div class="featured-card">
        <div class="featured-image">
          <span class="featured-badge">{f_badge}</span>
          <img src="{main_image}" alt="{p_name}" loading="lazy">
        </div>
        <div class="featured-info">
          <div>
            <div class="featured-tags">
              {segments_html}
              <span class="tag-subtype">{sub_type}</span>
              <span class="tag-form">{form_label}</span>
            </div>
            <h3 class="featured-title"><a href="{clean_url}">{p_name}</a></h3>
            <p class="featured-desc">{clean_weblink_boilerplate(p["description"], p_name)}</p>
          </div>
          <div class="featured-actions">
            <a href="{clean_url}" class="btn btn-secondary btn-sm" style="flex: 1; font-size: 13px; padding: 8px 12px;">Details</a>
            <a href="https://wa.me/919215660695?text=Hi%20Santosh,%20I'm%20interested%20in%20buying%20{urllib.parse.quote(p_name)}." target="_blank" class="btn btn-primary btn-sm" style="flex: 1; font-size: 13px; padding: 8px 12px;">Enquire</a>
          </div>
        </div>
      </div>
        '''

        # Version without badges or tags
        featured_products_no_labels_html += f'''
      <div class="featured-card">
        <div class="featured-image">
          <img src="{main_image}" alt="{p_name}" loading="lazy">
        </div>
        <div class="featured-info">
          <div>
            <h3 class="featured-title" style="margin-top: 10px;"><a href="{clean_url}">{p_name}</a></h3>
            <p class="featured-desc">{clean_weblink_boilerplate(p["description"], p_name)}</p>
          </div>
          <div class="featured-actions">
            <a href="{clean_url}" class="btn btn-secondary btn-sm" style="flex: 1; font-size: 13px; padding: 8px 12px;">Details</a>
            <a href="https://wa.me/919215660695?text=Hi%20Santosh,%20I'm%20interested%20in%20buying%20{urllib.parse.quote(p_name)}." target="_blank" class="btn btn-primary btn-sm" style="flex: 1; font-size: 13px; padding: 8px 12px;">Enquire</a>
          </div>
        </div>
      </div>
        '''

# Build products catalog grid HTML
products_grid_html = ""
for p in products:
    p_name = p["product_name"]
    filename = p["link"].split('/')[-1]
    dir_name = filename.replace('.htm', '')
    clean_url = f"/{dir_name}"
    
    segments = p.get("market_segments", [])
    segments_str = ",".join(segments)
    sub_type = p.get("sub_type", "Specialty")
    form_val = p.get("physical_form", "N/A")
    
    img_list = p["images"]
    main_image = img_list[0] if img_list else "images/product/default.webp"
    
    segments_html = make_segment_badges(segments)
    
    products_grid_html += f'''
      <div class="product-card" data-segments="{segments_str}" data-form="{form_val}">
        <div class="product-image">
          <img src="{main_image}" alt="{p_name}" loading="lazy">
        </div>
        <div class="product-info">
          <div>
            <div class="product-tags">
              {segments_html}
              <span class="tag-subtype">{sub_type}</span>
            </div>
            <h3 class="product-title"><a href="{clean_url}">{p_name}</a></h3>
            <p class="product-desc">{clean_weblink_boilerplate(p["description"], p_name)}</p>
          </div>
          <div class="product-actions">
            <a href="{clean_url}" class="btn btn-secondary btn-sm" style="flex: 1; font-size: 13px; padding: 8px 12px;">Details</a>
            <a href="https://wa.me/919215660695?text=Hi%20Santosh,%20I'm%20interested%20in%20buying%20{urllib.parse.quote(p_name)}." target="_blank" class="btn btn-primary btn-sm" style="flex: 1; font-size: 13px; padding: 8px 12px;">Enquire</a>
          </div>
        </div>
      </div>
    '''

# Read products source page
src_products_path = os.path.join(base_dir, "src", "products.html")
with open(src_products_path, 'r', encoding='utf-8') as f:
    src_products_content = f.read()

# Replace placeholders
products_content = src_products_content.replace("{{featured_products_html}}", featured_products_html)
products_content = products_content.replace("{{products_grid_html}}", products_grid_html)
products_content = products_content.replace("[PRODUCT_COUNT_CONFIRMED]", str(len(products)))

# Wrap in master layout
products_html = render_page(
    content=products_content,
    title="Products Catalog | Oleochemicals, Paper Sizing, Packaging Trays",
    desc="Browse our extensive range of high-quality oleochemicals, distilled fatty acids, paper chemicals, essential oils, and packaging products manufactured in Haryana, India.",
    keywords="oleic fatty acid, distilled palm fatty acid, akd wax emulsion, corrugated boxes, pulp egg trays, soya lecithin",
    active_menu="products"
)

# Save to products/index.html
os.makedirs(os.path.join(base_dir, "products"), exist_ok=True)
with open(os.path.join(base_dir, "products", "index.html"), 'w', encoding='utf-8') as f:
    f.write(products_html)
print("Generated core page: products/")

# ==========================================
# 3. BUILD OTHER CORE PAGES
# ==========================================
core_pages = [
    {
        "src": "index.html",
        "dest": "",
        "title": "Santosh Polymers | Oleochemicals & Packaging Manufacturer India",
        "desc": "Leading manufacturer and supplier of Oleochemicals, Distilled Fatty Acids, Soya Lecithin, Paper Chemicals (AKD Emulsion, DSR), and eco-friendly Pulp Packaging Trays in Kurukshetra, Haryana.",
        "keywords": "oleic fatty acid, distilled palm fatty acid, liquid soya lecithin, corrugated boxes, pulp egg trays, haryana, india",
        "menu": "home"
    },
    {
        "src": "about-us.html",
        "dest": "about-us",
        "title": "About Us | Santosh Polymers Kurukshetra Haryana",
        "desc": "Discover Santosh Polymers' history since 1997, our team leaders, state-of-the-art chemical manufacturing infrastructure, and our commitment to sustainable packaging and high-purity oleochemicals.",
        "keywords": "about company, founders, history, values, kurukshetra, haryana",
        "menu": "about"
    },
    {
        "src": "industries-we-serve.html",
        "dest": "industries",
        "title": "Industries We Serve | Santosh Polymers",
        "desc": "We supply specialty chemicals, distilled fatty acids, and eco-friendly packaging boxes to the Paint, Biodiesel fuel, Pharmaceutical, Petrochemical, and Plastic & Resin industries.",
        "keywords": "paint industry, biodiesel, pharmaceutical, petrochemical, resins, packaging",
        "menu": "industries"
    },
    {
        "src": "contact-us.html",
        "dest": "contact-us",
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
        
    if page["src"] == "index.html":
        src_content = src_content.replace("{{featured_products_html}}", featured_products_no_labels_html)
        
    final_html = render_page(
        content=src_content,
        title=page["title"],
        desc=page["desc"],
        keywords=page["keywords"],
        active_menu=page["menu"]
    )
    
    if page["dest"] == "":
        dest_path = os.path.join(base_dir, "index.html")
    else:
        dest_dir = os.path.join(base_dir, page["dest"])
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, "index.html")
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
    print(f"Generated core page: {'/' if page['dest'] == '' else page['dest'] + '/'}")

print("\n--- ALL PAGES GENERATED SUCCESSFULLY ---")
