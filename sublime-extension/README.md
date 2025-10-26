# Medicine Cabinet Plugin for Sublime Text

AI memory management system for Sublime Text with support for `.auractx` (Context Capsules) and `.auratab` (Memory Tablets) files.

## Features

- **Load Context Capsules**: Parse and view `.auractx` files containing AI conversation context
- **Load Memory Tablets**: Parse and view `.auratab` files containing code change histories
- **Visual Panel**: Display loaded memory in a dedicated output panel
- **Copy Context**: Copy all loaded context to clipboard for AI prompts
- **Syntax Highlighting**: Basic syntax highlighting for binary formats
- **Keyboard Shortcuts**: Fast access via key bindings
- **Context Menu**: Right-click integration for `.auractx` and `.auratab` files

## Installation

### Method 1: Package Control (Recommended - when published)
1. Open Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
2. Select "Package Control: Install Package"
3. Search for "Medicine Cabinet"
4. Click to install

### Method 2: Manual Installation
1. Download this repository
2. Open Sublime Text
3. Go to `Preferences > Browse Packages...`
4. Copy the `sublime-extension` folder into the `Packages` directory
5. Rename the folder to `MedicineCabinet`
6. Restart Sublime Text

### Method 3: Git Clone
```bash
cd ~/Library/Application\ Support/Sublime\ Text/Packages  # macOS
cd ~/.config/sublime-text/Packages                         # Linux
cd %APPDATA%\Sublime Text\Packages                         # Windows

git clone https://github.com/hendrixx-cnc/Medicine-Cabinet.git MedicineCabinet
```

## Usage

### Loading Files

#### Via Menu
1. Go to `Tools > Medicine Cabinet`
2. Select "Load Context Capsule (.auractx)" or "Load Memory Tablet (.auratab)"
3. Choose your file in the file dialog

#### Via Context Menu
1. Right-click on an `.auractx` or `.auratab` file in the sidebar or editor
2. Select "Medicine Cabinet > Load as Context Capsule/Tablet"

#### Via Keyboard Shortcuts
- `Ctrl+Shift+M, Ctrl+Shift+C` - Load Context Capsule
- `Ctrl+Shift+M, Ctrl+Shift+T` - Load Memory Tablet
- `Ctrl+Shift+M, Ctrl+Shift+P` - Show Medicine Cabinet Panel
- `Ctrl+Shift+M, Ctrl+Shift+X` - Copy Context to Clipboard

### Viewing Loaded Memory

Press `Ctrl+Shift+M, Ctrl+Shift+P` or go to `Tools > Medicine Cabinet > Show Medicine Cabinet Panel` to view:
- All loaded context capsules with their sections
- All loaded memory tablets with their entries
- File paths and version information

### Copying Context

Press `Ctrl+Shift+M, Ctrl+Shift+X` or go to `Tools > Medicine Cabinet > Copy Context to Clipboard` to:
- Copy all loaded capsules and tablets to clipboard
- Format for easy pasting into AI prompts
- Include all sections, entries, and metadata

## Binary Format Support

### Context Capsule (.auractx)
```
AURACTX1 format:
- Magic: AURACTX1 (8 bytes)
- Version: uint32 big-endian
- Section Count: uint32 big-endian
- Sections: [type, length, data]
  - Types: 1=TEXT, 2=JSON, 3=BINARY
```

### Memory Tablet (.auratab)
```
AURATAB1 format:
- Magic: AURATAB1 (8 bytes)
- Version: uint32 big-endian
- Entry Count: uint32 big-endian
- Entries: [path, diff, notes]
  - Each with length-prefixed data
```

## Commands

| Command | Description | Default Keybinding |
|---------|-------------|--------------------|
| `load_capsule` | Load a Context Capsule file | `Ctrl+Shift+M, Ctrl+Shift+C` |
| `load_tablet` | Load a Memory Tablet file | `Ctrl+Shift+M, Ctrl+Shift+T` |
| `show_medicine_cabinet_panel` | Show the Medicine Cabinet panel | `Ctrl+Shift+M, Ctrl+Shift+P` |
| `copy_medicine_cabinet_context` | Copy context to clipboard | `Ctrl+Shift+M, Ctrl+Shift+X` |
| `load_capsule_from_context` | Load capsule from context menu | (context menu only) |
| `load_tablet_from_context` | Load tablet from context menu | (context menu only) |

## Configuration

### Custom Key Bindings
Add to `Preferences > Key Bindings`:
```json
[
    { "keys": ["your+keys"], "command": "load_capsule" },
    { "keys": ["your+keys"], "command": "show_medicine_cabinet_panel" }
]
```

### Plugin Settings
Currently no configuration file needed - the plugin works out of the box.

## Use Cases

### AI-Assisted Development
1. Load context capsules before starting AI pair programming
2. Copy context to provide AI with project history
3. Track changes across sessions with memory tablets

### Code Review
1. Load memory tablets to see change histories
2. Review diffs and notes in a unified view
3. Copy formatted context for review comments

### Documentation
1. Load capsules containing API documentation
2. Extract sections for inline reference
3. Maintain context across editing sessions

## Compatibility

- **Sublime Text**: 3 and 4
- **Python**: 3.3+ (bundled with Sublime Text)
- **OS**: Windows, macOS, Linux
- **Format**: AURACTX1 and AURATAB1 binary formats

## Related Projects

- [Medicine Cabinet CLI](https://github.com/hendrixx-cnc/Medicine-Cabinet) - Python command-line tools
- [Safari Extension](../safari-extension/) - Medicine Cabinet for Safari
- [Chrome Extension](../chrome-extension/) - Medicine Cabinet for Chrome/Chromium
- [Firefox Extension](../firefox-extension/) - Medicine Cabinet for Firefox
- [Edge Extension](../edge-extension/) - Medicine Cabinet for Microsoft Edge
- [JetBrains Plugin](../jetbrains-plugin/) - Medicine Cabinet for JetBrains IDEs

## Development

### File Structure
```
sublime-extension/
├── medicine_cabinet_plugin.py  # Main plugin code
├── Main.sublime-menu           # Tools menu integration
├── Context.sublime-menu        # Right-click menu
├── .sublime-keymap             # Keyboard shortcuts
├── AURACTX.sublime-syntax      # Syntax highlighting for .auractx
├── AURATAB.sublime-syntax      # Syntax highlighting for .auratab
└── README.md                   # This file
```

### Extending the Plugin
The plugin is designed to be extensible:
- `BinaryParser` class handles format parsing
- `MedicineCabinetState` stores loaded data
- Commands inherit from `sublime_plugin.WindowCommand` or `TextCommand`

## License

MIT License - See [LICENSE](../LICENSE) for details

## Support

- **Issues**: [GitHub Issues](https://github.com/hendrixx-cnc/Medicine-Cabinet/issues)
- **Documentation**: [Main README](../README.md)
- **Examples**: [Quick Start Guide](../examples/quick_start.py)

## Version History

- **1.0.0** (2025-10-26)
  - Initial release
  - AURACTX1 and AURATAB1 format support
  - Panel view and clipboard copy
  - Syntax highlighting
  - Menu and keyboard integration
