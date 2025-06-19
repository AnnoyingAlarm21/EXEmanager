#!/usr/bin/env python3
import os
import sys
from PIL import Image, ImageDraw, ImageFont

def generate_icon():
    """Generate a simple icon for the Wine EXE Manager"""
    # Create a new image with a transparent background
    size = (512, 512)
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a rounded rectangle for the app icon
    radius = 60
    wine_color = (114, 47, 55)  # Wine red color
    
    # Draw the main background
    draw.rounded_rectangle([(0, 0), (512, 512)], radius=radius, fill=wine_color)
    
    # Draw a wine glass in the center
    glass_color = (255, 255, 255, 220)  # Slightly transparent white
    
    # Wine glass stem
    draw.rectangle([(236, 300), (276, 420)], fill=glass_color)
    
    # Wine glass base
    draw.ellipse([(196, 420), (316, 460)], fill=glass_color)
    
    # Wine glass bowl
    draw.ellipse([(156, 150), (356, 350)], fill=glass_color)
    
    # Wine liquid
    wine_liquid = (150, 0, 24)  # Darker red for wine
    draw.ellipse([(166, 160), (346, 340)], fill=wine_liquid)
    
    # Draw "EXE" text
    try:
        # Try to load a font, fall back to default if not available
        font = ImageFont.truetype("Arial Bold.ttf", 120)
    except IOError:
        font = ImageFont.load_default()
    
    draw.text((170, 220), "EXE", fill=(255, 255, 255), font=font)
    
    # Save the icon
    app_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(app_dir, "app_icon.png")
    img.save(icon_path)
    print(f"Icon saved to {icon_path}")
    
    return icon_path

if __name__ == "__main__":
    try:
        from PIL import Image, ImageDraw, ImageFont
        generate_icon()
    except ImportError:
        print("Pillow library is required. Install it with: pip install pillow")
        sys.exit(1) 