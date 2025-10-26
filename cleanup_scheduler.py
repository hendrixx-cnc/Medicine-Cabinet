#!/usr/bin/env python3
"""
Automatic cleanup scheduler for Medicine Cabinet sessions.
Checks every 7 days and prompts user to clean up temporary sessions.
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from tablet import Tablet


LAST_CLEANUP_FILE = Path.home() / '.medicine_cabinet' / 'last_cleanup.json'
CLEANUP_INTERVAL_DAYS = 7
AUTO_DELETE_DAYS = 30


def should_run_cleanup():
    """Check if it's time to run cleanup (every 7 days)."""
    LAST_CLEANUP_FILE.parent.mkdir(exist_ok=True)
    
    if not LAST_CLEANUP_FILE.exists():
        # First run, create the file
        save_last_cleanup()
        return True
    
    try:
        with open(LAST_CLEANUP_FILE, 'r') as f:
            data = json.load(f)
            last_cleanup = datetime.fromisoformat(data['last_cleanup'])
            
            # Check if 7 days have passed
            if datetime.now() - last_cleanup >= timedelta(days=CLEANUP_INTERVAL_DAYS):
                return True
    except Exception:
        # If file is corrupted, run cleanup
        return True
    
    return False


def save_last_cleanup():
    """Save the current timestamp as last cleanup time."""
    LAST_CLEANUP_FILE.parent.mkdir(exist_ok=True)
    with open(LAST_CLEANUP_FILE, 'w') as f:
        json.dump({
            'last_cleanup': datetime.now().isoformat(),
            'last_cleanup_human': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }, f, indent=2)


def get_temporary_sessions():
    """Get all temporary (auto-captured) sessions older than 30 days."""
    sessions_dir = Path('./sessions')
    if not sessions_dir.exists():
        return []
    
    cutoff_date = datetime.now() - timedelta(days=AUTO_DELETE_DAYS)
    temp_sessions = []
    
    for tablet_file in sessions_dir.glob('*.auratab'):
        try:
            tablet = Tablet.read(tablet_file)
            
            # Check if it's a temporary session
            is_temporary = (
                'temporary' in tablet.metadata.tags or
                'auto-captured' in tablet.metadata.tags
            ) and 'saved' not in tablet.metadata.tags
            
            # Check if it's older than 30 days
            is_old = tablet.metadata.created_at < cutoff_date
            
            if is_temporary and is_old:
                temp_sessions.append({
                    'path': tablet_file,
                    'tablet': tablet,
                    'age_days': (datetime.now() - tablet.metadata.created_at).days
                })
        except Exception as e:
            print(f"Warning: Could not read {tablet_file}: {e}")
    
    return temp_sessions


def check_memory_health():
    """Check if memory is getting too full (Alzheimer's warning)."""
    sessions_dir = Path('./sessions')
    if not sessions_dir.exists():
        return None
    
    total_sessions = 0
    temporary_sessions = 0
    total_size_mb = 0
    old_sessions = 0
    
    week_ago = datetime.now() - timedelta(days=7)
    
    for tablet_file in sessions_dir.glob('*.auratab'):
        try:
            total_sessions += 1
            size_mb = tablet_file.stat().st_size / (1024 * 1024)
            total_size_mb += size_mb
            
            tablet = Tablet.read(tablet_file)
            
            is_temp = (
                'temporary' in tablet.metadata.tags or
                'auto-captured' in tablet.metadata.tags
            ) and 'saved' not in tablet.metadata.tags
            
            if is_temp:
                temporary_sessions += 1
                
                if tablet.metadata.created_at < week_ago:
                    old_sessions += 1
        except:
            pass
    
    return {
        'total': total_sessions,
        'temporary': temporary_sessions,
        'old': old_sessions,
        'size_mb': total_size_mb
    }


