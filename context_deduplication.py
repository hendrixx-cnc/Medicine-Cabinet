#!/usr/bin/env python3
"""
Context deduplication for server-side loading

PROBLEM: Without dedup, we waste context window on repetitive info
- Same file mentioned 10 times → 10x redundant
- Similar code patterns → wasted space
- Repeated decisions → noise

SOLUTION: Smart deduplication before sending to server
"""

from pathlib import Path
from typing import List, Dict, Set
from collections import defaultdict
import hashlib
from tablet import Tablet


def deduplicate_memories(tablets: List[Path], max_kb: int = 75) -> Dict:
    """
    Load tablets and deduplicate before sending to server.
    
    Strategy:
    1. Track unique content by hash (avoid exact duplicates)
    2. Track mentioned files (show once, not 10 times)
    3. Group similar patterns (code, decisions, errors)
    4. Prioritize: Recent > Old, Unique > Repeated
    """
    
    seen_hashes: Set[str] = set()
    seen_files: Set[str] = set()
    
    result = {
        'unique_memories': [],
        'file_summary': defaultdict(list),
        'patterns': defaultdict(int),
        'stats': {
            'total_entries': 0,
            'unique_entries': 0,
            'duplicate_skipped': 0,
            'size_bytes': 0
        }
    }
    
    current_size = 0
    max_bytes = max_kb * 1024
    
    for tablet_path in tablets:
        try:
            tablet = Tablet.read(tablet_path)
            
            for entry in tablet.entries:
                result['stats']['total_entries'] += 1
                
                # Check if we're at size limit
                if current_size >= max_bytes:
                    break
                
                # Hash the content for dedup
                content_hash = hashlib.md5(entry.diff.encode()).hexdigest()
                
                # Skip exact duplicates
                if content_hash in seen_hashes:
                    result['stats']['duplicate_skipped'] += 1
                    continue
                
                seen_hashes.add(content_hash)
                
                # Extract mentioned files
                files_in_entry = extract_file_references(entry.diff)
                new_files = [f for f in files_in_entry if f not in seen_files]
                
                # Track patterns
                pattern = detect_pattern(entry.diff)
                result['patterns'][pattern] += 1
                
                # Create summary (120 chars, but dedupe context)
                summary = create_smart_summary(
                    entry.diff, 
                    new_files=new_files,
                    pattern=pattern
                )
                
                # Add to results
                memory = {
                    'content': summary,
                    'files': new_files,
                    'pattern': pattern,
                    'size': len(summary)
                }
                
                result['unique_memories'].append(memory)
                result['stats']['unique_entries'] += 1
                current_size += len(summary)
                
                # Mark files as seen
                seen_files.update(new_files)
                
                # Track file activity
                for f in new_files:
                    result['file_summary'][f].append(pattern)
        
        except Exception as e:
            continue
    
    result['stats']['size_bytes'] = current_size
    return result


def extract_file_references(text: str) -> List[str]:
    """Extract file paths from text."""
    import re
    
    # Match common file patterns
    patterns = [
        r'\b[\w\-\/]+\.(py|js|ts|jsx|tsx|json|md|html|css|yaml|yml)\b',
        r'`([^`]+\.(py|js|ts|jsx|tsx|json|md|html|css))`',
    ]
    
    files = set()
    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            if match.group(1) if match.lastindex else match.group(0):
                files.add(match.group(1) if match.lastindex else match.group(0))
    
    return list(files)


def detect_pattern(text: str) -> str:
    """Detect what type of memory this is."""
    text_lower = text.lower()
    
    if '```' in text:
        return 'CODE'
    elif any(word in text_lower for word in ['error', 'exception', 'failed', 'bug']):
        return 'ERROR'
    elif any(word in text_lower for word in ['implemented', 'created', 'added', 'refactored']):
        return 'IMPLEMENTATION'
    elif any(word in text_lower for word in ['decided', 'chose', 'strategy', 'approach']):
        return 'DECISION'
    elif any(word in text_lower for word in ['fixed', 'resolved', 'solved']):
        return 'FIX'
    else:
        return 'OTHER'


def create_smart_summary(text: str, new_files: List[str], pattern: str) -> str:
    """
    Create intelligent summary that avoids redundancy.
    
    If files already mentioned before, don't repeat them.
    Focus on the NOVEL information.
    """
    
    # Start with pattern prefix
    prefix_map = {
        'CODE': '💻',
        'ERROR': '❌',
        'IMPLEMENTATION': '✨',
        'DECISION': '🎯',
        'FIX': '🔧',
        'OTHER': '📝'
    }
    
    prefix = prefix_map.get(pattern, '📝')
    
    # If new files, mention them
    if new_files:
        files_str = ', '.join(new_files[:3])  # Max 3 files
        if len(new_files) > 3:
            files_str += f' +{len(new_files) - 3} more'
        summary = f"{prefix} [{files_str}] {text[:80]}"
    else:
        # No new files, just content
        summary = f"{prefix} {text[:110]}"
    
    return summary[:120]  # Hard cap at 120 chars


def format_deduplicated_context(dedup_result: Dict) -> str:
    """Format deduplicated context for Copilot."""
    
    lines = []
    lines.append("="*70)
    lines.append("💊 MEDICINE CABINET CONTEXT (Deduplicated)")
    
    stats = dedup_result['stats']
    lines.append(f"Unique: {stats['unique_entries']} / {stats['total_entries']} entries")
    lines.append(f"Skipped: {stats['duplicate_skipped']} duplicates")
    lines.append(f"Size: {stats['size_bytes'] / 1024:.1f}KB / 75KB")
    lines.append("="*70)
    lines.append("")
    
    # File summary (which files were worked on)
    if dedup_result['file_summary']:
        lines.append("📁 FILES WORKED ON:")
        for file, patterns in list(dedup_result['file_summary'].items())[:10]:
            pattern_counts = {}
            for p in patterns:
                pattern_counts[p] = pattern_counts.get(p, 0) + 1
            pattern_str = ', '.join(f"{k}({v})" for k, v in pattern_counts.items())
            lines.append(f"   {file}: {pattern_str}")
        lines.append("")
    
    # Pattern summary
    if dedup_result['patterns']:
        lines.append("📊 ACTIVITY PATTERNS:")
        for pattern, count in sorted(dedup_result['patterns'].items(), 
                                     key=lambda x: x[1], reverse=True):
            lines.append(f"   {pattern}: {count} entries")
        lines.append("")
    
    # Unique memories (chronological, most recent first)
    lines.append("💭 UNIQUE MEMORIES:")
    for i, memory in enumerate(dedup_result['unique_memories'], 1):
        lines.append(f"{i}. {memory['content']}")
    
    lines.append("")
    lines.append("="*70)
    
    return '\n'.join(lines)


def load_deduplicated_context(max_tablets: int = 10, max_kb: int = 75) -> str:
    """
    Main entry point for loading deduplicated context.
    
    This replaces the naive approach in load_context.py
    """
    from pathlib import Path
    
    sessions_dir = Path("sessions")
    if not sessions_dir.exists():
        return "💊 No Medicine Cabinet context yet"
    
    # Get recent tablets
    tablets = sorted(
        sessions_dir.glob("*.auratab"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )[:max_tablets]
    
    if not tablets:
        return "💊 No tablets found"
    
    # Deduplicate and format
    dedup_result = deduplicate_memories(tablets, max_kb=max_kb)
    return format_deduplicated_context(dedup_result)


if __name__ == "__main__":
    print(load_deduplicated_context())
