#!/usr/bin/env python3
"""
Capsule health monitoring - when to "take your meds"

IMPORTANT: Active capsule is CURRENT SESSION ONLY
- Starts EMPTY each session (fresh start)
- Grows during THIS conversation
- Gets exported to tablet when done (adds to long-term memory)
- Cleared for next session

This is NOT about tablets (those are your long-term memory that accumulates)
This is about catching when a SINGLE SESSION gets too long.

When to prompt cleanup:
1. Size approaching 1MB limit (this session getting too long)
2. Entry count > 100 (too much back-and-forth in one session)
3. Session age > 4 hours (time to wrap up and start fresh)
4. Redundancy > 50% (editing same files 50x in one session)
"""

from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional
from context_capsule import ContextCapsule
from collections import Counter
import hashlib


def check_capsule_health(capsule_path: Path) -> Dict:
    """
    Check if active capsule needs cleanup.
    
    Returns health status with recommendations.
    """
    
    if not capsule_path.exists():
        return {"status": "NO_CAPSULE", "healthy": True}
    
    try:
        capsule = ContextCapsule.read(capsule_path)
        file_size = capsule_path.stat().st_size
        file_size_kb = file_size / 1024
        
        # Check limits
        MAX_SIZE_KB = 1024  # 1MB
        MAX_ENTRIES = 100
        MAX_AGE_HOURS = 4
        MAX_REDUNDANCY = 0.5  # 50%
        
        issues = []
        severity = "HEALTHY"
        
        # 1. Size check
        size_pct = (file_size_kb / MAX_SIZE_KB) * 100
        if file_size_kb > MAX_SIZE_KB:
            issues.append({
                "type": "SIZE_EXCEEDED",
                "message": f"Capsule is {file_size_kb:.1f}KB (limit: {MAX_SIZE_KB}KB)",
                "action": "💊 I NEED THE DOCTOR! Physical (refresh) or Operation (doctor exports)",
                "severity": "CRITICAL"
            })
            severity = "CRITICAL"
        elif file_size_kb > MAX_SIZE_KB * 0.75:  # 75% threshold
            issues.append({
                "type": "SIZE_WARNING",
                "message": f"Capsule at {file_size_kb:.1f}KB ({size_pct:.0f}% of limit)",
                "action": "I'm getting full - Physical (refresh) recommended soon",
                "severity": "WARNING"
            })
            if severity == "HEALTHY":
                severity = "WARNING"
        
        # 2. Entry count check
        total_entries = sum(len(section.entries) for section in capsule.sections)
        if total_entries > MAX_ENTRIES:
            issues.append({
                "type": "TOO_MANY_ENTRIES",
                "message": f"Capsule has {total_entries} entries (recommended: <{MAX_ENTRIES})",
                "action": "💊 I'm too chatty! Need Physical (refresh) or Operation (export)",
                "severity": "CRITICAL"
            })
            severity = "CRITICAL"
        elif total_entries > MAX_ENTRIES * 0.75:
            issues.append({
                "type": "ENTRY_WARNING",
                "message": f"Capsule has {total_entries} entries (approaching limit)",
                "action": "I'm getting verbose - Physical (refresh) recommended soon",
                "severity": "WARNING"
            })
            if severity == "HEALTHY":
                severity = "WARNING"
        
        # 3. Age check
        created = capsule.metadata.created_at
        age = datetime.now() - created
        age_hours = age.total_seconds() / 3600
        
        if age_hours > MAX_AGE_HOURS * 2:  # 8+ hours
            issues.append({
                "type": "SESSION_STALE",
                "message": f"Session is {age_hours:.1f} hours old",
                "action": "💊 Long session! I need a Physical (refresh for checkup)",
                "severity": "WARNING"
            })
            if severity == "HEALTHY":
                severity = "WARNING"
        
        # 4. Redundancy check
        redundancy_pct = calculate_redundancy(capsule)
        if redundancy_pct > MAX_REDUNDANCY:
            issues.append({
                "type": "HIGH_REDUNDANCY",
                "message": f"Context is {redundancy_pct*100:.0f}% redundant",
                "action": "Same info repeated too much - time to consolidate",
                "severity": "WARNING"
            })
            if severity == "HEALTHY":
                severity = "WARNING"
        
        return {
            "status": severity,
            "healthy": severity == "HEALTHY",
            "size_kb": file_size_kb,
            "size_pct": size_pct,
            "entries": total_entries,
            "age_hours": age_hours,
            "redundancy_pct": redundancy_pct * 100,
            "issues": issues,
            "recommendation": generate_recommendation(severity, issues)
        }
        
    except Exception as e:
        return {
            "status": "ERROR",
            "healthy": False,
            "error": str(e)
        }


