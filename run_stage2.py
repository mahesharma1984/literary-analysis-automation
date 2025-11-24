#!/usr/bin/env python3
"""
STAGE 2 AUTOMATION - HYBRID TEMPLATE APPROACH
Generate worksheets by filling templates with data from Stage 1B + AI-generated content

Usage:
    python3 run_stage2.py outputs/Book_stage1b_v5_0.json --week 1
    python3 run_stage2.py outputs/Book_stage1b_v5_0.json --all-weeks
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from anthropic import Anthropic

# Configuration
class Config:
    API_KEY = os.environ.get("ANTHROPIC_API_KEY")
    MODEL = "claude-sonnet-4-20250514"
    MAX_TOKENS = 4000

def load_template(template_path):
    """Load template file"""
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def generate_placeholder_data(device, macro_focus, chapter_num, client):
    """Generate missing template data for one device using Claude API"""
    
    # Build examples text from device data
    examples_text = ""
    if device.get('examples'):
        for i, ex in enumerate(device['examples'][:3], 1):
            quote = ex.get('text', ex.get('quote_snippet', ''))
            examples_text += f"\nExample {i}: \"{quote}\"\n"
    
    prompt = f"""Generate pedagogical content for a literary device worksheet.

DEVICE: {device['name']}
DEFINITION: {device['definition']}
MACRO FOCUS: {macro_focus}
CHAPTER: {chapter_num}

TEXT EXAMPLES:
{examples_text if examples_text else "No specific examples provided"}

Generate the following in JSON format:

{{
  "multiple_choice": {{
    "option_a": "A plausible wrong answer about this device",
    "option_b": "The correct identification of this device",
    "option_c": "Another plausible wrong answer",
    "option_d": "A third plausible wrong answer",
    "correct": "B",
    "distractor_1_explanation": "Why option A is incorrect",
    "distractor_2_explanation": "Why option C is incorrect"
  }},
  "sequencing": {{
    "item_a": "First step in analyzing this device",
    "item_b": "Second step in analyzing this device", 
    "item_c": "Third step in analyzing this device",
    "correct_order": "A, B, C",
    "explanation": "Why this order is correct"
  }},
  "effects": {{
    "meaning": "How this device affects meaning in the text",
    "reader": "How this device affects the reader's experience",
    "theme": "How this device contributes to theme",
    "character": "How this device reveals character",
    "plot": "How this device advances plot",
    "structure": "How this device affects narrative structure"
  }},
  "examples": {{
    "model_example": "Complete quote from text showing this device",
    "model_paragraph": "Full TVODE paragraph analyzing the device with T, V, O, D, E components clearly visible",
    "sample_response": "Expected student answer for device identification",
    "location_prompt": "Where to find this device (e.g., 'page 23, paragraph 2')"
  }},
  "teaching": {{
    "teaching_note": "Pedagogical tip for teaching this device",
    "common_error_1": "Common student misconception about this device",
    "common_error_2": "Another common student error",
    "scaffolding_tip": "How to support struggling students"
  }}
}}

IMPORTANT: 
- Keep all text student-appropriate for high school level
- Multiple choice options should be plausible but clearly distinguishable
- Model paragraph must be a complete TVODE sentence
- All content should relate to the macro focus: {macro_focus}

