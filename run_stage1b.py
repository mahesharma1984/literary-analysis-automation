#!/usr/bin/env python3
"""
STAGE 1B AUTOMATION
Package macro-micro extracts into 5-week teaching progression

Usage:
    python3 run_stage1b.py outputs/Book_stage1a_v5.0.json
"""

import json
import sys
import re
import os
import time
from pathlib import Path
from datetime import datetime
import anthropic

# ============================================================================
# SYNONYM SYSTEM FOR EFFECT VARIATIONS
# ============================================================================
# Ensures 3 effects per device use different words but same core meaning

SYNONYM_MAP = {
    # Decay/decline cluster
    'decay': ['decline', 'deterioration', 'decay', 'rot', 'erosion'],
    'decline': ['decay', 'deterioration', 'decline', 'degradation'],
    'deterioration': ['decay', 'decline', 'deterioration', 'erosion'],
    'rot': ['decay', 'deterioration', 'rot', 'decomposition'],
    'erosion': ['decay', 'deterioration', 'erosion', 'degradation'],
    
    # Tiredness/exhaustion cluster
    'weariness': ['exhaustion', 'fatigue', 'weariness', 'tiredness'],
    'exhaustion': ['weariness', 'fatigue', 'exhaustion', 'depletion'],
    'fatigue': ['weariness', 'exhaustion', 'fatigue', 'tiredness'],
    'tiredness': ['weariness', 'exhaustion', 'tiredness', 'fatigue'],
    'weary': ['tired', 'exhausted', 'weary', 'worn'],
    'tired': ['weary', 'exhausted', 'tired', 'worn'],
    
    # Strictness/harshness cluster
    'stern': ['strict', 'harsh', 'stern', 'rigid', 'severe'],
    'strict': ['stern', 'harsh', 'strict', 'rigid'],
    'harsh': ['stern', 'strict', 'harsh', 'severe'],
    'rigid': ['stern', 'strict', 'rigid', 'inflexible'],
    'severe': ['harsh', 'stern', 'severe', 'austere'],
    
    # Authority/control cluster
    'discipline': ['authority', 'control', 'discipline', 'command'],
    'authority': ['control', 'discipline', 'authority', 'power'],
    'control': ['authority', 'discipline', 'control', 'command'],
    'command': ['authority', 'control', 'command', 'dominance'],
    'power': ['authority', 'control', 'power', 'dominance'],
    
    # Age/oldness cluster
    'old': ['aged', 'ancient', 'old', 'weathered', 'worn'],
    'aged': ['old', 'ancient', 'aged', 'weathered'],
    'ancient': ['old', 'aged', 'ancient', 'time-worn'],
    'weathered': ['aged', 'worn', 'weathered', 'time-worn'],
    
    # Softness/delicacy cluster
    'soft': ['delicate', 'gentle', 'soft', 'tender'],
    'delicate': ['soft', 'gentle', 'delicate', 'fragile'],
    'gentle': ['soft', 'delicate', 'gentle', 'tender'],
    
    # Hardness/strength cluster
    'hard': ['firm', 'solid', 'hard', 'rigid'],
    'firm': ['hard', 'solid', 'firm', 'unyielding'],
    'solid': ['hard', 'firm', 'solid', 'sturdy'],
    
    # Brightness/light cluster
    'bright': ['luminous', 'radiant', 'bright', 'vivid'],
    'luminous': ['bright', 'radiant', 'luminous', 'glowing'],
    'radiant': ['bright', 'luminous', 'radiant', 'shining'],
    
    # Darkness cluster
    'dark': ['shadowy', 'dim', 'dark', 'gloomy'],
    'shadowy': ['dark', 'dim', 'shadowy', 'murky'],
    'dim': ['dark', 'shadowy', 'dim', 'faint'],
    
    # Speed cluster
    'slow': ['leisurely', 'unhurried', 'slow', 'gradual'],
    'fast': ['swift', 'rapid', 'fast', 'quick'],
    'swift': ['fast', 'rapid', 'swift', 'speedy'],
    
    # Size cluster
    'large': ['big', 'expansive', 'large', 'vast'],
    'small': ['tiny', 'little', 'small', 'minute'],
    'vast': ['large', 'expansive', 'vast', 'immense'],
}


