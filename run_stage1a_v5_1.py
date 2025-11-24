#!/usr/bin/env python3
"""
STAGE 1A AUTOMATION - Location-Based Device Assignment
Extract macro-micro packages from kernel JSON using narrative chapter ranges

Usage:
    python3 run_stage1a.py kernels/Book_kernel_v3.3.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def parse_chapter_range(range_str):
    """Convert chapter range string to list of chapter numbers
    
    Examples:
        "1-3" -> [1, 2, 3]
        "4-14" -> [4, 5, 6, ..., 14]
        "15" -> [15]
    """
    if not range_str or range_str == "":
        return []
    
    range_str = str(range_str).strip()
    
    if '-' in range_str:
        start, end = range_str.split('-')
        return list(range(int(start), int(end) + 1))
    else:
        return [int(range_str)]


def find_device_chapters(device):
    """Determine which chapters contain this device's examples
    
    Returns:
        set of chapter numbers where device appears
    """
    chapters = set()
    
    for example in device.get("examples", []):
        chapter = example.get("chapter")
        if chapter:
            chapters.add(int(chapter))
    
    return chapters


def get_narrative_chapter_ranges(kernel):
    """Extract chapter ranges for each Freytag section from kernel
    
    Returns:
        dict mapping section names to chapter lists
    """
    extracts = kernel.get("extracts", {})
    
    ranges = {}
    for section_name, section_data in extracts.items():
        chapter_range = section_data.get("chapter_range", "")
        ranges[section_name] = parse_chapter_range(chapter_range)
    
    return ranges


def assign_devices_by_location(kernel):
    """Assign devices to narrative sections based on where they appear
    
    Logic:
        - Device assigned to section if its examples appear in that section's chapters
        - Devices can appear in multiple sections
        - Priority: exposition > rising_action > climax > falling_action > resolution
    
    Returns:
        dict mapping section names to lists of devices
    """
    # Get chapter ranges for each narrative section
    narrative_ranges = get_narrative_chapter_ranges(kernel)
    
    # Initialize output structure
    device_assignment = {
        "exposition": [],
        "rising_action": [],
        "climax": [],
        "falling_action": [],
        "resolution": []
    }
    
    # Process each device
    for device in kernel.get("micro_devices", []):
        device_chapters = find_device_chapters(device)
        
        if not device_chapters:
            # No chapter info - skip this device
            continue
        
        # Find which sections contain this device
        assigned = False
        for section_name, section_chapters in narrative_ranges.items():
            if not section_chapters:
                continue
            
            # Check if device appears in this section's chapters
            if any(ch in section_chapters for ch in device_chapters):
                device_data = {
                    "name": device.get("name", ""),
                    "layer": device.get("layer", ""),
                    "function": device.get("function", ""),
                    "definition": device.get("definition", device.get("student_facing_definition", "")),
                    "examples": device.get("examples", []),
                    "appears_in_chapters": sorted(list(device_chapters)),
                    "section_chapters": section_chapters
                }
                
                device_assignment[section_name].append(device_data)
                assigned = True
                break  # Assign to first matching section only
        
        if not assigned:
            # Device doesn't fit any section - could log this
            pass
    
    return device_assignment


def extract_tvode_components(device):
    """Extract or generate TVODE components from device data"""
    
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


def extract_macro_elements(kernel):
    """Extract macro alignment elements from kernel"""
    
    # Fixed: kernel v3.3 uses "macro_variables" not "narrative"
    macro_vars = kernel.get("macro_variables", {})
    narrative = macro_vars.get("narrative", {})
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


def create_macro_micro_packages(kernel, macro_elements, device_assignment):
    """Create 5-week macro-micro packages with chapter ranges
    
    Week 1: Exposition devices from exposition chapters
    Week 2: Rising Action/Literary Devices from rising action chapters  
    Week 3: Structure/Climax from climax chapters
    Week 4: Voice/Falling Action from falling action chapters
    Week 5: Resolution from resolution chapters
    """
    
    # Get narrative ranges for chapter metadata
    narrative_ranges = get_narrative_chapter_ranges(kernel)
    extracts = kernel.get("extracts", {})
    
    # Helper function to get primary_chapter with fallback
    def get_primary_chapter(section_name):
        section_data = extracts.get(section_name, {})
        # Try primary_chapter field first
        if "primary_chapter" in section_data:
            return section_data["primary_chapter"]
        # Fallback: use first chapter in range
        chapter_range = section_data.get("chapter_range", "")
        if chapter_range:
            chapters = parse_chapter_range(chapter_range)
            return chapters[0] if chapters else 1
        return 1
    
    # Add TVODE components to each device
    for section_devices in device_assignment.values():
        for device in section_devices:
            device["tvode_components"] = extract_tvode_components(device)
    
    return {
        "week1_exposition": {
            "week": 1,
            "macro_element": "Exposition",
            "macro_type": macro_elements["exposition"]["element_type"],
            "macro_description": macro_elements["exposition"]["description"],
            "macro_variables": macro_elements["exposition"]["variables"],
            "teaching_goal": "Understanding how exposition is built through devices",
            "activity_chapter": get_primary_chapter("exposition"),
            "reading_range": extracts.get("exposition", {}).get("chapter_range", ""),
            "chapter_range": narrative_ranges.get("exposition", []),
            "chapter_range_str": extracts.get("exposition", {}).get("chapter_range", ""),
            "micro_devices": device_assignment["exposition"][:4]
        },
        "week2_rising_action": {
            "week": 2,
            "macro_element": "Rising Action",
            "macro_type": "Narrative Development",
            "macro_description": "How conflict and tension develop through literary devices",
            "teaching_goal": "Understanding rising action and device recognition",
            "activity_chapter": get_primary_chapter("rising_action"),
            "reading_range": extracts.get("rising_action", {}).get("chapter_range", ""),
            "chapter_range": narrative_ranges.get("rising_action", []),
            "chapter_range_str": extracts.get("rising_action", {}).get("chapter_range", ""),
            "micro_devices": device_assignment["rising_action"][:4]
        },
        "week3_climax": {
            "week": 3,
            "macro_element": "Structure/Climax",
            "macro_type": macro_elements["structure"]["element_type"],
            "macro_description": macro_elements["structure"]["description"],
            "macro_variables": macro_elements["structure"]["variables"],
            "teaching_goal": "Understanding how structure and climax work through devices",
            "activity_chapter": get_primary_chapter("climax"),
            "reading_range": extracts.get("climax", {}).get("chapter_range", ""),
            "chapter_range": narrative_ranges.get("climax", []),
            "chapter_range_str": extracts.get("climax", {}).get("chapter_range", ""),
            "micro_devices": device_assignment["climax"][:4]
        },
        "week4_falling_action": {
            "week": 4,
            "macro_element": "Voice/Falling Action",
            "macro_type": macro_elements["voice"]["element_type"],
            "macro_description": macro_elements["voice"]["description"],
            "macro_variables": macro_elements["voice"]["variables"],
            "teaching_goal": "Understanding how narrative voice operates through devices",
            "activity_chapter": get_primary_chapter("falling_action"),
            "reading_range": extracts.get("falling_action", {}).get("chapter_range", ""),
            "chapter_range": narrative_ranges.get("falling_action", []),
            "chapter_range_str": extracts.get("falling_action", {}).get("chapter_range", ""),
            "micro_devices": device_assignment["falling_action"][:4]
        },
        "week5_resolution": {
            "week": 5,
            "macro_element": "Resolution",
            "macro_type": "Narrative Conclusion",
            "macro_description": "How conflicts resolve and themes culminate",
            "teaching_goal": "Understanding resolution and synthesizing all concepts",
            "activity_chapter": get_primary_chapter("resolution"),
            "reading_range": extracts.get("resolution", {}).get("chapter_range", ""),
            "chapter_range": narrative_ranges.get("resolution", []),
            "chapter_range_str": extracts.get("resolution", {}).get("chapter_range", ""),
            "micro_devices": device_assignment["resolution"][:4]
        }
    }


def run_stage1a(kernel_path):
    """Main Stage 1A processing"""
    
    print("\n" + "="*80)
    print("STAGE 1A: MACRO-MICRO EXTRACTION (Location-Based)")
    print("="*80)
    
    # Load kernel
    print(f"\nðŸ“– Loading kernel: {kernel_path}")
    with open(kernel_path, 'r', encoding='utf-8') as f:
        kernel = json.load(f)
    
    # Fixed: kernel v3.3 uses "metadata" not "text_metadata"
    title = kernel.get("metadata", {}).get("title", "Unknown")
    print(f"  âœ“ Loaded: {title}")
    
    # Extract narrative chapter ranges
    print("\nðŸ“ Extracting chapter ranges...")
    narrative_ranges = get_narrative_chapter_ranges(kernel)
    for section, chapters in narrative_ranges.items():
        if chapters:
            print(f"  âœ“ {section}: Chapters {min(chapters)}-{max(chapters)}")
    
    # Extract macro elements
    print("\nðŸ” Extracting macro elements...")
    macro_elements = extract_macro_elements(kernel)
    print(f"  âœ“ Extracted: Exposition, Structure, Voice")
    
    # Assign devices by location
    print("\nðŸ—ºï¸  Assigning devices by narrative location...")
    device_assignment = assign_devices_by_location(kernel)
    print(f"  âœ“ Exposition devices: {len(device_assignment['exposition'])}")
    print(f"  âœ“ Rising action devices: {len(device_assignment['rising_action'])}")
    print(f"  âœ“ Climax devices: {len(device_assignment['climax'])}")
    print(f"  âœ“ Falling action devices: {len(device_assignment['falling_action'])}")
    print(f"  âœ“ Resolution devices: {len(device_assignment['resolution'])}")
    
    # Create packages
    print("\nðŸ“¦ Creating macro-micro packages...")
    packages = create_macro_micro_packages(kernel, macro_elements, device_assignment)
    print(f"  âœ“ Created 4-week packages with chapter ranges")
    
    # Assemble output
    output = {
        "metadata": {
            "text_title": title,
            "author": kernel.get("metadata", {}).get("author", "Unknown"),
            "extraction_version": "5.0",
            "extraction_date": datetime.now().isoformat(),
            "source_kernel": str(kernel_path)
        },
        "narrative_chapter_ranges": narrative_ranges,
        "macro_elements": macro_elements,
        "device_assignment_by_location": device_assignment,
        "macro_micro_packages": packages
    }
    
    # Save output
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
    output_path = output_dir / f"{safe_title}_stage1a_v5.0.json"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nâœ… Stage 1A complete!")
    print(f"   Output: {output_path}")
    print(f"   Size: {output_path.stat().st_size:,} bytes")
    
    return output_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 run_stage1a.py kernels/Book_kernel_v3.3.json")
        sys.exit(1)
    
    kernel_path = Path(sys.argv[1])
    
    if not kernel_path.exists():
        print(f"âŒ Error: Kernel file not found: {kernel_path}")
        sys.exit(1)
    
    output_path = run_stage1a(kernel_path)
    
    print("\n" + "="*80)
    print("NEXT STEP:")
    print("="*80)
    print(f"python3 run_stage1b.py {output_path}")
    print("="*80)


if __name__ == "__main__":
    main()