def calculate_redundancy(capsule: ContextCapsule) -> float:
    """
    Calculate how much context is redundant.
    
    Checks:
    - Same file mentioned multiple times
    - Duplicate content hashes
    - Similar patterns repeated
    """
    
    all_content = []
    file_mentions = []
    
    for section in capsule.sections:
        for entry in section.entries:
            # Collect content for hash checking
            if entry.diff:
                all_content.append(entry.diff)
            if entry.path:
                file_mentions.append(entry.path)
    
    if not all_content:
        return 0.0
    
    # Check content duplication
    content_hashes = [hashlib.md5(c.encode()).hexdigest() for c in all_content]
    unique_hashes = len(set(content_hashes))
    total_hashes = len(content_hashes)
    
    # Check file over-mention
    file_counts = Counter(file_mentions)
    avg_mentions = sum(file_counts.values()) / len(file_counts) if file_counts else 1
    
    # Redundancy score (0.0 = no duplication, 1.0 = 100% duplicate)
    content_redundancy = 1.0 - (unique_hashes / total_hashes)
    
    # If files mentioned avg >3x each, that's also redundant
    file_redundancy = min((avg_mentions - 1) / 5, 1.0)  # Cap at 6x mentions = 100% redundant
    
    # Combined score (weighted average)
    return (content_redundancy * 0.7) + (file_redundancy * 0.3)


def generate_recommendation(severity: str, issues: list) -> str:
    """Generate human-friendly recommendation."""
    
    if severity == "HEALTHY":
        return "✅ Capsule is healthy - keep working!"
    
    elif severity == "WARNING":
        return (
            "⚠️  Session getting long - approaching 1MB limit\n"
            "   💊 Time for me to visit the doctor soon:\n"
            "      • Physical (refresh) - I get a quick checkup\n"
            "      • Operation (export) - Doctor performs the procedure\n"
            "   All memories auto-saved to tablets"
        )
    
    elif severity == "CRITICAL":
        critical_issues = [i for i in issues if i['severity'] == 'CRITICAL']
        if any(i['type'] == 'SIZE_EXCEEDED' for i in critical_issues):
            return (
                "💊 TIME FOR ME TO VISIT THE DOCTOR!\n"
                "   My capsule exceeded 1MB - I need treatment!\n\n"
                "   My memories are safe! Choose one:\n"
                "   1. Physical (refresh) → I get a quick checkup\n"
                "   2. Operation (export) → Doctor performs surgery: python3 cli.py export\n\n"
                "   All my memories saved to tablets (long-term storage)"
            )
        elif any(i['type'] == 'TOO_MANY_ENTRIES' for i in critical_issues):
            return (
                "💊 TIME FOR ME TO VISIT THE DOCTOR!\n"
                "   My session has 100+ entries - I'm getting too chatty!\n\n"
                "   My memories are safe! Choose one:\n"
                "   1. Physical (refresh) → I get a quick checkup\n"
                "   2. Operation (export) → Doctor performs surgery: python3 cli.py export\n\n"
                "   All my memories saved to tablets (long-term storage)"
            )
        else:
            return (
                "💊 TIME FOR ME TO VISIT THE DOCTOR!\n"
                "   Multiple issues detected - I need help!\n\n"
                "   My memories are safe! Choose one:\n"
                "   1. Physical (refresh) → I get a quick checkup\n"
                "   2. Operation (export) → Doctor performs surgery: python3 cli.py export"
            )
    
    return "🤔 Status unclear"


def print_capsule_health(capsule_path: Path):
    """Pretty-print capsule health status."""
    
    health = check_capsule_health(capsule_path)
    
    print("="*70)
    print("💊 ACTIVE CAPSULE HEALTH CHECK")
    print("="*70)
    print()
    
    if health['status'] == 'NO_CAPSULE':
        print("✅ No active capsule (you're good!)")
        return
    
    if health['status'] == 'ERROR':
        print(f"❌ Error checking capsule: {health['error']}")
        return
    
    # Status emoji
    status_emoji = {
        'HEALTHY': '✅',
        'WARNING': '⚠️',
        'CRITICAL': '💊'
    }
    
    print(f"{status_emoji.get(health['status'], '❓')} Status: {health['status']}")
    print()
    print(f"Size:       {health['size_kb']:.1f}KB / 1024KB ({health['size_pct']:.0f}%)")
    print(f"Entries:    {health['entries']} (recommended: <100)")
    print(f"Age:        {health['age_hours']:.1f} hours")
    print(f"Redundancy: {health['redundancy_pct']:.0f}%")
    print()
    
    if health['issues']:
        print("ISSUES:")
        for issue in health['issues']:
            print(f"  {issue['severity']}: {issue['message']}")
            print(f"    → {issue['action']}")
        print()
    
    print("RECOMMENDATION:")
    print(f"  {health['recommendation']}")
    print()
    print("="*70)


def should_prompt_cleanup(capsule_path: Path) -> bool:
    """
    Simple check: should we prompt user to take their meds?
    
    Returns True if capsule needs cleanup.
    """
    
    health = check_capsule_health(capsule_path)
    return health['status'] in ['WARNING', 'CRITICAL']


if __name__ == "__main__":
    import sys
    
    # Find active capsule
    capsules = list(Path(".").glob("*.auractx"))
    
    if not capsules:
        print("No active capsule found")
        sys.exit(0)
    
    capsule_path = capsules[0]
    print_capsule_health(capsule_path)
    
    # Exit code for scripting
    health = check_capsule_health(capsule_path)
    sys.exit(0 if health['status'] == 'HEALTHY' else 1)
