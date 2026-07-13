import json
import os

base_dir = r"c:\Users\arnav\Documents\GitHub\santoshpolymers-website"
json_path = os.path.join(base_dir, "products_full.json")

with open(json_path, 'r', encoding='utf-8') as f:
    products = json.load(f)

# Keywords mapping for products based on their names
keyword_db = {
    "Distilled Soya Fatty Acid Oil": {
        "primary": "distilled soya fatty acid oil manufacturer",
        "long_tail": ["soya fatty acid oil price India", "distilled soya fatty acid supplier Haryana"],
        "industry": "paint and coatings, alkyd resins"
    },
    "Distilled Rice Fatty Acid": {
        "primary": "distilled rice fatty acid manufacturer",
        "long_tail": ["bulk rice fatty acid price India", "rice fatty acid supplier Haryana"],
        "industry": "cosmetics, soap manufacturing, resins"
    },
    "Soya Acid Oil": {
        "primary": "soya acid oil manufacturer",
        "long_tail": ["soya acid oil price India", "bulk soya acid oil Haryana"],
        "industry": "poultry feed, soap making, biodiesel"
    },
    "Bypass Fat (Bypass Fat 84)": {
        "primary": "bypass fat 84 manufacturer",
        "long_tail": ["bypass fat for dairy cattle price", "bypass fat manufacturer Haryana"],
        "industry": "dairy feed, animal nutrition"
    },
    "Calcium Stearate Chemical": {
        "primary": "calcium stearate manufacturer India",
        "long_tail": ["bulk calcium stearate price", "calcium stearate powder supplier Haryana"],
        "industry": "plastics, rubber compounding, cosmetics"
    },
    "Castor Oil Fatty Acid": {
        "primary": "castor oil fatty acid manufacturer",
        "long_tail": ["castor oil fatty acid price India", "castor fatty acid supplier Haryana"],
        "industry": "lubricants, soaps, coatings"
    },
    "Distilled Palm Fatty Acid": {
        "primary": "distilled palm fatty acid manufacturer",
        "long_tail": ["palm fatty acid distillate price", "bulk palm fatty acid India"],
        "industry": "biodiesel, soap manufacturing, animal feed"
    },
    "Fatty Acid Methyl Esters": {
        "primary": "fatty acid methyl esters manufacturer",
        "long_tail": ["fame biodiesel supplier India", "fatty acid methyl ester price"],
        "industry": "biodiesel, lubricants, solvents"
    },
    "Food Additive Sorbitan Monooleate": {
        "primary": "sorbitan monooleate food additive",
        "long_tail": ["food grade sorbitan monooleate price", "sorbitan monooleate supplier India"],
        "industry": "food processing, cosmetics, emulsifiers"
    },
    "Liquid Glycerin": {
        "primary": "liquid glycerin manufacturer India",
        "long_tail": ["bulk liquid glycerin price", "industrial grade glycerin supplier Haryana"],
        "industry": "pharmaceuticals, cosmetics, alkyd resins"
    },
    "Liquid Soya Lecithin": {
        "primary": "liquid soya lecithin manufacturer",
        "long_tail": ["food grade liquid soya lecithin", "bulk soya lecithin price India"],
        "industry": "food processing, confectionery, paint"
    },
    "Oleic Fatty Acid": {
        "primary": "oleic fatty acid manufacturer India",
        "long_tail": ["high purity oleic acid price", "oleic fatty acid supplier Haryana"],
        "industry": "lubricants, cosmetics, textiles, soaps"
    },
    "PEG 400 Monooleate": {
        "primary": "peg 400 monooleate manufacturer",
        "long_tail": ["polyethylene glycol 400 monooleate price", "peg 400 monooleate supplier India"],
        "industry": "emulsifiers, textile auxiliaries, cosmetics"
    },
    "Rice Bran Lecithin": {
        "primary": "rice bran lecithin manufacturer",
        "long_tail": ["rice bran lecithin for animal feed", "bulk rice bran lecithin India"],
        "industry": "poultry feed, animal nutrition, paint"
    },
    "Sodium Oleate": {
        "primary": "sodium oleate manufacturer India",
        "long_tail": ["industrial sodium oleate price", "sodium oleate powder supplier Haryana"],
        "industry": "soaps, cosmetics, textile processing"
    },
    "Sodium Stearate": {
        "primary": "sodium stearate manufacturer India",
        "long_tail": ["bulk sodium stearate price", "sodium stearate supplier Haryana"],
        "industry": "pharmaceuticals, cosmetics, plastics"
    },
    "Tall Oil Fatty Acid": {
        "primary": "tall oil fatty acid manufacturer",
        "long_tail": ["tofa supplier India", "tall oil fatty acid price"],
        "industry": "alkyd resins, oilfield chemicals, lubricants"
    },
    "Terpineol Essential Oil": {
        "primary": "terpineol essential oil manufacturer",
        "long_tail": ["industrial terpineol price India", "terpineol supplier Haryana"],
        "industry": "perfumes, cosmetics, disinfectants"
    },
    "Zinc Ricinoleate": {
        "primary": "zinc ricinoleate manufacturer India",
        "long_tail": ["bulk zinc ricinoleate price", "zinc ricinoleate supplier Haryana"],
        "industry": "deodorants, cosmetics, odor absorbers"
    },
    "Zinc Stearate": {
        "primary": "zinc stearate manufacturer India",
        "long_tail": ["zinc stearate powder price", "industrial zinc stearate Haryana"],
        "industry": "plastics, rubber compounding, coatings"
    },
    "Gum Rosin (Colophony)": {
        "primary": "gum rosin manufacturer India",
        "long_tail": ["colophony rosin price", "gum rosin supplier Haryana"],
        "industry": "adhesives, printing inks, paper sizing"
    },
    "Pine Oil Industrial": {
        "primary": "pine oil industrial manufacturer",
        "long_tail": ["bulk industrial pine oil price", "pine oil supplier Haryana"],
        "industry": "disinfectants, cleaning products, mineral flotation"
    },
    "Ricinoleic Acid": {
        "primary": "ricinoleic acid manufacturer India",
        "long_tail": ["ricinoleic acid price", "bulk ricinoleic acid supplier Haryana"],
        "industry": "coatings, lubricants, cosmetics, plastics"
    },
    "Monobasic Fatty Acid": {
        "primary": "monobasic fatty acid manufacturer",
        "long_tail": ["monobasic fatty acids price India", "monobasic fatty acid supplier Haryana"],
        "industry": "alkyd resins, metalworking fluids, lubricants"
    },
    "Soya Fatty Acid (Soya Fatty Eco)": {
        "primary": "soya fatty acid manufacturer India",
        "long_tail": ["soya fatty eco acid price", "soya fatty acid supplier Haryana"],
        "industry": "alkyd resins, printing inks, soaps"
    },
    "Turmeric Essential Oil": {
        "primary": "turmeric essential oil manufacturer",
        "long_tail": ["pure turmeric oil bulk price", "turmeric essential oil supplier Haryana"],
        "industry": "cosmetics, pharmaceuticals, aromatherapy"
    },
    "Turmeric Extract": {
        "primary": "turmeric extract manufacturer India",
        "long_tail": ["curcumin extract bulk price", "turmeric extract supplier Haryana"],
        "industry": "pharmaceuticals, food coloring, cosmetics"
    },
    "Turmeric Oleoresin": {
        "primary": "turmeric oleoresin manufacturer",
        "long_tail": ["food grade turmeric oleoresin price", "turmeric oleoresin supplier India"],
        "industry": "food processing, pharmaceuticals, cosmetics"
    },
    "Akd Wax Emulsion": {
        "primary": "akd wax emulsion manufacturer",
        "long_tail": ["alkyl ketene dimer emulsion price", "akd wax emulsion supplier Haryana"],
        "industry": "paper sizing, paper mills"
    },
    "Defoamer": {
        "primary": "process defoamer manufacturer India",
        "long_tail": ["industrial silicone defoamer price", "process defoamer supplier Haryana"],
        "industry": "paper mills, wastewater treatment, paint"
    },
    "DSR Dry Strength Resin": {
        "primary": "dry strength resin manufacturer",
        "long_tail": ["dsr paper sizing chemical price", "dry strength resin supplier Haryana"],
        "industry": "paper manufacturing, packaging board"
    },
    "Violet Ink": {
        "primary": "violet ink manufacturer India",
        "long_tail": ["industrial violet ink price", "violet ink supplier Haryana"],
        "industry": "printing, packaging"
    },
    "Corrugated Packaging Boxes": {
        "primary": "corrugated packaging boxes manufacturer",
        "long_tail": ["bulk corrugated boxes price India", "packaging boxes supplier Haryana"],
        "industry": "packaging, logistics, shipping"
    },
    "Pulp Moulded Trays": {
        "primary": "pulp moulded trays manufacturer",
        "long_tail": ["biodegradable egg trays bulk price", "fruit packaging trays supplier Haryana"],
        "industry": "poultry, agriculture packaging, eco friendly"
    }
}

