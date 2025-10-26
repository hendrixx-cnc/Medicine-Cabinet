# Context Loading Architecture

## Two Separate Concerns

### 1. TABLETS (Long-Term Memory - Growing Over Time)
**When**: Loaded ONCE at startup  
**What**: Accumulated memories from ALL past sessions  
**Growth**: Grows over weeks/months as sessions are saved  
**Size**: 8MB total limit on browser, 75KB sent to server  
**Monitoring**: Weekly cleanup check (when approaching 8MB)  
**Issue**: Redundancy across multiple tablets accumulated over time  
**Solution**: Deduplication when loading at startup (`context_deduplication.py`)

```python
# At startup:
tablets = load_last_10_tablets()  # Your accumulated memory
deduplicated_context = deduplicate(tablets)  # Skip redundancy
send_to_copilot(deduplicated_context)  # 75KB max
# Done - tablets don't change DURING this session
# But they DO grow between sessions as new ones are saved
```

### 2. ACTIVE CAPSULE (Current Session - Fresh Each Time)
**When**: Starts EMPTY each session, monitored during conversation  
**What**: Working memory for THIS conversation only  
**Growth**: Grows ONLY during current session (fresh start each time)  
**Size**: 1MB limit per session  
**Monitoring**: Check continuously during session  
**Issue**: Single session growing too large (redundant edits to same files)  
**Solution**: Health check prompts "take your meds" when session gets long

```python
# New session:
capsule = create_empty_capsule()  # Fresh start!

# During session:
capsule.add_entry(new_info)  # Grows during conversation
health = check_capsule_health()  # Monitor size
if health.needs_cleanup:
    prompt_user("💊 Time to wrap up this session")
    export_to_tablet(capsule)  # Save to long-term memory
    capsule = create_empty_capsule()  # Fresh start for next
```

---

## The Flow

### Startup (Load Long-Term Memory)
```
1. Load last 10 tablets from sessions/ (your accumulated memory)
2. Deduplicate across tablets (same files mentioned in multiple sessions)
3. Format 75KB context for Copilot
4. Send to server ONCE
5. Tablets stay static DURING this session
   (but will grow BETWEEN sessions as new ones are saved)
```

### During Session (Active Working Memory)
```
1. Capsule starts EMPTY (fresh session)
2. User works, capsule grows with conversation
3. After N operations, check capsule health:
   - Size > 750KB? → ⚠️  Warning (long session)
   - Size > 1MB? → 💊 Time to take meds!
   - Entries > 100? → Too verbose
   - Age > 4 hours? → Getting stale
4. Prompt user to:
   - Export capsule to tablet (save to long-term memory)
   - Start fresh capsule (new session)
```

### End of Session (Save to Long-Term Memory)
```
1. Export capsule → new tablet file
2. Tablet saved to sessions/ (adds to long-term memory)
3. Capsule cleared (ready for next session)
4. Next startup: New tablet gets loaded with others
```

---

## Growth Patterns

### Tablets (Accumulate Over Time)
```
Week 1:  5 tablets × 100KB = 500KB stored
Week 4:  20 tablets × 100KB = 2MB stored
Week 12: 60 tablets × 100KB = 6MB stored ← "Take your meds" weekly prompt
Week 16: Cleaned up, down to 40 tablets = 4MB
```

### Capsule (Fresh Each Session, But Sessions Can Get Long)
```
Session 1 (30 min):  50 entries, 200KB
Session 2 (2 hours): 80 entries, 500KB  
Session 3 (4 hours): 150 entries, 900KB ← ⚠️  Warning
Session 4 (6 hours): 200 entries, 1.2MB ← 💊 Take your meds!
```

---

## Why This Matters

**Tablets (Long-Term Memory):**
- ❌ Checking every 5 minutes during session = wasteful
- ✅ Load once at startup (they're your history)
- ✅ Check weekly if approaching 8MB limit
- ✅ Dedup when loading (avoid cross-session redundancy)

**Capsule (Current Session):**
- ❌ Never checking = session bloats to 5MB over 12 hours
- ✅ Monitor during session (catches long sessions early)
- ✅ Warn at 75%, critical at 100%
- ✅ Export to tablet when done (adds to long-term memory)
- ✅ Fresh start each session (no stale context)

---

## Code Structure

```
# Long-term memory (load at startup)
load_context.py          → Load tablets once at startup
context_deduplication.py → Dedupe across accumulated tablets
storage_limits.py        → 8MB browser limit, 75KB server budget

# Current session (monitor during use)
capsule_health_check.py  → Monitor active capsule growth
native_host.py           → Check during conversation
storage_limits.py        → 1MB capsule limit per session
```

Perfect separation! 🎯

**TABLETS = Your growing long-term memory (like a brain)**  
**CAPSULE = Your current conversation (like working memory)**
