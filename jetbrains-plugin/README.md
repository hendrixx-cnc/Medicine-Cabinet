# Medicine Cabinet JetBrains Plugin

A plugin for IntelliJ IDEA and all JetBrains IDEs that brings AI memory management directly into your development environment.

## 🎯 Features

- **📁 Load Memory Files**: Import `.auractx` (Capsules) and `.auratab` (Tablets) into your IDE
- **🪟 Dedicated Tool Window**: View and manage all loaded capsules and tablets
- **📋 Quick Copy**: Copy formatted context to clipboard with one click
- **🎨 File Type Support**: Custom icons and associations for `.auractx` and `.auratab` files
- **🖱️ Context Menu Actions**: Right-click files to load them as memory
- **💾 Binary Parser**: Native Kotlin parser for Medicine Cabinet binary formats
- **🔔 Notifications**: Visual feedback for all operations

## 🛠️ Compatible IDEs

Works with **all JetBrains IDEs 2023.2+**:

- ✅ IntelliJ IDEA (Community & Ultimate)
- ✅ PyCharm (Community & Professional)
- ✅ WebStorm
- ✅ PhpStorm
- ✅ GoLand
- ✅ Rider
- ✅ CLion
- ✅ RubyMine
- ✅ DataGrip
- ✅ AppCode
- ✅ Android Studio

## 📦 Installation

### From JetBrains Marketplace (Coming Soon)

1. Open your JetBrains IDE
2. Go to: **Settings/Preferences** → **Plugins**
3. Click **Marketplace** tab
4. Search for **"Medicine Cabinet"**
5. Click **Install**
6. Restart the IDE

### From Disk (Development)

1. Download the plugin JAR file
2. Open your JetBrains IDE
3. Go to: **Settings/Preferences** → **Plugins**
4. Click the ⚙️ icon → **Install Plugin from Disk...**
5. Select the JAR file
6. Restart the IDE

### Build from Source

```bash
# Clone the repository
git clone https://github.com/hendrixx-cnc/Medicine-Cabinet.git
cd Medicine-Cabinet/jetbrains-plugin

# Build the plugin
./gradlew buildPlugin

# Plugin JAR will be in: build/distributions/
```

## 🚀 Usage

### Opening the Tool Window

1. Go to: **View** → **Tool Windows** → **Medicine Cabinet**
2. Or use keyboard shortcut (if configured)
3. The tool window opens on the right side

### Loading Memory Files

**Method 1: Tool Window**
1. Open the Medicine Cabinet tool window
2. Click **"Load Capsule"** or **"Load Tablet"**
3. Select your `.auractx` or `.auratab` file
4. File appears in the appropriate tab

**Method 2: Context Menu**
1. Right-click any `.auractx` or `.auratab` file in Project view
2. Select **"Load as Capsule"** or **"Load as Tablet"**
3. Confirmation notification appears

### Copying Context

1. Open the Capsules tab in the tool window
2. Select a capsule from the list
3. Click **"Copy Context"**
4. Formatted context is copied to clipboard
5. Paste into your AI assistant

### Context Format

The copied context includes:
```markdown
## 💊 Medicine Cabinet Context

**File:** myproject.auractx
**Created:** 2025-10-26T12:30:00Z
**Version:** 1

### task_objective
Implement user authentication with JWT tokens

### relevant_files
- src/auth/jwt.py
- tests/test_auth.py

### working_plan
1. Create JWT token generation
2. Implement token validation
3. Add refresh token logic
```

## 🔧 Configuration

### File Type Associations

The plugin automatically associates:
- `.auractx` files → Context Capsule type
- `.auratab` files → Memory Tablet type

### Keyboard Shortcuts

Configure shortcuts in:
**Settings/Preferences** → **Keymap** → **Plugins** → **Medicine Cabinet**

Recommended shortcuts:
- Load Capsule: `Ctrl+Alt+C` / `⌘⌥C`
- Copy Context: `Ctrl+Alt+M` / `⌘⌥M`

## 🏗️ Building & Development

### Prerequisites

