#!/usr/bin/env python3
"""
STAGE 2 AUTOMATION - FIXED VERSION
Generate worksheets using template system with proper placeholder replacement

Usage:
    python3 run_stage2_fixed.py Book_stage1b.json Book_kernel.json --week 1
    python3 run_stage2_fixed.py Book_stage1b.json Book_kernel.json --all-weeks
"""

import anthropic
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Configuration
class Config:
    API_KEY = os.getenv("ANTHROPIC_API_KEY")
    MODEL = "claude-sonnet-4-20250514"
    MAX_TOKENS = 4000

def load_template(template_name):
    """Load template file"""
    template_paths = [
        Path("protocols") / template_name,
        Path("templates") / template_name,
        Path(".") / template_name
    ]
    
    for template_path in template_paths:
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
    
    raise FileNotFoundError(f"Template not found: {template_name}")

def get_device_examples(device_name, kernel_data):
    """Extract examples for a specific device from kernel"""
    examples = []
    
    for device in kernel_data.get('devices', []):
        if device['name'] == device_name:
            for ex in device.get('examples', []):
                examples.append({
                    'location': f"Chapter {ex.get('chapter', '?')}, page {ex.get('page_range', '?')}",
                    'quote': ex.get('quote_snippet', ''),
                    'scene': ex.get('scene', '')
                })
            break
    
    return examples

def generate_multiple_choice_options(device, kernel_data, client):
    """Generate 4 multiple choice options for device function"""
    
    device_name = device['device_name']
    definition = device['definition']
    examples = get_device_examples(device_name, kernel_data)
    
    examples_text = "\n".join([
        f"- {ex['scene']}: \"{ex['quote'][:100]}...\""
        for ex in examples[:2]
    ]) if examples else "No specific examples available"
    
    prompt = f"""Generate 4 multiple choice options for this question:
"What does {device_name} DO in this text? What is its purpose or function?"

DEVICE: {device_name}
DEFINITION: {definition}
EXAMPLES FROM TEXT:
{examples_text}

Requirements:
- Each option should describe WHAT the device does (its function), not WHY it's effective
- All 4 options should be plausible and similar in length (one clause only)
- 2 options should be "quite possible" - the correct answer and one close alternative
- Options should be specific to this text, not generic
- Format as single clauses without complex sentences
- Do NOT use bullet points or letters - just list 4 options, one per line

Example format:
Shows how characters develop relationships through dialogue
Reveals the protagonist's internal conflict about society
Creates atmosphere of mystery and suspense
Establishes the setting as dystopian and controlled

OUTPUT: Exactly 4 options, one per line."""

    response = client.messages.create(
        model=Config.MODEL,
        max_tokens=Config.MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}]
    )
    
    options = response.content[0].text.strip().split('\n')
    # Clean up options
    options = [opt.strip() for opt in options if opt.strip()]
    
    # Ensure we have exactly 4
    while len(options) < 4:
        options.append("Additional context or meaning for the text")
    options = options[:4]
    
    return {
        'A': options[0],
        'B': options[1],
        'C': options[2],
        'D': options[3]
    }

def generate_sequencing_activity(device, kernel_data, client):
    """Generate 3-step sequencing activity"""
    
    device_name = device['device_name']
    definition = device['definition']
    examples = get_device_examples(device_name, kernel_data)
    
    examples_text = "\n".join([
        f"- {ex['scene']}: \"{ex['quote'][:100]}...\""
        for ex in examples[:2]
    ]) if examples else "No specific examples available"
    
    prompt = f"""Generate a 3-step sequence showing HOW {device_name} is used in the text.

DEVICE: {device_name}
DEFINITION: {definition}
EXAMPLES:
{examples_text}

Requirements:
- 3 steps that show the progression/process of how the device works
- Each step should be a short phrase or clause
- Steps should be in chronological or logical order
- Focus on HOW the device operates in THIS text
- Do NOT include letters/numbers - just list 3 steps, one per line

Example format:
Author introduces the symbol in an everyday context
Symbol is repeated in increasingly significant moments
Symbol's meaning becomes clear through accumulation

OUTPUT: Exactly 3 steps in correct order, one per line."""

    response = client.messages.create(
        model=Config.MODEL,
        max_tokens=Config.MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}]
    )
    
    steps = response.content[0].text.strip().split('\n')
    steps = [s.strip() for s in steps if s.strip()]
    
    # Ensure exactly 3 steps
    while len(steps) < 3:
        steps.append("The device creates additional layers of meaning")
    steps = steps[:3]
    
    # Randomize for worksheet (students will reorder)
    import random
    randomized = steps.copy()
    random.shuffle(randomized)
    
    return {
        'sequence_correct': steps,  # For answer key
        'sequence_randomized': {
            'A': randomized[0],
            'B': randomized[1],
            'C': randomized[2]
        }
    }

