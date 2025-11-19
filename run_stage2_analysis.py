#!/usr/bin/env python3
"""
Stage 2 Analysis: Generate Literary Analysis Content
Produces data for interactive web components showing device analysis + macro synthesis

Input: Stage 1B JSON + Kernel
Output: JSON data files (one per week) for React components
"""

import json
import sys
import os
from pathlib import Path
import anthropic

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_extract_for_devices(devices, kernel_extracts):
    """
    Find which kernel extract section contains the most devices
    Returns: (section_name, extract_text)
    """
    # Count devices per section
    section_counts = {}
    for device in devices[:3]:
        examples = device.get('examples', [])
        if examples and isinstance(examples[0], dict):
            freytag = examples[0].get('freytag_section', 'exposition')
            section_counts[freytag] = section_counts.get(freytag, 0) + 1
    
    # Get most common section
    if section_counts:
        primary_section = max(section_counts.items(), key=lambda x: x[1])[0]
    else:
        primary_section = 'exposition'
    
    # Get extract text
    extract_data = kernel_extracts.get(primary_section, {})
    extract_text = extract_data.get('text', '')
    
    return primary_section, extract_text

def find_device_in_text(device_snippet, full_text):
    """
    Find device location in full text
    Returns: (start, end, found_text) or (None, None, snippet) if not found
    """
    # Try exact match first
    if device_snippet in full_text:
        start = full_text.find(device_snippet)
        end = start + len(device_snippet)
        return start, end, device_snippet
    
    # Try partial match (first 30 chars)
    if len(device_snippet) > 30:
        partial = device_snippet[:30]
        if partial in full_text:
            start = full_text.find(partial)
            end = start + len(device_snippet)
            if end > len(full_text):
                end = len(full_text)
            return start, end, full_text[start:end]
    
    return None, None, device_snippet

def extract_context_passage(device_snippet, full_text, context_chars=200):
    """
    Extract a passage around the device with context
    Returns: (passage, start_in_passage, end_in_passage)
    """
    if device_snippet not in full_text:
        # Return just the snippet if not found
        return device_snippet, 0, len(device_snippet)
    
    device_start = full_text.find(device_snippet)
    device_end = device_start + len(device_snippet)
    
    # Get context before and after
    passage_start = max(0, device_start - context_chars)
    passage_end = min(len(full_text), device_end + context_chars)
    
    # Try to start/end at sentence boundaries
    if passage_start > 0:
        # Look for period before
        period_pos = full_text.rfind('. ', passage_start - 50, device_start)
        if period_pos != -1:
            passage_start = period_pos + 2  # After ". "
    
    if passage_end < len(full_text):
        # Look for period after
        period_pos = full_text.find('. ', device_end, passage_end + 50)
        if period_pos != -1:
            passage_end = period_pos + 1  # Include the period
    
    passage = full_text[passage_start:passage_end]
    device_pos_in_passage = device_start - passage_start
    
    return passage, device_pos_in_passage, device_pos_in_passage + len(device_snippet)

def generate_analysis_sentence(device_data, book_title):
    """Generate natural TVODE analysis sentence using Claude API"""
    examples = device_data.get('examples', [])
    passage = ""
    if examples and isinstance(examples[0], dict) and examples[0].get('quote_snippet'):
        passage = examples[0]['quote_snippet']
    
    tvode = device_data.get('tvode_components', {})
    
    prompt = f"""You are analyzing the book "{book_title}". 

Given this literary device data:
- Device: {device_data.get('name', 'Unknown')}
- Passage: {passage if passage else 'N/A'}
- TVODE Components:
  - Topic: {tvode.get('topic', 'N/A')}
  - Detail: {tvode.get('detail', 'N/A')}
  - Object: {tvode.get('object', 'N/A')}
  - Effect: {tvode.get('effect', 'N/A')}

Write a single natural analysis sentence following this pattern:
"[Device name] is evident in this passage through [detail/topic], which [object - what it does]. This [creates/establishes/reveals] [effect and connection to larger meaning]."

Keep it concise (2-3 sentences max). Be specific to the passage. Make it student-friendly.

IMPORTANT: Output ONLY the analysis sentence, no preamble or explanation."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text.strip()

def generate_macro_synthesis(week_devices, macro_context, book_title, week_label):
    """Generate macro synthesis showing how devices connect"""
    device_names = [d.get('name', 'Unknown') for d in week_devices]
    device_list = "\n".join([
        f"- {d.get('name', 'Unknown')}: {d.get('tvode_components', {}).get('effect', 'N/A')}" 
        for d in week_devices
    ])
    
    prompt = f"""You are analyzing "{book_title}" for {week_label}.

