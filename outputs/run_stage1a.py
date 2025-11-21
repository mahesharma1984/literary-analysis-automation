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

# Load device mapping
with open('device_taxonomy_mapping.json', 'r') as f:
    DEVICE_MAPPING = json.load(f)

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
        "literary_devices": {
            "element_type": "Literary Devices",
            "description": "Foundational figurative language and descriptive devices",
            "variables": {}
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
        "narrative_voice": {
            "element_type": "Narrative Voice",
            "description": "Point of view, focalization, and character consciousness",
            "variables": {
                "pov": voice.get("pov", ""),
                "focalization": voice.get("focalization", ""),
                "reliability": voice.get("reliability", ""),
                "temporal_distance": voice.get("temporal_distance", "")
            }
        },
        "rhetorical_voice": {
            "element_type": "Rhetorical Voice",
            "description": "Irony, persuasion, and interpretive control",
            "variables": {}
        }
    }


def fallback_categorization(device_name: str, classification: str) -> str:
    """Fallback heuristic categorization if device not in mapping"""
    
    name_lower = device_name.lower()
    
    # Week 1: Exposition keywords
    if any(kw in name_lower for kw in ['character', 'dialogue', 'scene', 'exposition', 'setting']):
        return 'week_1_exposition'
    
    # Week 2: Literary devices keywords
    if any(kw in name_lower for kw in ['metaphor', 'simile', 'imagery', 'symbol', 'personification', 'alliteration', 'figurative']):
        return 'week_2_literary_devices'
    
    # Week 3: Structure keywords
    if any(kw in name_lower for kw in ['structure', 'foreshadow', 'climax', 'motif', 'flashback', 'conflict', 'resolution', 'pacing']):
        return 'week_3_structure'
    
    # Week 4: Narrative voice keywords
    if any(kw in name_lower for kw in ['person', 'narrator', 'perspective', 'voice', 'monologue', 'consciousness', 'pov']):
        return 'week_4_narrative_voice'
    
    # Week 5: Rhetorical voice keywords
    if any(kw in name_lower for kw in ['irony', 'euphemism', 'understatement', 'juxtaposition', 'rhetorical', 'tone', 'diction', 'sarcasm']):
        return 'week_5_rhetorical_voice'
    
    # Default to week 2 if no match
    return 'week_2_literary_devices'


def categorize_device(device_name: str, classification: str) -> tuple:
    """Categorize device using mapping file, returns (week_key, week_label)"""
    
    # Check explicit mapping
    for week_key, devices in DEVICE_MAPPING['device_mappings'].items():
        for mapped_device in devices:
            if mapped_device['device_name'] == device_name:
                week_label = DEVICE_MAPPING['week_definitions'][week_key]['label']
                return week_key, week_label
    
    # Fallback to heuristics if needed
    week_key = fallback_categorization(device_name, classification)
    week_label = DEVICE_MAPPING['week_definitions'][week_key]['label']
    return week_key, week_label


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
    """Group devices by pedagogical week"""
    
    device_mapping = {
        'week_1_exposition': [],
        'week_2_literary_devices': [],
        'week_3_structure': [],
        'week_4_narrative_voice': [],
        'week_5_rhetorical_voice': []
    }
    
    # Check both 'devices' and 'micro_devices' for compatibility with different kernel versions
    devices_list = kernel.get("devices", kernel.get("micro_devices", []))
    
    for device in devices_list:
        week_key, week_label = categorize_device(
            device['name'], 
            device.get('classification', '')
        )
        
        device_data = {
            "name": device.get("name", ""),
            "layer": device.get("layer", ""),
            "function": device.get("function", ""),
            "definition": device.get("definition", device.get("student_facing_definition", "")),
            "examples": device.get("examples", []),
            "week_label": week_label,
            "tvode_components": extract_tvode_components(device)
        }
        
        device_mapping[week_key].append(device_data)
    
    return device_mapping


