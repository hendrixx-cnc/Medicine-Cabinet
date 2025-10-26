#!/usr/bin/env python3
"""
Auto-load Medicine Cabinet context for Copilot
Run this at the start of each session to populate context
"""

import json
from pathlib import Path
from tablet import load_tablet
from context_capsule import load_capsule

def load_medicine_cabinet_context():
    """Load all tablets and capsules into a compact context summary."""
    
    sessions_dir = Path("sessions")
    
    context = {
        "message_count": 0,
        "persistent_memories": [],
        "active_capsule": None,
        "last_updated": None
    }
    
    # Load all tablets (persistent memories)
    if sessions_dir.exists():
        for tablet_path in sorted(sessions_dir.glob("*.auratab")):
            try:
                tablet = load_tablet(str(tablet_path))
                
                # Extract compact memory
                memory = {
                    "title": tablet.metadata.title,
                    "tags": tablet.metadata.tags,
                    "created": tablet.metadata.created_at.isoformat(),
                    "entries": []
                }
                
                # Only include contextually important entries
                for entry in tablet.entries:
                    if len(entry.diff) > 50:  # Skip trivial entries
                        memory["entries"].append({
                            "path": entry.path,
                            "summary": entry.diff[:200] + "..." if len(entry.diff) > 200 else entry.diff,
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
    """Format context in a compact, Copilot-friendly format."""
    
    context = load_medicine_cabinet_context()
    
    output = ["=" * 70]
    output.append("💊 MEDICINE CABINET - CONTEXT LOADED")
    output.append("=" * 70)
    output.append("")
    
    # Show persistent memories
    if context["persistent_memories"]:
        output.append(f"📋 Persistent Memories: {len(context['persistent_memories'])}")
        output.append("")
        
        for memory in context["persistent_memories"]:
            output.append(f"  • {memory['title']}")
            output.append(f"    Tags: {', '.join(memory['tags'])}")
            output.append(f"    Entries: {len(memory['entries'])}")
            
            # Show first entry as preview
            if memory["entries"]:
                first_entry = memory["entries"][0]
                output.append(f"    Preview: {first_entry['path']}")
                output.append(f"             {first_entry['summary'][:80]}")
            output.append("")
    
    # Show active capsule
    if context["active_capsule"]:
        output.append("🗂️  Active Capsule:")
        output.append(f"  Project: {context['active_capsule']['project']}")
        output.append(f"  Summary: {context['active_capsule']['summary']}")
        output.append("")
    
    output.append("=" * 70)
    output.append("✅ Context loaded. Ready to assist with full memory.")
    output.append("=" * 70)
    
    return "\n".join(output)


if __name__ == "__main__":
    print(format_context_for_copilot())
