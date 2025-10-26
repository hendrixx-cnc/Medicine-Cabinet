# Medicine Cabinet

A collection of tools for managing AI agent memory, including long-term, portable memory ("Tablets") and project-specific context ("Capsules").

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/hendrixx-cnc/medicine-cabinet.git
cd medicine_cabinet

# Install locally
pip install -e .
```

### CLI Usage

The easiest way to use Medicine Cabinet is through the command-line interface:

```bash
# Create a context capsule
medicine-cabinet capsule create "MyApp" "Adding user authentication" --author "Todd"

# Set task details
medicine-cabinet capsule set-task myapp.auractx "Implement password hashing"
medicine-cabinet capsule set-files myapp.auractx src/auth.py tests/test_auth.py

# Read a capsule
medicine-cabinet capsule read myapp.auractx

# Create a tablet
medicine-cabinet tablet create "Auth Bug Fix" "Fixed SQL injection" --tags security authentication

# Add an entry to a tablet
medicine-cabinet tablet add-entry auth_bug_fix.auratab src/auth.py --diff-file changes.diff --notes '{"summary": "Used parameterized queries"}'

# Inspect any file
medicine-cabinet inspect myapp.auractx
medicine-cabinet inspect auth_bug_fix.auratab
```

### Python API Usage

```python
from medicine_cabinet import ContextCapsule, CapsuleMetadata, Tablet, TabletMetadata, TabletEntry

# Create a Context Capsule (working memory for a project)
capsule = ContextCapsule(metadata=CapsuleMetadata(
    project="MyApp",
    summary="Adding user authentication"
))

capsule.set_task_objective("Implement password hashing")
capsule.set_relevant_files(["src/auth.py", "tests/test_auth.py"])
capsule.write("myapp.auractx")

# Create a Tablet (long-term memory)
tablet = Tablet(metadata=TabletMetadata(
    title="Auth Bug Fix",
    summary="Fixed SQL injection vulnerability"
))

tablet.add_entry(TabletEntry(
    path="src/auth.py",
    diff="... your git diff ...",
    notes='{"summary": "Used parameterized queries"}'
))

tablet.write("auth_fix.auratab")
```

### Session Tracking

Medicine Cabinet includes automatic and manual session tracking tools:

**Automatic Tracking (Zero Configuration):**
```python
# Import once and it automatically tracks throughout your session
from auto_session_tracker import track

# Track changes anywhere in your code
track("file.py", "Added new feature", "+10 lines")
track("main.py", "Fixed bug", "+2, -1 lines")

# Session auto-saves when script ends - no manual save needed!
```

**Manual Session Tracking:**
```python
from session_tracker import AURASessionTracker

tracker = AURASessionTracker()
tablet = tracker.start_session("Feature Implementation", "Added user auth")
tracker.record_file_change(tablet, "auth.py", "+def login()...", "Added login")
tracker.save_session(tablet)
```

**View Sessions:**
```bash
# View all sessions
python3 view_session.py

# View specific session
python3 view_session.py sessions/session_20251026_204406.auratab
```

### Inspect Files

```bash
python -m medicine_cabinet.inspector myapp.auractx
python -m medicine_cabinet.inspector auth_fix.auratab
```

## What Is This?

This module is designed to be a self-contained package that can be easily copied into other projects.

### Related Projects

The Medicine Cabinet is a foundational component for enabling more advanced AI capabilities. It is designed to work in concert with other projects by Todd Hendricks:

*   **[Orkestra](https://github.com/hendrixx-cnc/Orkestra)**: A multi-AI task coordination platform that allows a "Conductor" to orchestrate complex, autonomous workflows across different AI models like Claude, Grok, ChatGPT, Gemini, and Copilot.
*   **[AURA](https://github.com/hendrixx-cnc/AURA)**: A hybrid AI-optimized compression library for chat and streaming applications. It uses a combination of template matching, multiple compression backends, and optional GPU acceleration to achieve high throughput and significant bandwidth savings, with a strong focus on enterprise-grade audit capabilities.

### Extensions & Integrations

The Medicine Cabinet provides a universal, portable memory layer for AI assistants, accessible across all development tools:

*   **IDE Extensions:**
    *   **[JetBrains Plugin](jetbrains-plugin/):** Native support for all JetBrains IDEs (IntelliJ IDEA, PyCharm, WebStorm, PhpStorm, GoLand, Rider, CLion, RubyMine, etc.) - Load capsules and tablets directly in the IDE with dedicated tool windows
    *   **[Sublime Text Plugin](sublime-extension/):** Python-based plugin with menu integration, keyboard shortcuts, and output panel for viewing loaded memory
    *   **[VS Code Extension](vscode-extension/):** Native TypeScript extension with sidebar views, health monitoring, and GitHub Copilot integration - Load capsules and tablets with visual status tracking

### Browser Extensions

Medicine Cabinet browser extensions provide automatic context injection and conversation capture:

*   **[Safari Extension](safari-extension/):** Manifest V3 extension for macOS Safari  
*   **[Chrome Extension](chrome-extension/):** Works with Chrome, Edge, Brave, Opera, Vivaldi, Arc
*   **[Firefox Extension](firefox-extension/):** Manifest V2 add-on for Firefox
*   **[Microsoft Edge Extension](edge-extension/):** Optimized for Bing Chat integration

**Features:**
- 💊 **Auto-Pop Context:** Automatically inject project context when visiting AI sites (ChatGPT, Claude, Gemini)
- 💬 **Conversation Capture:** Scrape and persist conversations in real-time (requires native messaging)
- 📖 **Read-Only Mode:** Browse extensions are read-only by default to prevent file corruption
- 🔄 **Bidirectional Sync:** With native messaging setup, conversations are automatically saved to tablets

**Setup Native Messaging (Optional but Recommended):**

For conversation capture and persistent storage:

```bash
# Run the setup script
python3 setup_extension.py

# Follow prompts to enter your extension ID
# Script will configure everything automatically
```

See [NATIVE_MESSAGING_SETUP.md](NATIVE_MESSAGING_SETUP.md) for detailed instructions.

### IDE Extensions

This ecosystem allows an AI's "memory" to follow the developer wherever they work, creating a seamless and truly context-aware experience.

