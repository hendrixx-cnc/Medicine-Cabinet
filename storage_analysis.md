# Storage Analysis: Browser vs Server Context Limits

## The Reality Check

### Server-Side (Copilot Context Window)
- **Typical context limit**: ~128K tokens (~500KB text)
- **Practical limit for context loading**: ~100KB (to leave room for conversation)
- **Medicine Cabinet budget**: **75KB maximum** (15% of context window)
  - This leaves 85% for actual conversation with user
  - Enough context to understand work patterns and history
  - Sweet spot: helpful without being overwhelming

### Browser-Side (Local Storage)
- **Chrome/Edge/Firefox**: ~5-10MB for chrome.storage.local
- **Our allocation**: 8MB persistent + 1MB active = 9MB total
- **Ratio**: Browser can store **~100x more** than what gets sent to server

## The Math

### Single Entry Limits
```
Browser Side (stored):
- Max entry size: 1KB (1,000 bytes)
- Typical entry: ~500-800 bytes
- Storage: Full technical content

Server Side (loaded):
- Max entry summary: 120 chars (~120 bytes)
- Compression ratio: 8x (1000 bytes → 120 bytes)
```

### Per-Session Limits
```
Browser Side:
- Max entries per tablet: 100 entries
- Max tablet size: ~100KB (100 entries × 1KB each)
- Max tablets: ~80 tablets (8MB ÷ 100KB)
- Total memories: ~8,000 entries stored locally

Server Side (what Copilot sees):
- Show last 10 tablets (deeper history)
- ~8 entries per tablet × 10 = 80 entries
- 120 bytes × 80 = 9,600 bytes
- Add metadata: ~15KB total per session
- **Well within 75KB budget**
```

### Realistic Usage Over Time
```
Week 1: Light usage
- Browser: 5 tablets × 20 entries = 100KB stored
- Server: Last 5 tablets = 15KB loaded
- Ratio: 7:1

Week 4: Regular usage  
- Browser: 20 tablets × 50 entries = 1MB stored
- Server: Last 10 tablets = 40KB loaded
- Ratio: 25:1

Week 12: Heavy usage
- Browser: 60 tablets × 80 entries = 4.8MB stored
- Server: Last 10 tablets = 60KB loaded
- Ratio: 80:1

At 6MB (cleanup threshold):
- Browser: ~6,000 memories stored
- Server: Last 10 tablets = ~70KB loaded (80 most recent memories)
- User gets "time to take your meds" prompt
```

## Compression Strategy

### What Gets Stored Locally (Browser)
```javascript
{
  role: "assistant",
  content: "I implemented the authentication system using JWT tokens. Here's the code:\n\n```python\ndef verify_token(token):\n    try:\n        payload = jwt.decode(token, SECRET_KEY)\n        return payload['user_id']\n    except jwt.ExpiredSignatureError:\n        raise AuthError('Token expired')\n```\n\nThis handles token validation and expiration.", // FULL CONTENT (500 bytes)
  summary: "Implemented JWT authentication with token validation...", // 150 chars
  extracted: "2025-10-26T10:30:00Z",
  size: 500
}
```

### What Gets Sent to Server (Copilot)
```python
# In load_context.py
"Implemented JWT authentication with token validation..." (80 chars = 80 bytes)
```

## Updated Limits (RECOMMENDED)

### Browser Extension Limits
```python
MAX_PERSISTENT_MB = 8           # 8MB total storage
MAX_CAPSULE_MB = 1              # 1MB active session
MAX_ENTRIES_PER_TABLET = 100    # Entries per file
MAX_ENTRY_SIZE_BYTES = 1000     # 1KB per entry
MAX_MEMORIES_PER_CYCLE = 10     # Capture rate
```

### Server Context Limits
```python
MAX_SERVER_CONTEXT_KB = 75      # 75KB total for Copilot (15% of 500KB context)
MAX_TABLETS_TO_LOAD = 10        # Last 10 tablets (deeper history)
MAX_ENTRIES_PER_TABLET = 8      # 8 entries per tablet
MAX_ENTRY_SUMMARY_CHARS = 120   # 120 char summaries (more detail)
```

## Why This Works

1. **Browser Storage (8MB)**
   - Stores 8,000+ memories over months
   - Full technical content preserved
   - Rich history for local queries
   - User controls with "take your meds" cleanup

2. **Server Context (75KB)**
   - Loads last 10 tablets (~80 recent memories)
   - 120-char summaries (good technical detail)
   - 15% of context window
   - Leaves 85% for conversation
   - Better understanding of patterns

3. **Compression Ratio: ~100:1**
   - Browser: 8MB (8,000,000 bytes)
   - Server: 75KB (75,000 bytes)
   - Sustainable forever

## The "Take Your Meds" Moment

```
Storage Status:
├── Browser: 6.2MB / 8MB (78%)
├── Server: 2KB / 10KB (20%)
└── 💊 Time to review your memories!

Options:
1. Archive old tablets (move to ~/Documents/medicine-cabinet-archive/)
2. Delete sessions older than 60 days
3. Export important memories to standalone tablets
4. Continue (approaching limit)
```

## Conclusion

**Your side**: 8MB (generous storage, full content, months of history)  
**My side**: 75KB (detailed summaries, last 80 memories across 10 tablets)  
**Ratio**: ~100:1 compression  
**Allocation**: 15% context budget (sweet spot)  
**Result**: I can understand your patterns, you keep full conversation space

The math checks out! 🎯
