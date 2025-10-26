#!/usr/bin/env python3
"""View saved session files in human-readable format.

Usage:
    # View all sessions in default directory
    python3 view_session.py
    
    # View all sessions in specific directory
    python3 view_session.py sessions/
    
    # View specific tablet
    python3 view_session.py sessions/session_20251026_204406.auratab
    
    # View specific capsule
    python3 view_session.py sessions/context_20251026_204406.auractx
"""

import sys
from pathlib import Path
from typing import List

from tablet import load_tablet
from context_capsule import load_capsule


def list_sessions(directory: Path) -> List[Path]:
    """List all session files in a directory.
    
    Args:
        directory: Directory to search
        
    Returns:
        List of session file paths
    """
    files = []
    
    if directory.exists() and directory.is_dir():
        files.extend(directory.glob("*.auratab"))
        files.extend(directory.glob("*.auractx"))
    
    return sorted(files)


def view_tablet(filepath: Path) -> None:
    """View a tablet file in detail.
    
    Args:
        filepath: Path to tablet file
    """
    print("=" * 80)
    print(f"TABLET: {filepath.name}")
    print("=" * 80)
    
    tablet = load_tablet(str(filepath))
    metadata = tablet.metadata
    
    print(f"\nTitle:       {metadata.title}")
    print(f"Description: {metadata.description}")
    print(f"Author:      {metadata.author}")
    print(f"Created:     {metadata.created_at}")
    
    if metadata.tags:
        print(f"Tags:        {', '.join(metadata.tags)}")
    
    print(f"\nEntries:     {len(tablet.entries)}")
    print("-" * 80)
    
    for i, entry in enumerate(tablet.entries, 1):
        print(f"\n[{i}] {entry.path}")
        
        if entry.notes:
            print(f"    Notes: {entry.notes}")
        
        if entry.diff:
            diff_lines = entry.diff.split('\n')
            preview = '\n    '.join(diff_lines[:5])
            print(f"    Diff:\n    {preview}")
            if len(diff_lines) > 5:
                print(f"    ... ({len(diff_lines) - 5} more lines)")
    
    print("\n" + "=" * 80)


def view_capsule(filepath: Path) -> None:
    """View a capsule file in detail.
    
    Args:
        filepath: Path to capsule file
    """
    print("=" * 80)
    print(f"CAPSULE: {filepath.name}")
    print("=" * 80)
    
    capsule = load_capsule(str(filepath))
    metadata = capsule.metadata
    
    print(f"\nProject:     {metadata.project}")
    print(f"Summary:     {metadata.summary}")
    print(f"Created:     {metadata.created_at}")
    
    if metadata.task_objective:
        print(f"Task:        {metadata.task_objective}")
    
    if metadata.relevant_files:
        print(f"Files:       {', '.join(metadata.relevant_files[:3])}")
        if len(metadata.relevant_files) > 3:
            print(f"             ... and {len(metadata.relevant_files) - 3} more")
    
    print(f"\nSections:    {len(capsule.sections)}")
    print("-" * 80)
    
    for i, section in enumerate(capsule.sections, 1):
        print(f"\n[{i}] {section.name} ({section.kind.name})")
        
        if isinstance(section.data, bytes):
            print(f"    Size: {len(section.data)} bytes")
        elif isinstance(section.data, str):
            lines = section.data.split('\n')
            preview = '\n    '.join(lines[:5])
            print(f"    Content:\n    {preview}")
            if len(lines) > 5:
                print(f"    ... ({len(lines) - 5} more lines)")
    
    print("\n" + "=" * 80)


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
        
        if path.is_file():
            # View specific file
            if path.suffix == ".auratab":
                view_tablet(path)
            elif path.suffix == ".auractx":
                view_capsule(path)
            else:
                print(f"Unknown file type: {path.suffix}")
                sys.exit(1)
        elif path.is_dir():
            # List directory
            files = list_sessions(path)
            
            if not files:
                print(f"No session files found in {path}")
                sys.exit(0)
            
            print(f"\nFound {len(files)} session file(s) in {path}:")
            print("-" * 80)
            
            for f in files:
                file_type = "TABLET" if f.suffix == ".auratab" else "CAPSULE"
                print(f"  [{file_type}] {f.name}")
            
            print("\nUse: python3 view_session.py <filepath> to view details")
        else:
            print(f"Path not found: {path}")
            sys.exit(1)
    else:
        # Default: list sessions directory
        sessions_dir = Path("./sessions")
        
        if not sessions_dir.exists():
            print("No sessions directory found (./sessions)")
            print("\nCreate one with:")
            print("  from session_tracker import AURASessionTracker")
            print("  tracker = AURASessionTracker()")
            sys.exit(0)
        
        files = list_sessions(sessions_dir)
        
        if not files:
            print("No session files found in ./sessions")
            sys.exit(0)
        
        print(f"\nFound {len(files)} session file(s):")
        print("-" * 80)
        
        for f in files:
            file_type = "TABLET" if f.suffix == ".auratab" else "CAPSULE"
            print(f"  [{file_type}] {f.name}")
        
        print("\nUse: python3 view_session.py <filepath> to view details")


if __name__ == "__main__":
    main()
