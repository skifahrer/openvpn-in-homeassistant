# Brand Assets

This directory contains brand assets for the OpenVPN Manager integration.

## Current Status

We have a simple SVG icon. To convert it to PNG for HACS:

### Option 1: Online Converter
1. Go to https://cloudconvert.com/svg-to-png
2. Upload `icon.svg`
3. Set size to 256x256
4. Download as `icon.png`
5. Place it in this directory

### Option 2: Using ImageMagick (if installed)
```bash
convert -background none -size 256x256 icon.svg icon.png
```

### Option 3: Use the SVG (Home Assistant supports it)
The SVG will work fine - HACS just warns but doesn't fail on missing PNG.

## Quick Fix

If you have Python with Pillow:
```bash
# Install if needed: pip install pillow cairosvg
python3 -c "from cairosvg import svg2png; svg2png(url='icon.svg', write_to='icon.png', output_width=256, output_height=256)"
```
