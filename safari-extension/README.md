# Medicine Cabinet Safari Extension

A Safari Web Extension that brings AI memory management to your browser, enabling context-aware assistance across GitHub, Stack Overflow, and popular AI chat platforms.

## 🎯 Features

- **Load & Manage Memory Files**: Import `.auractx` (Capsules) and `.auratab` (Tablets) directly in your browser
- **Active Context Injection**: Inject project context into AI chat interfaces, code editors, and documentation sites
- **Multi-Platform Support**: Works with GitHub, Stack Overflow, ChatGPT, Claude, and Google Gemini
- **Binary Parser**: Native JavaScript parser for Medicine Cabinet's binary formats
- **Persistent Storage**: Your loaded memory persists across browser sessions

## 📦 Installation

### For Development & Testing

1. **Open Safari**
   - Enable the Develop menu: Safari → Preferences → Advanced → Check "Show Develop menu in menu bar"

2. **Enable Unsigned Extensions**
   - Develop → Allow Unsigned Extensions

3. **Load the Extension**
   - Open Safari
   - Go to: Develop → Web Extension Background Content → Medicine Cabinet
   - Or use: Safari → Preferences → Extensions → Enable "Medicine Cabinet"

### Alternative: Using Xcode (Recommended for Distribution)

1. **Create a Safari Extension Project**
   ```bash
   # You'll need Xcode installed
   open -a Xcode
   # File → New → Project → Safari Extension
   ```

2. **Copy Extension Files**
   - Copy the contents of this `safari-extension` folder into the "Extension" folder of your Xcode project

3. **Configure the Extension**
   - Update Bundle Identifier in Xcode
   - Configure signing & capabilities

4. **Build & Run**
   - Select your Mac as the target
   - Click Run (⌘R)
   - Safari will open with the extension loaded

## 🚀 Usage

### 1. Load Memory Files

1. Click the Medicine Cabinet icon in Safari's toolbar
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

| Platform | Injection Method |
|----------|------------------|
| GitHub | Comment boxes, issue/PR descriptions |
| Stack Overflow | Question/answer editors |
| ChatGPT | Prompt textarea |
| Claude AI | Input field |
| Google Gemini | Input field |
| Others | Clipboard (automatic fallback) |

## 📂 Project Structure

```
safari-extension/
├── manifest.json           # Extension configuration
├── icons/                  # Extension icons (add your own)
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

### Binary Format Support

The extension includes a JavaScript implementation of the Medicine Cabinet binary parsers:

- **Capsules (.auractx)**: Parses AURACTX1 format with sections (TEXT, JSON, BINARY)
- **Tablets (.auratab)**: Parses AURATAB1 format with entries (path, diff, notes)

### Storage

- Uses `chrome.storage.local` for persistent storage
- Loaded capsules and tablets survive browser restarts
- Active capsule preference is remembered

### Permissions

- `storage`: For persistent memory storage
- `activeTab`: To inject context into current page
- `nativeMessaging`: Reserved for future file system bridge

## 🎨 Customization

### Icons

Add your own icons to the `icons/` directory:
- `icon-16.png` - 16×16px
- `icon-32.png` - 32×32px
- `icon-48.png` - 48×48px
- `icon-128.png` - 128×128px

You can create these from the Medicine Cabinet pill emoji or design your own.

### Adding New Sites

Edit `scripts/content.js` and add:

1. New hostname check in `injectContext()`
2. New injection function (e.g., `injectYourSite()`)
3. Update `manifest.json` content_scripts matches and host_permissions

Example:
```javascript
if (hostname.includes('yoursite.com')) {
  injectYourSite(capsule);
}
```

## 🔐 Security & Privacy

- **All data stays local**: Capsules and tablets are stored only in your browser
- **No external requests**: Extension doesn't phone home or track usage
- **File access**: Extension only reads files you explicitly select
- **Clipboard access**: Used only when direct injection isn't possible

## 🐛 Troubleshooting

### Extension Doesn't Appear

1. Check Safari → Preferences → Extensions
2. Ensure "Medicine Cabinet" is enabled
3. Try restarting Safari

### Context Not Injecting

1. Verify you have an active capsule set (check popup)
2. Check browser console for errors (Develop → Show JavaScript Console)
3. Ensure the site is in the supported list
4. Try the clipboard fallback (context will be copied automatically)

### Files Not Loading

1. Verify file extension is `.auractx` or `.auratab`
2. Check that files are valid Medicine Cabinet formats
3. Look for errors in the popup console

## 🔮 Future Enhancements

- [ ] Native file system integration (read/write capsules directly)
- [ ] Automatic context detection per site
- [ ] Tablet search and filtering
- [ ] Export/sync capabilities
- [ ] Dark mode
- [ ] Keyboard shortcuts
- [ ] Context preview before injection

## 📚 Related Projects

- [Medicine Cabinet](https://github.com/hendrixx-cnc/Medicine-Cabinet) - Main Python library
- [Orkestra](https://github.com/hendrixx-cnc/Orkestra) - Multi-AI task coordination
- [AURA](https://github.com/hendrixx-cnc/AURA) - AI-optimized compression

## 📝 License

Same license as the Medicine Cabinet project. See [../LICENSE](../LICENSE) for details.

## 👨‍💻 Author

Todd Hendricks ([hendrixx-cnc](https://github.com/hendrixx-cnc))

---

**Note**: This extension is part of the Medicine Cabinet ecosystem and works best when used alongside the Python CLI tools for creating and managing capsules and tablets.
