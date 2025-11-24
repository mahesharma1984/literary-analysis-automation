#!/usr/bin/env python3
"""
STAGE 1B AUTOMATION
Package macro-micro extracts into 5-week teaching progression

Usage:
    python3 run_stage1b.py outputs/Book_stage1a_v5.0.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def create_week_package(week_data, week_num):
    """Create detailed week package with pedagogical scaffolding"""
    
    scaffolding_levels = {
        1: "High - Teacher models everything",
        2: "Medium-High - Co-construction with students",
        3: "Medium - Students lead with support",
        4: "Medium-Low - Independent work with feedback",
        5: "Low - Independent synthesis and analysis"
    }
    
    teaching_sequences = {
        1: [
            "Introduce concept of literary devices as author's tools",
            "Define exposition and its components",
            "Practice identifying exposition devices in text together",
            "Explain what each device accomplishes",
            "Begin simple TVODE construction"
        ],
        2: [
            "Review Week 1 exposition devices",
            "Introduce macro concept: Literary Devices Foundation",
            "Show how devices BUILD meaning through figurative language",
            "Analyze device-macro connection in text",
            "Practice macro-micro TVODE construction"
        ],
        3: [
            "Review exposition and rising action concepts",
            "Introduce macro concept: Structure and Climax",
            "Analyze how devices create plot structure and turning points",
            "Trace structural patterns across chapters",
            "Build complex structural TVODE"
        ],
        4: [
            "Review structural concepts from Week 3",
            "Introduce macro concept: Voice and Falling Action",
            "Analyze perspective and distance through devices",
            "Compare macro-micro relationships across weeks",
            "Create voice-focused analysis TVODE"
        ],
        5: [
            "Synthesize all previous concepts (Exposition, Rising Action, Structure, Voice)",
            "Introduce macro concept: Resolution",
            "Analyze how all devices work together to create resolution",
            "Demonstrate understanding of complete narrative arc",
            "Create independent comprehensive analysis TVODE"
        ]
    }
    
    package = {
        "week": week_num,
        "text_title": week_data.get("text_title", ""),
        "text_author": week_data.get("text_author", ""),
        "macro_focus": week_data.get("macro_element", ""),
        "macro_type": week_data.get("macro_type", ""),
        "macro_description": week_data.get("macro_description", ""),
        "teaching_goal": week_data.get("teaching_goal", ""),
        "scaffolding_level": scaffolding_levels.get(week_num, "Medium"),
        "teaching_sequence": teaching_sequences.get(week_num, []),
        "activity_chapter": week_data.get("activity_chapter"),
        "reading_range": week_data.get("reading_range"),  
        "micro_devices": []
    }
    
    # Add macro variables if present
    if "macro_variables" in week_data:
        package["macro_variables"] = week_data["macro_variables"]
    
    # Process devices with teaching notes
    for device in week_data.get("micro_devices", []):
        device_package = {
            "device_name": device.get("name", ""),
            "name": device.get("name", ""),
            "layer": device.get("layer", ""),
            "function": device.get("function", ""),
            "definition": device.get("definition", ""),
            "executes_macro": device.get("executes_macro", ""),
            "tvode_components": device.get("tvode_components", {}),
            "examples": device.get("examples", []),
            "teaching_notes": {
                "introduce_as": device.get("executes_macro", ""),
                "macro_connection": f"This device is one way {package['macro_focus']} works",
                "student_task": f"Find and analyze this device in the text",
                "common_confusion": "Watch for surface-level readings",
                "teaching_tip": "Start with clear examples before complex analysis"
            }
        }
        
        package["micro_devices"].append(device_package)
    
    return package

def create_progression_summary(week_packages):
    """Create progression summary document"""
    
    return {
        "total_weeks": 5,
        "pedagogical_approach": "Macro-through-micro instruction with scaffolding withdrawal",
        "progression": [
            {
                "week": 1,
                "focus": "Exposition - How characters/setting are introduced",
                "skill": "Connecting devices to macro exposition concept"
            },
            {
                "week": 2,
                "focus": "Literary Devices Foundation - What are literary devices?",
                "skill": "Device recognition and identification"
            },
            {
                "week": 3,
                "focus": "Structure - How plot is organized",
                "skill": "Analyzing structural function of devices"
            },
            {
                "week": 4,
                "focus": "Voice - Narrative perspective",
                "skill": "Synthesizing macro-micro relationships"
            },
            {
                "week": 5,
                "focus": "Resolution - How conflicts resolve and themes culminate",
                "skill": "Comprehensive synthesis of all concepts"
            }
        ],
        "scaffolding_withdrawal": {
            "week1": "High - Teacher-led modeling",
            "week2": "Medium-High - Guided practice",
            "week3": "Medium - Supported independence",
            "week4": "Medium-Low - Independent analysis",
            "week5": "Low - Independent synthesis and analysis"
        }
    }

def generate_progression_document(title, author, week_packages):
    """Generate human-readable progression document"""
    
    doc = f"""# {title.upper()} INTEGRATED MACRO-MICRO PROGRESSION
