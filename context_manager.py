#!/usr/bin/env python3
"""
Context Manager for Medicine Cabinet
Handles automatic context loading, message counting, and tablet updates
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
            "message_count": 0,
            "active_tablet": None,
            "active_capsule": None,
            "last_load": None,
            "last_reminder": None
        }
    
    def save_state(self):
        """Save context state."""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def increment_message_count(self):
        """Increment message counter."""
        self.state["message_count"] += 1
        self.save_state()
        
        # Check if we need to remind about meds
        if self.state["message_count"] % 25 == 0:
            return True  # Time to take meds!
        return False
    
    def load_context(self):
        """Load Medicine Cabinet context and create/update capsule."""
        
        # Find or create active tablet (persistent memory)
        tablet = self._get_or_create_tablet()
        
        # Create fresh capsule for this session
        capsule = self._create_fresh_capsule()
        
        # Update state
        self.state["last_load"] = datetime.now(timezone.utc).isoformat()
        self.state["message_count"] = 0
        self.save_state()
        
        return {
            "tablet": tablet,
            "capsule": capsule,
            "message_count": self.state["message_count"]
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
    
    def update_from_conversation(self, user_message, copilot_response):
        """Update tablet and capsule from conversation turn."""
        
        # Load current context
        context = self.load_context()
        tablet = context["tablet"]
        
        # Extract if contextually important
        if self._is_contextual(user_message, copilot_response):
            tablet.add_entry(
                path=f"conversation/{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                diff=f"USER: {user_message}\n\nCOPILOT: {copilot_response[:500]}",
                notes="Contextual memory from conversation"
            )
            
            # Save updated tablet
            tablet_path = SESSIONS_DIR / f"persistent_{datetime.now().strftime('%Y%m%d')}.auratab"
            tablet.write(tablet_path)
        
        # Check if time for reminder
        needs_reminder = self.increment_message_count()
        
        return {
            "updated": True,
            "needs_reminder": needs_reminder,
            "message_count": self.state["message_count"]
        }
    
    def _is_contextual(self, user_msg, copilot_msg):
        """Check if conversation turn is contextually important."""
        
        combined = f"{user_msg} {copilot_msg}".lower()
        
        # Check for contextual keywords
        contextual_keywords = [
            'implement', 'code', 'function', 'class', 'error',
            'bug', 'fix', 'design', 'architecture', 'plan',
            'decision', 'approach', 'solution', 'algorithm'
        ]
        
        for keyword in contextual_keywords:
            if keyword in combined:
                return True
        
        # Check for code blocks
        if '```' in user_msg or '```' in copilot_msg:
            return True
        
        # Check for file references
        if any(ext in combined for ext in ['.py', '.js', '.ts', '.json']):
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
        # Load context
        manager = ContextManager()
        context = manager.load_context()
        print(f"✅ Context loaded: {context['tablet'].metadata.title}")
        print(f"📊 Message count: {context['message_count']}")
    
    elif len(sys.argv) > 1 and sys.argv[1] == "increment":
        # Increment message count
        manager = ContextManager()
        needs_reminder = manager.increment_message_count()
        
        if needs_reminder:
            take_your_meds_reminder()
        else:
            print(f"📊 Message count: {manager.state['message_count']}")
    
    else:
        print("Usage:")
        print("  python3 context_manager.py load       - Load context")
        print("  python3 context_manager.py increment  - Increment message counter")
