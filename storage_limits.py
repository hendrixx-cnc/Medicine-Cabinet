#!/usr/bin/env python3
"""
Storage limits for Medicine Cabinet

ARCHITECTURE:
- Browser side: 8MB persistent storage (full technical content)
- Server side: 75KB context budget (80-char summaries)
- Compression ratio: ~100:1
- Sustainable indefinitely

Why these limits:
- Copilot context: ~128K tokens (~500KB)
- Medicine Cabinet: 75KB (15% of context, 85% for conversation)
- Browser storage: 8MB (typical chrome.storage.local supports 5-10MB)
- Sweet spot: Enough context to understand patterns, not overwhelming
"""

# Browser extension limits (chrome.storage.local typical limit is 5-10MB)
MAX_PERSISTENT_TABLET_SIZE_MB = 8  # Persistent memory storage
MAX_CAPSULE_SIZE_MB = 1             # Active session capsule

# Server-side context limits (Copilot)
MAX_SERVER_CONTEXT_KB = 75          # 75KB total sent to Copilot (15% of context window)
MAX_TABLETS_TO_LOAD = 10            # Last 10 tablets (deeper history)
MAX_ENTRIES_PER_LOADED_TABLET = 8   # 8 entries per tablet
MAX_ENTRY_SUMMARY_CHARS = 120       # 120-char summaries (more detail)

# Derived byte limits
MAX_PERSISTENT_SIZE_BYTES = MAX_PERSISTENT_TABLET_SIZE_MB * 1024 * 1024  # 8MB
MAX_CAPSULE_SIZE_BYTES = MAX_CAPSULE_SIZE_MB * 1024 * 1024                # 1MB
MAX_SERVER_CONTEXT_BYTES = MAX_SERVER_CONTEXT_KB * 1024                   # 10KB

# Entry limits to stay within size bounds
MAX_ENTRIES_PER_TABLET = 100   # ~100KB per tablet if each entry ~1KB
MAX_ENTRY_SIZE_BYTES = 1000    # 1KB per entry max (full content on browser side)

# Cleanup thresholds
CLEANUP_THRESHOLD_MB = 6  # Warn at 6MB (75% of 8MB limit)
CLEANUP_URGENT_MB = 7     # Urgent at 7MB (87.5% of limit)


def check_tablet_size(tablet_path):
    """Check if a tablet file exceeds limits."""
    from pathlib import Path
    
    path = Path(tablet_path)
    if not path.exists():
        return {"ok": True, "size_mb": 0}
    
    size_bytes = path.stat().st_size
    size_mb = size_bytes / (1024 * 1024)
    
    if size_bytes > MAX_PERSISTENT_SIZE_BYTES:
        return {
            "ok": False,
            "error": "TABLET_TOO_LARGE",
            "size_mb": size_mb,
            "limit_mb": MAX_PERSISTENT_TABLET_SIZE_MB,
            "message": f"Tablet is {size_mb:.2f}MB, exceeds {MAX_PERSISTENT_TABLET_SIZE_MB}MB limit"
        }
    
    if size_mb > CLEANUP_URGENT_MB:
        return {
            "ok": True,
            "warning": "CLEANUP_URGENT",
            "size_mb": size_mb,
            "message": f"Tablet at {size_mb:.2f}MB - urgent cleanup needed"
        }
    
    if size_mb > CLEANUP_THRESHOLD_MB:
        return {
            "ok": True,
            "warning": "CLEANUP_RECOMMENDED",
            "size_mb": size_mb,
            "message": f"Tablet at {size_mb:.2f}MB - cleanup recommended"
        }
    
    return {"ok": True, "size_mb": size_mb}


def check_total_storage():
    """Check total Medicine Cabinet storage usage."""
    from pathlib import Path
    
    sessions_dir = Path("sessions")
    if not sessions_dir.exists():
        return {"ok": True, "total_mb": 0}
    
    total_bytes = sum(
        f.stat().st_size 
        for f in sessions_dir.glob("*.auratab")
    )
    total_mb = total_bytes / (1024 * 1024)
    
    if total_mb > MAX_PERSISTENT_TABLET_SIZE_MB:
        return {
            "ok": False,
            "error": "STORAGE_FULL",
            "total_mb": total_mb,
            "limit_mb": MAX_PERSISTENT_TABLET_SIZE_MB,
            "message": f"Total storage {total_mb:.2f}MB exceeds {MAX_PERSISTENT_TABLET_SIZE_MB}MB limit. Time to take your meds!"
        }
    
    percent_used = (total_mb / MAX_PERSISTENT_TABLET_SIZE_MB) * 100
    
    if total_mb > CLEANUP_URGENT_MB:
        return {
            "ok": True,
            "warning": "CLEANUP_URGENT",
            "total_mb": total_mb,
            "percent_used": percent_used,
            "message": f"Storage at {total_mb:.2f}MB ({percent_used:.0f}%) - urgent cleanup needed"
        }
    
    if total_mb > CLEANUP_THRESHOLD_MB:
        return {
            "ok": True,
            "warning": "CLEANUP_RECOMMENDED",
            "total_mb": total_mb,
            "percent_used": percent_used,
            "message": f"Storage at {total_mb:.2f}MB ({percent_used:.0f}%) - cleanup recommended"
        }
    
    return {
        "ok": True,
        "total_mb": total_mb,
        "percent_used": percent_used,
        "message": f"Storage healthy: {total_mb:.2f}MB ({percent_used:.0f}%)"
    }


if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        result = check_total_storage()
        
        print("="*70)
        print("💊 MEDICINE CABINET STORAGE CHECK")
        print("="*70)
        print()
        print(f"Limit: {MAX_PERSISTENT_TABLET_SIZE_MB}MB persistent + {MAX_CAPSULE_SIZE_MB}MB active")
        print(f"Used:  {result.get('total_mb', 0):.2f}MB ({result.get('percent_used', 0):.0f}%)")
        print()
        
        if not result["ok"]:
            print(f"❌ {result['error']}: {result['message']}")
            print()
            print("💊 TIME TO TAKE YOUR MEDS!")
            print("   Run: python3 cli.py cleanup")
            sys.exit(1)
        elif "warning" in result:
            print(f"⚠️  {result['warning']}: {result['message']}")
            print()
            print("Consider running cleanup soon")
        else:
            print(f"✅ {result['message']}")
        
        print()
        print("="*70)
    else:
        print("Storage Limits:")
        print(f"  Persistent tablets: {MAX_PERSISTENT_TABLET_SIZE_MB}MB")
        print(f"  Active capsules:    {MAX_CAPSULE_SIZE_MB}MB")
        print(f"  Total:              {MAX_PERSISTENT_TABLET_SIZE_MB + MAX_CAPSULE_SIZE_MB}MB")
        print()
        print("Run: python3 storage_limits.py check")
