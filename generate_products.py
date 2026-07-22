import os
import json
import urllib.parse
import re

base_dir = os.path.dirname(os.path.abspath(__file__))
products_json_path = os.path.join(base_dir, "products_full.json")
layout_path = os.path.join(base_dir, "templates", "layout.html")
prod_detail_template_path = os.path.join(base_dir, "templates", "product_detail.html")

# Read database
with open(products_json_path, 'r', encoding='utf-8-sig') as f:
    products = json.load(f)

# Read layout
with open(layout_path, 'r', encoding='utf-8-sig') as f:
    layout_tpl = f.read()

# Read product detail template
with open(prod_detail_template_path, 'r', encoding='utf-8-sig') as f:
    prod_detail_tpl = f.read()

# Read inner banner template
inner_banner_path = os.path.join(base_dir, "templates", "inner_banner.html")
with open(inner_banner_path, 'r', encoding='utf-8-sig') as f:
    inner_banner_tpl = f.read()

def render_banner(eyebrow, title, description, breadcrumbs, bg_image, stats_html=""):
    crumbs_html = '<a href="/">Home</a>'
    for label, url in breadcrumbs:
        crumbs_html += ' <span>&rsaquo;</span> '
        if url:
            crumbs_html += f'<a href="{url}">{label}</a>'
        else:
            crumbs_html += f'<span>{label}</span>'
            
    html = inner_banner_tpl
    html = html.replace("{{banner_eyebrow}}", eyebrow)
    html = html.replace("{{banner_title}}", title)
    html = html.replace("{{banner_description}}", description)
    html = html.replace("{{banner_breadcrumbs}}", crumbs_html)
    html = html.replace("{{banner_bg_image}}", bg_image)
    html = html.replace("{{banner_stats_html}}", stats_html)
    return html


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

default_org_schema = """  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "Santosh Polymers",
    "url": "https://santoshpolymers.com",
    "logo": "https://santoshpolymers.com/images/logo_3.webp",
    "contactPoint": {
      "@type": "ContactPoint",
      "telephone": "+91-9215660695",
      "contactType": "sales",
      "email": "info@santoshpolymers.com",
      "availableLanguage": ["en", "hi"]
    },
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "Vill. Gharaula, Ladwa",
      "addressLocality": "Kurukshetra",
      "addressRegion": "Haryana",
      "postalCode": "136132",
      "addressCountry": "IN"
    },
    "sameAs": [
      "https://www.indiamart.com/santosh-polymers-ladwa/",
      "https://wa.me/919215660695"
    ]
  }
  </script>"""