These devices appear in this week's focus:
{device_list}

Macro context:
- POV: {macro_context.get('pov', 'N/A')}
- Key themes: {', '.join(macro_context.get('themes', [])) if macro_context.get('themes') else 'N/A'}
- Narrative structure: {macro_context.get('structure', 'N/A')}

Generate 3 connection statements showing how these devices work TOGETHER:
1. How 2 specific devices interact/support each other
2. How a device serves the POV or narrative structure
3. How all devices together advance the theme

Format as JSON array:
[
  {{
    "devices": ["Device A", "Device B"],
    "relationship": "One clear sentence showing their interaction"
  }},
  {{
    "devices": ["Device C", "POV"],
    "relationship": "One sentence showing how device serves POV"
  }},
  {{
    "devices": ["All devices", "Theme"],
    "relationship": "One sentence showing unified thematic purpose"
  }}
]

Be specific to this book and week. Keep each relationship to ONE sentence. Make it insightful but accessible.

IMPORTANT: Output ONLY valid JSON array, no markdown formatting or explanation."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )
    
    response_text = message.content[0].text.strip()
    response_text = response_text.replace("```json", "").replace("```", "").strip()
    
    try:
        connections = json.loads(response_text)
        return connections
    except json.JSONDecodeError as e:
        print(f"Warning: Failed to parse macro synthesis JSON: {e}")
        return [
            {"devices": [device_names[0] if len(device_names) > 0 else "Device", 
                         device_names[1] if len(device_names) > 1 else "Device"],
             "relationship": "These devices work together to create meaning."},
            {"devices": [device_names[0] if len(device_names) > 0 else "Device", "POV"],
             "relationship": "This device serves the narrative perspective."},
            {"devices": ["All devices", "Theme"],
             "relationship": "Together, these devices advance the central themes."}
        ]

