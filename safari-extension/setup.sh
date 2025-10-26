#!/bin/bash
# Medicine Cabinet Safari Extension - Quick Setup Script

echo "🏥 Medicine Cabinet Safari Extension Setup"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "manifest.json" ]; then
    echo "❌ Error: Please run this script from the safari-extension directory"
    exit 1
fi

echo "✓ Found extension files"
echo ""

# Create placeholder icons if they don't exist
echo "📦 Setting up icon placeholders..."

for size in 16 32 48 128; do
    icon_file="icons/icon-${size}.png"
    if [ ! -f "$icon_file" ]; then
        echo "  Creating placeholder for ${size}x${size}..."
        # Create a simple colored square as placeholder
        # You'll need ImageMagick for this - or you can skip and add icons manually
        if command -v convert &> /dev/null; then
            convert -size ${size}x${size} xc:"#6366f1" \
                    -gravity center -pointsize $((size/2)) -fill white \
                    -annotate +0+0 "💊" "$icon_file" 2>/dev/null || \
            convert -size ${size}x${size} xc:"#6366f1" "$icon_file"
        else
            echo "    (ImageMagick not found - you'll need to add icons manually)"
            mkdir -p icons
            touch "$icon_file.placeholder"
        fi
    else
        echo "  ✓ ${size}x${size} icon exists"
    fi
done

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Open Safari"
echo "2. Enable: Safari → Preferences → Advanced → 'Show Develop menu'"
echo "3. Enable: Develop → Allow Unsigned Extensions"
echo "4. Load: Develop → Web Extension Background Content → Medicine Cabinet"
echo ""
echo "Or use Xcode:"
echo "1. Create a new Safari Extension project in Xcode"
echo "2. Copy these files into the Extension folder"
echo "3. Build and run (⌘R)"
echo ""
echo "📖 See README.md for detailed instructions"