# Helper to render base layout
def render_page(content, title, desc, keywords, active_menu="home", canonical_url="", schema_script=""):
    page = layout_tpl
    page = page.replace("{{title}}", title)
    page = page.replace("{{meta_description}}", desc)
    page = page.replace("{{meta_keywords}}", keywords)
    
    if not canonical_url:
        canonical_url = "https://santoshpolymers.com/"
    page = page.replace("{{canonical_url}}", canonical_url)
    
    if not schema_script:
        schema_script = default_org_schema
    page = page.replace("{{schema_script}}", schema_script)
    
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
print(f"Generating {len(products)} product detail pages...")
for p in products:
    p_name = p["product_name"]
    category = p["category"]
    filename = p["link"].split('/')[-1] # e.g. akd-wax-emulsion.htm
    dir_name = filename.replace('.htm', '') # e.g. akd-wax-emulsion
    
    # Format images with root-relative paths
    img_list = p["images"]
    main_image = "/" + img_list[0] if img_list else "/images/product/default.webp"
    
    # Dynamic image alt text
    main_image_alt = f"High purity {p_name} manufactured by Santosh Polymers in India for industrial use"
    
    # Thumbnails formatting
    has_thumbs = len(img_list) > 1
    thumbs_html = ""
    if has_thumbs:
        for idx, img in enumerate(img_list):
            active_class = "active" if idx == 0 else ""
            thumbs_html += f'<div class="gallery-thumb {active_class}" data-large="/{img}"><img src="/{img}" alt="High quality {p_name} thumbnail view {idx+1} - Santosh Polymers" loading="lazy"></div>'
            
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
          <img src="/{r_img}" alt="{r_name} manufacturer India - Santosh Polymers" loading="lazy">
        </div>
        <div class="related-product-info">
          <h4>{r_name}</h4>
          <a href="{r_url}" class="btn btn-secondary btn-xs card-link-stretched">View Product</a>
        </div>
      </div>
        '''

    # Slice first sentence of description for inner banner supporting text
    desc_clean = clean_weblink_boilerplate(p["description"], p_name)
    first_sentence = desc_clean.split('.')[0].strip() + '.' if '.' in desc_clean else desc_clean
    # Ensure it's not too long
    if len(first_sentence) > 160:
        first_sentence = first_sentence[:157] + "..."
        
    pdp_breadcrumbs = [("Products", "/products"), (category, f"/products#{get_cat_slug(category)}")]
    # Note: main_image is already absolute-path structured like '/images/product/xxx'
    # For css url('...'), it is fine to keep the leading slash
    pdp_banner_html = render_banner(
        eyebrow=category,
        title=p_name,
        description=first_sentence,
        breadcrumbs=pdp_breadcrumbs,
        bg_image=main_image,
        stats_html='<div class="hero-stats-badge"><span class="pulse-dot"></span><span>Premium Industrial Grade</span></div>'
    )

    # Render product details section
    detail_content = prod_detail_tpl
    detail_content = detail_content.replace("{{unified_banner_html}}", pdp_banner_html)
    detail_content = detail_content.replace("{{product_name}}", p_name)
    detail_content = detail_content.replace("{{product_name_url}}", urllib.parse.quote(p_name))
    detail_content = detail_content.replace("{{category}}", category)
    detail_content = detail_content.replace("{{category_slug}}", get_cat_slug(category))
    detail_content = detail_content.replace("{{description}}", desc_clean)
    detail_content = detail_content.replace("{{main_image}}", main_image)
    detail_content = detail_content.replace("{{main_image_alt}}", main_image_alt)
    
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

    # Generate Product & BreadcrumbList Schemas
    p_img_url = f"https://santoshpolymers.com{main_image}"
    p_url = f"https://santoshpolymers.com/{dir_name}/"
    cat_slug = get_cat_slug(category)
    
    prod_schema_dict = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": p_name,
        "image": p_img_url,
        "description": desc_clean,
        "category": category,
        "offers": {
            "@type": "Offer",
            "availability": "https://schema.org/InStock",
            "seller": {
                "@type": "Organization",
                "name": "Santosh Polymers",
                "url": "https://santoshpolymers.com"
            }
        },
        "manufacturer": {
            "@type": "Organization",
            "name": "Santosh Polymers",
            "url": "https://santoshpolymers.com",
            "logo": "https://santoshpolymers.com/images/logo_3.webp"
        }
    }
    
    breadcrumb_schema_dict = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Home",
                "item": "https://santoshpolymers.com"
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": "Products",
                "item": "https://santoshpolymers.com/products"
            },
            {
                "@type": "ListItem",
                "position": 3,
                "name": category,
                "item": f"https://santoshpolymers.com/products#{cat_slug}"
            },
            {
                "@type": "ListItem",
                "position": 4,
                "name": p_name,
                "item": p_url
            }
        ]
    }
    
    pdp_schema_script = f"""  <script type="application/ld+json">
  {json.dumps(prod_schema_dict, indent=2)}
  </script>
  <script type="application/ld+json">
  {json.dumps(breadcrumb_schema_dict, indent=2)}
  </script>"""

    # Wrap in master layout
    final_html = render_page(
        content=detail_content,
        title=p["title"],
        desc=p["meta_description"],
        keywords=p["meta_keywords"],
        active_menu="products",
        canonical_url=p_url,
        schema_script=pdp_schema_script
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
        main_image = "/" + img_list[0] if img_list else "/images/product/default.webp"
        
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
          <img src="{main_image}" alt="{p_name} manufacturer India - Santosh Polymers" loading="lazy">
        </div>
        <div class="featured-info">
          <div>
            <div class="featured-tags">
              {segments_html}
              <span class="tag-subtype">{sub_type}</span>
              <span class="tag-form">{form_label}</span>
            </div>
            <h3 class="featured-title"><a href="{clean_url}" class="card-link-stretched">{p_name}</a></h3>
            <p class="featured-desc">{clean_weblink_boilerplate(p["description"], p_name)}</p>
          </div>
          <div class="featured-actions" style="position: relative; z-index: 2;">
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
          <img src="{main_image}" alt="{p_name} manufacturer India - Santosh Polymers" loading="lazy">
        </div>
        <div class="featured-info">
          <div>
            <h3 class="featured-title" style="margin-top: 10px;"><a href="{clean_url}" class="card-link-stretched">{p_name}</a></h3>
            <p class="featured-desc">{clean_weblink_boilerplate(p["description"], p_name)}</p>
          </div>
          <div class="featured-actions" style="position: relative; z-index: 2;">
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
    cat_slug = get_cat_slug(p["category"])
    
    img_list = p["images"]
    main_image = "/" + img_list[0] if img_list else "/images/product/default.webp"
    
    segments_html = make_segment_badges(segments)
    
    products_grid_html += f'''
      <div class="product-card" data-category="{cat_slug}" data-segments="{segments_str}" data-form="{form_val}">
        <div class="product-image">
          <img src="{main_image}" alt="{p_name} supplier in India - Santosh Polymers" loading="lazy">
        </div>
        <div class="product-info">
          <div>
            <h3 class="product-title"><a href="{clean_url}" class="card-link-stretched">{p_name}</a></h3>
            <p class="product-desc">{clean_weblink_boilerplate(p["description"], p_name)}</p>
          </div>
          <div class="product-actions" style="position: relative; z-index: 2;">
            <a href="{clean_url}" class="btn btn-secondary btn-sm" style="flex: 1; font-size: 13px; padding: 8px 12px;">Details</a>
            <a href="https://wa.me/919215660695?text=Hi%20Santosh,%20I'm%20interested%20in%20buying%20{urllib.parse.quote(p_name)}." target="_blank" class="btn btn-primary btn-sm" style="flex: 1; font-size: 13px; padding: 8px 12px;">Enquire</a>
          </div>
        </div>
      </div>
    '''

# Read products source page
src_products_path = os.path.join(base_dir, "src", "products.html")
with open(src_products_path, 'r', encoding='utf-8-sig') as f:
    src_products_content = f.read()

# Replace placeholders
products_content = src_products_content.replace("{{featured_products_html}}", featured_products_no_labels_html)
products_content = products_content.replace("{{products_grid_html}}", products_grid_html)

products_banner_html = render_banner(
    eyebrow="Our Catalog",
    title="Industrial Specialty Chemicals",
    description="High-performance oleochemicals, distilled fatty acids, paper chemicals, and packaging solutions.",
    breadcrumbs=[("Products", "")],
    bg_image="/images/slider/3.webp",
    stats_html=f'<div class="hero-stats-badge"><span class="pulse-dot"></span><span>{len(products)} Specialty Products across 5 Industries</span></div>'
)
products_content = products_content.replace("{{unified_banner_html}}", products_banner_html)

# Breadcrumb schema for catalog page
products_breadcrumbs_schema = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
        {
            "@type": "ListItem",
            "position": 1,
            "name": "Home",
            "item": "https://santoshpolymers.com"
        },
        {
            "@type": "ListItem",
            "position": 2,
            "name": "Products",
            "item": "https://santoshpolymers.com/products"
        }
    ]
}
products_schema_script = f"""  <script type="application/ld+json">
  {json.dumps(products_breadcrumbs_schema, indent=2)}
  </script>"""

# Wrap in master layout
products_html = render_page(
    content=products_content,
    title="Pulp Moulded Trays Manufacturers and Suppliers from Kurukshetra India | Santosh Polymers",
    desc="Santosh Polymers are the leading Manufacturer & Supplier of Pulp Moulded Trays in Kurukshetra, Wholesale Corrugated Packaging Boxes, Pulp Moulded Trays trader in Haryana India.",
    keywords="pulp moulded trays manufacturer in kurukshetra, corrugated packaging boxes producer, pulp moulded trays manufacturer in haryana, wholesale corrugated packaging boxes supplier india, pulp moulded trays manufacturing company haryana india",
    active_menu="products",
    canonical_url="https://santoshpolymers.com/products/",
    schema_script=products_schema_script
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
        "title": "Santosh Polymers - Liquid Soya Lecithin Manufacturer Supplier from Kurukshetra",
        "desc": "Santosh Polymers are the leading Manufacturer and Supplier of Liquid Soya Lecithin in Kurukshetra, Wholesale Corrugated Packaging Boxes, Liquid Soya Lecithin trader in Haryana.",
        "keywords": "liquid soya lecithin manufacturer in kurukshetra, corrugated packaging boxes producer, liquid soya lecithin manufacturer in haryana, wholesale corrugated packaging boxes supplier india, liquid soya lecithin manufacturing company haryana india",
        "menu": "home",
        "canonical": "https://santoshpolymers.com/"
    },
    {
        "src": "about-us.html",
        "dest": "about-us",
        "title": "Santosh Polymers Kurukshetra, India | About Us",
        "desc": "Santosh Polymers, Kurukshetra, Haryana, India - Manufacturer & supplier of  manufacturer Kurukshetra, wholesale Poultry Feed Oil supplier,  manufacturer in Kurukshetra, India.",
        "keywords": "santosh polymers in kurukshetra,  manufacturer kurukshetra, poultry feed oil manufacturer india,  manufacturer, wholesale pulp moulded trays supplier,  supplier kurukshetra",
        "menu": "about",
        "canonical": "https://santoshpolymers.com/about-us/"
    },
    {
        "src": "industries-we-serve.html",
        "dest": "industries",
        "title": "Industries We Serve - Santosh Polymers from Kurukshetra Haryana India",
        "desc": "Industries We Serve - Santosh Polymers are one of the leading Manufacturer & Supplier in Kurukshetra Haryana India.",
        "keywords": "industries we serve santosh polymers, santosh polymers in kurukshetra, santosh polymers manufacturer & supplier, santosh polymers in haryana, industries we serve santosh polymers in india",
        "menu": "industries",
        "canonical": "https://santoshpolymers.com/industries/"
    },
    {
        "src": "contact-us.html",
        "dest": "contact-us",
        "title": "Contact to Santosh Polymers Kurukshetra India - Manufacturers and Suppliers",
        "desc": "Contact to best Distilled Palm Fatty Acid Manufacturing & Supplying Company in Kurukshetra - Wholesaler of Akd Wax Emulsion in Kurukshetra Manufacturing Company in India.",
        "keywords": "contact distilled palm fatty acid manufacturer in kurukshetra, contact to manufacturer of akd wax emulsion in kurukshetra, distilled rice fatty acid manufacturer, distilled palm fatty acid manufacturer in haryana, akd wax emulsion manufacturing company in india",
        "menu": "contact",
        "canonical": "https://santoshpolymers.com/contact-us/"
    }
]

for page in core_pages:
    src_path = os.path.join(base_dir, "src", page["src"])
    with open(src_path, 'r', encoding='utf-8-sig') as f:
        src_content = f.read()
        
    page_schema = ""
    
    if page["src"] == "index.html":
        src_content = src_content.replace("{{featured_products_html}}", featured_products_no_labels_html)
        # Homepage gets standard Organization schema
        page_schema = default_org_schema
    else:
        # Other pages get BreadcrumbList schema
        page_title_short = page["title"].split('|')[0].strip()
        bc_schema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Home",
                    "item": "https://santoshpolymers.com"
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": page_title_short,
                    "item": page["canonical"]
                }
            ]
        }
        page_schema = f"""  <script type="application/ld+json">
  {json.dumps(bc_schema, indent=2)}
  </script>"""

    if page["src"] == "about-us.html":
        pass  # About-us has its own static banner â€” no unified banner injection needed
    elif page["src"] == "industries-we-serve.html":
        banner_html = render_banner(
            eyebrow="Key Verticals",
            title="Industries We Serve",
            description="High-performance oleochemicals, paper chemicals, and packaging solutions powering six core industries across India.",
            breadcrumbs=[("Industries We Serve", "")],
            bg_image="/images/slider/3.webp",
            stats_html='''
            <div class="banner-stats-container">
              <div class="banner-stat-box"><span class="pulse-dot"></span><span>6 Core Sectors Supported</span></div>
            </div>
            '''
        )
        src_content = src_content.replace("{{unified_banner_html}}", banner_html)
    elif page["src"] == "contact-us.html":
        banner_html = render_banner(
            eyebrow="Get In Touch",
            title="Talk to Our Technical Sales Team",
            description="Have an industrial scale inquiry or custom chemical requirements? Reach out to our engineers and sales team for direct assistance.",
            breadcrumbs=[("Contact Us", "")],
            bg_image="/images/slider/2.webp",
            stats_html='''
            <div class="banner-stats-container">
              <div class="banner-stat-box"><span class="pulse-dot"></span><span>Average Response Time: &lt; 2 Hours</span></div>
            </div>
            '''
        )
        src_content = src_content.replace("{{unified_banner_html}}", banner_html)
        
    final_html = render_page(
        content=src_content,
        title=page["title"],
        desc=page["desc"],
        keywords=page["keywords"],
        active_menu=page["menu"],
        canonical_url=page["canonical"],
        schema_script=page_schema
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

# ==========================================
# 4. GENERATE SITEMAP (sitemap.xml)
# ==========================================
print("\nGenerating sitemap.xml...")
sitemap_path = os.path.join(base_dir, "sitemap.xml")

sitemap_urls = []
# Homepage
sitemap_urls.append({
    "loc": "https://santoshpolymers.com/",
    "changefreq": "daily",
    "priority": "1.0"
})

# Core pages
core_paths = ["products/", "about-us/", "industries/", "contact-us/"]
for cp in core_paths:
    sitemap_urls.append({
        "loc": f"https://santoshpolymers.com/{cp}",
        "changefreq": "weekly",
        "priority": "0.8"
    })
    
# Product detail pages
for p in products:
    filename = p["link"].split('/')[-1]
    dir_name = filename.replace('.htm', '')
    sitemap_urls.append({
        "loc": f"https://santoshpolymers.com/{dir_name}/",
        "changefreq": "weekly",
        "priority": "0.9"
    })
    
sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

for u in sitemap_urls:
    sitemap_xml += '  <url>\n'
    sitemap_xml += f'    <loc>{u["loc"]}</loc>\n'
    sitemap_xml += f'    <changefreq>{u["changefreq"]}</changefreq>\n'
    sitemap_xml += f'    <priority>{u["priority"]}</priority>\n'
    sitemap_xml += '  </url>\n'
    
sitemap_xml += '</urlset>\n'

with open(sitemap_path, 'w', encoding='utf-8') as f:
    f.write(sitemap_xml)
print("Generated sitemap.xml successfully!")

print("\n--- ALL PAGES GENERATED SUCCESSFULLY ---")
