# Medicine Cabinet CLI Updates

## Changes Made to CLI

- Updated docstring to include new commands: `sessions` and `view`

- Added function that lists all `.auratab` and `.auractx` files in a directory
  - Shows metadata for each session file
  - Accepts `--dir` argument to specify sessions directory

- Added function that views detailed contents of a session file
  - Determines file type and displays appropriately
  - Accepts file path as argument

- Added helper function that pretty-prints tablet file contents
  - Shows metadata, all entries, diffs, and notes
  - Formats output for readability

- Added helper function that pretty-prints capsule file contents
  - Shows metadata and all sections with previews
  - Displays text/JSON content, indicates binary data

- Registered new CLI command: `sessions`
  - Lists all saved sessions in a directory
  - Optional `--dir` argument for custom directory

- Registered new CLI command: `view`
  - Views a session file in detail
  - Accepts `.auratab` or `.auractx` file path

## New Auto Session Tracking Feature

- Created automatic session tracker that initializes on import
  - Uses singleton pattern to maintain one tracker per process
  - Automatically creates tablet on first use
  - Tracks file changes with simple function call
  - Auto-saves session on Python exit using `atexit` hook
  - No manual activation or save needed
  - Creates sessions directory automatically
  - Provides `track(filepath, description, diff)` function for easy use

### Implementation Details

**Singleton Pattern:**
- `AutoSessionTracker` class uses `__new__()` to ensure only one instance exists
- Stores instance in `_instance` class variable
- Prevents multiple trackers from interfering with each other

**Auto-initialization:**
- `__init__()` checks if session is already active via `_session_active` flag
- Creates `Tablet` with auto-generated metadata on first use
- Registers `atexit.register(self._save_on_exit)` to save on program termination

**Tracking Changes:**
- `track_change(filepath, description, diff)` method adds `TabletEntry` to tablet
- Appends entries to `tablet.entries` list
- No return value needed - just tracks in background

**Auto-save on Exit:**
- `_save_on_exit()` method registered with Python's `atexit` module
- Called automatically when Python interpreter shuts down
- Saves tablet to `sessions/auto_session_TIMESTAMP.auratab` file
- Only saves if tablet has entries (avoids empty files)
- Prints confirmation message with file path and entry count

**Simple API:**
- Module-level `track(filepath, description, diff)` function
- Module-level `get_tablet()` function returns current tablet
- Global `_tracker` instance created at module import time
- Zero configuration - just import and use

## Summary

CLI: 4 new functions added, 2 new CLI commands registered (~140 lines)
Auto-tracking: Complete automatic session capture system (~115 lines)
Total: Approximately 255 lines added to enable session management and automatic tracking
