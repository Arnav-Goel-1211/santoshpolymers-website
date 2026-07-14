import os

base_dir = r"c:\Users\arnav\Documents\GitHub\santoshpolymers-website"
audit_results_path = r"C:\Users\arnav\.gemini\antigravity-ide\brain\2cb7dd9f-c3c2-45ce-88b4-6c32d6822e9d\audit_results.md"
plan_path = r"C:\Users\arnav\.gemini\antigravity-ide\brain\2cb7dd9f-c3c2-45ce-88b4-6c32d6822e9d\implementation_plan.md"

with open(audit_results_path, 'r', encoding='utf-8') as f:
    audit_content = f.read()

# Strip title of audit content
audit_table_content = audit_content.replace("# SEO Product Audit & Keyword Research", "").strip()

plan_template = f"""# SEO & Product Visibility Overhaul Plan (with Email Updates)

This plan outlines the technical and on-page SEO changes for **santoshpolymers.com** to boost search visibility and qualified lead capture. It also addresses the user's secondary request to update contact email addresses.

## User Review Required

> [!IMPORTANT]
> - **Product SEO Meta Fields**: The titles and descriptions in the audit table below will be loaded directly into `products_full.json` so that the python generator propagates them to all product pages.
> - **Email Updates (Except Resend)**: We will replace `santoshpolymers.info@gmail.com` with `info@santoshpolymers.com` and `ankur.goel@santoshpolymers.com` in all layout templates, contact pages, and sticky CTAs. In the backend processors (`send_email.php` and `api/send-email.js`), the `to` field (recipient) will be updated to these new address listings, while keeping the `from` field as `onboarding@resend.dev` (the resend sender configuration).
> - **Zero Layout/Visual Impact**: Visuals, banners, layout alignments, and stats counters remain entirely unchanged.

## Proposed Changes

---

### 1. Database & Templates (On-Page SEO)

#### [MODIFY] [products_full.json](file:///{base_dir.replace('\\', '/')}/products_full.json)
- Update titles, meta descriptions, and keywords for each product to match the recommended values in the audit table below.

#### [MODIFY] [templates/layout.html](file:///{base_dir.replace('\\', '/')}/templates/layout.html)
- Add a `<link rel="canonical" href="{{{{canonical_url}}}}">` tag in the `<head>`.
- Add a homepage-specific Organization schema.
- Update contact points in the layout:
  - Header: Link email to `mailto:info@santoshpolymers.com` (and show `info@santoshpolymers.com`).
  - Mobile Menu: List both `info@santoshpolymers.com` and `ankur.goel@santoshpolymers.com`.
  - Footer Location & Links: List both email links.

#### [MODIFY] [templates/product_detail.html](file:///{base_dir.replace('\\', '/')}/templates/product_detail.html)
- Ensure the main product heading uses an `<h2>` structure where appropriate or maintains heading levels correctly (the H1 is already provided in the header banner).
- Setup JSON-LD structured data block for `Product` and `BreadcrumbList` schemas (e.g. `{{{{product_schema_json}}}}`).

#### [MODIFY] [generate_products.py](file:///{base_dir.replace('\\', '/')}/generate_products.py)
- Update dynamic variables passed to `render_page` to compute the canonical URL of the page.
- Generate dynamic, descriptive image alt text for the main gallery image and thumbnail images (e.g. `alt="High quality [Product Name] manufactured by Santosh Polymers"`).
- Generate JSON-LD `Product` and `BreadcrumbList` schema script blocks and inject them into each product page.
- Inject correct parent category canonicals and standard category tags.
- Programmatically add cross-linking references (internal links to 2-3 related products and category lists).

---

### 2. Core Pages & Sticky CTAs

#### [MODIFY] [src/contact-us.html](file:///{base_dir.replace('\\', '/')}/src/contact-us.html)
- Update displayed emails in the contact-info cards to display the new email links (`info@santoshpolymers.com` and `ankur.goel@santoshpolymers.com`).

#### [MODIFY] [src/industries-we-serve.html](file:///{base_dir.replace('\\', '/')}/src/industries-we-serve.html)
- Update the sticky CTA email mailto link to target the new emails: `mailto:info@santoshpolymers.com,ankur.goel@santoshpolymers.com`.

---

### 3. Backend Enquiries (Recipient Email Updates)

#### [MODIFY] [api/send-email.js](file:///{base_dir.replace('\\', '/')}/api/send-email.js)
- Update the recipient `to` field:
  ```javascript
  to: ["info@santoshpolymers.com", "ankur.goel@santoshpolymers.com"],
  ```
- Keep the `from` field as `"onboarding@resend.dev"` as required by Resend constraints.

#### [MODIFY] [send_email.php](file:///{base_dir.replace('\\', '/')}/send_email.php)
- Update the recipient `to` field:
  ```php
  "to" => "info@santoshpolymers.com, ankur.goel@santoshpolymers.com",
  ```
- Keep the `from` field as `"onboarding@resend.dev"`.

---

### 4. Technical SEO Assets

#### [NEW] [sitemap.xml](file:///{base_dir.replace('\\', '/')}/sitemap.xml)
- Generate a dynamic or static `sitemap.xml` listing all pages:
  - Homepage (priority 1.0)
  - Core pages: products, about-us, industries, contact-us (priority 0.8)
  - 34 product detail pages (priority 0.9)

#### [MODIFY] [robots.txt](file:///{base_dir.replace('\\', '/')}/robots.txt)
- Ensure correct crawling directives and link the sitemap URL.

---

## Verification Plan

### Automated Verification
- Run `python generate_products.py` to regenerate the entire static site.
- Validate sitemap format and check for 404 links.

### Manual Verification
- Review schema output in the generated HTML using Google's Rich Results Testing patterns.
- Verify that clicking footer, navigation, and page emails correctly triggers the mail client pre-filled with the new email addresses.
- Verify that heading hierarchies (H1 -> H2 -> H3) are clean on product pages.

---

{audit_table_content}
"""

with open(plan_path, 'w', encoding='utf-8') as f:
    f.write(plan_template)

print("Implementation plan assembled successfully!")
