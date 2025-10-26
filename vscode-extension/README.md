# Medicine Cabinet - VS Code Extension

AI memory management for GitHub Copilot and other AI assistants in VS Code.

## Features

- 💊 **Load Context Capsules**: Project-specific working memory
- 📚 **Load Tablets**: Long-term memory from previous sessions
- 🔄 **Auto-Load**: Automatically load tablets on startup
- ❤️ **Health Monitoring**: Track context size and usage
- 📊 **Visual Status**: See loaded context in sidebar
- 🚀 **Quick Export**: Save session to tablet via command

## Usage

1. Open Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`)
2. Type "Medicine Cabinet"
3. Choose an action:
   - Load Context Capsule (working memory)
   - Load Tablet (long-term memory)
   - Check Health Status
   - Export Session to Tablet

## Configuration

- `medicine-cabinet.capsulePath`: Path to capsules directory
- `medicine-cabinet.tabletPath`: Path to tablets directory (default: `~/.medicine_cabinet/tablets`)
- `medicine-cabinet.autoLoad`: Auto-load tablets on startup
- `medicine-cabinet.maxContextSize`: Max context in KB (default: 75KB = 15% of Copilot window)

## Medical Theme

The extension uses a medical metaphor:

- 🟢 **Healthy**: Context < 75% of limit
- 🟡 **Warning**: Context 75-90% of limit  
- 🔴 **Critical**: Context > 90% - "I need to visit the doctor!"

When critical, you can:
- **Physical (refresh)**: Reload context
- **Operation (export)**: Export session to tablet

## Requirements

- Python 3.x with `medicine_cabinet` package installed
- VS Code 1.80.0 or higher

## Installation

1. Copy this folder to your VS Code extensions directory:
   - macOS/Linux: `~/.vscode/extensions/`
   - Windows: `%USERPROFILE%\.vscode\extensions\`

2. Install dependencies:
   ```bash
   cd vscode-extension
   npm install
   npm run compile
   ```

3. Reload VS Code

## Development

```bash
# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Watch for changes
npm run watch
```

Press `F5` in VS Code to launch Extension Development Host for testing.

## Related

Part of the [Medicine Cabinet](https://github.com/hendrixx-cnc/Medicine-Cabinet) ecosystem for AI memory management.
