# Medicine Cabinet Chrome Extension

A Chrome/Chromium extension that brings AI memory management to your browser, enabling context-aware assistance across GitHub, Stack Overflow, and popular AI chat platforms.

## 🎯 Features

- **Load & Manage Memory Files**: Import `.auractx` (Capsules) and `.auratab` (Tablets) directly in your browser
- **Active Context Injection**: Inject project context into AI chat interfaces, code editors, and documentation sites
- **Multi-Platform Support**: Works with GitHub, Stack Overflow, ChatGPT, Claude, Google Gemini, Microsoft Copilot, and Poe
- **Binary Parser**: Native JavaScript parser for Medicine Cabinet's binary formats
- **Persistent Storage**: Your loaded memory persists across browser sessions
- **Cross-Browser**: Compatible with Chrome, Edge, Brave, Opera, and other Chromium-based browsers

## 📦 Installation

### For Users (Chrome Web Store)

1. Visit the [Chrome Web Store](#) (link coming soon)
2. Click "Add to Chrome"
3. Confirm the installation

### For Development & Testing

1. **Download/Clone** this repository
   ```bash
   git clone https://github.com/hendrixx-cnc/Medicine-Cabinet.git
   cd Medicine-Cabinet/chrome-extension
   ```

2. **Open Chrome Extensions Page**
   - Navigate to: `chrome://extensions/`
   - Or: Menu → More Tools → Extensions

3. **Enable Developer Mode**
   - Toggle the switch in the top-right corner

4. **Load Unpacked Extension**
   - Click "Load unpacked"
   - Select the `chrome-extension` folder
   - The Medicine Cabinet icon should appear in your toolbar

5. **Pin the Extension** (Optional)
   - Click the puzzle piece icon in toolbar
   - Pin Medicine Cabinet for easy access

## 🚀 Usage

### 1. Load Memory Files

1. Click the Medicine Cabinet icon (💊) in Chrome's toolbar
2. Click "📁 Load Capsule or Tablet"
3. Select your `.auractx` or `.auratab` files
4. View loaded files in the Capsules or Tablets tabs

### 2. Set Active Capsule

- In the Capsules tab, click the ⭐ button on a capsule to set it as active
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
chrome-extension/
├── manifest.json           # Extension configuration (Manifest V3)
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
    ├── background.js      # Background service worker
    ├── content.js         # Content script (page injection)
    └── parser.js          # Binary format parser
```

## 🔧 Technical Details

### Manifest V3

This extension uses **Manifest V3**, the latest Chrome extension format:
- Service workers instead of background pages
- Improved security and privacy
- Better performance
- Required for Chrome Web Store submissions after 2024

### Binary Format Support

JavaScript implementation of Medicine Cabinet binary parsers:
- **Capsules (.auractx)**: AURACTX1 format with TEXT, JSON, BINARY sections
- **Tablets (.auratab)**: AURATAB1 format with path, diff, notes entries

### Storage

- Uses `chrome.storage.local` API for persistent storage
- Data survives browser restarts
- No external servers or cloud sync

### Permissions

- `storage`: Persistent local storage
- `activeTab`: Inject context into current page
- `host_permissions`: Specified sites only

## 🎨 Compatible Browsers

This extension works on all Chromium-based browsers:

- ✅ **Google Chrome** (v88+)
- ✅ **Microsoft Edge** (v88+)
- ✅ **Brave Browser**
- ✅ **Opera** (v74+)
- ✅ **Vivaldi**
- ✅ **Arc Browser**
- ❌ Firefox (use Firefox add-on version instead)
- ❌ Safari (use Safari extension version instead)

## 📦 Building for Distribution

### Create a ZIP for Chrome Web Store

```bash
cd chrome-extension
zip -r medicine-cabinet-chrome.zip . -x "*.git*" -x "*.DS_Store" -x "README.md"
```

### Chrome Web Store Submission

1. Go to [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole)
2. Pay one-time $5 developer registration fee (if first time)
3. Click "New Item"
4. Upload `medicine-cabinet-chrome.zip`
5. Fill in store listing details:
   - Title: Medicine Cabinet
   - Description: AI memory management for developers
   - Category: Productivity
   - Screenshots: (capture popup UI, injection examples)
6. Submit for review (usually 1-3 days)

### Requirements for Chrome Web Store

- ✅ Manifest V3 (required)
- ✅ Clear privacy policy (if collecting data - we don't)
- ✅ 128x128 icon
- ✅ Detailed description
- ✅ At least 1 screenshot (1280x800 or 640x400)
- ✅ Small promotional tile (440x280)

## 🔐 Privacy & Security

- **100% Local**: All data stored locally in your browser
- **No Tracking**: Extension doesn't track usage or send analytics
- **No External Requests**: Doesn't connect to any servers
- **Minimal Permissions**: Only requests what's necessary
- **Open Source**: All code is auditable

## 🐛 Troubleshooting

### Extension Not Loading

1. Check `chrome://extensions/` - ensure Developer Mode is ON
2. Look for error messages in the extension card
3. Try "Reload" button on the extension
4. Check browser console for errors

### Context Not Injecting

1. Verify active capsule is set (popup should show ✓)
2. Open DevTools (F12) and check Console tab
3. Ensure you're on a supported site
4. Try refreshing the page
5. Check if context was copied to clipboard (fallback)

### Files Not Loading

1. Verify file extension is `.auractx` or `.auratab`
2. Check DevTools console for parser errors
3. Ensure files are valid Medicine Cabinet format (created with Python lib)
4. Try loading one file at a time

### Performance Issues

1. Clear browser cache
2. Limit number of loaded capsules/tablets
3. Check `chrome://extensions/` for memory usage
4. Restart browser

## 🔮 Roadmap

- [ ] Firefox add-on version
- [ ] Native file system integration
- [ ] Automatic context detection
- [ ] Tablet search and filtering
- [ ] Export/sync across devices
- [ ] Dark mode
- [ ] Keyboard shortcuts (Alt+Shift+M to inject)
- [ ] Context preview before injection
- [ ] Integration with VS Code extension

## 📚 Related Projects

- **[Medicine Cabinet](https://github.com/hendrixx-cnc/Medicine-Cabinet)** - Main Python library
- **[Orkestra](https://github.com/hendrixx-cnc/Orkestra)** - Multi-AI task coordination
- **[AURA](https://github.com/hendrixx-cnc/AURA)** - AI-optimized compression
- **[The Quantum Self](https://github.com/hendrixx-cnc/The-Quantum-Self)** - Book with proof-of-concept

## 🤝 Contributing

Contributions welcome! Areas of interest:
- Additional platform support
- UI/UX improvements
- Performance optimizations
- Documentation
- Bug fixes

## 📝 License

Same license as Medicine Cabinet. See [../LICENSE](../LICENSE) for details.

## 👨‍💻 Author

Todd Hendricks ([hendrixx-cnc](https://github.com/hendrixx-cnc))

---

**Compatible with**: Chrome 88+, Edge 88+, Brave, Opera 74+, Vivaldi, Arc, and other Chromium browsers.
