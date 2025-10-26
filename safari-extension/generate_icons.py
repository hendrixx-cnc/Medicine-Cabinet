#!/usr/bin/env python3
"""
Simple icon generator for Medicine Cabinet Safari Extension
Creates basic colored square icons with centered text
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    print("✓ PIL/Pillow found")
except ImportError:
    print("❌ Pillow not installed. Install with: pip install Pillow")
    exit(1)

import os

# Configuration
ICON_COLOR = (99, 102, 241)  # #6366f1 - Medicine Cabinet indigo
TEXT_COLOR = (255, 255, 255)  # White
SIZES = [16, 32, 48, 128]
OUTPUT_DIR = "icons"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("\n💊 Generating Medicine Cabinet icons...")
print("=" * 50)

for size in SIZES:
    filename = f"{OUTPUT_DIR}/icon-{size}.png"
    
    # Create image with solid color background
    img = Image.new('RGB', (size, size), ICON_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Draw a white pill shape (rounded rectangle)
    padding = size // 6
    pill_width = size - (padding * 2)
    pill_height = size // 2
    
    # Rounded rectangle (pill shape)
    pill_x = padding
    pill_y = (size - pill_height) // 2
    pill_coords = [pill_x, pill_y, pill_x + pill_width, pill_y + pill_height]
    
    # Draw pill body
    draw.rounded_rectangle(pill_coords, radius=pill_height//2, fill=TEXT_COLOR)
    
    # Draw center line
    center_x = size // 2
    line_width = max(1, size // 32)
    draw.line([(center_x, pill_y), (center_x, pill_y + pill_height)], 
              fill=ICON_COLOR, width=line_width)
    
    # Save
    img.save(filename)
    print(f"✓ Created {filename} ({size}x{size}px)")

print("\n✅ All icons generated successfully!")
print(f"📁 Icons saved to: {OUTPUT_DIR}/")
print("\nYou can now use these icons with the Safari extension.")