def prompt_cleanup():
    """Prompt user to clean up old temporary sessions."""
    print("\n" + "="*70)
    print("💊 TIME TO TAKE YOUR MEDS! - Weekly Memory Maintenance")
    print("="*70)
    
    # Check memory health
    health = check_memory_health()
    
    if health:
        print(f"\n📊 Cabinet Status:")
        print(f"   Total sessions: {health['total']}")
        print(f"   Temporary sessions: {health['temporary']}")
        print(f"   Old sessions (>7 days): {health['old']}")
        print(f"   Storage used: {health['size_mb']:.2f} MB")
        
        # Memory health guidance
        if health['old'] > 20 or health['size_mb'] > 50:
            print("\n🧠 Your Cabinet is getting full!")
            print("   💡 Did you know? Regular cleanup helps your AI maintain sharper context.")
            print("   Just like taking vitamins, clearing old sessions weekly keeps things fresh.")
            print("   Taking your meds = better AI performance! 🗑️💊")
            print()
        elif health['old'] > 10:
            print("\n💊 Reminder: Time for your weekly cleanup!")
            print("   Regular maintenance = sharper AI memory")
        else:
            print("\n✨ Cabinet is looking good! Keep up the weekly routine.")
    
    temp_sessions = get_temporary_sessions()
    
    if not temp_sessions:
        print("\n✨ Cabinet is clean! No old sessions to clear.")
        print("   Keep up the good maintenance routine! 💊")
        save_last_cleanup()
        return
    
    print(f"\nFound {len(temp_sessions)} temporary session(s) older than 30 days:\n")
    
    # Show sessions
    for i, session in enumerate(temp_sessions, 1):
        tablet = session['tablet']
        age = session['age_days']
        print(f"{i}. {tablet.metadata.title}")
        print(f"   Created: {tablet.metadata.created_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Age: {age} days old")
        print(f"   Entries: {len(tablet.entries)}")
        print(f"   File: {session['path'].name}")
        print()
    
    print("Options:")
    print("  [1] 🗑️  Clear old sessions (keeps your AI sharp!)")
    print("  [2] 🔍 Review each session individually")
    print("  [3] ⏰ Skip for now (remind me in 7 days)")
    print("  [4] 🧹 Clear all and take a break (remind me in 30 days)")
    
    if health and (health['old'] > 20 or health['size_mb'] > 50):
        print("\n  💡 Tip: Regular cleanup helps your AI work better - just like taking vitamins!")
    
    try:
        choice = input("\nYour choice (1-4): ").strip()
        
        if choice == '1':
            # Delete all
            deleted = 0
            for session in temp_sessions:
                session['path'].unlink()
                deleted += 1
            print(f"\n✨ Cleared {deleted} old session(s) - Cabinet refreshed!")
            print("   Your AI will appreciate the extra space. 💊✓")
            save_last_cleanup()
        
        elif choice == '2':
            # Review individually
            deleted = 0
            kept = 0
            for session in temp_sessions:
                tablet = session['tablet']
                print(f"\n--- {tablet.metadata.title} ---")
                print(f"Age: {session['age_days']} days | Entries: {len(tablet.entries)}")
                
                # Show first entry as preview
                if tablet.entries:
                    preview = tablet.entries[0].diff[:200]
                    print(f"Preview: {preview}...")
                
                action = input("(d)elete, (k)eep, or (s)ave permanently? ").strip().lower()
                
                if action == 'd':
                    session['path'].unlink()
                    deleted += 1
                    print("  ✓ Cleared")
                elif action == 's':
                    # Remove 'temporary' tag and add 'saved'
                    tablet.metadata.tags = [t for t in tablet.metadata.tags if t not in ['temporary', 'auto-captured']]
                    tablet.metadata.tags.append('saved')
                    tablet.write(session['path'])
                    kept += 1
                    print("  ✓ Saved (won't auto-delete)")
                else:
                    kept += 1
                    print("  ✓ Keeping for now")
            
            print(f"\n✨ Done! Cleared: {deleted}, Kept: {kept}")
            save_last_cleanup()
        
        elif choice == '3':
            # Remind in 7 days
            print("\n⏰ No problem! I'll check back in 7 days.")
            save_last_cleanup()
        
        elif choice == '4':
            # Delete all and extend reminder
            deleted = 0
            for session in temp_sessions:
                session['path'].unlink()
                deleted += 1
            
            # Save timestamp 23 days in future (30 - 7 = 23 more days)
            with open(LAST_CLEANUP_FILE, 'w') as f:
                future_date = datetime.now() + timedelta(days=23)
                json.dump({
                    'last_cleanup': future_date.isoformat(),
                    'last_cleanup_human': future_date.strftime('%Y-%m-%d %H:%M:%S')
                }, f, indent=2)
            
            print(f"\n✨ Cleared {deleted} old session(s) - Cabinet refreshed!")
            print("   Taking a break - see you in 30 days! 💊")
        
        else:
            print("\n❓ No worries, skipping cleanup for now")
    
    except KeyboardInterrupt:
        print("\n\n⏸️  Cleanup paused - no problem!")
    except Exception as e:
        print(f"\n⚠️  Oops, something went wrong: {e}")
    
    print("="*70 + "\n")


def check_and_prompt_cleanup():
    """Check if cleanup is needed and prompt if so."""
    if should_run_cleanup():
        prompt_cleanup()


if __name__ == '__main__':
    check_and_prompt_cleanup()
