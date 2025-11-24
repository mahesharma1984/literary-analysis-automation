#!/usr/bin/env python3
"""
STAGE 2 AUTOMATION
Generate worksheets from weekly packages

Usage:
    python3 run_stage2.py outputs/Book_stage1b_v5.0.json
    python3 run_stage2.py outputs/Book_stage1b_v5.0.json --week 1
    python3 run_stage2.py outputs/Book_stage1b_v5.0.json --all-weeks
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
    MAX_TOKENS = 8000

def generate_worksheet(week_package, client):
    """Generate literary analysis worksheet for a week"""
    
    week_num = week_package["week"]
    macro_focus = week_package["macro_focus"]
    devices = week_package["micro_devices"]
    
    print(f"\nðŸ¤– Generating Week {week_num} worksheet ({macro_focus})...")
    
    # Build device list
    device_list = "\n".join([
        f"- {d['name']}: {d['definition']}"
        for d in devices
    ])
    
    # Create prompt
    prompt = f"""Create a literary analysis worksheet for high school students.

WEEK: {week_num}
MACRO FOCUS: {macro_focus}
TEACHING GOAL: {week_package['teaching_goal']}
ACTIVITY CHAPTER: Chapter {week_package.get('activity_chapter', 'TBD')}
READING ASSIGNMENT: Chapters {week_package.get('reading_range', 'TBD')}

DEVICES TO TEACH:
{device_list}

TEACHING APPROACH:
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(week_package['teaching_sequence']))}

Create a worksheet with these sections:

1. **Reading & Chapter Focus** - START WITH: "This week, you will complete your assigned reading through Chapter {week_package.get('reading_range', 'TBD').split('-')[-1]}. Our analysis activities will focus specifically on Chapter {week_package.get('activity_chapter', 'TBD')}"

2. **Introduction** (2-3 sentences explaining the macro concept: {macro_focus})

3. **Device Definitions** (Define each device clearly for students)

4. **Text Analysis Activity** (6 analysis questions that guide students to analyze Chapter {week_package.get('activity_chapter', 'TBD')} specifically. EVERY question must reference "Chapter {week_package.get('activity_chapter', 'TBD')}" explicitly.)

5. **TVODE Construction** (Template and example for students to write TVODE sentences)

6. **Reflection** (2-3 questions for students to synthesize learning)

OUTPUT FORMAT: Markdown with clear headers and formatting suitable for students.
Keep language clear and age-appropriate for high school level.
"""

    print(f"DEBUG: activity_chapter = {week_package.get('activity_chapter')}")
    print(f"DEBUG: reading_range = {week_package.get('reading_range')}")
    
    # Call Claude API
    response = client.messages.create(
        model=Config.MODEL,
        max_tokens=Config.MAX_TOKENS,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    worksheet_content = response.content[0].text
    print(f"  âœ“ Generated {len(worksheet_content):,} characters")
    
    return worksheet_content

def generate_teacher_key(week_package, worksheet_content, client):
    """Generate teacher answer key for the worksheet"""
    
    week_num = week_package["week"]
    macro_focus = week_package["macro_focus"]
    
    print(f"\nðŸ”‘ Generating Week {week_num} teacher key...")
    
    prompt = f"""Create a teacher answer key for this literary analysis worksheet.

WEEK: {week_num}
MACRO FOCUS: {macro_focus}

WORKSHEET CONTENT:
{worksheet_content}

DEVICES COVERED:
{chr(10).join([f"- {d['name']}: {d.get('executes_macro', '')}" for d in week_package['micro_devices']])}

Create an answer key with:

1. **Teaching Notes** (How to introduce the macro concept and guide discussion)

2. **Answer Guide** (Sample answers for each analysis question)

3. **TVODE Examples** (3-4 strong example TVODE sentences)

4. **Common Student Misconceptions** (What to watch for and how to address)

5. **Extension Activities** (For advanced students)

