#!/usr/bin/env python3
"""
Setup script for Kernel Creation Automation

This script:
1. Creates necessary directory structure
2. Verifies protocol files are present
3. Checks API key configuration
4. Tests basic functionality
"""

import os
import sys
from pathlib import Path

def create_directories():
    """Create required directory structure"""
    print("\n📁 Creating directory structure...")
    
    dirs = [
        "protocols",
        "books",
        "kernels",
        "outputs"
    ]
    
    for dir_name in dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
            print(f"  ✓ Created: {dir_name}/")
        else:
            print(f"  ✓ Exists: {dir_name}/")

def check_protocol_files():
    """Check if protocol files are present"""
    print("\n📚 Checking protocol files...")
    
    required_files = [
        "Kernel_Validation_Protocol_v3_3.md",
        "Kernel_Protocol_Enhancement_v3_3.md",
        "Artifact_1_-_Device_Taxonomy_by_Alignment_Function",
        "Artifact_2_-_Text_Tagging_Protocol",
        "LEM_-_Stage_1_-_Narrative-Rhetoric_Triangulation"
    ]
    
    protocols_dir = Path("protocols")
    missing = []
    
    for filename in required_files:
        filepath = protocols_dir / filename
        if filepath.exists():
            print(f"  ✓ Found: {filename}")
        else:
            print(f"  ✗ Missing: {filename}")
            missing.append(filename)
    
    if missing:
        print(f"\n⚠️  Warning: {len(missing)} protocol file(s) missing")
        print("Please add these files to the protocols/ directory:")
        for f in missing:
            print(f"  - {f}")
        return False
    
    print("\n✅ All protocol files present")
    return True

def check_api_key():
    """Check if API key is configured"""
    print("\n🔑 Checking API key configuration...")
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("  ✗ ANTHROPIC_API_KEY not set")
        print("\n⚠️  Please set your API key:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        print("\nGet your API key from: https://console.anthropic.com")
        return False
    
    if api_key.startswith("sk-ant-"):
        print("  ✓ API key is set")
        print(f"  Key starts with: {api_key[:15]}...")
        return True
    else:
        print("  ⚠️  API key format looks incorrect")
        print(f"  Expected format: sk-ant-...")
        print(f"  Your key starts with: {api_key[:10]}...")
        return False

def check_dependencies():
    """Check if Python dependencies are installed"""
    print("\n📦 Checking Python dependencies...")
    
    required = {
        "anthropic": "Anthropic API client",
        "PyPDF2": "PDF processing"
    }
    
    missing = []
    
    for package, description in required.items():
        try:
            __import__(package)
            print(f"  ✓ {package}: {description}")
        except ImportError:
            print(f"  ✗ {package}: {description} - NOT INSTALLED")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Warning: {len(missing)} package(s) missing")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("\n✅ All dependencies installed")
    return True

def print_example_usage():
    """Print example usage"""
    print("\n" + "="*80)
    print("SETUP COMPLETE!")
    print("="*80)
    print("\nExample usage:")
    print("\n  python create_kernel.py \\")
    print('    books/TKAM.pdf \\')
    print('    "To Kill a Mockingbird" \\')
    print('    "Harper Lee" \\')
    print('    "Harper Perennial Modern Classics, 2006"')
    print("\nNext steps:")
    print("  1. Add your book PDF/txt files to books/")
    print("  2. Ensure protocol files are in protocols/")
    print("  3. Run the create_kernel.py script")
    print("\nFor more details, see README.md")
    print("="*80)

def main():
    """Run setup checks"""
    print("="*80)
    print("KERNEL CREATION AUTOMATION - SETUP")
    print("="*80)
    
    # Create directories
    create_directories()
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Check protocol files
    protocols_ok = check_protocol_files()
    
    # Check API key
    api_ok = check_api_key()
    
    # Summary
    print("\n" + "="*80)
    print("SETUP SUMMARY")
    print("="*80)
    print(f"  Directories: ✓ Created")
    print(f"  Dependencies: {'✓ OK' if deps_ok else '✗ MISSING'}")
    print(f"  Protocol Files: {'✓ OK' if protocols_ok else '✗ MISSING'}")
    print(f"  API Key: {'✓ OK' if api_ok else '✗ NOT SET'}")
    
    if deps_ok and protocols_ok and api_ok:
        print("\n✅ Setup complete! Ready to create kernels.")
        print_example_usage()
        return 0
    else:
        print("\n⚠️  Setup incomplete. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
