#!/usr/bin/env python3
"""Native messaging host for Medicine Cabinet browser extensions.

Enables bidirectional communication between browser and Python backend.
Allows extensions to:
- Read active capsules/tablets
- Update context with new information
- Capture ChatGPT conversations
- Sync session state in real-time

STORAGE LIMITS:
- 8MB persistent tablet storage (works on any modern browser)
- 1MB active capsule limit
- Max 100 entries per tablet
- Max 1KB per entry
"""

import sys
import json
import struct
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from tablet import Tablet, TabletEntry
from context_capsule import ContextCapsule
from storage_limits import (
    MAX_PERSISTENT_SIZE_BYTES,
    MAX_CAPSULE_SIZE_BYTES,
    MAX_ENTRIES_PER_TABLET,
    MAX_ENTRY_SIZE_BYTES,
    check_tablet_size,
    check_total_storage
)
from capsule_health_check import check_capsule_health, should_prompt_cleanup

# Setup logging
log_file = Path.home() / '.medicine_cabinet' / 'native_host.log'
log_file.parent.mkdir(exist_ok=True)
logging.basicConfig(
    filename=str(log_file),
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class NativeMessagingHost:
    """Handles native messaging protocol for browser extensions."""
    
    def __init__(self):
        self.active_capsule_path: Optional[Path] = None
        self.active_tablet_path: Optional[Path] = None
        self.sessions_dir = Path('./sessions')
        self.sessions_dir.mkdir(exist_ok=True)
        logging.info('Native messaging host started')
        
        # Check tablet cleanup schedule (runs every 7 days)
        # Tablets are static - only check periodically
        self.check_cleanup_schedule()
        
        # Check ACTIVE CAPSULE health (dynamic, needs monitoring)
        # This is the current session that grows during use
        self.check_active_capsule_health()
        
        # Cleanup old auto-captured sessions on startup
        self.cleanup_old_sessions()
    
    def read_message(self) -> Optional[Dict[str, Any]]:
        """Read a message from stdin (browser extension)."""
        try:
            # Read message length (4 bytes, little-endian)
            raw_length = sys.stdin.buffer.read(4)
            if len(raw_length) == 0:
                return None
            
            message_length = struct.unpack('=I', raw_length)[0]
            
            # Read message
            message = sys.stdin.buffer.read(message_length).decode('utf-8')
            return json.loads(message)
        except Exception as e:
            logging.error(f'Error reading message: {e}')
            return None
    
    def send_message(self, message: Dict[str, Any]) -> None:
        """Send a message to stdout (browser extension)."""
        try:
            encoded_message = json.dumps(message).encode('utf-8')
            encoded_length = struct.pack('=I', len(encoded_message))
            
            sys.stdout.buffer.write(encoded_length)
            sys.stdout.buffer.write(encoded_message)
            sys.stdout.buffer.flush()
            
            logging.debug(f'Sent message: {message.get("action")}')
        except Exception as e:
            logging.error(f'Error sending message: {e}')
    
    def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming message and return response."""
        action = message.get('action')
        logging.info(f'Handling action: {action}')
        
        try:
            if action == 'getActiveCapsule':
                return self.get_active_capsule()
            
            elif action == 'getActiveTablet':
                return self.get_active_tablet()
            
            elif action == 'updateCapsule':
                return self.update_capsule(message)
            
            elif action == 'addTabletEntry':
                return self.add_tablet_entry(message)
            
            elif action == 'captureConversation':
                return self.capture_conversation(message)
            
            elif action == 'createSession':
                return self.create_session(message)
            
            elif action == 'listSessions':
                return self.list_sessions()
            
            elif action == 'cleanupOldSessions':
                days_old = message.get('daysOld', 30)
                return self.cleanup_old_sessions(days_old)
            
            else:
                return {'success': False, 'error': f'Unknown action: {action}'}
        
        except Exception as e:
            logging.error(f'Error handling {action}: {e}', exc_info=True)
            return {'success': False, 'error': str(e)}
    
    def get_active_capsule(self) -> Dict[str, Any]:
        """Get the currently active capsule."""
        if not self.active_capsule_path or not self.active_capsule_path.exists():
            return {'success': False, 'error': 'No active capsule'}
        
        try:
            capsule = ContextCapsule.read(self.active_capsule_path)
            return {
                'success': True,
                'capsule': {
                    'path': str(self.active_capsule_path),
                    'metadata': capsule.metadata.to_dict(),
                    'task_objective': capsule.get_task_objective(),
                    'relevant_files': capsule.get_relevant_files()
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_active_tablet(self) -> Dict[str, Any]:
        """Get the currently active tablet."""
        if not self.active_tablet_path or not self.active_tablet_path.exists():
            return {'success': False, 'error': 'No active tablet'}
        
        try:
            tablet = Tablet.read(self.active_tablet_path)
            return {
                'success': True,
                'tablet': {
                    'path': str(self.active_tablet_path),
                    'metadata': tablet.metadata.to_dict(),
                    'entries': [e.to_dict() for e in tablet.entries]
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_capsule(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Update capsule with new information."""
        capsule_path = message.get('path')
        updates = message.get('updates', {})
        
        if not capsule_path:
            return {'success': False, 'error': 'No capsule path provided'}
        
        try:
            capsule = ContextCapsule.read(capsule_path)
            
            # Update task objective
            if 'task_objective' in updates:
                capsule.set_task_objective(updates['task_objective'])
            
            # Update relevant files
            if 'relevant_files' in updates:
                capsule.set_relevant_files(updates['relevant_files'])
            
            # Add working plan
            if 'working_plan' in updates:
                capsule.add_section('working_plan', updates['working_plan'])
            
            # Save changes
            capsule.write(capsule_path)
            self.active_capsule_path = Path(capsule_path)
            
            logging.info(f'Updated capsule: {capsule_path}')
            return {'success': True, 'message': 'Capsule updated'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def add_tablet_entry(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Add an entry to a tablet."""
        tablet_path = message.get('path')
        entry_data = message.get('entry', {})
        
        if not tablet_path:
            return {'success': False, 'error': 'No tablet path provided'}
        
        try:
            tablet = Tablet.read(tablet_path)
            
            # Add entry
            tablet.add_entry(
                path=entry_data.get('path', 'conversation'),
                diff=entry_data.get('diff', ''),
                notes=entry_data.get('notes', '')
            )
            
            # Save changes
            tablet.write(tablet_path)
            self.active_tablet_path = Path(tablet_path)
            
            logging.info(f'Added entry to tablet: {tablet_path}')
            return {'success': True, 'message': 'Entry added'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def capture_conversation(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Capture a ChatGPT conversation turn with storage limit enforcement."""
        
        # Check storage limits FIRST
        storage_check = check_total_storage()
        if not storage_check['ok']:
            logging.warning(f"Storage full: {storage_check['total_mb']:.2f}MB / 8MB")
            return {
                'success': False,
                'error': 'STORAGE_FULL',
                'message': storage_check['message'],
                'size_mb': storage_check['total_mb'],
                'limit_mb': 8
            }
        
        # Warn if approaching limit
        if 'warning' in storage_check:
            logging.warning(storage_check['message'])
        
        user_message = message.get('userMessage', '')
        ai_response = message.get('aiResponse', '')
        context = message.get('context', {})
        memories = message.get('memories', [])  # New: contextual memories from scraper
        
        # Create or update session tablet
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        tablet_path = self.sessions_dir / f'conversation_{timestamp}.auratab'
        
        try:
            # Create new tablet if doesn't exist
            if not tablet_path.exists():
                from tablet import TabletMetadata
                metadata = TabletMetadata(
                    title=f"ChatGPT Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    summary="Auto-captured ChatGPT conversation",
                    author=context.get('user', 'unknown'),
                    tags=['chatgpt', 'conversation', 'auto-captured', 'temporary']  # Mark as temporary
                )
                tablet = Tablet(metadata=metadata)
            else:
                tablet = Tablet.read(tablet_path)
            
            # Check tablet size before adding
            tablet_check = check_tablet_size(tablet_path)
            if not tablet_check['ok']:
                logging.warning(f"Tablet too large: {tablet_check['size_mb']:.2f}MB")
                return {
                    'success': False,
                    'error': 'TABLET_TOO_LARGE',
                    'message': tablet_check['message']
                }
            
            # Check entry count limit (max 100 entries per tablet)
            if len(tablet.entries) >= MAX_ENTRIES_PER_TABLET:
                logging.info(f"Tablet full ({len(tablet.entries)} entries), creating new one")
                # Create new tablet with incremented counter
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                tablet_path = self.sessions_dir / f'conversation_{timestamp}_cont.auratab'
                from tablet import TabletMetadata
                metadata = TabletMetadata(
                    title=f"ChatGPT Session {datetime.now().strftime('%Y-%m-%d %H:%M')} (continued)",
                    summary="Auto-captured ChatGPT conversation (continuation)",
                    author=context.get('user', 'unknown'),
                    tags=['chatgpt', 'conversation', 'auto-captured', 'temporary']
                )
                tablet = Tablet(metadata=metadata)
            
            # Add contextual memories (not full conversation)
            if memories:
                for memory in memories[:10]:  # Max 10 per call
                    content = memory.get('content', '')
                    
                    # Enforce 1KB per entry limit
                    if len(content) > MAX_ENTRY_SIZE_BYTES:
                        content = content[:MAX_ENTRY_SIZE_BYTES] + '...[truncated]'
                    
                    tablet.add_entry(
                        path='contextual_memory',
                        diff=content,
                        notes=f"Role: {memory.get('role', 'unknown')}, Type: {memory.get('type', 'memory')}"
                    )
            else:
                # Fallback to full conversation (legacy)
                conversation_text = f"USER: {user_message}\n\nASSISTANT: {ai_response}"
                
                # Enforce 1KB limit
                if len(conversation_text) > MAX_ENTRY_SIZE_BYTES:
                    conversation_text = conversation_text[:MAX_ENTRY_SIZE_BYTES] + '...[truncated]'
                
                tablet.add_entry(
                    path='chatgpt_conversation',
                    diff=conversation_text,
                    notes=json.dumps(context)
                )
            
            # Save
            tablet.write(tablet_path)
            
            logging.info(f'Captured conversation to: {tablet_path}')
            return {
                'success': True,
                'message': 'Conversation captured (auto-deletes after 30 days)',
                'tablet_path': str(tablet_path)
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_session(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new session tablet (explicitly saved, won't be auto-deleted)."""
        title = message.get('title', 'New Session')
        summary = message.get('summary', '')
        
        try:
            from tablet import TabletMetadata
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            metadata = TabletMetadata(
                title=title,
                summary=summary,
                tags=['session', 'browser', 'saved']  # 'saved' tag prevents auto-cleanup
            )
            tablet = Tablet(metadata=metadata)
            
            tablet_path = self.sessions_dir / f'session_{timestamp}.auratab'
            tablet.write(tablet_path)
            self.active_tablet_path = tablet_path
            
            logging.info(f'Created session: {tablet_path}')
            return {
                'success': True,
                'message': 'Session created',
                'tablet_path': str(tablet_path)
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def cleanup_old_sessions(self, days_old: int = 30) -> Dict[str, Any]:
        """Clean up auto-captured sessions older than specified days.
        
        Only removes tablets with 'auto-captured' or 'temporary' tags.
        Tablets with 'saved' tag are preserved.
        """
        try:
            cutoff_date = datetime.now() - __import__('datetime').timedelta(days=days_old)
            removed_count = 0
            preserved_count = 0
            
            for tablet_file in self.sessions_dir.glob('*.auratab'):
                try:
                    tablet = Tablet.read(tablet_file)
                    
                    # Skip if explicitly saved
                    if 'saved' in tablet.metadata.tags:
                        preserved_count += 1
                        continue
                    
                    # Check if auto-captured
                    is_auto = ('auto-captured' in tablet.metadata.tags or 
                              'temporary' in tablet.metadata.tags or
                              tablet_file.name.startswith('auto_'))
                    
                    if not is_auto:
                        preserved_count += 1
                        continue
                    
                    # Check age
                    if tablet.metadata.created_at < cutoff_date:
                        tablet_file.unlink()
                        removed_count += 1
                        logging.info(f'Cleaned up old session: {tablet_file}')
                    else:
                        preserved_count += 1
                
                except Exception as e:
                    logging.warning(f'Error processing {tablet_file}: {e}')
            
            logging.info(f'Cleanup: removed {removed_count}, preserved {preserved_count}')
            return {
                'success': True,
                'removed': removed_count,
                'preserved': preserved_count
            }
        
        except Exception as e:
            logging.error(f'Cleanup failed: {e}')
            return {'success': False, 'error': str(e)}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def list_sessions(self) -> Dict[str, Any]:
        """List all session tablets."""
        try:
            sessions = []
            for tablet_file in self.sessions_dir.glob('*.auratab'):
                try:
                    tablet = Tablet.read(tablet_file)
                    sessions.append({
                        'path': str(tablet_file),
                        'title': tablet.metadata.title,
                        'summary': tablet.metadata.summary,
                        'created': tablet.metadata.created_at.isoformat(),
                        'entries': len(tablet.entries)
                    })
                except Exception as e:
                    logging.warning(f'Error reading {tablet_file}: {e}')
            
            return {'success': True, 'sessions': sessions}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def check_active_capsule_health(self):
        """
        Check if ACTIVE CAPSULE needs cleanup and log warning.
        
        This is the CURRENT SESSION only - not tablets!
        Tablets are loaded once at startup (static).
        Capsule grows during the session (dynamic).
        
        When near limits, I need to "visit the doctor":
        - Physical (refresh) → I get a quick checkup, auto-saved
        - Operation (export) → You perform surgery on me via CLI
        - All my memories preserved in tablets
        """
        
        # Find active capsule
        capsules = list(Path(".").glob("*.auractx"))
        if not capsules:
            logging.info("No active capsule - starting fresh")
            return
        
        capsule_path = capsules[0]
        
        if should_prompt_cleanup(capsule_path):
            health = check_capsule_health(capsule_path)
            logging.warning("="*70)
            logging.warning("💊 ACTIVE CAPSULE NEEDS ATTENTION")
            logging.warning(f"Status: {health['status']}")
            logging.warning(f"Size: {health['size_kb']:.1f}KB / 1024KB ({health['size_pct']:.0f}%)")
            logging.warning(f"Entries: {health['entries']}")
            logging.warning(f"Age: {health['age_hours']:.1f} hours")
            logging.warning(f"Redundancy: {health['redundancy_pct']:.0f}%")
            
            if health['issues']:
                logging.warning("Issues:")
                for issue in health['issues']:
                    logging.warning(f"  - {issue['message']}")
            
            logging.warning("")
            logging.warning(f"{health['recommendation']}")
            logging.warning("="*70)
        else:
            health = check_capsule_health(capsule_path)
            logging.info(f"Active capsule healthy: {health['size_kb']:.1f}KB, {health['entries']} entries, {health['age_hours']:.1f}h old")
    
    def check_cleanup_schedule(self):
        """
        Check if it's time to prompt for TABLET cleanup (every 7 days).
        
        Tablets are static - only check periodically, not during session.
        """
        try:
            import subprocess
            # Run cleanup scheduler in background (will only prompt if needed)
            subprocess.Popen([
                'python3',
                str(Path(__file__).parent / 'cleanup_scheduler.py')
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logging.info('Cleanup scheduler check initiated')
        except Exception as e:
            logging.warning(f'Could not run cleanup scheduler: {e}')
    
    def run(self):
        """Main message loop."""
        logging.info('Starting message loop')
        
        while True:
            message = self.read_message()
            if message is None:
                logging.info('No more messages, exiting')
                break
            
            response = self.handle_message(message)
            self.send_message(response)


if __name__ == '__main__':
    host = NativeMessagingHost()
    host.run()
