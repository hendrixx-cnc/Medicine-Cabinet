# Creating Icons for Medicine Cabinet Extension

Since we can't include actual PNG files in the repository easily, here are several ways to create icons:

## Option 1: Use Online Tools (Easiest)

1. Go to https://favicon.io/favicon-generator/
2. Set:
   - Text: 💊 (pill emoji)
   - Background: #6366f1 (indigo)
   - Font Size: 70
3. Download and extract
4. Rename files to match:
   - favicon-16x16.png → icon-16.png
   - favicon-32x32.png → icon-32.png
   - android-chrome-192x192.png (resize to 48x48) → icon-48.png
   - android-chrome-192x192.png (resize to 128x128) → icon-128.png

## Option 2: Use Figma/Sketch/Design Tool

Create a simple design:
- Canvas: Square (16, 32, 48, 128 pixels)
- Background: Gradient from #6366f1 to #8b5cf6
- Icon: Medicine pill emoji 💊 or custom design
- Export as PNG at each size

## Option 3: Use ImageMagick (Command Line)

```bash
cd icons

# Create base icon
convert -size 128x128 xc:"#6366f1" \
        -fill white -gravity center \
        -pointsize 80 -font "Apple-Color-Emoji" \
        -annotate +0+0 "💊" icon-128.png

# Resize for other sizes
convert icon-128.png -resize 48x48 icon-48.png
convert icon-128.png -resize 32x32 icon-32.png
convert icon-128.png -resize 16x16 icon-16.png
```

## Option 4: Use Python + Pillow

```python
from PIL import Image, ImageDraw, ImageFont

sizes = [16, 32, 48, 128]
color = (99, 102, 241)  # #6366f1

for size in sizes:
    img = Image.new('RGB', (size, size), color)
    draw = ImageDraw.Draw(img)
    
    # Add white circle (pill shape)
    padding = size // 4
    draw.ellipse([padding, padding, size-padding, size-padding], 
                 fill='white', outline=color, width=size//16)
    
    img.save(f'icon-{size}.png')
```

## Temporary Placeholder

Until you create proper icons, the extension will still work. Safari will show a default icon.

You can also use any 16x16, 32x32, 48x48, and 128x128 PNG images temporarily.