def generate_effect_categorization(device, kernel_data, macro_focus, client):
    """Generate 6 effects for categorization activity"""
    
    device_name = device['device_name']
    definition = device['definition']
    
    prompt = f"""Generate 6 specific effects for this literary device, categorized into 3 types:

DEVICE: {device_name}
DEFINITION: {definition}
MACRO FOCUS: {macro_focus}

Generate EXACTLY 2 effects for each category:

**Reader Response** (2 effects): How the device affects what readers feel or experience
**Meaning Creation** (2 effects): How the device builds understanding or reveals ideas  
**Thematic Impact** (2 effects): How the device connects to the text's bigger message or theme

Requirements:
- Each effect should be specific to THIS device and THIS text
- Effects should be complete phrases (not single words)
- Similar length across all effects
- Do NOT label which category each belongs to - just list 6 effects numbered 1-6
- Mix the categories (don't group them)

Example format:
1. Creates emotional connection between reader and protagonist
2. Reveals the hidden corruption beneath surface appearances
3. Emphasizes the theme of individual versus society
4. Builds tension as readers anticipate consequences
5. Highlights the moral complexity of the central conflict
6. Makes readers question their own assumptions about normalcy

OUTPUT: Exactly 6 numbered effects, mixed categories."""

    response = client.messages.create(
        model=Config.MODEL,
        max_tokens=Config.MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}]
    )
    
    effects_text = response.content[0].text.strip()
    
    # Parse numbered effects
    effects = []
    for line in effects_text.split('\n'):
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith('-')):
            # Remove numbering
            effect = line.split('.', 1)[-1].strip()
            if effect:
                effects.append(effect)
    
    # Ensure exactly 6
    while len(effects) < 6:
        effects.append("Contributes to the overall meaning of the text")
    effects = effects[:6]
    
    return effects

def fill_device_section(worksheet, device, device_num, kernel_data, macro_focus, client):
    """Fill in all activities for one device section"""
    
    device_name = device['device_name']
    definition = device['definition']
    
    # Get examples
    examples = get_device_examples(device_name, kernel_data)
    example_location = examples[0]['location'] if examples else "Chapter ?, pages ?"
    
    # Generate activities
    print(f"    Generating multiple choice...")
    mc_options = generate_multiple_choice_options(device, kernel_data, client)
    
    print(f"    Generating sequencing...")
    sequencing = generate_sequencing_activity(device, kernel_data, client)
    
    print(f"    Generating effects...")
    effects = generate_effect_categorization(device, kernel_data, macro_focus, client)
    
    # Replace placeholders
    replacements = {
        f'[DEVICE_{device_num}_NAME]': device_name,
        f'[DEVICE_{device_num}_DEFINITION]': definition,
        f'[DEVICE_{device_num}_EXAMPLE_LOCATION]': example_location,
        f'[DEVICE_{device_num}_MC_A]': mc_options['A'],
        f'[DEVICE_{device_num}_MC_B]': mc_options['B'],
        f'[DEVICE_{device_num}_MC_C]': mc_options['C'],
        f'[DEVICE_{device_num}_MC_D]': mc_options['D'],
        f'[DEVICE_{device_num}_SEQ_A]': sequencing['sequence_randomized']['A'],
        f'[DEVICE_{device_num}_SEQ_B]': sequencing['sequence_randomized']['B'],
        f'[DEVICE_{device_num}_SEQ_C]': sequencing['sequence_randomized']['C'],
        f'[DEVICE_{device_num}_EFFECT_1]': effects[0],
        f'[DEVICE_{device_num}_EFFECT_2]': effects[1],
        f'[DEVICE_{device_num}_EFFECT_3]': effects[2],
        f'[DEVICE_{device_num}_EFFECT_4]': effects[3],
        f'[DEVICE_{device_num}_EFFECT_5]': effects[4],
        f'[DEVICE_{device_num}_EFFECT_6]': effects[5],
    }
    
    for placeholder, value in replacements.items():
        worksheet = worksheet.replace(placeholder, value)
    
    return worksheet

