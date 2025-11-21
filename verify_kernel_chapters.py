#!/usr/bin/env python3
"""
Verify kernel has chapter information (v3.4 structure)

Usage: python3 verify_kernel_chapters.py <kernel.json>
"""

import json
import sys
from pathlib import Path

def verify_kernel_chapters(kernel_path):
    """Check if kernel has v3.4 chapter-aware structure"""
    
    print(f"\n{'='*80}")
    print(f"KERNEL CHAPTER VERIFICATION")
    print(f"{'='*80}")
    print(f"File: {kernel_path}\n")
    
    # Load kernel
    try:
        with open(kernel_path, 'r') as f:
            kernel = json.load(f)
    except Exception as e:
        print(f"❌ Error loading kernel: {e}")
        return False
    
    passed = 0
    failed = 0
    
    # Check 1: Kernel version
    print("📋 Check 1: Kernel Version")
    kernel_version = kernel.get('metadata', {}).get('kernel_version')
    chapter_aware = kernel.get('metadata', {}).get('chapter_aware', False)
    
    if kernel_version == '3.4':
        print(f"   ✅ Kernel version: {kernel_version}")
        passed += 1
    else:
        print(f"   ⚠️  Kernel version: {kernel_version or 'not set'} (expected: 3.4)")
        failed += 1
    
    if chapter_aware:
        print(f"   ✅ Chapter-aware: {chapter_aware}")
        passed += 1
    else:
        print(f"   ❌ Chapter-aware: {chapter_aware}")
        failed += 1
    
    # Check 2: Text structure
    print("\n📋 Check 2: Text Structure")
    text_structure = kernel.get('text_structure', {})
    
    if text_structure:
        print(f"   ✅ Text structure present")
        print(f"      - Has chapters: {text_structure.get('has_chapters', 'unknown')}")
        print(f"      - Total chapters: {text_structure.get('total_chapters_estimate', 'unknown')}")
        passed += 1
    else:
        print(f"   ❌ Text structure missing")
        failed += 1
    
    # Check 3: Narrative position mapping
    print("\n📋 Check 3: Narrative Position Mapping")
    mapping = kernel.get('narrative_position_mapping', {})
    
    if mapping:
        print(f"   ✅ Narrative position mapping present")
        passed += 1
        
        expected_sections = ['exposition', 'rising_action', 'climax', 'falling_action', 'resolution']
        for section in expected_sections:
            if section in mapping:
                sect_map = mapping[section]
                chapter_range = sect_map.get('chapter_range', 'missing')
                primary_chapter = sect_map.get('primary_chapter', 'missing')
                print(f"      - {section}: Chapters {chapter_range}, Primary: {primary_chapter}")
            else:
                print(f"      ⚠️  {section}: missing")
    else:
        print(f"   ❌ Narrative position mapping missing")
        failed += 1
    
    # Check 4: Extracts have chapter info
    print("\n📋 Check 4: Extracts Chapter Information")
    extracts = kernel.get('extracts', {})
    
    if extracts:
        extract_chapters = 0
        extract_missing = 0
        
        for section, data in extracts.items():
            if 'chapter_range' in data or 'primary_chapter' in data:
                extract_chapters += 1
            else:
                extract_missing += 1
        
        if extract_chapters > 0:
            print(f"   ✅ {extract_chapters} extracts have chapter info")
            passed += 1
        else:
            print(f"   ❌ No extracts have chapter info")
            failed += 1
        
        if extract_missing > 0:
            print(f"   ⚠️  {extract_missing} extracts missing chapter info")
    else:
        print(f"   ❌ No extracts found")
        failed += 1
    
    # Check 5: Device examples have chapters
    print("\n📋 Check 5: Device Examples Chapter Information")
    devices = kernel.get('micro_devices', [])
    
    if devices:
        examples_with_chapters = 0
        examples_missing_chapters = 0
        
        for device in devices:
            for example in device.get('examples', []):
                if 'chapter' in example:
                    examples_with_chapters += 1
                else:
                    examples_missing_chapters += 1
        
        total_examples = examples_with_chapters + examples_missing_chapters
        
        if examples_with_chapters > 0:
            print(f"   ✅ {examples_with_chapters}/{total_examples} examples have chapter info ({examples_with_chapters/total_examples*100:.1f}%)")
            passed += 1
        else:
            print(f"   ❌ 0/{total_examples} examples have chapter info")
            failed += 1
        
        if examples_missing_chapters > 0:
            print(f"   ⚠️  {examples_missing_chapters} examples missing chapter info")
            
            # Show first few missing examples
            shown = 0
            for device in devices:
                if shown >= 3:
                    break
                for example in device.get('examples', []):
                    if shown >= 3:
                        break
                    if 'chapter' not in example:
                        print(f"      Example in '{device['name']}': {example.get('text', '')[:50]}...")
                        shown += 1
    else:
        print(f"   ❌ No devices found")
        failed += 1
    
    # Summary
    print(f"\n{'='*80}")
    print(f"VERIFICATION SUMMARY")
    print(f"{'='*80}")
    total = passed + failed
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {failed}/{total}")
    
    if failed == 0:
        print(f"\n✅ KERNEL IS FULLY CHAPTER-AWARE (v3.4)")
        print(f"   Ready for use with updated pipeline")
        return True
    elif passed >= 3:
        print(f"\n⚠️  KERNEL IS PARTIALLY CHAPTER-AWARE")
        print(f"   Some chapter info present but incomplete")
        print(f"   May work with fallback mechanisms")
        return True
    else:
        print(f"\n❌ KERNEL IS NOT CHAPTER-AWARE")
        print(f"   Regenerate with create_kernel_v3_4.py")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 verify_kernel_chapters.py <kernel.json>")
        print("\nExample:")
        print("  python3 verify_kernel_chapters.py kernels/The_Giver_kernel_v3_4.json")
        sys.exit(1)
    
    kernel_path = Path(sys.argv[1])
    
    if not kernel_path.exists():
        print(f"❌ Error: File not found: {kernel_path}")
        sys.exit(1)
    
    success = verify_kernel_chapters(kernel_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
