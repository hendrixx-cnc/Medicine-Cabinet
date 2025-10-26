#!/usr/bin/env python3
"""Manual session tracking using Medicine Cabinet.

Provides the AURASessionTracker class for explicit session management,
allowing developers to track coding sessions with tablets and capsules.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from tablet import Tablet, TabletMetadata, TabletEntry
from context_capsule import ContextCapsule, CapsuleMetadata, CapsuleSection, SectionKind


class AURASessionTracker:
    """Manual session tracker for coding sessions."""
    
    def __init__(self, sessions_dir: str = "./sessions"):
        """Initialize the session tracker.
        
        Args:
            sessions_dir: Directory to save session files (default: ./sessions)
        """
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
    
    def start_session(self, title: str, description: str, author: Optional[str] = None) -> Tablet:
        """Start a new session and return a Tablet.
        
        Args:
            title: Session title
            description: Session description
            author: Optional author name
            
        Returns:
            Tablet: New tablet for tracking file changes
        """
        metadata = TabletMetadata(
            title=title,
            description=description,
            author=author or os.environ.get("USER", "unknown"),
            tags=["session", "tracking"]
        )
        
        tablet = Tablet(metadata=metadata)
        print(f"Started session: {title}")
        return tablet
    
    def record_file_change(
        self,
        tablet: Tablet,
        file_path: str,
        diff: str,
        notes: str = ""
    ) -> None:
        """Record a file change in the tablet.
        
        Args:
            tablet: Tablet to add entry to
            file_path: Path to the changed file
            diff: Diff or change description
            notes: Optional notes about the change
        """
        entry = TabletEntry(path=file_path, diff=diff, notes=notes)
        tablet.add_entry(entry)
        print(f"Recorded change: {file_path}")
    
    def save_session(self, tablet: Tablet, filename: Optional[str] = None) -> Path:
        """Save the session tablet to disk.
        
        Args:
            tablet: Tablet to save
            filename: Optional custom filename (default: auto-generated)
            
        Returns:
            Path: Path to saved tablet file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"session_{timestamp}.auratab"
        
        filepath = self.sessions_dir / filename
        tablet.write(str(filepath))
        print(f"Saved session: {filepath}")
        return filepath
    
    def create_context_snapshot(
        self,
        project: str,
        summary: str,
        sections: Optional[list] = None,
        filename: Optional[str] = None
    ) -> Path:
        """Create a context capsule snapshot.
        
        Args:
            project: Project name
            summary: Summary of current state
            sections: Optional list of (name, kind, data) tuples
            filename: Optional custom filename (default: auto-generated)
            
        Returns:
            Path: Path to saved capsule file
        """
        metadata = CapsuleMetadata(project=project, summary=summary)
        capsule = ContextCapsule(metadata=metadata)
        
        if sections:
            for name, kind, data in sections:
                section = CapsuleSection(name=name, kind=kind, data=data)
                capsule.add_section(section)
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"context_{timestamp}.auractx"
        
        filepath = self.sessions_dir / filename
        capsule.write(str(filepath))
        print(f"Saved context snapshot: {filepath}")
        return filepath


# Example usage
if __name__ == "__main__":
    # Create tracker
    tracker = AURASessionTracker()
    
    # Start a session
    tablet = tracker.start_session(
        "Example Session",
        "Testing session tracking functionality"
    )
    
    # Record some changes
    tracker.record_file_change(
        tablet,
        "example.py",
        "+def new_function():\n+    pass",
        "Added new function"
    )
    
    tracker.record_file_change(
        tablet,
        "README.md",
        "+# New Section",
        "Updated documentation"
    )
    
    # Save the session
    tracker.save_session(tablet)
    
    # Create a context snapshot
    tracker.create_context_snapshot(
        "Example Project",
        "Current project state",
        sections=[
            ("readme", SectionKind.TEXT, "# Example Project\n\nThis is an example."),
            ("config", SectionKind.JSON, '{"version": "1.0.0"}'),
        ]
    )
    
    print("\n✓ Session tracking example complete!")
    print(f"  Check the {tracker.sessions_dir} directory for saved files.")
