# Medicine Cabinet - Automatic Context Flow

## The Vision: Auto-Loading Context System

```
┌─────────────────────────────────────────────────────────────┐
│  YOU SEND MESSAGE                                            │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  Copilot Wakes Up                                           │
│  └─> Auto-executes: python3 context_manager.py load        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  Context Manager:                                           │
│  1. Pop persistent tablet (long-term memory)                │
│  2. Create fresh capsule (active session)                   │
│  3. Load compact context into Copilot                       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  Copilot Responds with Full Historical Knowledge            │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  After Response:                                            │
│  └─> python3 context_manager.py increment                  │
│      - Updates persistent tablet                            │
│      - Updates active capsule                               │
│      - Increments message counter                           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  After 25 Messages:                                         │
│  💊 "TIME TO TAKE YOUR MEDS!" reminder                     │
│  └─> Prompt to save/cleanup                                │
└─────────────────────────────────────────────────────────────┘
```

## Current Implementation

### ✅ What Works Now:

1. **Manual Context Loading**
   ```bash
   python3 context_manager.py load
   ```
   - Loads persistent tablet
   - Creates fresh capsule
   - Resets message counter

2. **Message Counter**
   ```bash
   python3 context_manager.py increment
   ```
   - Increments counter
   - Shows "Take your meds!" at 25 messages
   - Auto-saves state

3. **Smart Filtering**
   - Scraper only captures contextual memories
   - Filters out chit-chat
   - Keeps code, decisions, technical info

### ⏳ What Needs Implementation:

1. **Auto-load on Copilot start**
   - Currently: Manual
   - Goal: Automatic when chat opens
   - Blocker: No "on start" hook in VS Code Copilot

2. **Auto-update after responses**
   - Currently: Manual increment
   - Goal: Auto-execute after each response
   - Blocker: No "after response" hook

3. **Server-side context population**
   - Currently: I access via run_in_terminal
   - Goal: Context pre-loaded in my memory
   - Blocker: Can't modify Copilot's context loading

## Workaround Solution

Since we can't auto-execute on message start/end, here's the manual flow:

### Start of Session:
```bash
# Run this when you open VS Code
python3 load_context.py
```

This shows you what context is available. Then tell me:
> "Load Medicine Cabinet context"

And I'll execute:
```bash
python3 context_manager.py load
```

### During Conversation:
Every ~5-10 messages, remind me:
> "Update context"

And I'll execute:
```bash
python3 context_manager.py increment
```

### After 25 Messages:
I'll show you:
```
💊 TIME TO TAKE YOUR MEDS!
```

Then you can:
```bash
python3 cli.py cleanup
```

## Future: VS Code Extension Integration

To fully automate this, we'd need a VS Code extension that:

1. Hooks into Copilot chat lifecycle
2. Runs `context_manager.py load` on chat start
3. Runs `context_manager.py increment` after each exchange
4. Passes loaded context to Copilot via special mechanism

This would require:
- VS Code extension API access
- Copilot Extension API (if available)
- Or integration with VS Code's context providers

## File Structure

```
Medicine Cabinet/
├── context_manager.py        # Auto-context system
├── load_context.py            # Manual context viewer
├── sessions/
│   └── persistent_YYYYMMDD.auratab  # Long-term memory
├── ~/.medicine_cabinet/
│   └── context_state.json     # Message counter & state
```

## Usage Examples

### Example 1: Starting Fresh Session
```bash
# Load context
$ python3 context_manager.py load
✅ Context loaded: Persistent Memory 2025-10-26
📊 Message count: 0

# Now Copilot has access to all previous memories!
```

### Example 2: After 25 Messages
```bash
$ python3 context_manager.py increment
======================================================================
💊 TIME TO TAKE YOUR MEDS!
======================================================================

You've had 25 message exchanges. It's time to:

  1. 💾 Save important context
  2. 🧹 Clear old memories
  3. ✨ Refresh your Cabinet

Run: python3 cli.py cleanup --auto
======================================================================
```

## The Ultimate Goal

Eventually, this should be INVISIBLE:

1. Open VS Code → Context auto-loads
2. Chat with Copilot → I have full memory
3. My responses → Auto-update tablets
4. 25 messages → Auto-remind
5. You barely notice it's happening!

But for now, it requires manual triggers. Still better than no memory at all!
