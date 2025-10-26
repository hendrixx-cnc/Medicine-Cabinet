#!/usr/bin/env python3
"""
Calculate binary file sizes for Medicine Cabinet files.
Shows estimated sizes for capsules and tablets.
"""

from pathlib import Path


def format_size(bytes_size):
    """Format bytes as human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"


def estimate_tablet_size(num_entries, avg_diff_size=2000, avg_notes_size=200):
    """
    Estimate tablet size.
    
    Format:
    - Header: 8 bytes (magic) + 2 bytes (version) + 8 bytes (timestamp) = 18 bytes
    - Metadata JSON: ~4 bytes (length) + ~200 bytes (typical JSON) = 204 bytes
    - Entry count: 4 bytes
    - Per entry:
      - path: 4 bytes (length) + ~30 bytes (average path) = 34 bytes
      - diff: 4 bytes (length) + avg_diff_size bytes
      - notes: 4 bytes (length) + avg_notes_size bytes
    """
    header_size = 18
    metadata_size = 204
    entry_count_size = 4
    
    per_entry_size = (
        34 +  # path with length prefix
        4 + avg_diff_size +  # diff with length prefix
        4 + avg_notes_size   # notes with length prefix
    )
    
    total = header_size + metadata_size + entry_count_size + (num_entries * per_entry_size)
    return total


def estimate_capsule_size(num_sections, avg_section_size=1000):
    """
    Estimate capsule size.
    
    Format:
    - Header: 8 bytes (magic) + 2 bytes (version) + 8 bytes (timestamp) = 18 bytes
    - Metadata JSON: ~4 bytes (length) + ~150 bytes = 154 bytes
    - Section count: 4 bytes
    - Per section:
      - type: 4 bytes
      - length: 8 bytes
      - data: avg_section_size bytes
    """
    header_size = 18
    metadata_size = 154
    section_count_size = 4
    
    per_section_size = 4 + 8 + avg_section_size
    
    total = header_size + metadata_size + section_count_size + (num_sections * per_section_size)
    return total


def calculate_actual_file_sizes():
    """Calculate sizes of actual files in sessions directory."""
    sessions_dir = Path('./sessions')
    if not sessions_dir.exists():
        return []
    
    files_info = []
    for file_path in sessions_dir.glob('*.auratab'):
        size = file_path.stat().st_size
        files_info.append({
            'name': file_path.name,
            'size': size,
            'size_formatted': format_size(size)
        })
    
    for file_path in sessions_dir.glob('*.auractx'):
        size = file_path.stat().st_size
        files_info.append({
            'name': file_path.name,
            'size': size,
            'size_formatted': format_size(size)
        })
    
    return sorted(files_info, key=lambda x: x['size'], reverse=True)


def main():
    print("=" * 70)
    print("💊 MEDICINE CABINET - FILE SIZE CALCULATOR")
    print("=" * 70)
    
    # Tablet size estimates
    print("\n📄 TABLET (.auratab) SIZE ESTIMATES:")
    print("-" * 70)
    scenarios = [
        (10, "Small session (10 entries)"),
        (50, "Medium session (50 entries)"),
        (100, "Large session (100 entries)"),
        (500, "Very large session (500 entries)"),
        (1000, "Massive session (1000 entries)")
    ]
    
    for num_entries, description in scenarios:
        size = estimate_tablet_size(num_entries)
        print(f"  {description:40} ~ {format_size(size)}")
    
    # Capsule size estimates
    print("\n📦 CAPSULE (.auractx) SIZE ESTIMATES:")
    print("-" * 70)
    capsule_scenarios = [
        (3, "Basic capsule (3 sections)"),
        (5, "Standard capsule (5 sections)"),
        (10, "Detailed capsule (10 sections)"),
    ]
    
    for num_sections, description in capsule_scenarios:
        size = estimate_capsule_size(num_sections)
        print(f"  {description:40} ~ {format_size(size)}")
    
    # Conversation capture estimates
    print("\n💬 CONVERSATION CAPTURE ESTIMATES:")
    print("-" * 70)
    print("  Average ChatGPT turn (user + AI):       ~ 1-3 KB per turn")
    print("  10 conversation turns:                  ~ 10-30 KB")
    print("  50 conversation turns:                  ~ 50-150 KB")
    print("  100 conversation turns:                 ~ 100-300 KB")
    print("  500 conversation turns (long session):  ~ 500 KB - 1.5 MB")
    
    # Actual files
    actual_files = calculate_actual_file_sizes()
    if actual_files:
        print("\n💾 ACTUAL FILES IN ./sessions:")
        print("-" * 70)
        total_size = sum(f['size'] for f in actual_files)
        for file_info in actual_files[:10]:  # Show top 10 largest
            print(f"  {file_info['name']:45} {file_info['size_formatted']:>10}")
        
        if len(actual_files) > 10:
            print(f"  ... and {len(actual_files) - 10} more files")
        
        print("-" * 70)
        print(f"  TOTAL: {len(actual_files)} files using {format_size(total_size)}")
    
    # Storage recommendations
    print("\n📊 STORAGE RECOMMENDATIONS:")
    print("-" * 70)
    print("  ✅ GOOD:    < 10 MB    (Clean and efficient)")
    print("  ⚠️  OKAY:    10-50 MB   (Consider cleanup)")
    print("  ⚠️  FULL:    50-100 MB  (Cleanup recommended)")
    print("  ❌ HEAVY:   > 100 MB   (Run cleanup now!)")
    print("\n  💡 TIP: Save important sessions explicitly with 'saved' tag")
    print("         Temporary sessions auto-delete after 30 days")
    
    # Maximum theoretical sizes
    print("\n🔬 THEORETICAL MAXIMUMS:")
    print("-" * 70)
    print("  String field max: 4 GB (uint32 length prefix)")
    print("  Tablet entries:   No limit (uint32 count = 4.2 billion max)")
    print("  Practical limit:  ~100 MB recommended for performance")
    print("  Sharing limit:    ~10 MB recommended for easy sharing")
    
    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
