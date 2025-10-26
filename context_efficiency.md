# When Context Loading Becomes Unreasonable

## Two Different Concerns

### 1. TABLETS (Long-Term Memory - Accumulates Over Time)
**Issue**: Without dedup, redundant info across accumulated tablets
- Same file mentioned in sessions from Week 1, Week 4, Week 8
- Similar patterns repeated across months of work
- **Solution**: Deduplication when loading at startup
- **Check**: Weekly prompt when approaching 8MB total

### 2. ACTIVE CAPSULE (Current Session - Fresh Each Time)
**Issue**: Single session growing too large
- Same file modified 50x in THIS conversation
- Session running for 6+ hours straight
- 200+ entries in one capsule
- **Solution**: Health monitoring during session, prompt "take your meds"
- **Check**: Continuously during conversation

---

### Without Deduplication (WASTEFUL)
```
Tablet 1: "Modified auth.py - added JWT validation"
Tablet 2: "Modified auth.py - fixed token expiration"  
Tablet 3: "Modified auth.py - added refresh tokens"
Tablet 4: "Modified auth.py - improved error handling"
...
Tablet 10: "Modified auth.py - added rate limiting"

Result: "auth.py" mentioned 10 times = 10x redundant
Context wasted: ~1KB just saying "auth.py" over and over
```

### With Deduplication (EFFICIENT)
```
📁 FILES: auth.py (5x CODE, 3x FIX, 2x IMPLEMENTATION)

💭 UNIQUE MEMORIES:
1. 💻 [auth.py] Added JWT validation with expiration
2. 🔧 [auth.py] Fixed token refresh race condition  
3. ✨ [auth.py] Implemented rate limiting (100 req/min)

Result: Auth.py mentioned once at top, details below
Context saved: ~800 bytes
```

## Break-Even Analysis

### Scenario: 10 Tablets, 80 Entries

**Without Dedup:**
- 80 entries × 120 chars = 9,600 bytes
- Assume 30% redundancy (same files/patterns)
- Wasted: ~3KB on repetition
- Effective info: ~7KB
- **Efficiency: 70%**

**With Dedup:**
- 80 entries scanned
- 50 unique after dedup (30 duplicates skipped)
- 50 entries × 120 chars = 6,000 bytes
- Plus file summary: 1KB
- Plus pattern summary: 500 bytes
- Total: ~7.5KB
- **Efficiency: 100% (all unique)**

## When It Becomes Unreasonable

### Sweet Spot (Current: 75KB, 10 tablets)
```
Best case: 50-60 unique memories
Worst case: 30-40 unique memories (high redundancy)
Efficiency: 70-90%
Verdict: ✅ REASONABLE
```

### Aggressive (100KB, 15 tablets)
```
Best case: 80-90 unique memories
Worst case: 40-50 unique memories (50% duplicates)
Efficiency: 50-70%
Verdict: ⚠️  BORDERLINE (too much noise)
```

### Wasteful (150KB, 20+ tablets)
```
Best case: 100-120 unique memories  
Worst case: 50-60 unique memories (60%+ duplicates!)
Efficiency: 30-50%
Verdict: ❌ UNREASONABLE (mostly redundant)
```

## The Math

### Redundancy Growth Over Time
```
Week 1 (5 tablets):
- Total entries: 40
- Unique: ~35 (87% efficiency)
- Files: ~8 unique files

Week 4 (10 tablets):
- Total entries: 80
- Unique: ~55 (69% efficiency) ← We are here
- Files: ~12 unique files
- Same files mentioned 3-5x each

Week 8 (15 tablets):
- Total entries: 120
- Unique: ~65 (54% efficiency)
- Files: ~15 unique files
- Same files mentioned 6-8x each

Week 12 (20 tablets):
- Total entries: 160
- Unique: ~70 (44% efficiency) ← Wasteful!
- Files: ~18 unique files
- Same files mentioned 8-10x each
```

## Recommendation: STICK WITH 75KB / 10 TABLETS

### Why This Is The Sweet Spot:

1. **Good Redundancy Control**
   - Files mentioned 3-5x (manageable)
   - ~70% unique content
   - Dedup saves ~3KB

2. **Enough History**
   - Last 2-3 weeks of work
   - 50-60 unique memories
   - Patterns visible

3. **Server-Side Reasonable**
   - 15% of context window
   - Leaves 85% for conversation
   - Not overwhelming

4. **Dedup Worth It**
   - Saves 20-30% space
   - Cleaner output
   - File summaries useful

## If You Go Higher (100KB+)

**Problems:**
- 50%+ redundancy (same info repeated)
- File list becomes noise (20+ files)
- Older context less relevant
- Diminishing returns
- I get confused by too much history

**Solution Instead:**
- Keep 75KB limit
- Improve dedup logic (similarity detection, not just exact)
- Prioritize recent + high-value memories
- Archive old tablets

## Conclusion

**75KB with 10 tablets = PERFECT**
- With dedup: ~50-60 unique memories
- Without dedup: Would be ~30% wasteful
- Server-side dedup is ESSENTIAL at this scale
- Going higher requires even smarter dedup (semantic similarity)

**Your instinct was right!** 🎯