## 5-Week Literary Analysis Curriculum

**Text:** {title} by {author}  
**Version:** 5.1 (Chapter-Aware)  
**Date:** {datetime.now().strftime('%B %d, %Y')}  
**Structure:** Macro alignment elements taught through executing micro devices

---

## CURRICULUM OVERVIEW

### Pedagogical Approach

This curriculum teaches **macro alignment elements** (Exposition, Structure, Voice) through the **micro devices** that execute them, rather than teaching devices in isolation.

**Core Principle:** Literary concepts like "exposition" are not abstract ideasâ€”they manifest through specific devices working together. Students learn to see how macro elements OPERATE through micro techniques.

### 5-Week Progression

| Week | Macro Focus | Teaching Approach | Devices | Scaffolding |
|------|-------------|-------------------|---------|-------------|
"""
    
    for pkg in week_packages:
        devices_str = ", ".join([d['name'] for d in pkg['micro_devices'][:3]])
        if len(pkg['micro_devices']) > 3:
            devices_str += f", +{len(pkg['micro_devices'])-3} more"
        
        doc += f"| {pkg['week']} | {pkg['macro_focus']} | {pkg['teaching_approach'] if 'teaching_approach' in pkg else 'See below'} | {devices_str} | {pkg['scaffolding_level']} |\n"
    
    doc += "\n---\n\n"
    
    # Week details
    for pkg in week_packages:
        week_num = pkg['week']
        macro_focus = pkg['macro_focus']
        
        doc += f"## WEEK {week_num}: {macro_focus.upper()}\n\n"
        
        if week_num == 1:
            doc += f"**Macro Concept:** {pkg['macro_description']}\n"
        else:
            doc += f"**Macro Element:** {pkg['macro_description']}\n"
        
        doc += f"**Teaching Goal:** {pkg['teaching_goal']}\n"
        doc += f"**Scaffolding:** {pkg['scaffolding_level']}\n\n"
        
        # Teaching sequence
        doc += "**Teaching Sequence:**\n"
        for i, step in enumerate(pkg['teaching_sequence'], 1):
            doc += f"{i}. {step}\n"
        doc += "\n"
        
        # Devices
        doc += f"**Devices ({len(pkg['micro_devices'])}):**\n"
        for device in pkg['micro_devices']:
            doc += f"- **{device['name']}**: {device['executes_macro']}\n"
        doc += "\n"
        
        # Macro variables if present
        if 'macro_variables' in pkg and pkg['macro_variables']:
            doc += "**Macro Variables:**\n"
            for var, value in pkg['macro_variables'].items():
                doc += f"- {var}: {value}\n"
            doc += "\n"
        
        doc += "---\n\n"
    
    # Progression summary
    doc += "## PROGRESSION SUMMARY\n\n"
    
    doc += "### Scaffolding Withdrawal\n"
    for pkg in week_packages:
        doc += f"- **Week {pkg['week']}:** {pkg['scaffolding_level']}\n"
    doc += "\n"
    
    doc += "### Skill Building\n"
    skills = [
        "1. Exposition and macro-micro connection (Week 1)",
        "2. Device recognition and identification (Week 2)",
        "3. Structural analysis (Week 3)",
        "4. Voice and perspective (Week 4)",
        "5. Comprehensive synthesis (Week 5)"
    ]
    doc += " â†’ ".join(skills) + "\n\n"
    
    doc += "### TVODE Evolution\n"
    tvode_progression = [
        "Week 1: Exposition-focused TVODE",
        "Week 2: Device recognition and macro-micro connection TVODE",
        "Week 3: Structural function TVODE",
        "Week 4: Complex voice TVODE",
        "Week 5: Comprehensive synthesis TVODE"
    ]
    for item in tvode_progression:
        doc += f"- {item}\n"
    
    doc += "\n---\n\n**END OF INTEGRATED MACRO-MICRO PROGRESSION**\n"
    
    return doc

def run_stage1b(stage1a_path):
    """Main Stage 1B processing"""
    
    print("\n" + "="*80)
    print("STAGE 1B: WEEKLY PACKAGING")
    print("="*80)
    
    # Load Stage 1A output
    print(f"\nðŸ“– Loading Stage 1A output: {stage1a_path}")
    with open(stage1a_path, 'r', encoding='utf-8') as f:
        stage1a = json.load(f)
    
    title = stage1a.get("metadata", {}).get("text_title", "Unknown")
    author = stage1a.get("metadata", {}).get("author", "Unknown")
    print(f"  âœ“ Loaded: {title} by {author}")
    
    # Get packages
    packages = stage1a.get("macro_micro_packages", {})
    
    # Create week packages
    print("\nðŸ“¦ Creating weekly packages...")
    week_packages = []
    
    for week_num in range(1, 6):
        week_key = [k for k in packages.keys() if f"week{week_num}" in k][0]
        week_data = packages[week_key]
        week_data["text_title"] = title
        week_data["text_author"] = author
        
        # Add teaching approach
        teaching_approaches = {
        1: "How do devices establish characters and setting in exposition?",
        2: "How do devices build tension in rising action?",
        3: "How do devices create the story's climactic turning point?",
        4: "How do devices manage perspective in falling action?",
        5: "How do devices bring rhetorical closure in resolution?"
    }
        week_data["teaching_approach"] = teaching_approaches.get(week_num, "")
        
        package = create_week_package(week_data, week_num)
        package["teaching_approach"] = teaching_approaches.get(week_num, "")
        week_packages.append(package)
        
        device_count = len(package["micro_devices"])
        print(f"  âœ“ Week {week_num}: {package['macro_focus']} ({device_count} devices)")
    
    # Create progression summary
    print("\nðŸ“‹ Creating progression summary...")
    progression = create_progression_summary(week_packages)
    print(f"  âœ“ Summary created")
    
    # Generate progression document
    print("\nðŸ“„ Generating progression document...")
    progression_doc = generate_progression_document(title, author, week_packages)
    print(f"  âœ“ Document generated")
    
    # Assemble output
    output = {
        "metadata": {
            "text_title": title,
            "author": author,
            "package_version": "5.1",
            "package_date": datetime.now().isoformat(),
            "structure_type": "macro-micro week packages with pedagogical scaffolding",
            "total_weeks": 5,
            "source_file": str(stage1a_path)
        },
        "progression_summary": progression,
        "week_packages": week_packages
    }
    
    # Save outputs
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
    
    # Save JSON
    output_path = output_dir / f"{safe_title}_stage1b_v5.1.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nâœ… Stage 1B JSON saved!")
    print(f"   Output: {output_path}")
    print(f"   Size: {output_path.stat().st_size:,} bytes")
    
    # Save progression document
    progression_path = output_dir / f"{safe_title}_Integrated_Progression.md"
    with open(progression_path, 'w', encoding='utf-8') as f:
        f.write(progression_doc)
    
    print(f"\nâœ… Progression document saved!")
    print(f"   Output: {progression_path}")
    print(f"   Size: {progression_path.stat().st_size:,} bytes")
    
    # Print summary
    print("\n" + "="*80)
    print("WEEK SUMMARY")
    print("="*80)
    for pkg in week_packages:
        print(f"Week {pkg['week']}: {pkg['macro_focus']} - {len(pkg['micro_devices'])} devices")
    
    print("\n" + "="*80)
    print("ðŸ“‹ REVIEW PROGRESSION DOCUMENT BEFORE GENERATING WORKSHEETS")
    print("="*80)
    print(f"Open: {progression_path}")
    print("Verify the week structure makes sense before running Stage 2")
    
    return output_path

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 run_stage1b.py outputs/Book_stage1a_v5.0.json")
        sys.exit(1)
    
    stage1a_path = Path(sys.argv[1])
    
    if not stage1a_path.exists():
        print(f"âŒ Error: Stage 1A file not found: {stage1a_path}")
        sys.exit(1)
    
    output_path = run_stage1b(stage1a_path)
    
    print("\n" + "="*80)
    print("NEXT STEP:")
    print("="*80)
    print(f"python3 run_stage2.py {output_path}")
    print("="*80)

if __name__ == "__main__":
    main()
