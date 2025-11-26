#!/usr/bin/env python3
"""
PATCH TKAM KERNEL
Updates the existing TKAM kernel with missing fields from a newly regenerated kernel.

This script:
1. Loads the newly regenerated kernel (from create_kernel.py)
2. Backs up the existing kernel with version suffix
3. Updates the existing TKAM kernel with missing fields
4. Preserves existing data where possible
5. Adds chapter_range/primary_chapter to extracts
6. Adds assigned_section and taxonomy fields to devices
7. Increments version number (v3.4 -> v3.5, v3.5 -> v3.6, etc.)

Usage:
    python patch_tkam_kernel.py <new_kernel_path> <existing_kernel_path> [--version <version>]
    
Example:
    python patch_tkam_kernel.py kernels/To_Kill_a_Mockingbird_kernel_v3_4.json kernels/To_Kill_a_Mockingbird_kernel_v3_4.json
    
Options:
    --version <version>  Specify target version (e.g., "3.5"). If not provided, auto-increments.
    --no-backup         Don't create backup of existing kernel
"""

import json
import sys
import re
import shutil
from pathlib import Path
from datetime import datetime


def patch_extracts(existing_extracts, new_extracts, narrative_position_mapping):
    """Add missing chapter_range and primary_chapter to extracts"""
    
    for section_name in ['exposition', 'rising_action', 'climax', 'falling_action', 'resolution']:
        if section_name in existing_extracts:
            # Get chapter info from narrative_position_mapping (preferred) or new_extracts
            if narrative_position_mapping and section_name in narrative_position_mapping:
                existing_extracts[section_name]['chapter_range'] = narrative_position_mapping[section_name].get('chapter_range', '')
                existing_extracts[section_name]['primary_chapter'] = narrative_position_mapping[section_name].get('primary_chapter', 1)
            elif new_extracts and section_name in new_extracts:
                existing_extracts[section_name]['chapter_range'] = new_extracts[section_name].get('chapter_range', '')
                existing_extracts[section_name]['primary_chapter'] = new_extracts[section_name].get('primary_chapter', 1)
    
    return existing_extracts


def patch_device(existing_device, new_device):
    """Patch a single device with missing fields from new device"""
    
    # Preserve existing fields
    patched = existing_device.copy()
    
    # Add missing taxonomy fields from new device
    taxonomy_fields = [
        'assigned_section', 'layer', 'function', 'engagement', 
        'classification', 'position_code', 'student_facing_type', 
        'pedagogical_function'
    ]
    
    for field in taxonomy_fields:
        if field not in patched and field in new_device:
            patched[field] = new_device[field]
    
    # Update examples structure if needed (preserve existing examples)
    # Only add missing fields to examples, don't replace them
    if 'examples' in new_device and 'examples' in patched:
        for i, new_ex in enumerate(new_device['examples']):
            if i < len(patched['examples']):
                # Merge example fields
                for field in ['freytag_section', 'scene', 'page_range', 'quote_snippet']:
                    if field not in patched['examples'][i] and field in new_ex:
                        patched['examples'][i][field] = new_ex[field]
    
    return patched


def patch_devices(existing_devices, new_devices):
    """Patch all devices with missing fields"""
    
    # Create a lookup by device name
    new_devices_by_name = {d.get('name', ''): d for d in new_devices}
    
    patched_devices = []
    
    for existing_device in existing_devices:
        device_name = existing_device.get('name', '')
        
        if device_name in new_devices_by_name:
            # Patch with matching new device
            patched = patch_device(existing_device, new_devices_by_name[device_name])
            patched_devices.append(patched)
        else:
            # Keep existing device as-is (no match found)
            patched_devices.append(existing_device)
    
    return patched_devices


def extract_version_from_filename(filename):
    """Extract version number from filename like 'kernel_v3_4.json' -> '3.4'"""
    match = re.search(r'v(\d+)[._](\d+)', str(filename))
    if match:
        return f"{match.group(1)}.{match.group(2)}"
    return None


