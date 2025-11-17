#!/usr/bin/env python3
"""
STAGE 1A AUTOMATION
Extract macro-micro packages from kernel JSON

Usage:
    python3 run_stage1a.py kernels/Book_kernel_v3.3.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def extract_macro_elements(kernel):
    """Extract macro alignment elements from kernel"""
    
    narrative = kernel.get("narrative", {})
    voice = narrative.get("voice", {})
    structure = narrative.get("structure", {})
    
    return {
        "exposition": {
            "element_type": "Exposition",
            "description": "How characters and setting are introduced",
            "variables": {
                "characterization_method": voice.get("character_revelation", ""),
                "mode_dominance": voice.get("mode_dominance", ""),
                "mode_description": voice.get("mode_dominance_description", "")
            }
        },
        "structure": {
            "element_type": "Structure",
            "description": "How plot is organized and paced",
            "variables": {
                "plot_architecture": structure.get("plot_architecture", ""),
                "chronology": structure.get("chronology", ""),
                "causation": structure.get("causation", ""),
                "pacing_dominance": structure.get("pacing_dominance", "")
            }
        },
        "voice": {
            "element_type": "Voice",
            "description": "Narrative perspective and narration",
            "variables": {
                "pov": voice.get("pov", ""),
                "focalization": voice.get("focalization", ""),
                "reliability": voice.get("reliability", ""),
                "temporal_distance": voice.get("temporal_distance", "")
            }
        }
    }


def categorize_device(device):
    """Determine which macro element this device executes"""
    
    layer = device.get("layer", "")
    function = device.get("function", "")
    name = device.get("name", "").lower()
    
    # Week 2: Foundation devices (clear examples for teaching)
    if any(term in name for term in ["symbol", "metaphor", "foreshadow"]):
        return "devices_general", "Foundation device for teaching device recognition"
    
    # Week 1: Exposition devices
    if "characterization" in name or "imagery" in name or "dialect" in name:
        return "exposition", "Builds exposition through descriptive technique"
    
    if layer == "N" and function in ["Re"]:
        return "exposition", "Establishes character/setting through narrative technique"
    
    # Week 4: Voice devices  
    if any(term in name for term in ["irony", "perspective", "narration", "pov", "voice", "focalization", "temporal", "distance", "reliability"]):
        return "voice", "Creates perspective gaps or narrative distance"
    
    # Week 3: Structure devices (Freytag-related: conflict, climax, resolution, pacing)
    if any(term in name for term in ["conflict", "climax", "resolution", "pacing", "scene", "summary", "tension", "suspense"]):
        return "structure", "Builds plot structure and pacing"
    
    # Default to structure for remaining
    return "structure", "Builds plot structure"


def extract_tvode_components(device):
    """Extract or generate TVODE components"""
    
    name = device.get("name", "Unknown Device")
    examples = device.get("examples", [])
    
    # If examples exist, use first one
    if examples and len(examples) > 0:
        example = examples[0]
        return {
            "topic": name,
            "verb": "demonstrates",
            "object": "literary technique",
            "detail": example.get("quote_snippet", example.get("text", "")),
            "effect": example.get("analysis", "creates meaning in text")
        }
    
    # Generic TVODE
    return {
        "topic": name,
        "verb": "functions as",
        "object": "literary device",
        "detail": "throughout the text",
        "effect": "to create meaning and effect"
    }

def categorize_devices(kernel):
    """Group devices by which macro element they execute"""
    
    device_mapping = {
        "devices_general": [],
        "exposition": [],
        "structure": [],
        "voice": []
    }
    
    for device in kernel.get("devices", []):
        category, executes_macro = categorize_device(device)
        
        device_data = {
            "name": device.get("name", ""),
            "layer": device.get("layer", ""),
            "function": device.get("function", ""),
            "definition": device.get("definition", device.get("student_facing_definition", "")),
            "examples": device.get("examples", []),
            "executes_macro": executes_macro,
            "tvode_components": extract_tvode_components(device)
        }
        
        device_mapping[category].append(device_data)
    
    return device_mapping


def create_macro_micro_packages(macro_elements, device_mapping):
    """Create 4-week macro-micro packages"""
    
    return {
    "week1_exposition": {
        "week": 1,
        "macro_element": "Exposition",
        "macro_type": macro_elements["exposition"]["element_type"],
        "macro_description": macro_elements["exposition"]["description"],
        "macro_variables": macro_elements["exposition"]["variables"],
        "teaching_goal": "Understanding how exposition is built through devices",
        "micro_devices": device_mapping["exposition"][:4]
    },
    "week2_devices": {
        "week": 2,
        "macro_element": "Literary Devices",
        "macro_type": "Foundation Concept",
        "macro_description": "What literary devices are and how to identify them",
        "teaching_goal": "Device recognition and identification",
        "micro_devices": device_mapping["devices_general"][:3]
    },
    "week3_structure": {
        "week": 3,
        "macro_element": "Structure",
        
            "macro_type": macro_elements["structure"]["element_type"],
            "macro_description": macro_elements["structure"]["description"],
            "macro_variables": macro_elements["structure"]["variables"],
            "teaching_goal": "Understanding how structure unfolds through devices",
            "micro_devices": device_mapping["structure"][:4]
    },
    "week4_voice": {
        "week": 4,
        "macro_element": "Voice",
        "macro_type": macro_elements["voice"]["element_type"],
        "macro_description": macro_elements["voice"]["description"],
        "macro_variables": macro_elements["voice"]["variables"],
        "teaching_goal": "Understanding how voice operates through devices",
        "micro_devices": device_mapping["voice"][:4]
    }
    }

def run_stage1a(kernel_path):
    """Main Stage 1A processing"""
    
    print("\n" + "="*80)
    print("STAGE 1A: MACRO-MICRO EXTRACTION")
    print("="*80)
    
    # Load kernel
    print(f"\n📖 Loading kernel: {kernel_path}")
    with open(kernel_path, 'r', encoding='utf-8') as f:
        kernel = json.load(f)
    
    title = kernel.get("text_metadata", {}).get("title", "Unknown")
    print(f"  ✓ Loaded: {title}")
    
    # Extract macro elements
    print("\n🔍 Extracting macro elements...")
    macro_elements = extract_macro_elements(kernel)
    print(f"  ✓ Extracted: Exposition, Structure, Voice")
    
    # Categorize devices
    print("\n🏷️  Categorizing devices...")
    device_mapping = categorize_devices(kernel)
    print(f"  ✓ Foundation devices: {len(device_mapping['devices_general'])}")
    print(f"  ✓ Exposition devices: {len(device_mapping['exposition'])}")
    print(f"  ✓ Structure devices: {len(device_mapping['structure'])}")
    print(f"  ✓ Voice devices: {len(device_mapping['voice'])}")
    
    # Create packages
    print("\n📦 Creating macro-micro packages...")
    packages = create_macro_micro_packages(macro_elements, device_mapping)
    print(f"  ✓ Created 4-week packages")
    
    # Assemble output
    output = {
        "metadata": {
            "text_title": title,
            "author": kernel.get("text_metadata", {}).get("author", "Unknown"),
            "extraction_version": "5.0",
            "extraction_date": datetime.now().isoformat(),
            "source_kernel": str(kernel_path)
        },
        "macro_elements": macro_elements,
        "device_mapping": device_mapping,
        "macro_micro_packages": packages
    }
    
    # Save output
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
    output_path = output_dir / f"{safe_title}_stage1a_v5.0.json"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Stage 1A complete!")
    print(f"   Output: {output_path}")
    print(f"   Size: {output_path.stat().st_size:,} bytes")
    
    return output_path

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 run_stage1a.py kernels/Book_kernel_v3.3.json")
        sys.exit(1)
    
    kernel_path = Path(sys.argv[1])
    
    if not kernel_path.exists():
        print(f"❌ Error: Kernel file not found: {kernel_path}")
        sys.exit(1)
    
    output_path = run_stage1a(kernel_path)
    
    print("\n" + "="*80)
    print("NEXT STEP:")
    print("="*80)
    print(f"python3 run_stage1b.py {output_path}")
    print("="*80)

if __name__ == "__main__":
    main()