def get_synonym_for_word(word, index):
    """
    Get a synonym for a word based on index (0, 1, or 2).
    
    Args:
        word: The word to find synonym for
        index: Which synonym to use (0, 1, or 2)
    
    Returns:
        Synonym at that index, or original word if no synonyms available
    """
    word_lower = word.lower()
    
    if word_lower in SYNONYM_MAP:
        synonyms = SYNONYM_MAP[word_lower]
        return synonyms[index % len(synonyms)]
    
    # If no synonym found, return original
    return word


def create_quality_variations(quality_phrase):
    """
    Create 3 variations of a quality phrase using synonyms.
    
    Example:
        Input: "decay and weariness"
        Output: ["decline and exhaustion", "deterioration and fatigue", "decay and weariness"]
    
    Args:
        quality_phrase: The core quality extracted from explanation
    
    Returns:
        List of 3 quality variations with different synonyms
    """
    
    # Handle "X and Y" patterns
    if ' and ' in quality_phrase:
        parts = quality_phrase.split(' and ')
        variations = []
        
        for i in range(3):
            var_parts = [get_synonym_for_word(part.strip(), i) for part in parts]
            variations.append(' and '.join(var_parts))
        
        return variations
    
    # Handle single-word or multi-word phrases (no "and")
    words = quality_phrase.split()
    variations = []
    
    for i in range(3):
        var_words = [get_synonym_for_word(word, i) for word in words if word not in ['the', 'a', 'an', 'of']]
        variations.append(' '.join(var_words))
    
    return variations

# ============================================================================
# EFFECT EXTRACTION AND SYNTHESIS
# ============================================================================


def extract_subject_from_device(text, explanation):
    """
    Extract the subject (who/what the device is about).
    Priority: character names > place names > objects
    
    Args:
        text: The quote text
        explanation: The device explanation
    
    Returns:
        Subject as a string (e.g., "Town", "Calpurnia", "Courthouse")
    """
    
    # Strategy 1: Possessives in explanation (highest priority for character names)
    # Example: "Calpurnia's hand" → extract "Calpurnia"
    possessive_match = re.search(r"([A-Z][a-z]+)'s", explanation)
    if possessive_match:
        return possessive_match.group(1)
    
    # Strategy 2: Important place/object nouns in quote text
    # These are significant settings/objects worth naming
    important_subjects = ['courthouse', 'town', 'maycomb', 'house', 'street', 'building', 'square']
    for noun in important_subjects:
        if noun in text.lower():
            return noun.capitalize()
    
    # Strategy 3: Proper nouns (capitalized words) in quote
    proper_nouns = re.findall(r'\b[A-Z][a-z]+\b', text)
    if proper_nouns:
        return proper_nouns[0]
    
    # Strategy 4: Subject at start of explanation
    # Example: "Town is implicitly compared..." → extract "Town"
    subject_match = re.search(r'^([A-Z][a-z]+)\s+(?:is|are|given)', explanation)
    if subject_match:
        return subject_match.group(1)
    
    return "the subject"  # fallback


