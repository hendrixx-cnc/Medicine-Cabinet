# 🚀 Quick Start - Medicine Cabinet Safari Extension

## Installation (Development Mode)

### Step 1: Enable Developer Features
```
Safari → Preferences → Advanced
☑️ Show Develop menu in menu bar
```

### Step 2: Allow Unsigned Extensions
```
Develop Menu → Allow Unsigned Extensions
```

### Step 3: Load Extension
```
Develop Menu → Web Extension Background Content → Medicine Cabinet
```

Or alternatively:
```
Safari → Preferences → Extensions → Enable "Medicine Cabinet"
```

## First Use

1. **Click** the 💊 icon in Safari toolbar
2. **Load** a `.auractx` or `.auratab` file  
3. **Set** active capsule (click ⭐)
4. **Visit** GitHub, ChatGPT, Claude, etc.
5. **Click** "💉 Inject Active Context"

## File Generation

### Create Icons (Already Done! ✅)
```bash
cd safari-extension
python3 generate_icons.py
```

### Create Capsule Files
```bash
# From main Medicine Cabinet directory
medicine-cabinet capsule create "MyProject" "Working on auth" --author "Your Name"
medicine-cabinet capsule set-task myproject.auractx "Implement JWT tokens"
```

### Create Tablet Files
```bash
medicine-cabinet tablet create "Bug Fix" "Fixed memory leak" --tags performance
medicine-cabinet tablet add-entry bugfix.auratab src/memory.py --diff-file changes.diff
```

## Testing

Open the test page:
```bash
open safari-extension/test.html
```

Or test on real sites:
- github.com (any repo)
- stackoverflow.com (ask question)
- chat.openai.com
- claude.ai
- gemini.google.com

## Troubleshooting

### Extension not appearing?
- Check Safari → Preferences → Extensions
- Restart Safari
- Re-enable in Develop menu

### Context not injecting?
1. Verify active capsule is set (look for ✓ in popup)
2. Check Web Inspector console (Develop → Show Web Inspector)
3. Ensure you're on a supported site
4. Check clipboard - context might have been copied there

### Files not loading?
- Verify file extension (`.auractx` or `.auratab`)
- Check console for parser errors
- Ensure files are valid Medicine Cabinet format

## Keyboard Shortcuts (Safari)

| Action | Shortcut |
|--------|----------|
| Open Extension | Click toolbar icon |
| Web Inspector | ⌘⌥I |
| Develop Menu | ⌘⌥C (Console) |

## What Gets Injected?

When you inject a capsule, the extension adds:
- **Project name** and summary
- **Task objective** (if set)
- **Relevant files** list (if set)
- **Working plan** (if set)
- **Creation date** and metadata

Example output:
```markdown
## 💊 Medicine Cabinet Context

**Project:** MyApp Authentication
**Summary:** Implementing JWT-based auth
**Branch:** feature/auth
**Created:** 2025-10-26

**Task Objective:**
Implement secure JWT token generation and validation

**Relevant Files:**
- src/auth.py
- tests/test_auth.py
- config/jwt_settings.py
```

## Distribution (Xcode)

To package for App Store:

1. Create Safari Extension project in Xcode
2. Copy `safari-extension/*` to Extension folder
3. Configure Bundle ID and signing
4. Build (⌘B) and Archive (⌘⌥⇧K)
5. Submit to App Store

See README.md for detailed Xcode instructions.

## Support

- 📖 Full docs: `safari-extension/README.md`
- 🔧 Technical details: `safari-extension/development_summary.md`
- 🎨 Icon help: `safari-extension/icons/icon_creation_guide.md`
- 🧪 Test page: `safari-extension/test.html`

## Links

- Main Project: https://github.com/hendrixx-cnc/Medicine-Cabinet
- Orkestra: https://github.com/hendrixx-cnc/Orkestra
- AURA: https://github.com/hendrixx-cnc/AURA

---

**Ready to use!** The extension is fully functional and all files are in place. 🎉