def create_macro_micro_packages(macro_elements, device_mapping):
    """Create 5-week macro-micro packages"""
    
    return {
        "week1_exposition": {
            "week": 1,
            "macro_element": "Exposition",
            "macro_type": macro_elements["exposition"]["element_type"],
            "macro_description": macro_elements["exposition"]["description"],
            "macro_variables": macro_elements["exposition"]["variables"],
            "teaching_goal": "Understanding how exposition is built through devices",
            "scaffolding": "High - Teacher models everything",
            "micro_devices": device_mapping["week_1_exposition"]
        },
        "week2_literary_devices": {
            "week": 2,
            "macro_element": "Literary Devices",
            "macro_type": macro_elements["literary_devices"]["element_type"],
            "macro_description": macro_elements["literary_devices"]["description"],
            "macro_variables": macro_elements["literary_devices"]["variables"],
            "teaching_goal": "Device recognition and identification",
            "scaffolding": "Medium-High - Co-construction with students",
            "micro_devices": device_mapping["week_2_literary_devices"]
        },
        "week3_structure": {
            "week": 3,
            "macro_element": "Structure",
            "macro_type": macro_elements["structure"]["element_type"],
            "macro_description": macro_elements["structure"]["description"],
            "macro_variables": macro_elements["structure"]["variables"],
            "teaching_goal": "Understanding how structure unfolds through devices",
            "scaffolding": "Medium - Students lead with support",
            "micro_devices": device_mapping["week_3_structure"]
        },
        "week4_narrative_voice": {
            "week": 4,
            "macro_element": "Narrative Voice",
            "macro_type": macro_elements["narrative_voice"]["element_type"],
            "macro_description": macro_elements["narrative_voice"]["description"],
            "macro_variables": macro_elements["narrative_voice"]["variables"],
            "teaching_goal": "Understanding perspective and consciousness",
            "scaffolding": "Medium-Low - Independent work with feedback",
            "micro_devices": device_mapping["week_4_narrative_voice"]
        },
        "week5_rhetorical_voice": {
            "week": 5,
            "macro_element": "Rhetorical Voice",
            "macro_type": macro_elements["rhetorical_voice"]["element_type"],
            "macro_description": macro_elements["rhetorical_voice"]["description"],
            "macro_variables": macro_elements["rhetorical_voice"]["variables"],
            "teaching_goal": "Understanding irony and persuasive techniques",
            "scaffolding": "Low - Independent application",
            "micro_devices": device_mapping["week_5_rhetorical_voice"]
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
    
    title = kernel.get("metadata", {}).get("title", "Unknown")
    print(f"  ✓ Loaded: {title}")
    
    # Extract macro elements
    print("\n🔍 Extracting macro elements...")
    macro_elements = extract_macro_elements(kernel)
    print(f"  ✓ Extracted: Exposition, Literary Devices, Structure, Narrative Voice, Rhetorical Voice")
    
    # Categorize devices
    print("\n🏷️  Categorizing devices...")
    device_mapping = categorize_devices(kernel)
    print(f"  ✓ Week 1 (Exposition): {len(device_mapping['week_1_exposition'])}")
    print(f"  ✓ Week 2 (Literary Devices): {len(device_mapping['week_2_literary_devices'])}")
    print(f"  ✓ Week 3 (Structure): {len(device_mapping['week_3_structure'])}")
    print(f"  ✓ Week 4 (Narrative Voice): {len(device_mapping['week_4_narrative_voice'])}")
    print(f"  ✓ Week 5 (Rhetorical Voice): {len(device_mapping['week_5_rhetorical_voice'])}")
    
    # Create packages
    print("\n📦 Creating macro-micro packages...")
    packages = create_macro_micro_packages(macro_elements, device_mapping)
    print(f"  ✓ Created 5-week packages")
    
    # Assemble output
    output = {
        "metadata": {
            "text_title": title,
            "author": kernel.get("metadata", {}).get("author", "Unknown"),
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