def extract_version_from_metadata(kernel):
    """Extract version from kernel metadata"""
    return kernel.get('metadata', {}).get('kernel_version', None)


def increment_version(version_str):
    """Increment version string: '3.4' -> '3.5', '3.5' -> '3.6'"""
    if not version_str:
        return '3.4'
    
    parts = version_str.split('.')
    if len(parts) == 2:
        major, minor = int(parts[0]), int(parts[1])
        return f"{major}.{minor + 1}"
    return '3.4'


def get_versioned_filename(base_path, version):
    """Generate versioned filename: 'kernel_v3_4.json'"""
    base_path = Path(base_path)
    # Replace version in filename
    name = base_path.stem
    # Remove existing version pattern
    name = re.sub(r'_v\d+[._]\d+', '', name)
    name = re.sub(r'v\d+[._]\d+', '', name)
    # Add new version
    version_str = version.replace('.', '_')
    new_name = f"{name}_v{version_str}{base_path.suffix}"
    return base_path.parent / new_name


def patch_kernel(existing_kernel_path, new_kernel_path, target_version=None, create_backup=True):
    """Main patching function"""
    
    print("\n" + "="*80)
    print("PATCHING TKAM KERNEL")
    print("="*80)
    
    # Load kernels
    print(f"\n📖 Loading existing kernel: {existing_kernel_path}")
    with open(existing_kernel_path, 'r', encoding='utf-8') as f:
        existing_kernel = json.load(f)
    
    print(f"📖 Loading new kernel: {new_kernel_path}")
    with open(new_kernel_path, 'r', encoding='utf-8') as f:
        new_kernel = json.load(f)
    
    # Determine version
    current_version = extract_version_from_metadata(existing_kernel) or extract_version_from_filename(existing_kernel_path)
    if target_version:
        new_version = target_version
    else:
        new_version = increment_version(current_version)
    
    print(f"\n📌 Version: {current_version} -> {new_version}")
    
    # Create backup of existing kernel
    backup_path = None
    if create_backup:
        backup_path = get_versioned_filename(existing_kernel_path, current_version)
        # If backup already exists, add timestamp
        if backup_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_path.parent / f"{backup_path.stem}_{timestamp}{backup_path.suffix}"
        
        print(f"\n💾 Creating backup: {backup_path.name}")
        shutil.copy2(existing_kernel_path, backup_path)
        print(f"  ✓ Backup saved: {backup_path}")
    
    # Start with existing kernel
    patched_kernel = existing_kernel.copy()
    
    # Update metadata
    print("\n🔧 Updating metadata...")
    patched_kernel['metadata']['kernel_version'] = new_version
    patched_kernel['metadata']['chapter_aware'] = True
    patched_kernel['metadata']['patch_date'] = datetime.now().isoformat()
    patched_kernel['metadata']['patch_method'] = 'regenerated_and_patched'
    if 'upgrade_date' not in patched_kernel['metadata']:
        patched_kernel['metadata']['upgrade_date'] = datetime.now().isoformat()
    print(f"  ✓ Metadata updated (version: {new_version})")
    
    # Patch extracts
    print("\n🔧 Patching extracts with chapter_range and primary_chapter...")
    existing_extracts = patched_kernel.get('extracts', {})
    new_extracts = new_kernel.get('extracts', {})
    narrative_position_mapping = patched_kernel.get('narrative_position_mapping', {})
    
    patched_extracts = patch_extracts(existing_extracts, new_extracts, narrative_position_mapping)
    patched_kernel['extracts'] = patched_extracts
    print("  ✓ Extracts patched")
    
    # Patch devices
    print("\n🔧 Patching devices with taxonomy fields...")
    existing_devices = patched_kernel.get('micro_devices', [])
    new_devices = new_kernel.get('micro_devices', [])
    
    patched_devices = patch_devices(existing_devices, new_devices)
    patched_kernel['micro_devices'] = patched_devices
    print(f"  ✓ Patched {len(patched_devices)} devices")
    
    # Ensure text_structure exists
    if 'text_structure' not in patched_kernel:
        patched_kernel['text_structure'] = new_kernel.get('text_structure', {
            'has_chapters': True,
            'total_chapters_estimate': 31
        })
    
    # Ensure narrative_position_mapping exists
    if 'narrative_position_mapping' not in patched_kernel or not patched_kernel['narrative_position_mapping']:
        patched_kernel['narrative_position_mapping'] = new_kernel.get('narrative_position_mapping', {})
    
    # Generate output filename with new version
    output_path = get_versioned_filename(existing_kernel_path, new_version)
    
    print(f"\n💾 Saving patched kernel to: {output_path.name}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(patched_kernel, f, indent=2)
    
    file_size = Path(output_path).stat().st_size
    print(f"  ✓ Saved ({file_size:,} bytes)")
    
    # Summary
    print("\n" + "="*80)
    print("PATCHING SUMMARY")
    print("="*80)
    
    # Count added fields
    extracts_patched = sum(1 for s in patched_extracts.values() if 'chapter_range' in s)
    devices_with_assigned = sum(1 for d in patched_devices if 'assigned_section' in d)
    devices_with_taxonomy = sum(1 for d in patched_devices if 'layer' in d and 'function' in d)
    
    print(f"✓ Extracts with chapter_range: {extracts_patched}/5")
    print(f"✓ Devices with assigned_section: {devices_with_assigned}/{len(patched_devices)}")
    print(f"✓ Devices with taxonomy fields: {devices_with_taxonomy}/{len(patched_devices)}")
    
    print("\n✅ Kernel patching complete!")
    print(f"   Output: {output_path.name}")
    if create_backup and backup_path:
        print(f"   Backup: {backup_path.name}")
    
    return output_path


def main():
    if len(sys.argv) < 3:
        print("Usage: python patch_tkam_kernel.py <new_kernel_path> <existing_kernel_path> [options]")
        print("\nOptions:")
        print("  --version <version>  Target version (e.g., '3.5'). Auto-increments if not provided.")
        print("  --no-backup         Don't create backup of existing kernel")
        print("\nExample:")
        print("  python patch_tkam_kernel.py \\")
        print("    kernels/To_Kill_a_Mockingbird_kernel_v3_4.json \\")
        print("    kernels/To_Kill_a_Mockingbird_kernel_v3_4.json")
        print("\n  python patch_tkam_kernel.py \\")
        print("    kernels/To_Kill_a_Mockingbird_kernel_v3_4.json \\")
        print("    kernels/To_Kill_a_Mockingbird_kernel_v3_4.json \\")
        print("    --version 3.6")
        sys.exit(1)
    
    # Parse arguments
    args = sys.argv[1:]
    new_kernel_path = None
    existing_kernel_path = None
    target_version = None
    create_backup = True
    
    i = 0
    while i < len(args):
        if args[i] == '--version' and i + 1 < len(args):
            target_version = args[i + 1]
            i += 2
        elif args[i] == '--no-backup':
            create_backup = False
            i += 1
        elif not new_kernel_path:
            new_kernel_path = Path(args[i])
            i += 1
        elif not existing_kernel_path:
            existing_kernel_path = Path(args[i])
            i += 1
        else:
            i += 1
    
    if not new_kernel_path or not existing_kernel_path:
        print("❌ Error: Both new_kernel_path and existing_kernel_path are required")
        sys.exit(1)
    
    if not new_kernel_path.exists():
        print(f"❌ Error: New kernel not found: {new_kernel_path}")
        sys.exit(1)
    
    if not existing_kernel_path.exists():
        print(f"❌ Error: Existing kernel not found: {existing_kernel_path}")
        sys.exit(1)
    
    patch_kernel(existing_kernel_path, new_kernel_path, target_version, create_backup)


if __name__ == "__main__":
    main()