def process_week(week_data, kernel_data, book_title):
    """Process one week of analysis - returns structured data for React component"""
    week_num = week_data.get('week', 1)
    macro_focus = week_data.get('macro_focus', 'Literary Analysis')
    macro_description = week_data.get('macro_description', '')
    
    print(f"\nProcessing Week {week_num}: {macro_focus}...")
    
    learning_goal = f"This week, you'll explore {macro_description.lower() if macro_description else 'how literary devices create meaning'}. Notice how individual devices work together to serve the story's larger purpose."
    
    devices = week_data.get('micro_devices', [])
    if not devices:
        print(f"  Warning: No devices found for Week {week_num}")
        return None
    
    # Find primary extract from kernel
    kernel_extracts = kernel_data.get('extracts', {})
    primary_section, primary_text = find_extract_for_devices(devices, kernel_extracts)
    print(f"  Primary extract: {primary_section}")
    
    if not primary_text:
        print(f"  Warning: No extract text found for {primary_section}")
        return None
    
    # Extract macro context
    macro_context = {
        'pov': kernel_data.get('narrative', {}).get('voice', {}).get('pov_description', ''),
        'themes': kernel_data.get('macro_variables', {}).get('themes', []),
        'structure': kernel_data.get('narrative', {}).get('structure', {}).get('overall_structure', '')
    }
    
    # Process devices
    annotations = []
    supplementary_passages = []
    device_count = min(3, len(devices))
    
    for idx in range(device_count):
        device = devices[idx]
        device_name = device.get('name') or device.get('device_name', 'Unknown')
        
        print(f"  Processing: {device_name}")
        
        # Get device info
        examples = device.get('examples', [])
        device_snippet = ""
        device_section = primary_section
        chapter = "N/A"
        
        if examples and isinstance(examples[0], dict):
            device_snippet = examples[0].get('quote_snippet', '')
            device_section = examples[0].get('freytag_section', primary_section)
            chapter = examples[0].get('chapter', 'N/A')
        
        # Try to find in primary extract
        start, end, found_text = find_device_in_text(device_snippet, primary_text)
        
        # Generate analysis
        try:
            analysis_sentence = generate_analysis_sentence(device, book_title)
        except Exception as e:
            print(f"    Warning: Failed to generate analysis: {e}")
            analysis_sentence = f"{device_name} contributes to the text's meaning through its specific application."
        
        tvode = device.get('tvode_components', {})
        
        if start is not None:
            # Found in primary passage
            print(f"    Found in primary extract at position {start}")
            annotation = {
                'id': idx + 1,
                'device': device_name,
                'start': start,
                'end': end,
                'text': found_text,
                'detail': tvode.get('detail', ''),
                'object': tvode.get('object', ''),
                'effect': tvode.get('effect', ''),
                'analysis': analysis_sentence,
                'inPrimaryPassage': True
            }
            annotations.append(annotation)
        else:
            # Not found - need supplementary passage
            print(f"    Not in primary extract - creating supplementary passage from {device_section}")
            
            # Get the correct extract for this device
            device_extract_text = kernel_extracts.get(device_section, {}).get('text', '')
            
            if device_extract_text:
                # Extract context passage around device
                passage, device_start, device_end = extract_context_passage(
                    device_snippet, 
                    device_extract_text
                )
                
                supplementary_passages.append({
                    'id': idx + 1,
                    'section': device_section,
                    'chapter': chapter,
                    'passage': passage,
                    'annotation': {
                        'id': idx + 1,
                        'device': device_name,
                        'start': device_start,
                        'end': device_end,
                        'text': device_snippet,
                        'detail': tvode.get('detail', ''),
                        'object': tvode.get('object', ''),
                        'effect': tvode.get('effect', ''),
                        'analysis': analysis_sentence,
                        'inPrimaryPassage': False
                    }
                })
                print(f"    Added supplementary passage ({len(passage)} chars)")
            else:
                print(f"    Warning: No extract found for {device_section}")
    
    # Generate macro synthesis
    print(f"  Generating macro synthesis...")
    try:
        macro_synthesis = generate_macro_synthesis(
            devices[:device_count],
            macro_context,
            book_title,
            f"Week {week_num}: {macro_focus}"
        )
    except Exception as e:
        print(f"    Warning: Failed to generate macro synthesis: {e}")
        macro_synthesis = []
    
    # Structure output
    output = {
        'title': f"{book_title} - Week {week_num}",
        'weekFocus': f"Week {week_num}: {macro_focus}",
        'learningGoal': learning_goal,
        'passage': primary_text,
        'extractSection': primary_section,
        'annotations': annotations,
        'supplementaryPassages': supplementary_passages,
        'macroSynthesis': {
            'title': 'How These Devices Work Together',
            'connections': macro_synthesis
        }
    }
    
    return output

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 run_stage2_analysis.py <stage1b_json> <kernel_json> [--week N]")
        print("\nExample:")
        print("  python3 run_stage2_analysis.py outputs/The_Giver_stage1b_v5.0.json kernels/The_Giver_kernel_v3.3.json --week 1")
        sys.exit(1)
    
    stage1b_path = sys.argv[1]
    kernel_path = sys.argv[2]
    
    target_week = None
    if '--week' in sys.argv:
        week_idx = sys.argv.index('--week')
        if week_idx + 1 < len(sys.argv):
            target_week = int(sys.argv[week_idx + 1])
    
    print(f"Loading Stage 1B JSON: {stage1b_path}")
    try:
        stage1b_data = load_json(stage1b_path)
    except FileNotFoundError:
        print(f"Error: File not found: {stage1b_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {stage1b_path}: {e}")
        sys.exit(1)
    
    print(f"Loading kernel: {kernel_path}")
    try:
        kernel_data = load_json(kernel_path)
    except FileNotFoundError:
        print(f"Error: File not found: {kernel_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {kernel_path}: {e}")
        sys.exit(1)
    
    book_title = stage1b_data.get('metadata', {}).get('text_title', 'Unknown Book')
    print(f"\nGenerating analysis content for: {book_title}")
    
    week_packages = stage1b_data.get('week_packages', [])
    if not week_packages:
        print("Error: No week_packages found in Stage 1B data")
        sys.exit(1)
    
    output_dir = Path('outputs/analysis_data')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if target_week:
        week_data = None
        for package in week_packages:
            if package.get('week') == target_week:
                week_data = package
                break
        
        if not week_data:
            print(f"Error: Week {target_week} not found")
            sys.exit(1)
        
        result = process_week(week_data, kernel_data, book_title)
        
        if result:
            output_filename = f"{book_title.replace(' ', '_')}_Week{target_week}_analysis.json"
            output_path = output_dir / output_filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"\n✓ Generated: {output_path}")
            print(f"  Main passage annotations: {len(result.get('annotations', []))}")
            print(f"  Supplementary passages: {len(result.get('supplementaryPassages', []))}")
        else:
            print(f"\n✗ Failed to generate Week {target_week}")
    else:
        for package in week_packages:
            week_num = package.get('week')
            if not week_num:
                continue
            
            result = process_week(package, kernel_data, book_title)
            
            if result:
                output_filename = f"{book_title.replace(' ', '_')}_Week{week_num}_analysis.json"
                output_path = output_dir / output_filename
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                print(f"  ✓ Saved: {output_path}")
        
        print(f"\n✓ Completed processing for {book_title}")

if __name__ == "__main__":
    main()
