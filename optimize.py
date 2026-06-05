import os
from PIL import Image
import rcssmin
import rjsmin

def optimize_images(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                filepath = os.path.join(root, file)
                try:
                    # Get original size
                    orig_size = os.path.getsize(filepath)
                    
                    # Open image
                    img = Image.open(filepath)
                    
                    # If RGBA and saving as JPEG, convert to RGB
                    if img.mode == 'RGBA' and file.lower().endswith(('.jpg', '.jpeg')):
                        img = img.convert('RGB')
                        
                    # Save with optimization
                    if file.lower().endswith(('.jpg', '.jpeg')):
                        img.save(filepath, "JPEG", optimize=True, quality=80)
                    elif file.lower().endswith('.png'):
                        img.save(filepath, "PNG", optimize=True)
                        
                    new_size = os.path.getsize(filepath)
                    if new_size < orig_size:
                        print(f"Optimized {filepath}: {orig_size//1024}KB -> {new_size//1024}KB")
                except Exception as e:
                    print(f"Error optimizing {filepath}: {e}")

def minify_css(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.css') and not file.endswith('.min.css'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        css = f.read()
                    minified = rcssmin.cssmin(css)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(minified)
                    print(f"Minified {filepath}")
                except Exception as e:
                    print(f"Error minifying {filepath}: {e}")

def minify_js(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.js') and not file.endswith('.min.js'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        js = f.read()
                    minified = rjsmin.jsmin(js)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(minified)
                    print(f"Minified {filepath}")
                except Exception as e:
                    print(f"Error minifying {filepath}: {e}")

if __name__ == '__main__':
    base_dir = r"c:\Users\arnav\Desktop\santoshpolymers-website"
    print("Optimizing images...")
    optimize_images(os.path.join(base_dir, 'images'))
    
    print("Minifying CSS...")
    minify_css(os.path.join(base_dir, 'css'))
    
    print("Minifying JS...")
    minify_js(os.path.join(base_dir, 'js'))
    
    print("Optimization complete!")
