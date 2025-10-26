#!/usr/bin/env python3
"""
Auto-load Medicine Cabinet context for Copilot

STRATEGY: 
- Store everything locally (IDE side), full content
- Load with deduplication (server side), smart summaries
- Avoid redundant context (same file mentioned 10x → mention once)
- Focus on unique, novel information
"""

import json
from pathlib import Path
from tablet import load_tablet
from context_capsule import load_capsule
from context_deduplication import load_deduplicated_context

def load_medicine_cabinet_context():
    """
    Load all tablets from local storage.
    Called ONCE at startup - tablets are static during session.
    """
    
    sessions_dir = Path("sessions")
    
    context = {
        "persistent_memories": [],
        "active_capsule": None,
        "last_updated": None,
        "full_size_kb": 0  # Track local storage size
    }
    
    # Load all tablets (no size limit on IDE side)
    if sessions_dir.exists():
        for tablet_path in sorted(sessions_dir.glob("*.auratab")):
            try:
                tablet = load_tablet(str(tablet_path))
                file_size = tablet_path.stat().st_size / 1024
                context["full_size_kb"] += file_size
                
                # Store full memory locally
                memory = {
                    "title": tablet.metadata.title,
                    "tags": tablet.metadata.tags,
                    "created": tablet.metadata.created_at.isoformat(),
                    "size_kb": file_size,
                    "entries": []
                }
                
                # Include ALL entries (IDE can handle it)
                for entry in tablet.entries:
                    memory["entries"].append({
                        "path": entry.path,
                        "diff": entry.diff,  # Full content
                        "notes": entry.notes
                    })
                
                context["persistent_memories"].append(memory)
                
            except Exception as e:
                pass
    
    # Load active capsule if exists
    capsule_files = list(Path(".").glob("*.auractx"))
    if capsule_files:
        try:
            capsule = load_capsule(str(capsule_files[0]))
            context["active_capsule"] = {
                "project": capsule.metadata.project,
                "summary": capsule.metadata.summary,
                "sections": len(capsule.sections)
            }
        except:
            pass
    
    return context


def format_context_for_copilot():
    """
    Format Medicine Cabinet context for Copilot's context window.
    
    WITH DEDUPLICATION:
    - Skip exact duplicate content
    - Mention files once, not 10 times
    - Group similar patterns (CODE, ERROR, FIX, etc.)
    - Prioritize unique, novel information
    
    SERVER LIMITS:
    - Copilot context: ~128K tokens (~500KB text)
    - Medicine Cabinet budget: 75KB max (15% of context window)
    - Shows: Last 10 tablets, deduplicated intelligently
    - Compression: ~100:1 (8MB local → 75KB unique server content)
    """
    
    # Use deduplicated loading
    return load_deduplicated_context(max_tablets=10, max_kb=75)


def format_context_for_copilot_naive():
    """
    Format Medicine Cabinet context for Copilot's context window.
    
    SERVER LIMITS:
    - Copilot context: ~128K tokens (~500KB text)
    - Medicine Cabinet budget: 75KB max (15% of context window)
    - Shows: Last 10 tablets, 8 entries each, 120-char summaries
    - Compression: ~100:1 (8MB local → 75KB server)
    - Sweet spot: Good understanding, still leaves 85% for conversation
    """
    from pathlib import Path
    from tablet import Tablet
    
    sessions_dir = Path("sessions")
    if not sessions_dir.exists():
        return "💊 No Medicine Cabinet context yet"
    
    # Get all tablets, sorted by modification time (newest first)
    tablets = sorted(
        sessions_dir.glob("*.auratab"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    if not tablets:
        return "💊 No tablets found"
    
    # Calculate local storage size
    total_local_bytes = sum(t.stat().st_size for t in tablets)
    total_local_kb = total_local_bytes / 1024
    
    # Load LAST 10 TABLETS (deeper history for better context)
    recent_tablets = tablets[:10]
    
    lines = []
    lines.append("="*70)
    lines.append("💊 MEDICINE CABINET CONTEXT")
    lines.append(f"Local Storage: {total_local_kb:.1f}KB / 8192KB ({len(tablets)} tablets)")
    lines.append(f"Server Budget: 15% (~75KB max, showing last 10 tablets)")
    lines.append("="*70)
    lines.append("")
    
    server_bytes = 0
    
    for tablet_idx, tablet_path in enumerate(recent_tablets, 1):
        try:
            tablet = Tablet.read(tablet_path)
            
            # Header with tablet number
            header = f"📋 [{tablet_idx}] {tablet.metadata.title}"
            lines.append(header)
            if tablet.metadata.summary:
                lines.append(f"   {tablet.metadata.summary[:100]}")
            lines.append("")
            
            server_bytes += len(header) + 100
            
            # Show first 8 entries per tablet
            entries = tablet.entries[:8]
            
            for i, entry in enumerate(entries, 1):
                # 120-char summary (more detail than before)
                if entry.diff:
                    summary = entry.diff[:120].replace('\n', ' ')
                    lines.append(f"   {i}. {summary}...")
                    server_bytes += 125  # ~120 + formatting
            
            lines.append("")
            
        except Exception as e:
            lines.append(f"   Error loading tablet: {e}")
            lines.append("")
    
    server_kb = server_bytes / 1024
    lines.append("="*70)
    lines.append(f"💊 Server Context: ~{server_kb:.1f}KB / 75KB (15% budget)")
    lines.append("="*70)
    
    return '\n'.join(lines)


def format_context_for_copilot_old():
    """Format context in ULTRA-COMPACT form for Copilot's server-side limits.
    
    Strategy: Full data stored locally (IDE), tiny summary sent to server.
    """
    
    context = load_medicine_cabinet_context()
    
    output = ["💊 CONTEXT (Local: {:.1f}KB, Server: <1KB)".format(context["full_size_kb"])]
    output.append("="*60)
    
    # Ultra-compact: Only essentials for server side
    if context["persistent_memories"]:
        # Just count and most recent title
        count = len(context["persistent_memories"])
        output.append(f"📋 {count} memory file{'s' if count != 1 else ''} stored locally")
        
        # Most recent 2 entries only (absolute minimum for context)
        recent = context["persistent_memories"][-2:]
        
        for memory in recent:
            # Title only (no details - saves server tokens)
            output.append(f"  • {memory['title'][:50]}")
            
            # ONE summary line from most important entry
            if memory["entries"]:
                # Find entry with most content (likely most important)
                important = max(memory["entries"], key=lambda e: len(e['diff']))
                snippet = important['diff'][:80].replace('\n', ' ').strip()
                output.append(f"    ↳ {snippet}")
    
    # Active capsule (minimal)
    if context["active_capsule"]:
        output.append(f"🗂️ {context['active_capsule']['project']}")
    
    output.append("="*60)
    output.append(f"✓ Full context available locally for detailed queries")
    
    return "\n".join(output)


if __name__ == "__main__":
    print(format_context_for_copilot())