for p in products:
    name = p.get("product_name")
    kw_data = keyword_db.get(name)
    if not kw_data:
        clean_name = name.split('(')[0].strip()
        kw_data = {
            "primary": f"{clean_name.lower()} manufacturer India",
            "long_tail": [f"bulk {clean_name.lower()} price", f"{clean_name.lower()} supplier Haryana"],
            "industry": "industrial applications"
        }
    
    primary = kw_data["primary"]
    long_tails = ", ".join(kw_data["long_tail"])
    
    # Generate Title
    rec_title = f"{name} Manufacturer & Supplier India | Santosh Polymers"
    if len(rec_title) > 65:
        rec_title = f"{name} Manufacturer India | Santosh Polymers"
        
    # Generate Meta Description
    clean_name = name.split('(')[0].strip()
    desc_words = f"Buy high-purity {clean_name} from Santosh Polymers, a leading manufacturer and supplier in Haryana, India. Inquire for wholesale pricing & custom bulk grades."
    
    cat = p.get("category", "")
    if "Oleo" in cat:
        desc_words = f"Leading {primary} in Kurukshetra, Haryana. High-purity {clean_name} for paints, rubber, and industrial coatings. Inquire for bulk pricing."
    elif "Paper" in cat:
        desc_words = f"Premium {primary} in Ladwa, Haryana. High-efficiency {clean_name} to optimize paper sizing & strength. Contact us for wholesale quotes."
    elif "Herbal" in cat:
        desc_words = f"Pure {primary} in Kurukshetra, Haryana. Premium organic {clean_name} for cosmetics & pharma. Inquire for custom bulk packaging."
    elif "Packaging" in cat:
        desc_words = f"Eco-friendly {primary} in Haryana. Sustainable {clean_name} for secure shipping & retail packaging. Request wholesale samples."
        
    if len(desc_words) > 160:
        desc_words = desc_words[:157] + "..."
        
    # Inject SEO optimized values
    p["title"] = rec_title
    p["meta_description"] = desc_words
    
    # Build list of meta keywords
    all_kws = [primary] + kw_data["long_tail"] + [k.strip() for k in kw_data["industry"].split(',')] + ["Santosh Polymers", "Haryana", "Kurukshetra", "Ladwa"]
    p["meta_keywords"] = ", ".join(all_kws)

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(products, f, indent=4, ensure_ascii=False)

print("Updated products_full.json with new SEO metadata!")
