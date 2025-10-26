#!/usr/bin/env python3
"""
Medicine Cabinet Extension Setup
Automatically configures native messaging host when extension is installed
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path


def get_extension_id():
    """Prompt user for extension ID"""
    print("\n" + "="*60)
    print("MEDICINE CABINET NATIVE MESSAGING SETUP")
    print("="*60)
    print("\nTo find your extension ID:")
    print("1. Open chrome://extensions in your browser")
    print("2. Enable 'Developer mode' (top right)")
    print("3. Find 'Medicine Cabinet' extension")
    print("4. Copy the ID (long string like: abcdefghijklmnopqrstuvwxyz123456)")
    print()
    
    extension_id = input("Enter your extension ID: ").strip()
    return extension_id


def get_install_dir():
    """Get installation directory"""
    # Default to current directory
    script_dir = Path(__file__).parent.absolute()
    return script_dir


def create_wrapper_script(install_dir):
    """Create wrapper script for native host"""
    wrapper_path = Path("/usr/local/bin/medicine-cabinet-host")
    native_host_path = install_dir / "native_host.py"
    
    wrapper_content = f"""#!/bin/bash
exec python3 "{native_host_path}" "$@"
"""
    
    print(f"\n📝 Creating wrapper script at {wrapper_path}")
    
    try:
        # Write wrapper
        with open(wrapper_path, 'w') as f:
            f.write(wrapper_content)
        
        # Make executable
        os.chmod(wrapper_path, 0o755)
        print(f"✅ Wrapper script created")
        return True
    
    except PermissionError:
        print(f"⚠️  Need sudo permissions to create {wrapper_path}")
        print(f"   Running: sudo bash -c 'cat > {wrapper_path}'")
        
        try:
            subprocess.run(
                ['sudo', 'bash', '-c', f'cat > {wrapper_path}'],
                input=wrapper_content.encode(),
                check=True
            )
            subprocess.run(['sudo', 'chmod', '+x', str(wrapper_path)], check=True)
            print(f"✅ Wrapper script created with sudo")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create wrapper: {e}")
            return False


def install_manifest(browser, manifest_path, extension_id):
    """Install native messaging manifest for a browser"""
    
    # Read template
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    # Update with extension ID
    if 'allowed_origins' in manifest:
        # Chrome/Edge format
        manifest['allowed_origins'] = [
            f"chrome-extension://{extension_id}/"
        ]
    elif 'allowed_extensions' in manifest:
        # Firefox format
        manifest['allowed_extensions'] = [
            f"{extension_id}@medicinecabinet"
        ]
    
    # Determine installation path
    home = Path.home()
    
    if browser == 'chrome':
        if sys.platform == 'darwin':  # macOS
            manifest_dir = home / "Library/Application Support/Google/Chrome/NativeMessagingHosts"
        else:  # Linux
            manifest_dir = home / ".config/google-chrome/NativeMessagingHosts"
    
    elif browser == 'chromium':
        manifest_dir = home / ".config/chromium/NativeMessagingHosts"
    
    elif browser == 'edge':
        if sys.platform == 'darwin':
            manifest_dir = home / "Library/Application Support/Microsoft Edge/NativeMessagingHosts"
        else:
            manifest_dir = home / ".config/microsoft-edge/NativeMessagingHosts"
    
    elif browser == 'firefox':
        if sys.platform == 'darwin':
            manifest_dir = home / "Library/Application Support/Mozilla/NativeMessagingHosts"
        else:
            manifest_dir = home / ".mozilla/native-messaging-hosts"
    
    else:
        return False
    
    # Create directory and install manifest
    try:
        manifest_dir.mkdir(parents=True, exist_ok=True)
        manifest_file = manifest_dir / "com.medicinecabinet.host.json"
        
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✅ Installed manifest for {browser}")
        return True
    
    except Exception as e:
        print(f"⚠️  Failed to install for {browser}: {e}")
        return False


def main():
    """Main setup routine"""
    
    # Get extension ID
    extension_id = get_extension_id()
    
    if not extension_id or len(extension_id) < 20:
        print("❌ Invalid extension ID")
        return 1
    
    # Get installation directory
    install_dir = get_install_dir()
    native_host_path = install_dir / "native_host.py"
    
    if not native_host_path.exists():
        print(f"❌ native_host.py not found at {native_host_path}")
        return 1
    
    # Make native_host.py executable
    os.chmod(native_host_path, 0o755)
    
    # Create wrapper script
    if not create_wrapper_script(install_dir):
        print("❌ Failed to create wrapper script")
        return 1
    
    # Determine which browsers to install for
    print("\n🔍 Detecting browsers...")
    browsers = []
    
    if sys.platform == 'darwin':
        # macOS
        if Path("/Applications/Google Chrome.app").exists():
            browsers.append('chrome')
        if Path("/Applications/Microsoft Edge.app").exists():
            browsers.append('edge')
        if Path("/Applications/Firefox.app").exists():
            browsers.append('firefox')
    else:
        # Linux
        if Path.home().joinpath(".config/google-chrome").exists():
            browsers.append('chrome')
        if Path.home().joinpath(".config/chromium").exists():
            browsers.append('chromium')
        if Path.home().joinpath(".config/microsoft-edge").exists():
            browsers.append('edge')
        if Path.home().joinpath(".mozilla").exists():
            browsers.append('firefox')
    
    if not browsers:
        print("⚠️  No supported browsers detected")
        print("   Browsers will be configured when first installed")
        browsers = ['chrome', 'edge', 'firefox']  # Install for all
    
    # Install manifests
    print(f"\n📦 Installing native messaging manifests...")
    manifest_template = install_dir / "native-messaging/com.medicinecabinet.host.json"
    manifest_firefox = install_dir / "native-messaging/com.medicinecabinet.host.firefox.json"
    
    success_count = 0
    for browser in browsers:
        if browser == 'firefox':
            if manifest_firefox.exists():
                if install_manifest(browser, manifest_firefox, extension_id):
                    success_count += 1
        else:
            if manifest_template.exists():
                if install_manifest(browser, manifest_template, extension_id):
                    success_count += 1
    
    # Summary
    print("\n" + "="*60)
    if success_count > 0:
        print("✅ SETUP COMPLETE!")
        print(f"   Installed for {success_count} browser(s)")
        print("\nNext steps:")
        print("1. Reload your browser extension")
        print("2. Load a .auractx file in the extension")
        print("3. Visit ChatGPT - context will auto-pop!")
        print("4. Conversations will be automatically captured")
        print(f"\nLogs: ~/.medicine_cabinet/native_host.log")
    else:
        print("⚠️  SETUP INCOMPLETE")
        print("   No browsers were successfully configured")
        print("   You may need to run this script with sudo")
    print("="*60)
    
    return 0 if success_count > 0 else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
