#!/usr/bin/env python3
"""
EMPIRICAL SCRIPT VERIFICATION
Tests what's actually working by examining files, not trusting docs.
"""

import json
import os
from pathlib import Path

def test_result(label, success, details=""):
    """Print test result"""
    icon = "✓" if success else "✗"
    print(f"{icon} {label}")
    if details:
        print(f"   {details}")

def verify_stage1a_output(filepath):
    """Check if Stage 1A output has expected structure"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        has_metadata = 'metadata' in data
        has_macro_micro = 'macro_micro_packages' in data
        
        if has_macro_micro:
            packages = data['macro_micro_packages']
            week_count = len([k for k in packages.keys() if 'week' in k.lower()])
        else:
            week_count = 0
            
        return {
            'valid': has_metadata and has_macro_micro,
            'week_count': week_count,
            'has_metadata': has_metadata,
            'has_packages': has_macro_micro
        }
    except Exception as e:
        return {'valid': False, 'error': str(e)}

def verify_stage1b_output(filepath):
    """Check if Stage 1B output has expected structure"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        has_metadata = 'metadata' in data
        has_week_packages = 'week_packages' in data
        
        if has_week_packages:
            packages = data['week_packages']
            if isinstance(packages, list):
                week_count = len(packages)
            else:
                week_count = len(packages.keys())
        else:
            week_count = 0
            
        return {
            'valid': has_metadata and has_week_packages,
            'week_count': week_count,
            'has_metadata': has_metadata,
            'has_packages': has_week_packages
        }
    except Exception as e:
        return {'valid': False, 'error': str(e)}

def main():
    print("=" * 60)
    print("EMPIRICAL SCRIPT VERIFICATION")
    print("=" * 60)
    print()
    
    # Work in current directory
    project_dir = Path('.')
    print(f"📁 Checking: {project_dir.resolve()}")
    print()
    
    # 1. Check for required scripts
    print("=== CHECKING SCRIPT FILES ===")
    scripts = {
        'run_stage1a.py': 'run_stage1a.py',
        'run_stage1b.py': 'run_stage1b.py',
        'run_stage2_fixed.py': 'run_stage2_fixed.py',
        'device_taxonomy_mapping.json': 'device_taxonomy_mapping.json'
    }
    
    all_exist = True
    for name, filename in scripts.items():
        exists = Path(filename).exists()
        test_result(f"{name} exists", exists)
        if not exists:
            all_exist = False
    print()
    
    if not all_exist:
        print("⚠️  Missing required files. Cannot verify pipeline.")
        return 1
    
    # 2. Find output files - check both root and outputs/ directory
    print("=== CHECKING OUTPUT FILES ===")
    
    # Determine where to look for outputs
    outputs_dir = Path('outputs')
    if outputs_dir.exists() and outputs_dir.is_dir():
        search_locations = [outputs_dir, Path('.')]
        print("📂 Searching in: ./ and outputs/")
    else:
        search_locations = [Path('.')]
        print("📂 Searching in: ./")
    print()
    
    # Find stage1a outputs
    stage1a_files = []
    for loc in search_locations:
        stage1a_files.extend(list(loc.glob('*_stage1a_*.json')))
    
    if stage1a_files:
        print(f"Found {len(stage1a_files)} Stage 1A output file(s):")
        for f in stage1a_files:
            result = verify_stage1a_output(f)
            location = f"[{f.parent}]" if str(f.parent) != '.' else "[root]"
            if result['valid']:
                test_result(f"  {f.name}", True, 
                          f"{result['week_count']} weeks {location}")
            else:
                test_result(f"  {f.name}", False, 
                          result.get('error', 'Invalid structure'))
    else:
        print("No Stage 1A output files found")
    print()
    
    # Find stage1b outputs
    stage1b_files = []
    for loc in search_locations:
        stage1b_files.extend(list(loc.glob('*_stage1b_*.json')))
    
    if stage1b_files:
        print(f"Found {len(stage1b_files)} Stage 1B output file(s):")
        for f in stage1b_files:
            result = verify_stage1b_output(f)
            location = f"[{f.parent}]" if str(f.parent) != '.' else "[root]"
            if result['valid']:
                test_result(f"  {f.name}", True, 
                          f"{result['week_count']} weeks {location}")
            else:
                test_result(f"  {f.name}", False, 
                          result.get('error', 'Invalid structure'))
    else:
        print("No Stage 1B output files found")
    print()
    
    # 3. Check compatibility if outputs exist
    if stage1a_files and stage1b_files:
        print("=== CHECKING PIPELINE COMPATIBILITY ===")
        
        # Quick check: do outputs have expected keys?
        stage1a_sample = stage1a_files[0]
        stage1b_sample = stage1b_files[0]
        
        try:
            with open(stage1a_sample) as f:
                stage1a_data = json.load(f)
            with open(stage1b_sample) as f:
                stage1b_data = json.load(f)
            
            # Stage 1B needs macro_micro_packages from Stage 1A
            stage1b_compat = 'macro_micro_packages' in stage1a_data
            test_result("Stage 1B ← Stage 1A", stage1b_compat)
            
            # Stage 2 needs week_packages from Stage 1B
            stage2_compat = 'week_packages' in stage1b_data
            test_result("Stage 2 ← Stage 1B", stage2_compat)
            
        except Exception as e:
            print(f"✗ Compatibility check failed: {e}")
        print()
    
    # 4. Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    
    if stage1a_files and stage1b_files:
        week_counts = set()
        for f in stage1a_files:
            result = verify_stage1a_output(f)
            if result['valid']:
                week_counts.add(result['week_count'])
        
        if week_counts:
            weeks = list(week_counts)[0]
            print(f"✓ Pipeline is configured for {weeks}-week progression")
        print(f"✓ Stage 1A outputs: {len(stage1a_files)} file(s)")
        print(f"✓ Stage 1B outputs: {len(stage1b_files)} file(s)")
        print()
        print("Your WORKING pipeline:")
        print("  1. run_stage1a.py → *_stage1a_v5_0.json")
        print("  2. run_stage1b.py → *_stage1b_v5_0.json")
        print("  3. run_stage2_fixed.py → worksheets")
    else:
        print("⚠️  Pipeline outputs not found")
        print()
        print("This means either:")
        print("  • You haven't run the pipeline yet, OR")
        print("  • Output files are in a different location")
        print()
        print("To verify setup, try running:")
        print("  python3 run_stage1a.py kernels/[book]_kernel_v3_3.json")
    
    print()
    return 0

if __name__ == '__main__':
    exit(main())