- JDK 17 or higher
- Gradle 8.0+
- IntelliJ IDEA 2023.2+ for development

### Build Commands

```bash
# Build the plugin
./gradlew buildPlugin

# Run in IDE sandbox
./gradlew runIde

# Run tests
./gradlew test

# Verify plugin structure
./gradlew verifyPlugin
```

### Project Structure

```
jetbrains-plugin/
├── build.gradle.kts              # Gradle build configuration
├── src/main/
│   ├── kotlin/com/medicinecabinet/
│   │   ├── parser/               # Binary format parsers
│   │   │   └── BinaryParser.kt
│   │   ├── toolwindow/           # Tool window UI
│   │   │   ├── MedicineCabinetToolWindowFactory.kt
│   │   │   └── MedicineCabinetToolWindow.kt
│   │   ├── filetype/             # File type definitions
│   │   │   └── FileTypes.kt
│   │   ├── icons/                # Icon providers
│   │   │   └── MedicineCabinetIconProvider.kt
│   │   └── actions/              # IDE actions
│   │       └── Actions.kt
│   └── resources/
│       └── META-INF/
│           └── plugin.xml        # Plugin descriptor
└── README.md
```

## 📝 Publishing

### To JetBrains Marketplace

1. **Create JetBrains Account**
   - Sign up at https://account.jetbrains.com

2. **Get Plugin Repository Token**
   - Go to https://plugins.jetbrains.com/author/me/tokens
   - Create new token with "Upload" permission

3. **Set Environment Variables**
   ```bash
   export PUBLISH_TOKEN=your_token_here
   ```

4. **Build and Publish**
   ```bash
   ./gradlew publishPlugin
   ```

5. **Verification**
   - Plugin goes through JetBrains review (1-3 days)
   - Will be available on Marketplace after approval

### Manual Distribution

```bash
# Build plugin JAR
./gradlew buildPlugin

# Find JAR in:
# build/distributions/jetbrains-plugin-1.0.0.zip

# Distribute via:
# - GitHub Releases
# - Custom update server
# - Direct download link
```

## 🔍 Troubleshooting

### Plugin Not Loading

1. Check IDE version (must be 2023.2+)
2. Verify plugin is enabled: **Settings** → **Plugins**
3. Check IDE logs: **Help** → **Show Log in Finder/Explorer**
4. Try: **File** → **Invalidate Caches / Restart**

### Files Not Parsing

1. Verify file is valid `.auractx` or `.auratab`
2. Check file was created with Medicine Cabinet Python library
3. Look for errors in: **Help** → **Show Log**
4. Try loading file in tool window (shows detailed errors)

### Tool Window Not Appearing

1. Check: **View** → **Tool Windows** → **Medicine Cabinet**
2. If missing, reinstall plugin
3. Check IDE logs for errors

## 🧪 Testing

### Run Tests

```bash
# Unit tests
./gradlew test

# Integration tests with IDE
./gradlew runPluginVerifier
```

### Manual Testing

1. Run plugin in sandbox: `./gradlew runIde`
2. Create test project with sample files
3. Test all features:
   - Load capsules and tablets
   - Copy context
   - View details
   - Remove items
   - File type recognition

## 🤝 Contributing

Contributions welcome! Areas of interest:

- Enhanced UI/UX
- Additional file format versions
- Custom icons
- Performance optimizations
- Integration with AI assistant plugins
- Localization/i18n

## 📚 Related Projects

- **[Medicine Cabinet](https://github.com/hendrixx-cnc/Medicine-Cabinet)** - Main Python library
- **Browser Extensions** - Chrome, Firefox, Safari, Edge
- **[Orkestra](https://github.com/hendrixx-cnc/Orkestra)** - Multi-AI coordination
- **[AURA](https://github.com/hendrixx-cnc/AURA)** - AI-optimized compression

## 📄 License

Same license as Medicine Cabinet. See [../LICENSE](../LICENSE) for details.

## 👨‍💻 Author

Todd Hendricks ([hendrixx-cnc](https://github.com/hendrixx-cnc))

---

**For JetBrains IDEs 2023.2+** | Built with ❤️ and Kotlin
