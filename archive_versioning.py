#!/usr/bin/env python3
"""
Archive Versioning System
Properly label and track file versions in the archive directory

Usage:
    # Archive a file with version info
    python3 archive_versioning.py run_stage1a.py --version 5.0 --reason "Replaced by v5.1" --description "taxonomy fix"
    
    # List archived versions of a file
    python3 archive_versioning.py --list run_stage1a
    
    # Show archive metadata
    python3 archive_versioning.py --show-metadata
    
    # Retroactively label existing archive files
    python3 archive_versioning.py --retroactive-label
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import shutil

ARCHIVE_DIR = Path("archive")
METADATA_FILE = ARCHIVE_DIR / "archive_metadata.json"

# Version naming pattern: filename_vX.Y.Z_[description].ext
VERSION_PATTERN = "{base}_v{version}_{description}.{ext}"


def load_metadata() -> Dict:
    """Load archive metadata from JSON file"""
    if METADATA_FILE.exists():
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "archive_version": "1.0",
        "created": datetime.now().isoformat(),
        "files": {}
    }


def save_metadata(metadata: Dict):
    """Save archive metadata to JSON file"""
    metadata["last_updated"] = datetime.now().isoformat()
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)


def get_file_info(file_path: Path) -> tuple:
    """Extract base name, extension from file path"""
    stem = file_path.stem
    ext = file_path.suffix.lstrip('.')
    
    # Try to extract base name if it already has version info
    # e.g., "run_stage1a_v5_1" -> "run_stage1a"
    parts = stem.split('_')
    if len(parts) > 1 and parts[-1].startswith('v'):
        base = '_'.join(parts[:-1])
    else:
        base = stem
    
    return base, ext


def generate_versioned_name(base: str, ext: str, version: str, description: str) -> str:
    """Generate versioned filename"""
    # Clean description for filename (alphanumeric, underscore, hyphen only)
    clean_desc = "".join(c for c in description if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
    if not clean_desc:
        clean_desc = "archived"
    
    # Normalize version (v5.0 -> v5_0, v5.1 -> v5_1)
    version_clean = version.replace('.', '_').replace('-', '_')
    if not version_clean.startswith('v'):
        version_clean = f"v{version_clean}"
    
    return f"{base}_{version_clean}_{clean_desc}.{ext}"


def archive_file(
    source_path: Path,
    version: str,
    reason: str,
    description: str = "",
    replaced_by: Optional[str] = None,
    notes: str = ""
) -> Path:
    """
    Archive a file with proper versioning
    
    Args:
        source_path: Path to file to archive
        version: Version number (e.g., "5.0", "5.1")
        reason: Why this file is being archived
        description: Short description for filename
        replaced_by: What version/file replaced this one
        notes: Additional notes
    
    Returns:
        Path to archived file
    """
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")
    
    # Load metadata
    metadata = load_metadata()
    
    # Get file info
    base, ext = get_file_info(source_path)
    
    # Generate versioned filename
    if not description:
        description = reason.lower().replace(' ', '_')[:30]
    
    versioned_name = generate_versioned_name(base, ext, version, description)
    archive_path = ARCHIVE_DIR / versioned_name
    
    # Handle duplicates
    counter = 1
    original_archive_path = archive_path
    while archive_path.exists():
        versioned_name = generate_versioned_name(base, ext, version, f"{description}_{counter}")
        archive_path = ARCHIVE_DIR / versioned_name
        counter += 1
    
    # Copy file to archive
    shutil.copy2(source_path, archive_path)
    print(f"✓ Archived: {source_path.name} -> {archive_path.name}")
    
    # Update metadata
    if base not in metadata["files"]:
        metadata["files"][base] = []
    
    file_entry = {
        "archived_name": archive_path.name,
        "original_name": source_path.name,
        "version": version,
        "archived_date": datetime.now().isoformat(),
        "reason": reason,
        "description": description,
        "replaced_by": replaced_by,
        "notes": notes,
        "file_size": archive_path.stat().st_size,
        "source_path": str(source_path)
    }
    
    metadata["files"][base].append(file_entry)
    save_metadata(metadata)
    
    return archive_path


def list_archived_versions(base_name: str):
    """List all archived versions of a file"""
    metadata = load_metadata()
    
    if base_name not in metadata["files"]:
        print(f"No archived versions found for: {base_name}")
        return
    
    versions = metadata["files"][base_name]
    print(f"\nArchived versions of '{base_name}':")
    print("=" * 80)
    
    for i, entry in enumerate(sorted(versions, key=lambda x: x["archived_date"], reverse=True), 1):
        print(f"\n{i}. {entry['archived_name']}")
        print(f"   Version: {entry['version']}")
        print(f"   Date: {entry['archived_date']}")
        print(f"   Reason: {entry['reason']}")
        if entry.get('replaced_by'):
            print(f"   Replaced by: {entry['replaced_by']}")
        if entry.get('notes'):
            print(f"   Notes: {entry['notes']}")
        print(f"   Size: {entry['file_size']:,} bytes")


def show_metadata():
    """Display archive metadata summary"""
    metadata = load_metadata()
    
    print("\n" + "=" * 80)
    print("ARCHIVE METADATA")
    print("=" * 80)
    print(f"Created: {metadata.get('created', 'Unknown')}")
    print(f"Last Updated: {metadata.get('last_updated', 'Unknown')}")
    print(f"\nTotal files tracked: {len(metadata['files'])}")
    
    total_versions = sum(len(versions) for versions in metadata["files"].values())
    print(f"Total archived versions: {total_versions}")
    
    print("\nFiles with archived versions:")
    for base_name, versions in sorted(metadata["files"].items()):
        print(f"  - {base_name}: {len(versions)} version(s)")


def retroactive_label():
    """Interactively label existing archive files"""
    metadata = load_metadata()
    
    # Files to skip (system files, documentation, etc.)
    skip_files = {".DS_Store", "archive_metadata.json", "README.md", "commit_message.txt"}
    
    # Find all files recursively in archive directory
    archive_files = []
    for file_path in ARCHIVE_DIR.rglob("*"):
        if file_path.is_file() and file_path.name not in skip_files:
            archive_files.append(file_path)
    
    print(f"\nFound {len(archive_files)} files in archive directory (including subdirectories)")
    print("=" * 80)
    
    for file_path in sorted(archive_files):
        base, ext = get_file_info(file_path)
        rel_path = file_path.relative_to(ARCHIVE_DIR)
        rel_path_str = str(rel_path)
        
        # Check if already in metadata
        already_tracked = False
        if base in metadata["files"]:
            for entry in metadata["files"][base]:
                if entry["archived_name"] == rel_path_str or entry["archived_name"] == file_path.name:
                    already_tracked = True
                    break
        
        if already_tracked:
            print(f"✓ {rel_path_str} (already tracked)")
            continue
        
        # Show relative path for files in subdirectories
        print(f"\n📄 {rel_path_str}")
        print(f"   Detected base name: {base}")
        
        # Try to extract version from filename
        version = input("   Version (e.g., 5.0, 5.1, or 'skip'): ").strip()
        if version.lower() == 'skip':
            continue
        
        reason = input("   Reason for archiving: ").strip()
        description = input("   Description (short, for filename): ").strip()
        replaced_by = input("   Replaced by (optional): ").strip() or None
        notes = input("   Additional notes (optional): ").strip()
        
        # Add to metadata
        if base not in metadata["files"]:
            metadata["files"][base] = []
        
        # Store relative path for files in subdirectories
        file_entry = {
            "archived_name": rel_path_str,
            "original_name": file_path.name,  # We don't know original
            "version": version,
            "archived_date": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            "reason": reason,
            "description": description,
            "replaced_by": replaced_by,
            "notes": notes,
            "file_size": file_path.stat().st_size,
            "source_path": "unknown (retroactive labeling)"
        }
        
        metadata["files"][base].append(file_entry)
        print(f"   ✓ Added to metadata")
    
    save_metadata(metadata)
    print("\n✓ Metadata updated!")


def main():
    parser = argparse.ArgumentParser(
        description="Archive file versioning system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "file",
        nargs="?",
        help="File to archive (or base name for --list)"
    )
    
    parser.add_argument(
        "--version", "-v",
        help="Version number (e.g., 5.0, 5.1)"
    )
    
    parser.add_argument(
        "--reason", "-r",
        help="Reason for archiving"
    )
    
    parser.add_argument(
        "--description", "-d",
        default="",
        help="Short description for filename"
    )
    
    parser.add_argument(
        "--replaced-by",
        help="What version/file replaced this one"
    )
    
    parser.add_argument(
        "--notes", "-n",
        default="",
        help="Additional notes"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List archived versions of a file"
    )
    
    parser.add_argument(
        "--show-metadata",
        action="store_true",
        help="Show archive metadata summary"
    )
    
    parser.add_argument(
        "--retroactive-label",
        action="store_true",
        help="Interactively label existing archive files"
    )
    
    args = parser.parse_args()
    
    # Ensure archive directory exists
    ARCHIVE_DIR.mkdir(exist_ok=True)
    
    # Initialize metadata if it doesn't exist
    if not METADATA_FILE.exists():
        save_metadata(load_metadata())
    
    # Handle different modes
    if args.retroactive_label:
        retroactive_label()
    elif args.show_metadata:
        show_metadata()
    elif args.list:
        if not args.file:
            print("Error: --list requires a base filename")
            sys.exit(1)
        list_archived_versions(args.file)
    elif args.file:
        # Archive mode
        if not args.version or not args.reason:
            print("Error: --version and --reason are required for archiving")
            sys.exit(1)
        
        source_path = Path(args.file)
        archive_path = archive_file(
            source_path,
            args.version,
            args.reason,
            args.description,
            args.replaced_by,
            args.notes
        )
        print(f"\n✓ File archived successfully!")
        print(f"  Location: {archive_path}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
