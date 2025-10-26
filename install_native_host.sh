#!/bin/bash
# Install Medicine Cabinet native messaging host

set -e

echo "📦 Installing Medicine Cabinet Native Messaging Host..."

# Get the absolute path to native_host.py
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
NATIVE_HOST_PATH="$SCRIPT_DIR/native_host.py"

# Make it executable
chmod +x "$NATIVE_HOST_PATH"

# Create wrapper script
WRAPPER_PATH="/usr/local/bin/medicine-cabinet-host"
echo "Creating wrapper at $WRAPPER_PATH"

sudo tee "$WRAPPER_PATH" > /dev/null << EOF
#!/bin/bash
exec python3 "$NATIVE_HOST_PATH" "\$@"
EOF

sudo chmod +x "$WRAPPER_PATH"

# Install for Chrome/Edge (Linux)
if [ -d "$HOME/.config/google-chrome/NativeMessagingHosts" ]; then
    echo "Installing for Chrome..."
    mkdir -p "$HOME/.config/google-chrome/NativeMessagingHosts"
    cp "$SCRIPT_DIR/native-messaging/com.medicinecabinet.host.json" \
       "$HOME/.config/google-chrome/NativeMessagingHosts/"
fi

if [ -d "$HOME/.config/chromium/NativeMessagingHosts" ]; then
    echo "Installing for Chromium..."
    mkdir -p "$HOME/.config/chromium/NativeMessagingHosts"
    cp "$SCRIPT_DIR/native-messaging/com.medicinecabinet.host.json" \
       "$HOME/.config/chromium/NativeMessagingHosts/"
fi

if [ -d "$HOME/.config/microsoft-edge/NativeMessagingHosts" ]; then
    echo "Installing for Edge..."
    mkdir -p "$HOME/.config/microsoft-edge/NativeMessagingHosts"
    cp "$SCRIPT_DIR/native-messaging/com.medicinecabinet.host.json" \
       "$HOME/.config/microsoft-edge/NativeMessagingHosts/"
fi

# Install for Firefox (Linux)
if [ -d "$HOME/.mozilla/native-messaging-hosts" ]; then
    echo "Installing for Firefox..."
    mkdir -p "$HOME/.mozilla/native-messaging-hosts"
    cp "$SCRIPT_DIR/native-messaging/com.medicinecabinet.host.firefox.json" \
       "$HOME/.mozilla/native-messaging-hosts/com.medicinecabinet.host.json"
fi

# macOS locations
if [ "$(uname)" == "Darwin" ]; then
    echo "Installing for macOS browsers..."
    
    # Chrome
    mkdir -p "$HOME/Library/Application Support/Google/Chrome/NativeMessagingHosts"
    cp "$SCRIPT_DIR/native-messaging/com.medicinecabinet.host.json" \
       "$HOME/Library/Application Support/Google/Chrome/NativeMessagingHosts/"
    
    # Firefox
    mkdir -p "$HOME/Library/Application Support/Mozilla/NativeMessagingHosts"
    cp "$SCRIPT_DIR/native-messaging/com.medicinecabinet.host.firefox.json" \
       "$HOME/Library/Application Support/Mozilla/NativeMessagingHosts/com.medicinecabinet.host.json"
fi

echo "✅ Native messaging host installed!"
echo ""
echo "Next steps:"
echo "1. Update the extension ID in the manifest files"
echo "2. Add 'nativeMessaging' permission to your extension manifest"
echo "3. Reload your browser extension"
echo ""
echo "Logs will be written to: ~/.medicine_cabinet/native_host.log"
