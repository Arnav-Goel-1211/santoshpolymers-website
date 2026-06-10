import os
import re
from PIL import Image

def defer_js(html_content):
    def add_defer(match):
        tag = match.group(0)
        if ' src=' in tag and ' defer' not in tag and ' async' not in tag:
            return tag.replace('<script ', '<script defer ')
        return tag
    return re.sub(r'<script\s+[^>]*>', add_defer, html_content, flags=re.IGNORECASE)

def preload_css(html_content):
    def replace_css(match):
        tag = match.group(0)
        critical_css = ['bootstrap', 'theme', 'responsive', 'settings', 'navigation', 'preset']
        if any(c in tag for c in critical_css):
            return tag
        if 'rel="stylesheet"' in tag:
            return tag.replace('rel="stylesheet"', 'rel="preload" as="style" onload="this.onload=null;this.rel=\'stylesheet\'"')
        return tag
    return re.sub(r'<link\s+[^>]*rel="stylesheet"[^>]*>', replace_css, html_content, flags=re.IGNORECASE)

def set_image_dimensions(html_content, html_filepath, base_dir):
    def replace_img(match):
        img_tag = match.group(0)
        src_match = re.search(r'src=["\'](.*?)["\']', img_tag)
        if not src_match:
            return img_tag
        
        src = src_match.group(1)
        
        # Add loading="lazy" if not present
        if 'loading=' not in img_tag.lower():
            if img_tag.endswith('/>'):
                img_tag = img_tag[:-2] + ' loading="lazy" />'
            else:
                img_tag = img_tag[:-1] + ' loading="lazy">'

        # Try to resolve the image path to get dimensions
        img_path = None
        if src.startswith('http') or src.startswith('//') or src.startswith('data:'):
            return img_tag
            
        if src.startswith('/'):
            img_path = os.path.join(base_dir, src.lstrip('/'))
        else:
            img_path = os.path.join(os.path.dirname(html_filepath), src)
            
        img_path = os.path.normpath(img_path)
        
        if os.path.exists(img_path) and ('width=' not in img_tag and 'height=' not in img_tag):
            try:
                with Image.open(img_path) as img:
                    width, height = img.size
                
                if img_tag.endswith('/>'):
                    new_tag = img_tag[:-2] + f' width="{width}" height="{height}" />'
                else:
                    new_tag = img_tag[:-1] + f' width="{width}" height="{height}">'
                return new_tag
            except Exception as e:
                pass
                
        return img_tag

    return re.sub(r'<img\s+[^>]*>', replace_img, html_content, flags=re.IGNORECASE)

def process_html_files(base_dir):
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    new_content = defer_js(content)
                    new_content = preload_css(new_content)
                    new_content = set_image_dimensions(new_content, filepath, base_dir)
                    
                    if new_content != content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Updated HTML: {filepath}")
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

def add_font_display_swap(base_dir):
    for root, dirs, files in os.walk(os.path.join(base_dir, 'css')):
        for file in files:
            if file.endswith('.css'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    def replace_font_face(match):
                        block = match.group(0)
                        if 'font-display' not in block:
                            return block.replace('@font-face{', '@font-face{font-display:swap;')\
                                        .replace('@font-face {', '@font-face {font-display:swap;')
                        return block
                        
                    new_content = re.sub(r'@font-face\s*\{[^}]*\}', replace_font_face, content, flags=re.IGNORECASE)
                    
                    if new_content != content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Updated CSS fonts: {filepath}")
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

if __name__ == '__main__':
    base_dir = r"c:\Users\arnav\Desktop\santoshpolymers-website"
    print("Processing HTML files...")
    process_html_files(base_dir)
    print("Processing CSS files...")
    add_font_display_swap(base_dir)
    print("Done!")
