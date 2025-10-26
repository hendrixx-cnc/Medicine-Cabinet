#!/usr/bin/env python3
"""Automatic session tracking - no manual activation needed.

Import this module once and it automatically tracks changes throughout
your Python session, saving when the script exits.

Usage:
    from auto_session_tracker import track
    
    track("file.py", "Added feature", "+10 lines")
    track("main.py", "Fixed bug", "+2, -1 lines")
    # Auto-saves on exit!
"""

import atexit
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from tablet import Tablet, TabletMetadata, TabletEntry


class AutoSessionTracker:
    """Singleton auto-tracker that captures changes automatically."""
    
    _instance: Optional['AutoSessionTracker'] = None
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Only initialize once
        if AutoSessionTracker._initialized:
            return
        
        AutoSessionTracker._initialized = True
        
        # Setup
        self.sessions_dir = Path("./sessions")
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        # Create tablet
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.metadata = TabletMetadata(
            title=f"Auto-tracked Session {timestamp}",
            summary="Automatically tracked coding session",
            author=os.environ.get("USER", "unknown"),
            tags=["auto-session", "tracking"]
        )
        self.tablet = Tablet(metadata=self.metadata)
        
        # Register auto-save on exit
        atexit.register(self._save_on_exit)
        
        print(f"🔍 Auto-session tracking started: {timestamp}")
    
    def track(self, file_path: str, diff: str, notes: str = "") -> None:
        """Track a file change in the current session.
        
        Args:
            file_path: Path to the changed file
            diff: Description of the changes
            notes: Optional notes about the change
        """
        if self.tablet is None:
            print("⚠️  Auto-session tracker not initialized")
            return
            
        self.tablet.add_entry(path=file_path, diff=diff, notes=notes)
    
    def _save_on_exit(self):
        """Save the session when Python exits."""
        if len(self.tablet.entries) == 0:
            print("📝 Auto-session: No changes tracked")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"auto_session_{timestamp}.auratab"
        filepath = self.sessions_dir / filename
        
        try:
            self.tablet.write(str(filepath))
            print(f"💾 Auto-session saved: {filepath} ({len(self.tablet.entries)} entries)")
        except Exception as e:
            print(f"⚠️  Failed to save auto-session: {e}")


# Global singleton instance
_tracker = AutoSessionTracker()


def track(file_path: str, notes: str = "", diff: str = ""):
    """Track a file change in the auto-session.
    
    Args:
        file_path: Path to the changed file
        notes: Notes about the change
        diff: Optional diff content
        
    Example:
        >>> from auto_session_tracker import track
        >>> track("main.py", "Fixed bug in login", "+2, -1 lines")
        >>> track("README.md", "Updated docs")
    """
    _tracker.track(file_path, notes, diff)


# Example usage
if __name__ == "__main__":
    print("Testing auto-session tracker...")
    
    # Track some changes
    track("example.py", "Added new function", "+def new_func(): pass")
    track("test.py", "Added test case", "+def test_new_func(): ...")
    track("README.md", "Updated documentation", "+## New Section")
    
    print(f"\nTracked {len(_tracker.tablet.entries)} changes")
    print("Session will auto-save on exit...")