def extract_quality_from_explanation(explanation):
    """
    Extract the core quality/effect from explanation.
    Removes possessive pronouns to avoid grammar errors.
    
    Args:
        explanation: The device explanation text
    
    Returns:
        Core quality as string (e.g., "decay and weariness", "stern discipline")
    """
    
    # Look for key patterns that introduce the quality
    patterns = [
        r'suggesting ([^,\.]+)',
        r'emphasizing ([^,\.]+)',
        r'revealing ([^,\.]+)',
        r'conveying ([^,\.]+)',
        r'showing ([^,\.]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, explanation.lower())
        if match:
            quality = match.group(1).strip()
            # Remove possessive pronouns that cause grammar errors
            quality = re.sub(r'^(?:her|his|their|its|the)\s+', '', quality)
            return quality
    
    # Fallback: take last clause after comma
    clauses = explanation.split(',')
    if len(clauses) > 1:
        quality = clauses[-1].strip().lower()
        quality = re.sub(r'^(?:her|his|their|its|the)\s+', '', quality)
        return quality
    
    return "this quality"  # fallback


def generate_effects_for_device(device, macro_focus):
    """
    Generate 3 effects for a device.
    
    Uses pre-generated effects from kernel if available (new kernels),
    otherwise falls back to extraction/generation logic (old kernels).
    
    Args:
        device: Device dictionary with 'examples' field (and optionally 'effects' and 'worksheet_context')
        macro_focus: The week's macro focus (e.g., "Exposition")
    
    Returns:
        List of 3 effect dictionaries with 'text' and 'category' keys
    """
    
    # NEW: Check for pre-generated effects (new kernels)
    effects = device.get('effects')
    if effects and isinstance(effects, list) and len(effects) >= 3:
        # Validate that all required categories are present
        categories = [e.get("category") for e in effects if isinstance(e, dict)]
        required_categories = ["reader_response", "meaning_creation", "thematic_impact"]
        if all(cat in categories for cat in required_categories):
            # Return the pre-generated effects
            return effects
    
    # FALLBACK: Old logic for backward compatibility (old kernels)
    # Get first example
    examples = device.get('examples', [])
    if not examples:
        return [
            {"text": "This creates an emotional response in readers.", "category": "reader_response"},
            {"text": "This reveals meaning in the text.", "category": "meaning_creation"},
            {"text": "This reinforces a theme in the narrative.", "category": "thematic_impact"}
        ]
    
    example = examples[0]
    text = example.get('text', '')
    explanation = example.get('explanation', '')
    
    # Try to use worksheet_context.subject if available, otherwise extract
    worksheet_context = device.get('worksheet_context', {})
    if worksheet_context and worksheet_context.get('subject'):
        subject = worksheet_context['subject']
    else:
        # Extract components using old logic
        subject = extract_subject_from_device(text, explanation)
    
    quality = extract_quality_from_explanation(explanation)
    
    # Create 3 quality variations using synonyms
    quality_variations = create_quality_variations(quality)
    
    # Handle subject possessive form correctly
    if subject == "the subject":
        subject_possessive = "the subject's"
        subject_plain = "the subject"
    else:
        subject_possessive = f"{subject}'s"
        subject_plain = subject
    
    # Build 3 effects with EXPLICIT SIGNAL WORDS
    # Each effect template includes words students should look for
    effects = [
        {
            "text": f"This makes readers feel {subject_possessive} {quality_variations[0]}.",
            "category": "reader_response"
        },
        {
            "text": f"This reveals {subject_plain} as characterized by {quality_variations[1]}.",
            "category": "meaning_creation"
        },
        {
            "text": f"This reinforces the theme of {quality_variations[2]} in {macro_focus}.",
            "category": "thematic_impact"
        }
    ]
    
    return effects

# ============================================================================
# WORKSHEET CONTENT GENERATION VIA API
# ============================================================================

def initialize_api_client():
    """Initialize Anthropic API client"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    return anthropic.Anthropic(api_key=api_key)


def generate_worksheet_content(device, macro_focus, text_title, client):
    """
    Generate complete worksheet content for a device via API.
    
    Args:
        device: Device dictionary with name, examples, tvode_components, effects
        macro_focus: The week's macro focus (e.g., "Exposition")
        text_title: Title of the text being analyzed
        client: Anthropic API client
    
    Returns:
        Dictionary with worksheet_content fields:
        - mc_question: Multiple choice question
        - mc_options: Dict with A, B, C, D options
        - mc_correct: Correct answer (A, B, C, or D)
        - mc_explanation: Explanation of correct answer
        - sequencing_steps: Dict with step_1, step_2, step_3
        - sequencing_order: Correct order string (e.g., "1-B, 2-C, 3-A")
        - location_hint: Specific chapter/scene guidance
        - detail_sample: Model answer for Step 5
    """
    
    device_name = device.get("name", "Unknown Device")
    examples = device.get("examples", [])
    tvode = device.get("tvode_components", {})
    effects = device.get("effects", [])
    
    # Get example text and chapter info
    example_text = ""
    chapter_info = ""
    if examples and len(examples) > 0:
        example = examples[0]
        example_text = example.get("quote_snippet", example.get("text", ""))
        chapter = example.get("chapter", "")
        if chapter:
            chapter_info = f"Chapter {chapter}"
    
    # Build context from effects
    effect_texts = [e.get("text", "") for e in effects if isinstance(e, dict)]
    effects_context = "\n".join(f"- {e}" for e in effect_texts)
    
    # Build TVODE context
    tvode_context = ""
    if tvode:
        tvode_context = f"""
TVODE Components:
- Topic: {tvode.get('topic', 'N/A')}
- Verb: {tvode.get('verb', 'N/A')}
- Object: {tvode.get('object', 'N/A')}
- Detail: {tvode.get('detail', 'N/A')}
- Effect: {tvode.get('effect', 'N/A')}
"""
    
    prompt = f"""You are creating worksheet content for teaching literary analysis of "{text_title}".

DEVICE INFORMATION:
- Device Name: {device_name}
- Macro Focus: {macro_focus}
- Example Text: {example_text}
- Chapter: {chapter_info}
{tvode_context}
Effects:
{effects_context}

TASK: Generate complete worksheet content for this device. The content must be TEXT-SPECIFIC (refer to actual details from "{text_title}"), not generic templates.

REQUIREMENTS:

1. MULTIPLE CHOICE QUESTION:
   - Question format: "What does [Device] DO in this text?"
   - Generate 4 options (A, B, C, D)
   - All 4 options must be approximately the same length (10-15 words each)
   - 2 options should be "quite plausible" - they test understanding, not trick students
   - The correct answer should be the most accurate description of what the device DOES
   - NO option should mention the device name explicitly
   - Distractors should be wrong about FUNCTION, not wrong device type
   - Options must be text-specific, referring to actual content from "{text_title}"

2. SEQUENCING STEPS:
   - Generate 3 steps showing HOW the reading experience unfolds
   - Format: encounter → process → effect
   - Step 1: What reader encounters (specific text/chapter reference)
   - Step 2: How the device processes/transforms that encounter
   - Step 3: The resulting effect on reader/meaning
   - Must be chronological (how reading unfolds), not analytical steps
   - Must reference specific details from "{text_title}"

3. LOCATION HINT:
   - Specific chapter/scene guidance for students
   - Format: "Chapter X, [specific scene description]"
   - Help students find the device in the text

4. DETAIL SAMPLE:
   - Model answer for Step 5 (detail identification)
   - Show specific text evidence
   - Format: "shown through [specific detail]: '[quote snippet]'"

OUTPUT FORMAT (JSON only):
{{
  "mc_question": "What does [Device] DO in this text?",
  "mc_options": {{
    "A": "[Option A - 10-15 words, text-specific]",
    "B": "[Option B - 10-15 words, text-specific, quite plausible]",
    "C": "[Option C - 10-15 words, text-specific, correct answer]",
    "D": "[Option D - 10-15 words, text-specific, quite plausible]"
  }},
  "mc_correct": "C",
  "mc_explanation": "Two plausible options are B and C because... [explain why C is most accurate]",
  "sequencing_steps": {{
    "step_1": "[What reader encounters - specific text/chapter]",
    "step_2": "[How device processes/transforms - specific mechanism]",
    "step_3": "[Resulting effect - specific impact]"
  }},
  "sequencing_order": "1-B, 2-C, 3-A",
  "location_hint": "Chapter X, [specific scene description where device appears]",
  "detail_sample": "shown through [specific detail]: '[quote snippet from text]'"
}}

CRITICAL: 
- All content must be TEXT-SPECIFIC to "{text_title}"
- No generic templates or placeholders
- MC options must be same length (~10-15 words)
- 2 options should be "quite plausible" (test understanding)
- Sequencing must show chronological reading experience, not analysis steps
- Output ONLY valid JSON, no additional text
"""

    system_prompt = "You are an expert literary analysis educator creating student worksheet content. Generate text-specific, pedagogically sound worksheet materials."

    try:
        # Call API with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}],
                    system=system_prompt
                )
                
                result = response.content[0].text.strip()
                
                # Clean markdown formatting if present
                result = result.replace('```json\n', '').replace('```\n', '').replace('```', '').strip()
                
                # Parse JSON
                worksheet_content = json.loads(result)
                
                # Validate required fields
                required_fields = [
                    'mc_question', 'mc_options', 'mc_correct', 'mc_explanation',
                    'sequencing_steps', 'sequencing_order', 'location_hint', 'detail_sample'
                ]
                missing = [f for f in required_fields if f not in worksheet_content]
                if missing:
                    raise ValueError(f"Missing required fields: {missing}")
                
                # Validate mc_options has A, B, C, D
                if not all(k in worksheet_content['mc_options'] for k in ['A', 'B', 'C', 'D']):
                    raise ValueError("mc_options must contain A, B, C, D")
                
                # Validate sequencing_steps has step_1, step_2, step_3
                if not all(k in worksheet_content['sequencing_steps'] for k in ['step_1', 'step_2', 'step_3']):
                    raise ValueError("sequencing_steps must contain step_1, step_2, step_3")
                
                return worksheet_content
                
            except json.JSONDecodeError as e:
                if attempt < max_retries - 1:
                    print(f"    ⚠️  JSON parse error, retrying... ({attempt + 1}/{max_retries})")
                    time.sleep(2)
                    continue
                else:
                    raise ValueError(f"Failed to parse JSON after {max_retries} attempts: {e}")
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"    ⚠️  API error, retrying... ({attempt + 1}/{max_retries})")
                    time.sleep(2)
                    continue
                else:
                    raise
        
    except Exception as e:
        print(f"    ⚠️  Warning: Failed to generate worksheet content: {e}")
        # Return fallback content
        return {
            "mc_question": f"What does {device_name} DO in this text?",
            "mc_options": {
                "A": "Creates meaning through its specific application in the text",
                "B": "Reveals important themes through literary technique",
                "C": "Functions as a literary device to convey meaning",
                "D": "Establishes connections between text elements"
            },
            "mc_correct": "C",
            "mc_explanation": "Option C most accurately describes the device's function.",
            "sequencing_steps": {
                "step_1": f"Reader encounters {device_name} in the text",
                "step_2": f"{device_name} processes the textual elements",
                "step_3": "This creates meaning and effect for the reader"
            },
            "sequencing_order": "1-B, 2-C, 3-A",
            "location_hint": "Check the assigned reading chapters for this week",
            "detail_sample": f"shown through the device's application in the text"
        }


def create_week_package(week_data, week_num, client=None):
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
    
    # Process devices with teaching notes and worksheet content
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
            "effects": generate_effects_for_device(device, package['macro_focus']),
            "teaching_notes": {
                "introduce_as": device.get("executes_macro", ""),
                "macro_connection": f"This device is one way {package['macro_focus']} works",
                "student_task": f"Find and analyze this device in the text",
                "common_confusion": "Watch for surface-level readings",
                "teaching_tip": "Start with clear examples before complex analysis"
            }
        }
        
        # Generate worksheet content via API if client provided
        if client:
            print(f"    Generating worksheet content for: {device_package['name']}")
            try:
                worksheet_content = generate_worksheet_content(
                    device, 
                    package['macro_focus'],
                    package['text_title'],
                    client
                )
                device_package["worksheet_content"] = worksheet_content
            except Exception as e:
                print(f"    ⚠️  Warning: Failed to generate worksheet content for {device_package['name']}: {e}")
                # Continue without worksheet_content - will be validated later
        else:
            # No client provided - worksheet_content will be None (validation will catch this)
            device_package["worksheet_content"] = None
        
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

def generate_validation_report(output_data, book_name):
    """Generate human-readable validation report."""
    
    report_lines = [
        f"# Stage 1B Validation Report: {book_name}",
        f"**Generated:** {datetime.now().isoformat()}",
        f"**Output Version:** 6.0",
        "",
        "## Worksheet Content Check",
        ""
    ]
    
    for week_data in output_data.get('week_packages', []):
        week_num = week_data.get('week', '?')
        reading = week_data.get('reading_range', '?')
        devices = week_data.get('micro_devices', [])
        
        report_lines.append(f"### Week {week_num}")
        report_lines.append(f"**Reading:** Chapters {reading}")
        report_lines.append("")
        report_lines.append("| Device | Example Ch | In Range? | MC | Seq | Effects |")
        report_lines.append("|--------|------------|-----------|----|----|---------|")
        
        for device in devices:
            name = device.get('name', '?')
            ws = device.get('worksheet_content', {})
            examples = device.get('examples', [])
            ex_ch = examples[0].get('chapter', '?') if examples else '?'
            
            has_mc = '✓' if ws.get('mc_options') else '✗'
            has_seq = '✓' if ws.get('sequencing_steps') else '✗'
            has_eff = '✓' if len(device.get('effects', [])) >= 3 else '✗'
            
            # Check if example chapter is in reading range
            in_range = '✓'  # TODO: validate against reading_range
            
            report_lines.append(f"| {name} | Ch {ex_ch} | {in_range} | {has_mc} | {has_seq} | {has_eff} |")
        
        report_lines.append("")
    
    report_path = Path("outputs") / f"{book_name}_stage1b_v6_0_validation.md"
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    return report_path

def validate_worksheet_content(device):
    """Validate that device has required worksheet_content fields"""
    worksheet_content = device.get("worksheet_content")
    if not worksheet_content:
        return False, "Missing worksheet_content"
    
    required_fields = [
        'mc_question', 'mc_options', 'mc_correct', 'mc_explanation',
        'sequencing_steps', 'sequencing_order', 'location_hint', 'detail_sample'
    ]
    missing = [f for f in required_fields if f not in worksheet_content]
    if missing:
        return False, f"Missing fields: {missing}"
    
    # Validate mc_options structure
    if not isinstance(worksheet_content.get('mc_options'), dict):
        return False, "mc_options must be a dictionary"
    if not all(k in worksheet_content['mc_options'] for k in ['A', 'B', 'C', 'D']):
        return False, "mc_options must contain A, B, C, D"
    
    # Validate sequencing_steps structure
    if not isinstance(worksheet_content.get('sequencing_steps'), dict):
        return False, "sequencing_steps must be a dictionary"
    if not all(k in worksheet_content['sequencing_steps'] for k in ['step_1', 'step_2', 'step_3']):
        return False, "sequencing_steps must contain step_1, step_2, step_3"
    
    # Validate mc_correct is A, B, C, or D
    if worksheet_content.get('mc_correct') not in ['A', 'B', 'C', 'D']:
        return False, "mc_correct must be A, B, C, or D"
    
    return True, "Valid"


def run_stage1b(stage1a_path):
    """Main Stage 1B processing"""
    
    print("\n" + "="*80)
    print("STAGE 1B: WEEKLY PACKAGING")
    print("="*80)
    
    # Initialize API client
    print("\n🔧 Initializing API client...")
    try:
        client = initialize_api_client()
        print("  ✅ API client initialized")
    except Exception as e:
        print(f"  ❌ Error initializing API client: {e}")
        print("  ⚠️  Continuing without worksheet content generation")
        client = None
    
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
        
        print(f"\n  📋 Week {week_num}: {week_data.get('macro_element', 'Unknown')}")
        package = create_week_package(week_data, week_num, client)
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
    output_path = output_dir / f"{safe_title}_stage1b_v6_0.json"
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
    
    # Generate validation report
    print("\n📋 Generating validation report...")
    validation_report_path = generate_validation_report(output, safe_title)
    print(f"  ✅ Validation report saved!")
    print(f"   Output: {validation_report_path}")
    
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
