# Native Messaging Setup

This enables **bidirectional communication** between the browser extension and Python backend for:
- ✅ Real-time conversation capture
- ✅ Automatic context updates  
- ✅ Persistent session storage
- ✅ Live sync between browser and files

## Quick Setup

### 1. Install the Browser Extension

**Chrome/Edge/Brave:**
1. Go to `chrome://extensions`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select the appropriate extension folder:
   - `chrome-extension/` for Chrome
   - `edge-extension/` for Edge  
   - `safari-extension/` for Brave/Chromium

**Firefox:**
1. Go to `about:debugging#/runtime/this-firefox`
2. Click "Load Temporary Add-on"
3. Select `firefox-extension/manifest.json`

### 2. Get Your Extension ID

**Chrome/Edge/Brave:**
1. In `chrome://extensions`, find "Medicine Cabinet"
2. Copy the ID (looks like: `abcdefghijklmnopqrstuvwxyz123456`)

**Firefox:**
1. Use the ID from manifest.json: `medicine-cabinet@hendrixx-cnc.github.io`

### 3. Run Setup Script

```bash
cd /path/to/Medicine-Cabinet
python3 setup_extension.py
```

The script will:
- Prompt for your extension ID
- Create wrapper script at `/usr/local/bin/medicine-cabinet-host`
- Install native messaging manifests for all detected browsers
- Configure permissions automatically

**Note:** You may need `sudo` for system directories.

### 4. Reload Extension

Go back to your browser's extensions page and click the reload button for Medicine Cabinet.

## Verification

Check that it's working:

```bash
# Check wrapper script exists
ls -l /usr/local/bin/medicine-cabinet-host

# Check manifest installed (Chrome example)
ls -l ~/.config/google-chrome/NativeMessagingHosts/com.medicinecabinet.host.json

# Check logs after using extension
tail -f ~/.medicine_cabinet/native_host.log
```

## Manual Installation

If the automatic setup fails, you can install manually:

### macOS

**Chrome:**
```bash
mkdir -p ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts
cp native-messaging/com.medicinecabinet.host.json \
   ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts/
```

**Firefox:**
```bash
mkdir -p ~/Library/Application\ Support/Mozilla/NativeMessagingHosts  
cp native-messaging/com.medicinecabinet.host.firefox.json \
   ~/Library/Application\ Support/Mozilla/NativeMessagingHosts/com.medicinecabinet.host.json
```

### Linux

**Chrome:**
```bash
mkdir -p ~/.config/google-chrome/NativeMessagingHosts
cp native-messaging/com.medicinecabinet.host.json \
   ~/.config/google-chrome/NativeMessagingHosts/
```

**Firefox:**
```bash
mkdir -p ~/.mozilla/native-messaging-hosts
cp native-messaging/com.medicinecabinet.host.firefox.json \
   ~/.mozilla/native-messaging-hosts/com.medicinecabinet.host.json
```

**Important:** Edit the manifest file and replace `EXTENSION_ID_HERE` with your actual extension ID!

## How It Works

```
Browser Extension ←→ Native Messaging ←→ Python Backend
     (JavaScript)         (JSON/stdio)      (native_host.py)
         ↓                                          ↓
    Pop context                              Write to .auratab
    Scrape chat                              Update .auractx
    Store in memory                          Persist to disk
```

**Without native messaging:** Extension is read-only  
**With native messaging:** Full bidirectional sync with persistence

## Troubleshooting

### Extension shows "Native host not available"
- Check wrapper script exists: `ls /usr/local/bin/medicine-cabinet-host`
- Check manifest installed: `ls ~/.config/google-chrome/NativeMessagingHosts/`
- Verify extension ID matches in manifest file
- Reload the extension

### Permission denied errors
- Run setup with sudo: `sudo python3 setup_extension.py`
- Or manually create wrapper with sudo

### Python script not executing
- Ensure `native_host.py` is executable: `chmod +x native_host.py`
- Test directly: `echo '{"action":"listSessions"}' | python3 native_host.py`

### Check logs
```bash
tail -f ~/.medicine_cabinet/native_host.log
```

## Uninstall

Remove native messaging components:

```bash
# Remove wrapper
sudo rm /usr/local/bin/medicine-cabinet-host

# Remove manifests
rm ~/.config/google-chrome/NativeMessagingHosts/com.medicinecabinet.host.json
rm ~/.mozilla/native-messaging-hosts/com.medicinecabinet.host.json

# Remove logs
rm -rf ~/.medicine_cabinet/
```

## Security Note

Native messaging allows the extension to run local Python scripts. The extension:
- ✅ Only communicates with `native_host.py`
- ✅ Cannot execute arbitrary commands
- ✅ Cannot access files outside Medicine Cabinet directory
- ✅ Requires explicit user installation

The Python backend runs with your user permissions.
