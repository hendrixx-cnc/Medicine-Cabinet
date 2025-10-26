# Medicine Cabinet Firefox Extension

A Firefox add-on that brings AI memory management to your browser, enabling context-aware assistance across GitHub, Stack Overflow, and popular AI chat platforms.

## 🎯 Features

- **Load & Manage Memory Files**: Import `.auractx` (Capsules) and `.auratab` (Tablets) directly in your browser
- **Active Context Injection**: Inject project context into AI chat interfaces, code editors, and documentation sites
- **Multi-Platform Support**: Works with GitHub, Stack Overflow, ChatGPT, Claude, Google Gemini, Microsoft Copilot, and Poe
- **Binary Parser**: Native JavaScript parser for Medicine Cabinet's binary formats
- **Persistent Storage**: Your loaded memory persists across browser sessions
- **Firefox Native**: Optimized for Firefox with Manifest V2

## 📦 Installation

### For Users (Firefox Add-ons - AMO)

1. Visit [Firefox Add-ons](https://addons.mozilla.org/) (link coming soon)
2. Click "Add to Firefox"
3. Approve the permissions
4. The 💊 icon appears in your toolbar

### For Development & Testing

1. **Download/Clone** the repository
   ```bash
   git clone https://github.com/hendrixx-cnc/Medicine-Cabinet.git
   cd Medicine-Cabinet/firefox-extension
   ```

2. **Open Firefox Debugging Page**
   - Navigate to: `about:debugging#/runtime/this-firefox`
   - Or: Menu → More Tools → Browser Console → Debugger

3. **Load Temporary Add-on**
   - Click "Load Temporary Add-on..."
   - Select `manifest.json` from the `firefox-extension` folder
   - The extension loads and icon appears in toolbar

4. **Keep Loaded** (Development)
   - Extension stays loaded until Firefox restarts
   - Reload after code changes: Click "Reload" in about:debugging

## 🚀 Usage

### 1. Load Memory Files

1. Click the Medicine Cabinet icon (💊) in Firefox toolbar
2. Click "📁 Load Capsule or Tablet"
3. Select your `.auractx` or `.auratab` files
4. View loaded files in the Capsules or Tablets tabs

### 2. Set Active Capsule

- In the Capsules tab, click the ⭐ button to set a capsule as active
- The active capsule will be used for context injection

### 3. Inject Context

1. Navigate to a supported site (GitHub, ChatGPT, etc.)
2. Open the Medicine Cabinet popup
3. Click "💉 Inject Active Context"
4. The capsule's context will be inserted into the current page

### Supported Sites

| Platform | Status | Injection Method |
|----------|--------|------------------|
| GitHub | ✅ | Comment boxes, issue/PR descriptions |
| Stack Overflow | ✅ | Question/answer editors |
| ChatGPT | ✅ | Prompt textarea |
| Claude AI | ✅ | Input field |
| Google Gemini | ✅ | Input field |
| Microsoft Copilot | ✅ | Input field |
| Poe | ✅ | Chat input |
| Others | ✅ | Clipboard (automatic fallback) |

## 📂 Project Structure

```
firefox-extension/
├── manifest.json           # Extension manifest (Manifest V2)
├── icons/                  # Extension icons
│   ├── icon-16.png
│   ├── icon-32.png
│   ├── icon-48.png
│   └── icon-128.png
├── popup/
│   ├── popup.html         # Extension popup UI
│   ├── popup.css          # Popup styles
│   └── popup.js           # Popup logic
└── scripts/
    ├── background.js      # Background script
    ├── content.js         # Content script (page injection)
    └── parser.js          # Binary format parser
```

## 🔧 Technical Details

### Manifest V2

This extension uses **Manifest V2** for maximum Firefox compatibility:
- Background scripts (not service workers)
- `browser_action` instead of `action`
- Compatible with Firefox ESR
- Works on Firefox 109+

### Browser API Compatibility

The extension uses standard WebExtensions APIs that work across browsers:
- `browser.*` or `chrome.*` namespace (both supported)
- `browser.storage.local` for persistence
- Standard content script messaging

### Binary Format Support

Pure JavaScript implementation:
- **Capsules (.auractx)**: AURACTX1 format with TEXT, JSON, BINARY sections
- **Tablets (.auratab)**: AURATAB1 format with entries

### Storage

- Uses `browser.storage.local` API
- Data persists across sessions
- No external servers or sync

### Permissions

- `storage`: Local persistence
- `activeTab`: Current page injection
- Host permissions for supported sites

## 🎨 Firefox Features

### Works Great With

- ✅ **Firefox Desktop** (109+)
- ✅ **Firefox Developer Edition**
- ✅ **Firefox ESR** (Extended Support Release)
- ✅ **Firefox Nightly**
- 🔜 **Firefox for Android** (with modifications)

### Firefox-Specific Optimizations

- Non-persistent background page for better performance
- Native `browser.*` API usage
- Optimized for Firefox's multi-process architecture
- Compatible with Firefox containers

## 📦 Building for Distribution

### Create XPI for Self-Hosting

```bash
cd firefox-extension
zip -r -FS ../medicine-cabinet-firefox-v1.0.0.xpi * \
  -x "*.git*" \
  -x "*.DS_Store" \
  -x "README.md" \
  -x "*.md"
```

### Sign for Distribution

Firefox requires signed add-ons. Two options:

**Option 1: Submit to AMO** (Recommended)
- Automatic signing
- Listed in Firefox Add-ons
- Automatic updates

**Option 2: Self-Signing**
```bash
# Install web-ext
npm install -g web-ext

# Sign the extension
web-ext sign --api-key=$AMO_JWT_ISSUER --api-secret=$AMO_JWT_SECRET
```

Get API keys from: https://addons.mozilla.org/developers/addon/api/key/

## 🔐 Privacy & Security

- **100% Local**: All data stored in browser's local storage
- **No Tracking**: No analytics or usage tracking
- **No External Requests**: Doesn't connect to any servers
- **Minimal Permissions**: Only what's necessary
- **Open Source**: Fully auditable code

## 🐛 Troubleshooting

### Extension Not Loading

1. Go to `about:debugging#/runtime/this-firefox`
2. Check for error messages
3. Ensure manifest.json is valid
4. Try reloading the extension

### Context Not Injecting

1. Check that active capsule is set
2. Open Browser Console (Ctrl+Shift+J)
3. Look for content script errors
4. Verify you're on a supported site
5. Check if context was copied to clipboard

### Files Not Loading

1. Verify file extension is `.auractx` or `.auratab`
2. Check Browser Console for parser errors
3. Ensure files are valid Medicine Cabinet format
4. Try loading one file at a time

### Performance Issues

1. Open `about:performance` to check impact
2. Limit number of loaded capsules
3. Clear storage if needed
4. Restart Firefox

## 🧪 Testing

### Using web-ext (Recommended)

```bash
# Install web-ext
npm install -g web-ext

# Run in temporary Firefox profile
cd firefox-extension
web-ext run

# Run with specific Firefox version
web-ext run --firefox=/path/to/firefox

# Run tests
web-ext lint
```

### Manual Testing

1. Load in `about:debugging`
2. Test on each supported platform
3. Check console for errors
4. Verify injection works
5. Test file loading

## 🔮 Roadmap

- [ ] Firefox for Android support
- [ ] Native file system integration
- [ ] Automatic context detection
- [ ] Sidebar panel option
- [ ] Keyboard shortcuts
- [ ] Dark mode
- [ ] Multi-account container support
- [ ] Sync via Firefox Sync

## 📚 Related Projects

- **[Medicine Cabinet](https://github.com/hendrixx-cnc/Medicine-Cabinet)** - Main Python library
- **Chrome Extension** - `../chrome-extension/`
- **Safari Extension** - `../safari-extension/`
- **[Orkestra](https://github.com/hendrixx-cnc/Orkestra)** - Multi-AI coordination
- **[AURA](https://github.com/hendrixx-cnc/AURA)** - AI-optimized compression

## 🤝 Contributing

Contributions welcome! Areas of interest:
- Firefox for Android optimization
- Performance improvements
- Additional platform support
- Localization/i18n
- Accessibility improvements

## 📝 License

Same license as Medicine Cabinet. See [../LICENSE](../LICENSE) for details.

## 👨‍💻 Author

Todd Hendricks ([hendrixx-cnc](https://github.com/hendrixx-cnc))

---

**Compatible with**: Firefox 109+, Firefox ESR, Firefox Developer Edition, Firefox Nightly