def generate_worksheet(week_package, kernel_data, client):
    """Generate complete worksheet using templates"""
    
    week_num = week_package["week"]
    macro_focus = week_package["macro_focus"]
    devices = week_package["micro_devices"]
    
    print(f"\n📝 Generating Week {week_num} worksheet...")
    print(f"  Macro focus: {macro_focus}")
    
    # Load template
    try:
        template = load_template("Template_Literary_Analysis_6Step.md")
    except FileNotFoundError:
        print("  ⚠ Template not found, generating basic worksheet...")
        template = f"""# Week {week_num} Literary Analysis Worksheet
## {macro_focus}

[Worksheet content would go here]
"""
    
    # Replace week-level placeholders
    worksheet = template.replace('[WEEK_NUMBER]', str(week_num))
    worksheet = worksheet.replace('[MACRO_FOCUS]', macro_focus)
    worksheet = worksheet.replace('[TEXT_TITLE]', week_package.get('text_title', 'The Text'))
    
    num_devices = len(devices)
    
    print(f"  ✓ Processing {num_devices} devices...")
    
    for i, device in enumerate(devices, 1):
        print(f"  → Device {i}/{num_devices}: {device['device_name']}")
        worksheet = fill_device_section(worksheet, device, i, kernel_data, macro_focus, client)
    
    # Clean up any remaining placeholders for unused devices
    for i in range(num_devices + 1, 7):  # Support up to 6 devices
        # Remove DEVICE_N section if not used
        section_header = f"### DEVICE {i}:"
        if section_header in worksheet:
            start = worksheet.find(section_header)
            end = worksheet.find("## TVODE CONNECTION", start)
            if end == -1:
                end = worksheet.find("**END OF WORKSHEET", start)
            if end > start:
                worksheet = worksheet[:start] + worksheet[end:]
    
    print(f"  ✓ Generated {len(worksheet):,} characters")
    
    return worksheet

def generate_tvode_worksheet(week_package, kernel_data, client):
    """Generate TVODE construction worksheet"""
    
    week_num = week_package["week"]
    macro_focus = week_package["macro_focus"]
    
    print(f"\n📝 Generating Week {week_num} TVODE worksheet...")
    
    try:
        template = load_template("Template_TVODE_Construction.md")
    except FileNotFoundError:
        # Generate basic TVODE worksheet
        template = f"""# Week {week_num} TVODE Construction Worksheet
## Connecting Devices to {macro_focus}

### What is TVODE?

**T**opic - The literary device name
**V**erb - Action word (demonstrates, reveals, creates, establishes, etc.)
**O**bject - What it acts upon
**D**etail - Specific evidence from text
**E**ffect - The result or impact

### Practice Constructing TVODE Sentences

For each device you analyzed, create a TVODE sentence that connects it to {macro_focus}.

**Example:**
*Direct Dialogue* **demonstrates** *character relationships* **through** *Jonas's formal exchanges with his parents* **which reveals** *the emotionally distant society.*

---

[DEVICE_PRACTICE_SECTIONS]

**END OF TVODE WORKSHEET**
"""
    
    worksheet = template.replace('[WEEK_NUMBER]', str(week_num))
    worksheet = worksheet.replace('[MACRO_FOCUS]', macro_focus)
    
    return worksheet

