#!/usr/bin/env python3
"""
FULL PIPELINE INTEGRATION TEST
Tests Stage 1A → Stage 1B → Stage 2 pipeline on a known kernel

Usage:
    python3 test_full_pipeline.py
    python3 test_full_pipeline.py --kernel kernels/The_Giver_kernel_v3.3.json
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BLUE}{'='*80}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def run_command(cmd, description):
    """Run a command and capture output"""
    print(f"\n{Colors.BLUE}Running: {description}{Colors.END}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print_success(f"{description} completed")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print_error(f"{description} failed")
        print(f"Error output:\n{e.stderr}")
        return None

def validate_json_structure(file_path, expected_keys, stage_name):
    """Validate JSON file has expected structure"""
    print(f"\n{Colors.BLUE}Validating {stage_name} output...{Colors.END}")
    
    if not file_path.exists():
        print_error(f"File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Check expected keys
        missing_keys = [key for key in expected_keys if key not in data]
        if missing_keys:
            print_error(f"Missing keys: {missing_keys}")
            return False
        
        print_success(f"All expected keys present: {expected_keys}")
        return True
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON: {e}")
        return False
    except Exception as e:
        print_error(f"Error reading file: {e}")
        return False

def validate_stage1a_output(output_path):
    """Validate Stage 1A JSON output"""
    expected_keys = ["metadata", "macro_elements", "device_mapping", "macro_micro_packages"]
    
    if not validate_json_structure(output_path, expected_keys, "Stage 1A"):
        return False
    
    with open(output_path, 'r') as f:
        data = json.load(f)
    
    # Validate 5 weeks in device_mapping
    device_mapping = data.get("device_mapping", {})
    expected_weeks = [
        'week_1_exposition',
        'week_2_literary_devices',
        'week_3_structure',
        'week_4_narrative_voice',
        'week_5_rhetorical_voice'
    ]
    
    missing_weeks = [week for week in expected_weeks if week not in device_mapping]
    if missing_weeks:
        print_error(f"Missing weeks in device_mapping: {missing_weeks}")
        return False
    
    print_success(f"All 5 weeks present in device_mapping")
    
    # Validate macro_micro_packages
    packages = data.get("macro_micro_packages", {})
    expected_package_keys = [
        'week1_exposition',
        'week2_literary_devices',
        'week3_structure',
        'week4_narrative_voice',
        'week5_rhetorical_voice'
    ]
    
    missing_packages = [key for key in expected_package_keys if key not in packages]
    if missing_packages:
        print_error(f"Missing package keys: {missing_packages}")
        return False
    
    print_success(f"All 5 week packages present")
    
    # Print device distribution
    print(f"\n{Colors.BLUE}Device Distribution:{Colors.END}")
    for week_key, devices in device_mapping.items():
        print(f"  {week_key}: {len(devices)} devices")
    
    return True

def validate_stage1b_output(json_path, md_path):
    """Validate Stage 1B JSON and Markdown outputs"""
    
    # Validate JSON
    expected_keys = ["metadata", "progression_summary", "week_packages"]
    if not validate_json_structure(json_path, expected_keys, "Stage 1B"):
        return False
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Check total_weeks in metadata
    total_weeks = data.get("metadata", {}).get("total_weeks", 0)
    if total_weeks != 5:
        print_error(f"Expected 5 weeks, got {total_weeks}")
        return False
    
    print_success(f"Metadata shows 5 weeks")
    
    # Validate week_packages
    week_packages = data.get("week_packages", [])
    if len(week_packages) != 5:
        print_error(f"Expected 5 week packages, got {len(week_packages)}")
        return False
    
    print_success(f"5 week packages present")
    
    # Validate each week has required fields
    required_fields = ["week", "macro_focus", "teaching_goal", "scaffolding_level", "micro_devices"]
    for pkg in week_packages:
        week_num = pkg.get("week", "?")
        missing = [field for field in required_fields if field not in pkg]
        if missing:
            print_error(f"Week {week_num} missing fields: {missing}")
            return False
    
    print_success(f"All weeks have required fields")
    
    # Validate Markdown file exists
    if not md_path.exists():
        print_error(f"Markdown file not found: {md_path}")
        return False
    
    # Check markdown has 5 weeks
    with open(md_path, 'r') as f:
        md_content = f.read()
    
    if "## WEEK 5:" not in md_content:
        print_error("Markdown file missing Week 5 section")
        return False
    
    print_success("Markdown file contains Week 5")
    
    return True

def validate_stage2_output(output_dir, week_num):
    """Validate Stage 2 worksheet outputs"""
    
    expected_files = [
        f"Week_{week_num}_Literary_Analysis_Worksheet.md",
        f"Week_{week_num}_TVODE_Construction.md",
        f"Week_{week_num}_Teacher_Key.md"
    ]
    
    print(f"\n{Colors.BLUE}Checking for Week {week_num} worksheets...{Colors.END}")
    
    all_found = True
    for filename in expected_files:
        file_path = output_dir / filename
        if file_path.exists():
            size = file_path.stat().st_size
            print_success(f"Found {filename} ({size:,} bytes)")
        else:
            print_error(f"Missing {filename}")
            all_found = False
    
    return all_found

def test_full_pipeline(kernel_path):
    """Run full pipeline test"""
    
    print_header("FULL PIPELINE INTEGRATION TEST")
    print(f"Kernel: {kernel_path}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Extract title for output file names
    with open(kernel_path, 'r') as f:
        kernel = json.load(f)
    title = kernel.get("text_metadata", {}).get("title", "Unknown")
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
    
    output_dir = Path("outputs")
    
    # Expected output paths
    stage1a_output = output_dir / f"{safe_title}_stage1a_v5.0.json"
    stage1b_json = output_dir / f"{safe_title}_stage1b_v5.0.json"
    stage1b_md = output_dir / f"{safe_title}_Integrated_Progression.md"
    
    # Test counters
    tests_passed = 0
    tests_failed = 0
    
    # ========================================================================
    # STAGE 1A TEST
    # ========================================================================
    print_header("STAGE 1A: MACRO-MICRO EXTRACTION")
    
    output = run_command(
        ["python3", "run_stage1a.py", str(kernel_path)],
        "Stage 1A extraction"
    )
    
    if output is None:
        tests_failed += 1
        print_error("Stage 1A failed to run")
    else:
        if validate_stage1a_output(stage1a_output):
            tests_passed += 1
            print_success("Stage 1A validation passed")
        else:
            tests_failed += 1
            print_error("Stage 1A validation failed")
    
    # ========================================================================
    # STAGE 1B TEST
    # ========================================================================
    print_header("STAGE 1B: WEEKLY PACKAGING")
    
    if stage1a_output.exists():
        output = run_command(
            ["python3", "run_stage1b.py", str(stage1a_output)],
            "Stage 1B packaging"
        )
        
        if output is None:
            tests_failed += 1
            print_error("Stage 1B failed to run")
        else:
            if validate_stage1b_output(stage1b_json, stage1b_md):
                tests_passed += 1
                print_success("Stage 1B validation passed")
            else:
                tests_failed += 1
                print_error("Stage 1B validation failed")
    else:
        tests_failed += 1
        print_error("Skipping Stage 1B (Stage 1A output missing)")
    
    # ========================================================================
    # STAGE 2 TEST (Week 1 only)
    # ========================================================================
    print_header("STAGE 2: WORKSHEET GENERATION (Week 1)")
    
    if stage1b_json.exists():
        output = run_command(
            ["python3", "run_stage2_fixed.py", str(stage1b_json), str(kernel_path), "--week", "1"],
            "Stage 2 worksheet generation"
        )
        
        if output is None:
            tests_failed += 1
            print_error("Stage 2 failed to run")
        else:
            if validate_stage2_output(output_dir, 1):
                tests_passed += 1
                print_success("Stage 2 validation passed")
            else:
                tests_failed += 1
                print_error("Stage 2 validation failed")
    else:
        tests_failed += 1
        print_error("Skipping Stage 2 (Stage 1B output missing)")
    
    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    print_header("TEST RESULTS")
    
    total_tests = tests_passed + tests_failed
    
    print(f"Total tests: {total_tests}")
    print_success(f"Passed: {tests_passed}")
    if tests_failed > 0:
        print_error(f"Failed: {tests_failed}")
    
    if tests_failed == 0:
        print(f"\n{Colors.GREEN}{'='*80}{Colors.END}")
        print(f"{Colors.GREEN}ALL TESTS PASSED ✓{Colors.END}")
        print(f"{Colors.GREEN}{'='*80}{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{'='*80}{Colors.END}")
        print(f"{Colors.RED}SOME TESTS FAILED ✗{Colors.END}")
        print(f"{Colors.RED}{'='*80}{Colors.END}\n")
        return 1

def main():
    # Default kernel
    default_kernel = "kernels/The_Giver_kernel_v3.3.json"
    
    # Parse command line args
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("Usage: python3 test_full_pipeline.py [--kernel path/to/kernel.json]")
            sys.exit(0)
        elif sys.argv[1] == "--kernel" and len(sys.argv) > 2:
            kernel_path = Path(sys.argv[2])
        else:
            kernel_path = Path(sys.argv[1])
    else:
        kernel_path = Path(default_kernel)
    
    # Validate kernel exists
    if not kernel_path.exists():
        print_error(f"Kernel file not found: {kernel_path}")
        print("Usage: python3 test_full_pipeline.py [--kernel path/to/kernel.json]")
        sys.exit(1)
    
    # Run tests
    exit_code = test_full_pipeline(kernel_path)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