OUTPUT FORMAT: Markdown with clear headers. Provide specific, detailed answers that teachers can use as reference.
"""
    
    response = client.messages.create(
        model=Config.MODEL,
        max_tokens=Config.MAX_TOKENS,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    key_content = response.content[0].text
    print(f"  âœ“ Generated {len(key_content):,} characters")
    
    return key_content

def run_stage2(stage1b_path, week_num=None, all_weeks=False):
    """Main Stage 2 processing"""
    
    print("\n" + "="*80)
    print("STAGE 2: WORKSHEET GENERATION")
    print("="*80)
    
    # Check API key
    if not Config.API_KEY:
        print("\nâŒ Error: ANTHROPIC_API_KEY not set")
        print("Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)
    
    # Initialize client
    client = anthropic.Anthropic(api_key=Config.API_KEY)
    
    # Load Stage 1B output
    print(f"\nðŸ“– Loading Stage 1B output: {stage1b_path}")
    with open(stage1b_path, 'r', encoding='utf-8') as f:
        stage1b = json.load(f)
    
    title = stage1b.get("metadata", {}).get("text_title", "Unknown")
    author = stage1b.get("metadata", {}).get("author", "Unknown")
    print(f"  âœ“ Loaded: {title} by {author}")
    
    # Determine which weeks to generate
    week_packages = stage1b.get("week_packages", [])
    
    if all_weeks:
        weeks_to_generate = week_packages
        print(f"\nðŸ“ Generating worksheets for all {len(week_packages)} weeks...")
    elif week_num:
        weeks_to_generate = [pkg for pkg in week_packages if pkg["week"] == week_num]
        if not weeks_to_generate:
            print(f"\nâŒ Error: Week {week_num} not found")
            sys.exit(1)
        print(f"\nðŸ“ Generating worksheet for Week {week_num}...")
    else:
        # Default: generate Week 1 only
        weeks_to_generate = [pkg for pkg in week_packages if pkg["week"] == 1]
        print(f"\nðŸ“ Generating worksheet for Week 1 (default)...")
        print("   Use --all-weeks to generate all weeks")
    
    # Create output directory
    output_dir = Path("outputs") / "worksheets"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
    
    # Generate worksheets
    generated_files = []
    
    for week_pkg in weeks_to_generate:
        week_num = week_pkg["week"]
        
        # Generate worksheet
        worksheet = generate_worksheet(week_pkg, client)
        
        # Save worksheet
        worksheet_path = output_dir / f"{safe_title}_Week{week_num}_Worksheet.md"
        with open(worksheet_path, 'w', encoding='utf-8') as f:
            f.write(f"# {title} - Week {week_num} Literary Analysis Worksheet\n\n")
            f.write(f"**Macro Focus:** {week_pkg['macro_focus']}\n\n")
            f.write(f"---\n\n")
            f.write(worksheet)
        
        print(f"  âœ“ Saved: {worksheet_path.name}")
        generated_files.append(worksheet_path)
        
        # Generate teacher key
        teacher_key = generate_teacher_key(week_pkg, worksheet, client)
        
        # Save teacher key
        key_path = output_dir / f"{safe_title}_Week{week_num}_TeacherKey.md"
        with open(key_path, 'w', encoding='utf-8') as f:
            f.write(f"# {title} - Week {week_num} Teacher Answer Key\n\n")
            f.write(f"**Macro Focus:** {week_pkg['macro_focus']}\n\n")
            f.write(f"---\n\n")
            f.write(teacher_key)
        
        print(f"  âœ“ Saved: {key_path.name}")
        generated_files.append(key_path)
    
    # Summary
    print("\n" + "="*80)
    print("âœ… STAGE 2 COMPLETE!")
    print("="*80)
    print(f"\nGenerated {len(generated_files)} files:")
    for file_path in generated_files:
        print(f"  - {file_path}")
    
    print(f"\nðŸ“‚ All worksheets saved to: {output_dir}")
    
    # Cost estimate
    num_weeks = len(weeks_to_generate)
    estimated_cost = num_weeks * 0.20  # ~$0.20 per week (worksheet + key)
    print(f"\nðŸ’° Estimated API cost: ~${estimated_cost:.2f}")
    
    return generated_files

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 run_stage2.py outputs/Book_stage1b_v5.0.json")
        print("  python3 run_stage2.py outputs/Book_stage1b_v5.0.json --week 1")
        print("  python3 run_stage2.py outputs/Book_stage1b_v5.0.json --all-weeks")
        sys.exit(1)
    
    stage1b_path = Path(sys.argv[1])
    
    if not stage1b_path.exists():
        print(f"âŒ Error: Stage 1B file not found: {stage1b_path}")
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
            print("âŒ Error: --week requires a number (1-4)")
            sys.exit(1)
    
    run_stage2(stage1b_path, week_num, all_weeks)

if __name__ == "__main__":
    main()