def generate_teacher_key(week_package, worksheet_content, client):
    """Generate teacher answer key"""
    
    week_num = week_package["week"]
    macro_focus = week_package["macro_focus"]
    
    print(f"\n🔑 Generating Week {week_num} teacher key...")
    
    # Build device information using week_label instead of executes_macro
    device_info = []
    for device in week_package['micro_devices']:
        device_label = device.get('week_label', device['definition'])
        device_info.append(f"**{device['device_name']}**: {device_label}")
    
    device_text = "\n".join(device_info)
    
    prompt = f"""Create a teacher answer key for this literary analysis worksheet.

WEEK: {week_num}
MACRO FOCUS: {macro_focus}
TEXT: {week_package.get('text_title', 'The text')}

DEVICES COVERED:
{device_text}

WORKSHEET STRUCTURE:
- Section 1: Understanding {macro_focus}
- Section 2: Device Analysis (6-step scaffolded activities per device)
- Section 3: Macro-Micro TVODE construction

Create an answer key with:

## TEACHING NOTES
Brief guidance on how to introduce {macro_focus} and facilitate the macro-micro connection.

## SECTION 1: COMPREHENSION CHECK
Expected responses for the two entry activities.

## SECTION 2: DEVICE ANALYSIS ANSWERS
For each device:
- Step 2: Strong example students might find
- Step 3: Correct multiple choice answer with brief explanation
- Step 4: Correct sequence (e.g., "1-B, 2-A, 3-C")
- Step 5: Example textual detail
- Step 6: Correct categorization with explanation of which effect best applies

## SECTION 3: SAMPLE TVODE SENTENCES
2-3 strong example sentences connecting {macro_focus} to the devices.

## COMMON MISCONCEPTIONS
What students often get wrong and how to address it.

Format in clear markdown with headers. Be specific and practical for teachers."""

    response = client.messages.create(
        model=Config.MODEL,
        max_tokens=Config.MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}]
    )
    
    key_content = response.content[0].text
    print(f"  ✓ Generated {len(key_content):,} characters")
    
    return key_content

