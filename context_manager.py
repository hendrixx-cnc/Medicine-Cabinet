#!/usr/bin/env python3
"""
Context Manager for Medicine Cabinet
Handles automatic context loading and tablet updates

NOTE: Message counter removed - not needed with new architecture
- Tablets load ONCE at startup (static long-term memory)
- Browser sends NEW memories only (no re-sending)
- Capsule health check handles "take your meds"
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from tablet import Tablet, TabletMetadata, load_tablet
from context_capsule import ContextCapsule, CapsuleMetadata, CapsuleSection

STATE_FILE = Path.home() / ".medicine_cabinet" / "context_state.json"
SESSIONS_DIR = Path("sessions")

class ContextManager:
    def __init__(self):
        self.state_file = STATE_FILE
        self.state_file.parent.mkdir(exist_ok=True)
        self.state = self.load_state()
        
    def load_state(self):
        """Load current context state."""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        
        return {
            "active_tablet": None,
            "active_capsule": None,
            "last_load": None
        }
    
    def save_state(self):
        """Save context state."""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def load_context(self):
        """
        Load Medicine Cabinet context.
        Called ONCE at startup to load tablets.
        No need to call repeatedly - tablets are static during session.
        """
        self.state["last_load"] = datetime.now(timezone.utc).isoformat()
        self.save_state()
        
        return {
            "loaded": True,
            "timestamp": self.state["last_load"]
        }
    
    def _get_or_create_tablet(self):
        """Get persistent tablet or create new one."""
        
        # Look for existing persistent tablet
        tablet_files = list(SESSIONS_DIR.glob("persistent_*.auratab"))
        
        if tablet_files:
            # Load most recent
            latest = sorted(tablet_files)[-1]
            return load_tablet(str(latest))
        
        # Create new persistent tablet
        metadata = TabletMetadata(
            title=f"Persistent Memory {datetime.now().strftime('%Y-%m-%d')}",
            summary="Long-term contextual memories for Medicine Cabinet",
            tags=['persistent', 'long-term', 'saved']
        )
        
        tablet = Tablet(metadata=metadata)
        tablet_path = SESSIONS_DIR / f"persistent_{datetime.now().strftime('%Y%m%d')}.auratab"
        SESSIONS_DIR.mkdir(exist_ok=True)
        tablet.write(tablet_path)
        
        return tablet
    
    def _create_fresh_capsule(self):
        """Create fresh capsule for current session."""
        
        metadata = CapsuleMetadata(
            project="Medicine-Cabinet",
            summary=f"Active session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            branch="main"
        )
        
        capsule = ContextCapsule(metadata=metadata)
        
        # Add task objective section
        capsule.set_task_objective(
            "Assist with Medicine Cabinet development and usage"
        )
        
        return capsule
    
    def update_from_conversation(self, user_msg: str, copilot_msg: str):
        """
        Update context from conversation.
        Browser sends NEW memories only - no counter needed.
        """
    
    def _is_contextual(self, user_msg, copilot_msg):
        """Check if conversation turn is contextually important.
        VERY selective to prevent bloat - only critical information.
        """
        
        combined = f"{user_msg} {copilot_msg}".lower()
        
        # Skip if too short
        if len(combined) < 150:
            return False
        
        # HIGH-VALUE keywords only (implementation, not discussion)
        high_value_keywords = [
            'implemented', 'refactored', 'fixed bug', 'created file',
            'modified function', 'error:', 'exception:', 'traceback',
            'decided to', 'architecture', 'data flow'
        ]
        
        for keyword in high_value_keywords:
            if keyword in combined:
                return True
        
        # Code blocks with substantial content
        if '```' in user_msg or '```' in copilot_msg:
            # Only if code block is substantial
            code_content = combined.split('```')[1] if '```' in combined else ''
            if len(code_content) > 100:
                return True
        
        # Specific file operations (not just mentions)
        import re
        if re.search(r'\b(modified|created|updated|deleted|renamed)\s+[\w\/\.\-]+\.(py|js|ts|json)', combined):
            return True
        
        return False


def take_your_meds_reminder():
    """Show reminder to save/cleanup context."""
    
    print("\n" + "=" * 70)
    print("💊 TIME TO TAKE YOUR MEDS!")
    print("=" * 70)
    print()
    print("You've had 25 message exchanges. It's time to:")
    print()
    print("  1. 💾 Save important context")
    print("  2. 🧹 Clear old memories")  
    print("  3. ✨ Refresh your Cabinet")
    print()
    print("Run: python3 cli.py cleanup --auto")
    print()
    print("=" * 70)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "load":
        # Load context at startup
        manager = ContextManager()
        context = manager.load_context()
        
        print("="*70)
        print("💊 MEDICINE CABINET - Context Loaded")
        print("="*70)
        print(f"✅ Loaded at: {context['timestamp']}")
        print()
        print("Tablets are now in context (static for this session)")
        print("Browser will send NEW memories as they happen")
        print("="*70)
    
    else:
        print("Usage:")
        print("  python3 context_manager.py load")
        print()
        print("NOTE: Message counter removed - not needed anymore!")
        print("  - Tablets load ONCE at startup")
        print("  - Browser sends NEW memories only")
        print("  - Capsule health check handles cleanup")