Output ONLY valid JSON, no other text."""

    try:
        response = client.messages.create(
            model=Config.MODEL,
            max_tokens=Config.MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result_text = response.content[0].text.strip()
        # Remove markdown code blocks if present
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
            result_text = result_text.strip()
        
        return json.loads(result_text)
    except Exception as e:
        print(f"  ⚠ Error generating data for {device['name']}: {e}")
        return None

def fill_worksheet_template(template, week_package, enriched_devices):
    """Fill worksheet template with all data"""
    
    output = template
    
    # Fill metadata
    output = output.replace("{{TEXT_TITLE}}", week_package.get('text_title', 'Unknown'))
    output = output.replace("{{TEXT_AUTHOR}}", week_package.get('text_author', 'Unknown'))
    output = output.replace("{{EDITION_REFERENCE}}", "2003 edition")  # TODO: Get from kernel
    output = output.replace("{{EXTRACT_FOCUS}}", week_package.get('macro_focus', ''))
    output = output.replace("{{YEAR_LEVEL}}", "9-10")  # TODO: Make configurable
    output = output.replace("{{PROFICIENCY_TIER}}", "Standard")  # TODO: Make configurable
    activity_ch = week_package.get('activity_chapter', 'TBD')
    reading_range = week_package.get('reading_range', 'TBD')
    output = output.replace(
    "1. Read the indicated chapters",
    f"1. Read Chapters {reading_range} (focus on Chapter {activity_ch} for activities)"
)
    
    # Fill device data
    for i, (device, enriched) in enumerate(zip(week_package['micro_devices'][:3], enriched_devices), 1):
        if enriched is None:
            continue
            
        # Basic device info
        output = output.replace(f"{{{{DEVICE_{i}_NAME}}}}", device['name'])
        output = output.replace(f"{{{{DEVICE_{i}_DEFINITION}}}}", device.get('definition', ''))
        
        # Multiple choice
        if 'multiple_choice' in enriched:
            mc = enriched['multiple_choice']
            output = output.replace(f"{{{{DEVICE_{i}_OPTION_A}}}}", mc.get('option_a', ''))
            output = output.replace(f"{{{{DEVICE_{i}_OPTION_B}}}}", mc.get('option_b', ''))
            output = output.replace(f"{{{{DEVICE_{i}_OPTION_C}}}}", mc.get('option_c', ''))
            output = output.replace(f"{{{{DEVICE_{i}_OPTION_D}}}}", mc.get('option_d', ''))
        
        # Sequencing
        if 'sequencing' in enriched:
            seq = enriched['sequencing']
            output = output.replace(f"{{{{DEVICE_{i}_SEQUENCE_A}}}}", seq.get('item_a', ''))
            output = output.replace(f"{{{{DEVICE_{i}_SEQUENCE_B}}}}", seq.get('item_b', ''))
            output = output.replace(f"{{{{DEVICE_{i}_SEQUENCE_C}}}}", seq.get('item_c', ''))
        
        # Effects
        if 'effects' in enriched:
            eff = enriched['effects']
            output = output.replace(f"{{{{DEVICE_{i}_EFFECT_1}}}}", eff.get('meaning', ''))
            output = output.replace(f"{{{{DEVICE_{i}_EFFECT_2}}}}", eff.get('reader', ''))
            output = output.replace(f"{{{{DEVICE_{i}_EFFECT_3}}}}", eff.get('theme', ''))
            output = output.replace(f"{{{{DEVICE_{i}_EFFECT_4}}}}", eff.get('character', ''))
            output = output.replace(f"{{{{DEVICE_{i}_EFFECT_5}}}}", eff.get('plot', ''))
            output = output.replace(f"{{{{DEVICE_{i}_EFFECT_6}}}}", eff.get('structure', ''))
        
        # Examples
        if 'examples' in enriched:
            ex = enriched['examples']
            output = output.replace(f"{{{{DEVICE_{i}_MODEL_EXAMPLE}}}}", ex.get('model_example', ''))
            output = output.replace(f"{{{{DEVICE_{i}_EXAMPLE_LOCATIONS}}}}", ex.get('location_prompt', ''))
    
    return output

def fill_teacher_key_template(template, week_package, enriched_devices):
    """Fill teacher key template with all data"""
    
    output = template
    
    # Fill metadata (same as worksheet)
    output = output.replace("{{TEXT_TITLE}}", week_package.get('text_title', 'Unknown'))
    output = output.replace("{{TEXT_AUTHOR}}", week_package.get('text_author', 'Unknown'))
    output = output.replace("{{WEEK_NUMBER}}", str(week_package.get('week', '')))
    output = output.replace("{{WEEK_FOCUS}}", week_package.get('macro_focus', ''))
    output = output.replace("{{EDITION_REFERENCE}}", "2003 edition")
    output = output.replace("{{EXTRACT_FOCUS}}", week_package.get('macro_focus', ''))
    output = output.replace("{{YEAR_LEVEL}}", "9-10")
    output = output.replace("{{PROFICIENCY_TIER}}", "Standard")
    
    # Fill device data (includes answers and teaching notes)
    for i, (device, enriched) in enumerate(zip(week_package['micro_devices'][:3], enriched_devices), 1):
        if enriched is None:
            continue
            
        # Basic info
        output = output.replace(f"{{{{DEVICE_{i}_NAME}}}}", device['name'])
        output = output.replace(f"{{{{DEVICE_{i}_DEFINITION}}}}", device.get('definition', ''))
        
        # Multiple choice with answers
        if 'multiple_choice' in enriched:
            mc = enriched['multiple_choice']
            output = output.replace(f"{{{{DEVICE_{i}_OPTION_A}}}}", mc.get('option_a', ''))
            output = output.replace(f"{{{{DEVICE_{i}_OPTION_B}}}}", mc.get('option_b', ''))
            output = output.replace(f"{{{{DEVICE_{i}_OPTION_C}}}}", mc.get('option_c', ''))
            output = output.replace(f"{{{{DEVICE_{i}_OPTION_D}}}}", mc.get('option_d', ''))
            output = output.replace(f"{{{{DEVICE_{i}_CORRECT_OPTION}}}}", mc.get('correct', ''))
            output = output.replace(f"{{{{DEVICE_{i}_DISTRACTOR_1}}}}", mc.get('distractor_1_explanation', ''))
            output = output.replace(f"{{{{DEVICE_{i}_DISTRACTOR_2}}}}", mc.get('distractor_2_explanation', ''))
        
        # Sequencing with answer
        if 'sequencing' in enriched:
            seq = enriched['sequencing']
            output = output.replace(f"{{{{DEVICE_{i}_SEQUENCE_A}}}}", seq.get('item_a', ''))
            output = output.replace(f"{{{{DEVICE_{i}_SEQUENCE_B}}}}", seq.get('item_b', ''))
            output = output.replace(f"{{{{DEVICE_{i}_SEQUENCE_C}}}}", seq.get('item_c', ''))
            output = output.replace(f"{{{{DEVICE_{i}_SEQUENCE_ANSWER}}}}", seq.get('correct_order', ''))
            output = output.replace(f"{{{{DEVICE_{i}_SEQUENCE_EXPLANATION}}}}", seq.get('explanation', ''))
        
        # Effects (same as worksheet)
        if 'effects' in enriched:
            eff = enriched['effects']
            output = output.replace(f"{{{{DEVICE_{i}_EFFECT_1}}}}", eff.get('meaning', ''))
            output = output.replace(f"{{{{DEVICE_{i}_EFFECT_2}}}}", eff.get('reader', ''))
            output = output.replace(f"{{{{DEVICE_{i}_EFFECT_3}}}}", eff.get('theme', ''))
            output = output.replace(f"{{{{DEVICE_{i}_EFFECT_4}}}}", eff.get('character', ''))
            output = output.replace(f"{{{{DEVICE_{i}_EFFECT_5}}}}", eff.get('plot', ''))
            output = output.replace(f"{{{{DEVICE_{i}_EFFECT_6}}}}", eff.get('structure', ''))
        
        # Examples and teaching
        if 'examples' in enriched:
            ex = enriched['examples']
            output = output.replace(f"{{{{DEVICE_{i}_MODEL_EXAMPLE}}}}", ex.get('model_example', ''))
            output = output.replace(f"{{{{DEVICE_{i}_MODEL_PARAGRAPH}}}}", ex.get('model_paragraph', ''))
            output = output.replace(f"{{{{DEVICE_{i}_SAMPLE_RESPONSE}}}}", ex.get('sample_response', ''))
            output = output.replace(f"{{{{DEVICE_{i}_EXAMPLE_LOCATIONS}}}}", ex.get('location_prompt', ''))
        
        if 'teaching' in enriched:
            teach = enriched['teaching']
            output = output.replace(f"{{{{DEVICE_{i}_TEACHING_NOTE}}}}", teach.get('teaching_note', ''))
    
    return output

def process_week(week_package, template_dir, output_dir, client):
    """Process one week: generate data and fill templates"""
    
    week_num = week_package['week']
    macro_focus = week_package['macro_focus']
    activity_chapter = week_package.get('activity_chapter', 'TBD')
    
    print(f"\n📝 Processing Week {week_num}: {macro_focus}")
    print(f"   Activity Chapter: {activity_chapter}")
    print(f"   Devices: {len(week_package['micro_devices'])}")
    
    # Generate enriched data for each device
    print(f"\n🤖 Generating pedagogical content...")
    enriched_devices = []
    
    for device in week_package['micro_devices'][:3]:  # Limit to 3 devices per worksheet
        print(f"   - {device['name']}...", end='', flush=True)
        enriched = generate_placeholder_data(device, macro_focus, activity_chapter, client)
        enriched_devices.append(enriched)
        print(" ✓")
    
    # Load templates
    print(f"\n📄 Filling templates...")
    worksheet_template = load_template(template_dir / "Template_Literary_Analysis_6Step.md")
    teacher_key_template = load_template(template_dir / "Template_Teacher_Key.md")
    
    # Fill templates
    worksheet = fill_worksheet_template(worksheet_template, week_package, enriched_devices)
    teacher_key = fill_teacher_key_template(teacher_key_template, week_package, enriched_devices)
    
    # Save outputs
    output_dir.mkdir(parents=True, exist_ok=True)
    
    title = week_package.get('text_title', 'Book').replace(' ', '_')
    
    worksheet_path = output_dir / f"{title}_Week{week_num}_Worksheet.md"
    teacher_key_path = output_dir / f"{title}_Week{week_num}_TeacherKey.md"
    
    with open(worksheet_path, 'w', encoding='utf-8') as f:
        f.write(worksheet)
    print(f"   ✓ Worksheet: {worksheet_path.name}")
    
    with open(teacher_key_path, 'w', encoding='utf-8') as f:
        f.write(teacher_key)
    print(f"   ✓ Teacher Key: {teacher_key_path.name}")
    
    return worksheet_path, teacher_key_path

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 run_stage2.py outputs/Book_stage1b_v5_0.json --week 1")
        print("       python3 run_stage2.py outputs/Book_stage1b_v5_0.json --all-weeks")
        sys.exit(1)
    
    stage1b_path = Path(sys.argv[1])
    
    # Parse options
    all_weeks = '--all-weeks' in sys.argv
    week_num = None
    if '--week' in sys.argv:
        week_idx = sys.argv.index('--week')
        if week_idx + 1 < len(sys.argv):
            week_num = int(sys.argv[week_idx + 1])
    
    if not stage1b_path.exists():
        print(f"❌ Error: Stage 1B file not found: {stage1b_path}")
        sys.exit(1)
    
    # Initialize API client
    if not Config.API_KEY:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    
    client = Anthropic(api_key=Config.API_KEY)
    
    print("\n" + "="*80)
    print("STAGE 2: TEMPLATE-BASED WORKSHEET GENERATION")
    print("="*80)
    
    # Load Stage 1B data
    print(f"\n📖 Loading Stage 1B output: {stage1b_path}")
    with open(stage1b_path, 'r', encoding='utf-8') as f:
        stage1b = json.load(f)
    
    title = stage1b['metadata']['text_title']
    author = stage1b['metadata']['author']
    print(f"  ✓ Loaded: {title} by {author}")
    
    # Setup paths
    template_dir = Path(__file__).parent
    output_dir = Path("outputs/worksheets")
    
    # Process weeks
    week_packages = stage1b['week_packages']
    
    if all_weeks:
        print(f"\n📚 Generating worksheets for all {len(week_packages)} weeks...")
        generated_files = []
        
        for week_package in week_packages:
            files = process_week(week_package, template_dir, output_dir, client)
            generated_files.extend(files)
        
        print("\n" + "="*80)
        print("✅ ALL WEEKS COMPLETE!")
        print("="*80)
        print(f"\nGenerated {len(generated_files)} files in: {output_dir}")
        
    else:
        if week_num is None:
            week_num = 1
            print(f"\n📝 Generating worksheet for Week {week_num} (default)")
            print("   Use --all-weeks to generate all weeks")
        else:
            print(f"\n📝 Generating worksheet for Week {week_num}")
        
        week_package = week_packages[week_num - 1]
        worksheet_path, teacher_key_path = process_week(week_package, template_dir, output_dir, client)
        
        print("\n" + "="*80)
        print("✅ STAGE 2 COMPLETE!")
        print("="*80)
        print(f"\nGenerated files:")
        print(f"  - {worksheet_path}")
        print(f"  - {teacher_key_path}")
    
    print(f"\n📂 All worksheets saved to: {output_dir}")
    print(f"\n💰 Estimated API cost: ~${len(week_packages) * 3 * 0.015:.2f}")

if __name__ == "__main__":
    main()