def run_stage2(stage1b_path, kernel_path, week_num=None, all_weeks=False):
    """Main Stage 2 processing with template system"""
    
    print("\n" + "="*80)
    print("STAGE 2: WORKSHEET GENERATION (FIXED - TEMPLATE SYSTEM)")
    print("="*80)
    
    # Check API key
    if not Config.API_KEY:
        print("\n❌ Error: ANTHROPIC_API_KEY not set")
        print("Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)
    
    # Initialize client
    client = anthropic.Anthropic(api_key=Config.API_KEY)
    
    # Load Stage 1B output
    print(f"\n📖 Loading Stage 1B output: {stage1b_path}")
    with open(stage1b_path, 'r', encoding='utf-8') as f:
        stage1b = json.load(f)
    
    title = stage1b.get("metadata", {}).get("text_title", "Unknown")
    print(f"  ✓ Loaded: {title}")
    
    # Load kernel data
    print(f"\n🧬 Loading kernel data: {kernel_path}")
    with open(kernel_path, 'r', encoding='utf-8') as f:
        kernel_data = json.load(f)
    
    kernel_title = kernel_data.get("text_metadata", {}).get("title", "Unknown")
    print(f"  ✓ Loaded: {kernel_title}")
    
    # Determine which weeks to generate
    week_packages = stage1b.get("week_packages", [])
    
    if all_weeks:
        weeks_to_generate = week_packages
        print(f"\n📋 Generating worksheets for all {len(week_packages)} weeks...")
    elif week_num:
        weeks_to_generate = [pkg for pkg in week_packages if pkg["week"] == week_num]
        if not weeks_to_generate:
            print(f"\n❌ Error: Week {week_num} not found")
            sys.exit(1)
        print(f"\n📋 Generating worksheet for Week {week_num}...")
    else:
        # Default: generate Week 1 only
        weeks_to_generate = [pkg for pkg in week_packages if pkg["week"] == 1]
        print(f"\n📋 Generating worksheet for Week 1 (default)...")
        print("   Use --all-weeks to generate all weeks")
    
    # Create output directory - directly in outputs, not outputs/worksheets
    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate worksheets
    generated_files = []
    
    for week_pkg in weeks_to_generate:
        week_num = week_pkg["week"]
        
        # Generate Literary Analysis worksheet
        worksheet = generate_worksheet(week_pkg, kernel_data, client)
        
        # Save with standard naming: Week_N_Literary_Analysis_Worksheet.md
        worksheet_path = output_dir / f"Week_{week_num}_Literary_Analysis_Worksheet.md"
        with open(worksheet_path, 'w', encoding='utf-8') as f:
            f.write(worksheet)
        
        print(f"  ✅ Saved: {worksheet_path.name}")
        generated_files.append(worksheet_path)
        
        # Generate TVODE Construction worksheet
        tvode_worksheet = generate_tvode_worksheet(week_pkg, kernel_data, client)
        
        tvode_path = output_dir / f"Week_{week_num}_TVODE_Construction.md"
        with open(tvode_path, 'w', encoding='utf-8') as f:
            f.write(tvode_worksheet)
        
        print(f"  ✅ Saved: {tvode_path.name}")
        generated_files.append(tvode_path)
        
        # Generate teacher key
        teacher_key = generate_teacher_key(week_pkg, worksheet, client)
        
        # Save with standard naming: Week_N_Teacher_Key.md
        key_path = output_dir / f"Week_{week_num}_Teacher_Key.md"
        with open(key_path, 'w', encoding='utf-8') as f:
            f.write(f"# Week {week_num} Teacher Answer Key\n\n")
            f.write(f"**Text:** {title}\n")
            f.write(f"**Macro Focus:** {week_pkg['macro_focus']}\n\n")
            f.write(f"---\n\n")
            f.write(teacher_key)
        
        print(f"  ✅ Saved: {key_path.name}")
        generated_files.append(key_path)
    
    # Summary
    print("\n" + "="*80)
    print("✅ STAGE 2 COMPLETE!")
    print("="*80)
    print(f"\nGenerated {len(generated_files)} files:")
    for file_path in generated_files:
        print(f"  - {file_path}")
    
    print(f"\n📂 All worksheets saved to: {output_dir}")
    
    # Cost estimate
    num_weeks = len(weeks_to_generate)
    num_devices_total = sum(len(pkg.get('micro_devices', [])) for pkg in weeks_to_generate)
    estimated_cost = num_devices_total * 0.15  # ~$0.15 per device (MC + sequence + effects)
    print(f"\n💰 Estimated API cost: ~${estimated_cost:.2f}")
    
    return generated_files

def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python3 run_stage2_fixed.py stage1b.json kernel.json")
        print("  python3 run_stage2_fixed.py stage1b.json kernel.json --week 1")
        print("  python3 run_stage2_fixed.py stage1b.json kernel.json --all-weeks")
        sys.exit(1)
    
    stage1b_path = Path(sys.argv[1])
    kernel_path = Path(sys.argv[2])
    
    if not stage1b_path.exists():
        print(f"❌ Error: Stage 1B file not found: {stage1b_path}")
        sys.exit(1)
    
    if not kernel_path.exists():
        print(f"❌ Error: Kernel file not found: {kernel_path}")
        sys.exit(1)
    
    # Parse arguments
    week_num = None
    all_weeks = False
    
    if "--all-weeks" in sys.argv:
        all_weeks = True
    elif "--week" in sys.argv:
        try:
            week_idx = sys.argv.index("--week")
            week_num = int(sys.argv[week_idx + 1])
        except (IndexError, ValueError):
            print("❌ Error: --week requires a number (1-5)")
            sys.exit(1)
    
    run_stage2(stage1b_path, kernel_path, week_num, all_weeks)

if __name__ == "__main__":
    main()
