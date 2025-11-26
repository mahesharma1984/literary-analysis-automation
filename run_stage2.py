#!/usr/bin/env python3
"""
STAGE 2 AUTOMATION - PURE EXTRACTION
Extract pre-generated worksheet content from Stage 1B JSON
NO GENERATION - everything extracted directly from Stage 1B data

Usage:
    python3 run_stage2.py outputs/Book_stage1b_v5_0.json --week 1
    python3 run_stage2.py outputs/Book_stage1b_v5_0.json --all-weeks
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import re

# ============================================================================
# TEMPLATE LOADING
# ============================================================================

def load_template(template_path):
    """Load template file"""
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

# ============================================================================
# THESIS ALIGNMENT SECTION GENERATION
# ============================================================================

def find_kernel_path(text_title):
    """Find kernel JSON file for a given text title"""
    kernels_dir = Path("kernels")
    if not kernels_dir.exists():
        return None
    
    safe_title = "".join(c for c in text_title if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
    pattern = f"{safe_title}_kernel*.json"
    matches = list(kernels_dir.glob(pattern))
    
    if matches:
        return sorted(matches, key=lambda p: p.stat().st_mtime, reverse=True)[0]
    return None

def find_reasoning_doc_path(text_title):
    """Find reasoning document for a given text title"""
    kernels_dir = Path("kernels")
    if not kernels_dir.exists():
        return None
    
    safe_title = "".join(c for c in text_title if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
    pattern = f"{safe_title}_ReasoningDoc*.md"
    matches = list(kernels_dir.glob(pattern))
    
    if matches:
        return sorted(matches, key=lambda p: p.stat().st_mtime, reverse=True)[0]
    return None

def extract_overall_thesis(reasoning_doc_path):
    """Extract overall thesis statement from reasoning document"""
    if not reasoning_doc_path or not reasoning_doc_path.exists():
        return None
    
    with open(reasoning_doc_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for alignment pattern description (most reliable thesis source)
    alignment_match = re.search(r'Identified Alignment Pattern[:\s]*\n(.+?)(?=\n\n|\n##|\\Z)', content, re.IGNORECASE | re.DOTALL)
    if alignment_match:
        alignment_text = alignment_match.group(1).strip()
        pattern_match = re.search(r'The primary alignment pattern[^\.]+is[^\.]+\.(.+?)(?=\n\n|\n-|\\Z)', alignment_text, re.IGNORECASE | re.DOTALL)
        if pattern_match:
            thesis = pattern_match.group(1).strip()
        else:
            sentences = re.split(r'[.!?]+', alignment_text)
            thesis = sentences[0].strip() if sentences else alignment_text[:200]
        
        thesis = re.sub(r'\*\*|__', '', thesis)
        thesis = re.sub(r'\n+', ' ', thesis)
        thesis = re.sub(r'^[-*]\s+', '', thesis)
        if len(thesis) > 500:
            thesis = thesis[:497] + "..."
        return thesis
    
    # Fallback patterns
    patterns = [
        r'overall thesis[:\s]+(.+?)(?:\n\n|\n##|\\Z)',
        r'thesis[:\s]+(.+?)(?:\n\n|\n##|\\Z)',
        r'central theme[:\s]+(.+?)(?:\n\n|\n##|\\Z)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        if match:
            thesis = match.group(1).strip()
            thesis = re.sub(r'\*\*|__', '', thesis)
            thesis = re.sub(r'\n+', ' ', thesis)
            thesis = re.sub(r'^Text Selection Rationale[:\s]*', '', thesis, flags=re.IGNORECASE)
            if len(thesis) > 500:
                thesis = thesis[:497] + "..."
            return thesis
    
    # Fallback: extract from overview section
    overview_match = re.search(r'##\s*1\.\s*Overview[^\n]*(.+?)(?=##|\\Z)', content, re.IGNORECASE | re.DOTALL)
    if overview_match:
        overview = overview_match.group(1).strip()
        paragraphs = [p.strip() for p in overview.split('\n\n') if len(p.strip()) > 50 and 'Text Selection Rationale' not in p]
        if paragraphs:
            thesis = paragraphs[0]
            thesis = re.sub(r'\*\*|__', '', thesis)
            if len(thesis) > 500:
                thesis = thesis[:497] + "..."
            return thesis
    
    return None

def extract_macro_summary(reasoning_doc_path, macro_type):
    """Extract summary for a macro element (voice, structure, rhetoric)"""
    if not reasoning_doc_path or not reasoning_doc_path.exists():
        return "Not available"
    
    with open(reasoning_doc_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    macro_keywords = {
        'voice': ['narrative voice', 'voice', 'perspective', 'point of view', 'pov'],
        'structure': ['structure', 'plot', 'narrative structure', 'plot architecture'],
        'rhetoric': ['rhetoric', 'rhetorical', 'alignment', 'strategy']
    }
    
    keywords = macro_keywords.get(macro_type.lower(), [macro_type])
    
    for keyword in keywords:
        pattern = f'({keyword}[^#]+?)(?=##|\\Z)'
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        if match:
            section = match.group(1).strip()
            sentences = [s.strip() for s in re.split(r'[.!?]+', section) if len(s.strip()) > 30]
            if sentences:
                summary = sentences[0]
                summary = re.sub(r'\*\*|__', '', summary)
                if len(summary) > 200:
                    summary = summary[:197] + "..."
                return summary
    
    return "Not available"

def extract_macro_from_kernel(kernel, macro_type):
    """Extract macro variable summary from kernel JSON"""
    if not kernel:
        return "Not available"
    
    macro_vars = kernel.get('macro_variables', {})
    narrative = macro_vars.get('narrative', kernel.get('narrative', {}))
    rhetoric = macro_vars.get('rhetoric', kernel.get('rhetoric', {}))
    
    if macro_type.lower() == 'voice':
        voice_data = narrative.get('voice', {})
        pov_desc = voice_data.get('pov_description', '')
        if pov_desc:
            return pov_desc
        pov = voice_data.get('pov', 'Unknown')
        focalization_desc = voice_data.get('focalization_description', '')
        if focalization_desc:
            return f"{pov} perspective with {focalization_desc}"
        focalization = voice_data.get('focalization', 'Unknown')
        return f"{pov} perspective with {focalization} focalization"
    
    elif macro_type.lower() == 'structure':
        structure_data = narrative.get('structure', {})
        plot_desc = structure_data.get('plot_architecture_description', '')
        if plot_desc:
            return plot_desc
        plot_type = structure_data.get('plot_architecture', 'Unknown')
        return f"{plot_type} structure"
    
    elif macro_type.lower() == 'rhetoric':
        alignment = rhetoric.get('alignment_type', 'Unknown')
        alignment_desc = rhetoric.get('alignment_type_description', '')
        if alignment_desc:
            return alignment_desc
        mechanism = rhetoric.get('dominant_mechanism', 'Unknown')
        return f"{alignment} alignment through {mechanism}"
    
    return "Not available"

def generate_dramatic_purpose(freytag_section, reading_range, week_focus, reasoning_doc_path, kernel):
    """Generate 2-3 sentences explaining this week's dramatic purpose"""
    
    freytag_templates = {
        "exposition": "These opening chapters introduce the main characters, setting, and initial circumstances. This establishes the foundation for the central conflict and themes that will drive the entire narrative.",
        "rising_action": "This section builds tension through escalating events and complications. These developments raise the stakes and move the narrative toward its climactic turning point.",
        "climax": "This is the turning point where the central conflict reaches its peak. This moment determines the direction of the resolution and reveals the story's core meaning.",
        "falling_action": "Following the climax, these chapters show the consequences and aftermath of the turning point. This section begins to resolve subplots and move toward closure.",
        "resolution": "The final chapters resolve remaining conflicts and bring closure to the narrative arc. This section completes the thematic exploration and provides final insight into the text's meaning."
    }
    
    if reasoning_doc_path and reasoning_doc_path.exists():
        with open(reasoning_doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        section_keywords = {
            "exposition": ["exposition", "opening", "introduction", "beginning"],
            "rising_action": ["rising action", "escalation", "tension", "complications"],
            "climax": ["climax", "turning point", "peak", "crisis"],
            "falling_action": ["falling action", "consequences", "aftermath"],
            "resolution": ["resolution", "conclusion", "closure", "ending"]
        }
        
        keywords = section_keywords.get(freytag_section.lower(), [])
        for keyword in keywords:
            pattern = f'({keyword}[^#]+?)(?=##|\\Z)'
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                section_text = match.group(1).strip()
                sentences = [s.strip() for s in re.split(r'[.!?]+', section_text) if len(s.strip()) > 30]
                if sentences:
                    purpose = sentences[0]
                    if len(sentences) > 1:
                        purpose += ". " + sentences[1]
                    purpose = re.sub(r'\*\*|__', '', purpose)
                    if len(purpose) > 300:
                        purpose = purpose[:297] + "..."
                    return purpose
    
    return freytag_templates.get(freytag_section.lower(), freytag_templates["exposition"])

def generate_thematic_connections(freytag_section, devices, reasoning_doc_path):
    """Generate 2-3 thematic connection bullet points"""
    connections = []
    
    if not reasoning_doc_path or not reasoning_doc_path.exists():
        return [
            f"Devices in this section connect to the text's exploration of central themes",
            f"The {freytag_section} function supports the overall narrative purpose"
        ]
    
    with open(reasoning_doc_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    theme_patterns = [
        r'theme[s]?[:\s]+(.+?)(?:\n\n|\n##|\\Z)',
        r'central theme[:\s]+(.+?)(?:\n\n|\n##|\\Z)',
        r'thematic[:\s]+(.+?)(?:\n\n|\n##|\\Z)',
    ]
    
    themes = []
    for pattern in theme_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            theme_text = match.group(1).strip()
            theme_phrases = re.findall(r'\b(?:theme|exploration|critique|message|commentary)\s+of\s+([^,\.]+)', theme_text, re.IGNORECASE)
            themes.extend(theme_phrases)
    
    device_names = [d.get('name', '') for d in devices[:3]]
    
    if themes:
        for i, theme in enumerate(themes[:2]):
            connections.append(f"Devices like {', '.join(device_names[:2])} support the theme of {theme.strip()}")
    else:
        connections.append(f"Devices in this section work together to establish the {freytag_section} function")
        connections.append(f"The {freytag_section} section connects to the text's central themes through device usage")
    
    if device_names:
        connections.append(f"These devices build meaning that supports the overall narrative purpose")
    
    return connections[:3]

def generate_what_to_notice(devices, freytag_section, week_focus):
    """Generate 3 'What to Notice' points"""
    device_names = [d.get('name', 'device') for d in devices[:3]]
    
    notices = []
    
    function_descriptions = {
        "exposition": "establish characters, setting, and initial circumstances",
        "rising_action": "build tension and escalate conflict",
        "climax": "create the turning point and reveal core meaning",
        "falling_action": "show consequences and begin resolution",
        "resolution": "bring closure and complete thematic exploration"
    }
    function_desc = function_descriptions.get(freytag_section.lower(), "serve the narrative function")
    
    notices.append(f"Literary devices like {', '.join(device_names[:2])} work together to {function_desc}")
    notices.append(f"Devices maintain narrative coherence while fulfilling the {freytag_section} function")
    notices.append(f"Devices build meaning that connects to the text's overall exploration of its central themes")
    
    return notices

def generate_thesis_alignment_section(week_package, kernel, reasoning_doc_path):
    """Generate the Thesis Alignment section for a worksheet"""
    
    title = week_package.get('text_title', 'Unknown')
    macro_focus = week_package.get('macro_focus', '')
    
    macro_to_freytag = {
        'Exposition': 'exposition',
        'Rising Action': 'rising_action',
        'Climax': 'climax',
        'Falling Action': 'falling_action',
        'Resolution': 'resolution',
        'Literary Devices Foundation': 'exposition',
        'Structure': 'rising_action',
        'Voice': 'falling_action',
    }
    
    freytag_section = macro_to_freytag.get(macro_focus, macro_focus.lower().replace(' ', '_'))
    week_focus = week_package.get('week_focus', macro_focus)
    reading_range = week_package.get('reading_range', 'TBD')
    activity_chapter = week_package.get('activity_chapter', 'TBD')
    micro_devices = week_package.get('micro_devices', [])
    
    overall_thesis = extract_overall_thesis(reasoning_doc_path)
    if not overall_thesis:
        overall_thesis = f"{title} explores central themes through its narrative structure and literary devices."
    
    narrative_voice = extract_macro_summary(reasoning_doc_path, "voice")
    if narrative_voice == "Not available":
        narrative_voice = extract_macro_from_kernel(kernel, "voice")
    
    structure = extract_macro_summary(reasoning_doc_path, "structure")
    if structure == "Not available":
        structure = extract_macro_from_kernel(kernel, "structure")
    
    rhetoric = extract_macro_summary(reasoning_doc_path, "rhetoric")
    if rhetoric == "Not available":
        rhetoric = extract_macro_from_kernel(kernel, "rhetoric")
    
    dramatic_purpose = generate_dramatic_purpose(
        freytag_section,
        reading_range,
        week_focus,
        reasoning_doc_path,
        kernel
    )
    
    thematic_connections = generate_thematic_connections(
        freytag_section,
        micro_devices,
        reasoning_doc_path
    )
    
    what_to_notice = generate_what_to_notice(
        micro_devices,
        freytag_section,
        week_focus
    )
    
    freytag_display = freytag_section.capitalize() if freytag_section else "Exposition"
    
    section = f"""## PART A: THESIS ALIGNMENT

**Purpose:** Understand how this week's focus connects to the text's overall meaning

### The Text's Overall Thesis

{overall_thesis}

**Key Elements:**

- **Narrative Voice:** {narrative_voice}
- **Structure:** {structure}
- **Rhetorical Strategy:** {rhetoric}

### This Week's Role in the Thesis

**Chapter Function:** {freytag_display}

**Dramatic Purpose:** {dramatic_purpose}

**Thematic Connection:**

"""
    
    for connection in thematic_connections:
        section += f"- {connection}\n"
    
    section += f"""
**What to Notice:**

"""
    
    for i, notice in enumerate(what_to_notice, 1):
        section += f"{i}. {notice}\n"
    
    return section

def generate_instructions_section(week_package, kernel):
    """Generate Instructions section with reading context"""
    
    title = week_package.get('text_title', 'Unknown')
    reading_range = week_package.get('reading_range', 'TBD')
    activity_chapter = week_package.get('activity_chapter', 'TBD')
    
    edition = "2003 edition"
    if kernel and 'metadata' in kernel:
        edition = kernel['metadata'].get('edition', '2003 edition')
    
    instructions = f"""## INSTRUCTIONS FOR STUDENTS

This worksheet guides you through analyzing literary devices in *{title}*.

**Edition Note:** Page numbers refer to the {edition} edition. If you're using a different edition, chapter numbers will match but page numbers may vary slightly.

**Reading Assignment:** Chapters {reading_range}  
**Activity Focus:** Chapter {activity_chapter}

**How to use this worksheet:**

1. Read the Thesis Alignment section to understand the big picture
2. Read Chapters {reading_range} (focus on Chapter {activity_chapter} for activities)
3. Find examples of each device
4. Complete the activities in order
5. Use the examples to understand how devices work
"""
    
    return instructions

# ============================================================================
# WORKSHEET DATA EXTRACTION (PURE EXTRACTION - NO GENERATION)
# ============================================================================

def extract_worksheet_data_from_stage1b(device, macro_focus, text_title, chapter_num):
    """Extract pre-generated worksheet content from Stage 1B."""
    
    ws = device.get('worksheet_content', {})
    tvode = device.get('tvode_components', {})
    effects = device.get('effects', [])
    examples = device.get('examples', [])
    
    primary_example = examples[0] if examples else {}
    
    # Get MC options
    mc_options = ws.get('mc_options', {})
    
    # Get sequencing steps
    seq_steps = ws.get('sequencing_steps', {})
    
    # Extract effects (up to 6)
    effect_list = []
    for i, effect_item in enumerate(effects[:6]):
        if isinstance(effect_item, dict):
            effect_list.append(effect_item.get('text', ''))
        else:
            effect_list.append(str(effect_item))
    
    # Pad to 6 if needed
    while len(effect_list) < 6:
        effect_list.append('')
    
    return {
        # Multiple Choice
        "mc_question": ws.get('mc_question', f"What does {device.get('name', 'device')} DO in this text?"),
        "mc_option_a": mc_options.get('A', ''),
        "mc_option_b": mc_options.get('B', ''),
        "mc_option_c": mc_options.get('C', ''),
        "mc_option_d": mc_options.get('D', ''),
        "mc_correct": ws.get('mc_correct', ''),
        
        # Sequencing
        "seq_step_1": seq_steps.get('step_1', ''),
        "seq_step_2": seq_steps.get('step_2', ''),
        "seq_step_3": seq_steps.get('step_3', ''),
        "seq_order": ws.get('sequencing_order', ''),
        
        # Device info
        "definition": device.get('definition', ''),
        "model_example": primary_example.get('quote_snippet', primary_example.get('text', '')),
        "location_hint": ws.get('location_hint', ''),
        "detail_sample": ws.get('detail_sample', ''),
        
        # Effects (6 total)
        "effect_1": effect_list[0],
        "effect_2": effect_list[1],
        "effect_3": effect_list[2],
        "effect_4": effect_list[3],
        "effect_5": effect_list[4],
        "effect_6": effect_list[5],
    }

# ============================================================================
# TEMPLATE FILLING
# ============================================================================

def fill_worksheet_template(template, week_package, enriched_devices, thesis_alignment, instructions, stage1b_source=None):
    """Fill worksheet template with extracted data"""
    
    output = template
    
    # Update version in header (replace any v2.2 references with v6.0)
    output = output.replace("v2.2", "v6.0")
    output = output.replace("Device Recognition v2.2", "Device Recognition v6.0")
    if "# LITERARY ANALYSIS WORKSHEET" in output and "v6.0" not in output[:100]:
        # Ensure header has v6.0
        output = output.replace("# LITERARY ANALYSIS WORKSHEET - Device Recognition", "# LITERARY ANALYSIS WORKSHEET - Device Recognition v6.0")
    
    # Fill metadata
    output = output.replace("{{TEXT_TITLE}}", week_package.get('text_title', 'Unknown'))
    output = output.replace("{{TEXT_AUTHOR}}", week_package.get('text_author', 'Unknown'))
    output = output.replace("{{EDITION_REFERENCE}}", "2003 edition")
    output = output.replace("{{EXTRACT_FOCUS}}", week_package.get('macro_focus', ''))
    output = output.replace("{{YEAR_LEVEL}}", "9-10")
    output = output.replace("{{PROFICIENCY_TIER}}", "Standard")
    
    # Add version metadata after metadata section
    version_metadata = f"""
**Generated:** {datetime.now().strftime('%Y-%m-%d')}
**Pipeline Version:** 6.0
**Source:** {stage1b_source if stage1b_source else 'Stage 1B output'}

"""
    
    # Insert version metadata after scaffolding configuration
    if "**Scaffolding Configuration:**" in output:
        config_end = output.find("---", output.find("**Scaffolding Configuration:**"))
        if config_end != -1:
            insert_point = output.find("\n", config_end) + 1
            output = output[:insert_point] + version_metadata + output[insert_point:]
    elif "## METADATA SECTION" in output:
        # Fallback: insert after metadata section
        metadata_end = output.find("---", output.find("## METADATA SECTION"))
        if metadata_end != -1:
            insert_point = output.find("\n", metadata_end) + 1
            output = output[:insert_point] + version_metadata + output[insert_point:]
    
    # Insert thesis alignment section (after metadata, before old instructions)
    metadata_section_end = output.find("---", output.find("## METADATA SECTION"))
    
    if metadata_section_end != -1:
        insert_point = output.find("\n", metadata_section_end) + 1
        old_instructions_start = output.find("## INSTRUCTIONS FOR STUDENTS")
        old_instructions_end = output.find("## ENTRY ACTIVITY", old_instructions_start)
        
        if old_instructions_start != -1 and old_instructions_end != -1:
            output = (output[:insert_point] + 
                      thesis_alignment + "\n\n---\n\n" + 
                      instructions + "\n\n---\n\n" + 
                      output[old_instructions_end:])
        else:
            output = (output[:insert_point] + 
                      thesis_alignment + "\n\n---\n\n" + 
                      instructions + "\n\n---\n\n" + 
                      output[insert_point:])
    else:
        first_separator = output.find("---")
        if first_separator != -1:
            insert_point = output.find("\n", first_separator) + 1
            output = (output[:insert_point] + 
                      thesis_alignment + "\n\n---\n\n" + 
                      instructions + "\n\n---\n\n" + 
                      output[insert_point:])
    
    # Fill device data
    for i, (device, enriched) in enumerate(zip(week_package['micro_devices'][:3], enriched_devices), 1):
        if enriched is None:
            continue
        
        # Basic device info
        output = output.replace(f"{{{{DEVICE_{i}_NAME}}}}", device['name'])
        output = output.replace(f"{{{{DEVICE_{i}_DEFINITION}}}}", enriched.get('definition', ''))
        
        # Multiple choice
        output = output.replace(f"{{{{DEVICE_{i}_OPTION_A}}}}", enriched.get('mc_option_a', ''))
        output = output.replace(f"{{{{DEVICE_{i}_OPTION_B}}}}", enriched.get('mc_option_b', ''))
        output = output.replace(f"{{{{DEVICE_{i}_OPTION_C}}}}", enriched.get('mc_option_c', ''))
        output = output.replace(f"{{{{DEVICE_{i}_OPTION_D}}}}", enriched.get('mc_option_d', ''))
        
        # Sequencing
        output = output.replace(f"{{{{DEVICE_{i}_SEQUENCE_STEP_RANDOMIZED_1}}}}", enriched.get('seq_step_1', ''))
        output = output.replace(f"{{{{DEVICE_{i}_SEQUENCE_STEP_RANDOMIZED_2}}}}", enriched.get('seq_step_2', ''))
        output = output.replace(f"{{{{DEVICE_{i}_SEQUENCE_STEP_RANDOMIZED_3}}}}", enriched.get('seq_step_3', ''))
        output = output.replace(f"{{{{DEVICE_{i}_SEQUENCE_CORRECT_ORDER}}}}", "")
        
        # Effects
        output = output.replace(f"{{{{DEVICE_{i}_EFFECT_1_SIMPLIFIED}}}}", enriched.get('effect_1', ''))
        output = output.replace(f"{{{{DEVICE_{i}_EFFECT_2_SIMPLIFIED}}}}", enriched.get('effect_2', ''))
        output = output.replace(f"{{{{DEVICE_{i}_EFFECT_3_SIMPLIFIED}}}}", enriched.get('effect_3', ''))
        output = output.replace(f"{{{{DEVICE_{i}_EFFECT_4_SIMPLIFIED}}}}", enriched.get('effect_4', ''))
        output = output.replace(f"{{{{DEVICE_{i}_EFFECT_5_SIMPLIFIED}}}}", enriched.get('effect_5', ''))
        output = output.replace(f"{{{{DEVICE_{i}_EFFECT_6_SIMPLIFIED}}}}", enriched.get('effect_6', ''))
        
        # Examples
        output = output.replace(f"{{{{DEVICE_{i}_MODEL_EXAMPLE}}}}", enriched.get('model_example', ''))
        output = output.replace(f"{{{{DEVICE_{i}_EXAMPLE_LOCATIONS}}}}", enriched.get('location_hint', ''))
    
    return output

def fill_teacher_key_template(template, week_package, enriched_devices, thesis_alignment, instructions):
    """Fill teacher key template with extracted data"""
    
    output = template
    
    # Fill metadata
    output = output.replace("{{TEXT_TITLE}}", week_package.get('text_title', 'Unknown'))
    output = output.replace("{{TEXT_AUTHOR}}", week_package.get('text_author', 'Unknown'))
    output = output.replace("{{WEEK_NUMBER}}", str(week_package.get('week', '')))
    output = output.replace("{{WEEK_FOCUS}}", week_package.get('macro_focus', ''))
    output = output.replace("{{EDITION_REFERENCE}}", "2003 edition")
    output = output.replace("{{EXTRACT_FOCUS}}", week_package.get('macro_focus', ''))
    output = output.replace("{{YEAR_LEVEL}}", "9-10")
    output = output.replace("{{PROFICIENCY_TIER}}", "Standard")
    
    # Fill device data
    for i, (device, enriched) in enumerate(zip(week_package['micro_devices'][:3], enriched_devices), 1):
        if enriched is None:
            continue
        
        # Basic info
        output = output.replace(f"{{{{DEVICE_{i}_NAME}}}}", device['name'])
        output = output.replace(f"{{{{DEVICE_{i}_DEFINITION}}}}", enriched.get('definition', ''))
        
        # Multiple choice with answers
        output = output.replace(f"{{{{DEVICE_{i}_OPTION_A}}}}", enriched.get('mc_option_a', ''))
        output = output.replace(f"{{{{DEVICE_{i}_OPTION_B}}}}", enriched.get('mc_option_b', ''))
        output = output.replace(f"{{{{DEVICE_{i}_OPTION_C}}}}", enriched.get('mc_option_c', ''))
        output = output.replace(f"{{{{DEVICE_{i}_OPTION_D}}}}", enriched.get('mc_option_d', ''))
        output = output.replace(f"{{{{DEVICE_{i}_CORRECT_OPTION}}}}", enriched.get('mc_correct', ''))
        
        # Sequencing with answer
        output = output.replace(f"{{{{DEVICE_{i}_SEQUENCE_STEP_RANDOMIZED_1}}}}", enriched.get('seq_step_1', ''))
        output = output.replace(f"{{{{DEVICE_{i}_SEQUENCE_STEP_RANDOMIZED_2}}}}", enriched.get('seq_step_2', ''))
        output = output.replace(f"{{{{DEVICE_{i}_SEQUENCE_STEP_RANDOMIZED_3}}}}", enriched.get('seq_step_3', ''))
        output = output.replace(f"{{{{DEVICE_{i}_SEQUENCE_ANSWER}}}}", enriched.get('seq_order', ''))
        output = output.replace(f"{{{{DEVICE_{i}_SEQUENCE_CORRECT_ORDER}}}}", f"**Correct Answer:** {enriched.get('seq_order', '')}")
        
        # Effects
        output = output.replace(f"{{{{DEVICE_{i}_EFFECT_1_SIMPLIFIED}}}}", enriched.get('effect_1', ''))
        output = output.replace(f"{{{{DEVICE_{i}_EFFECT_2_SIMPLIFIED}}}}", enriched.get('effect_2', ''))
        output = output.replace(f"{{{{DEVICE_{i}_EFFECT_3_SIMPLIFIED}}}}", enriched.get('effect_3', ''))
        output = output.replace(f"{{{{DEVICE_{i}_EFFECT_4_SIMPLIFIED}}}}", enriched.get('effect_4', ''))
        output = output.replace(f"{{{{DEVICE_{i}_EFFECT_5_SIMPLIFIED}}}}", enriched.get('effect_5', ''))
        output = output.replace(f"{{{{DEVICE_{i}_EFFECT_6_SIMPLIFIED}}}}", enriched.get('effect_6', ''))
        
        # Examples
        output = output.replace(f"{{{{DEVICE_{i}_MODEL_EXAMPLE}}}}", enriched.get('model_example', ''))
        output = output.replace(f"{{{{DEVICE_{i}_EXAMPLE_LOCATIONS}}}}", enriched.get('location_hint', ''))
        output = output.replace(f"{{{{DEVICE_{i}_DETAIL_SAMPLE}}}}", enriched.get('detail_sample', ''))
    
    return output

# ============================================================================
# MAIN PROCESSING
# ============================================================================

def process_week(week_package, template_dir, output_dir, stage1b_source=None):
    """Process one week: extract data from Stage 1B and fill templates"""
    
    week_num = week_package['week']
    macro_focus = week_package['macro_focus']
    activity_chapter = week_package.get('activity_chapter', 'TBD')
    
    print(f"\n📝 Processing Week {week_num}: {macro_focus}")
    print(f"   Activity Chapter: {activity_chapter}")
    print(f"   Devices: {len(week_package['micro_devices'])}")
    
    # Load kernel and reasoning doc for thesis alignment
    title = week_package.get('text_title', 'Book')
    print(f"\n📚 Loading kernel and reasoning doc for thesis alignment...")
    
    kernel_path = find_kernel_path(title)
    kernel = None
    if kernel_path:
        print(f"   ✓ Found kernel: {kernel_path.name}")
        with open(kernel_path, 'r', encoding='utf-8') as f:
            kernel = json.load(f)
    else:
        print(f"   ⚠ No kernel found for {title}")
    
    reasoning_doc_path = find_reasoning_doc_path(title)
    if reasoning_doc_path:
        print(f"   ✓ Found reasoning doc: {reasoning_doc_path.name}")
    else:
        print(f"   ⚠ No reasoning doc found for {title}")
    
    # Extract worksheet data from Stage 1B (PURE EXTRACTION)
    print(f"\n📊 Extracting worksheet data from Stage 1B...")
    enriched_devices = []
    
    for device in week_package['micro_devices'][:3]:
        print(f"   - {device['name']}...", end='', flush=True)
        enriched = extract_worksheet_data_from_stage1b(
            device, 
            macro_focus, 
            title,
            activity_chapter
        )
        enriched_devices.append(enriched)
        print(" ✓")
    
    # Generate thesis alignment section
    print(f"\n📝 Generating thesis alignment section...")
    thesis_alignment = generate_thesis_alignment_section(week_package, kernel, reasoning_doc_path)
    instructions = generate_instructions_section(week_package, kernel)
    
    # Load templates
    print(f"\n📄 Filling templates...")
    worksheet_template = load_template(template_dir / "Template_Literary_Analysis_6Step.md")
    teacher_key_template = load_template(template_dir / "Template_Teacher_Key.md")
    
    # Fill templates
    worksheet = fill_worksheet_template(worksheet_template, week_package, enriched_devices, thesis_alignment, instructions, stage1b_source)
    teacher_key = fill_teacher_key_template(teacher_key_template, week_package, enriched_devices, thesis_alignment, instructions)
    
    # Save outputs
    output_dir.mkdir(parents=True, exist_ok=True)
    
    title_safe = week_package.get('text_title', 'Book').replace(' ', '_')
    
    worksheet_path = output_dir / f"{title_safe}_Week{week_num}_Worksheet_v6_0.md"
    teacher_key_path = output_dir / f"{title_safe}_Week{week_num}_TeacherKey_v6_0.md"
    
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
    
    print("\n" + "="*80)
    print("STAGE 2: PURE EXTRACTION FROM STAGE 1B")
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
    
    # Get source filename for version metadata
    stage1b_source = stage1b_path.name
    
    # Process weeks
    week_packages = stage1b['week_packages']
    
    if all_weeks:
        print(f"\n📚 Generating worksheets for all {len(week_packages)} weeks...")
        generated_files = []
        
        for week_package in week_packages:
            files = process_week(week_package, template_dir, output_dir, stage1b_source)
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
        worksheet_path, teacher_key_path = process_week(week_package, template_dir, output_dir, stage1b_source)
        
        print("\n" + "="*80)
        print("✅ STAGE 2 COMPLETE!")
        print("="*80)
        print(f"\nGenerated files:")
        print(f"  - {worksheet_path}")
        print(f"  - {teacher_key_path}")
    
    print(f"\n📂 All worksheets saved to: {output_dir}")
    print(f"\n💰 API cost: $0.00 (pure extraction, no generation)")

if __name__ == "__main__":
    main()
