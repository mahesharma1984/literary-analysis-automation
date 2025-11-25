#!/usr/bin/env python3
"""
STAGE 2 AUTOMATION - TEMPLATE-BASED EXTRACTION
Generate worksheets by extracting data from Stage 1B JSON using pedagogical templates
NO API CALLS - everything extracted programmatically from Stage 1B data

Usage:
    python3 run_stage2.py outputs/Book_stage1b_v5_0.json --week 1
    python3 run_stage2.py outputs/Book_stage1b_v5_0.json --all-weeks
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
import random
import re
from collections import Counter

# No configuration needed - Stage 2 extracts from Stage 1B data

# ============================================================================
# DEVICE TYPE CLASSIFICATION SYSTEM
# ============================================================================
# Maps specific devices to pedagogical categories for template selection

DEVICE_TYPE_MAP = {
    # Comparison devices
    'Metaphor': 'comparison',
    'Simile': 'comparison',
    'Extended Metaphor': 'comparison',
    
    # Human quality devices
    'Personification': 'human_quality',
    'Apostrophe': 'human_quality',
    
    # Sensory devices
    'Imagery': 'sensory',
    'Synesthesia': 'sensory',
    
    # Sound devices
    'Alliteration': 'sound',
    'Assonance': 'sound',
    'Consonance': 'sound',
    'Onomatopoeia': 'sound',
    
    # Representational devices
    'Symbolism': 'representation',
    'Allegory': 'representation',
    'Motif': 'representation',
    
    # Structural devices
    'Juxtaposition': 'contrast',
    'Parallelism': 'pattern',
    'Repetition': 'pattern',
    
    # Exaggeration devices
    'Hyperbole': 'exaggeration',
    'Understatement': 'exaggeration'
}

def get_device_type(device_name):
    """Get pedagogical category for a device."""
    return DEVICE_TYPE_MAP.get(device_name, 'other')

# ============================================================================
# MULTIPLE CHOICE DISTRACTOR TEMPLATES
# ============================================================================
# Templates for generating wrong answers that test understanding, not device recognition

MC_DISTRACTOR_TEMPLATES = {
    'comparison': [
        {
            'pattern': 'Creates musical rhythm in the description of {subject}',
            'type': 'wrong_device_sound'
        },
        {
            'pattern': 'Uses {subject} as a symbol representing larger themes',
            'type': 'wrong_device_symbolism'
        },
        {
            'pattern': 'Directly states that {subject} is {quality} without comparison',
            'type': 'wrong_mechanism'
        }
    ],
    'human_quality': [
        {
            'pattern': 'Compares {subject} to something else through metaphor',
            'type': 'wrong_device_comparison'
        },
        {
            'pattern': 'Describes only the physical appearance of {subject}',
            'type': 'wrong_mechanism'
        },
        {
            'pattern': 'Uses {subject} as a symbol without giving it human traits',
            'type': 'wrong_device_symbolism'
        }
    ],
    'sensory': [
        {
            'pattern': 'Creates metaphor by comparing {subject} to something else',
            'type': 'wrong_device_comparison'
        },
        {
            'pattern': 'Gives {subject} human qualities or emotions',
            'type': 'wrong_device_personification'
        },
        {
            'pattern': 'Uses {subject} to symbolize abstract themes',
            'type': 'wrong_device_symbolism'
        }
    ],
    'sound': [
        {
            'pattern': 'Creates visual imagery of {subject}',
            'type': 'wrong_device_imagery'
        },
        {
            'pattern': 'Compares the sounds to something else metaphorically',
            'type': 'wrong_device_comparison'
        },
        {
            'pattern': 'Directly states the meaning without sound patterns',
            'type': 'wrong_mechanism'
        }
    ],
    'representation': [
        {
            'pattern': 'Compares {subject} directly to something else',
            'type': 'wrong_device_comparison'
        },
        {
            'pattern': 'Describes {subject} using sensory details only',
            'type': 'wrong_device_imagery'
        },
        {
            'pattern': 'Gives {subject} human qualities without symbolic meaning',
            'type': 'wrong_device_personification'
        }
    ],
    'contrast': [
        {
            'pattern': 'Shows similarity between {subject} and another element',
            'type': 'opposite_mechanism'
        },
        {
            'pattern': 'Uses {subject} as symbol for larger themes',
            'type': 'wrong_device_symbolism'
        },
        {
            'pattern': 'Creates sensory imagery of {subject}',
            'type': 'wrong_device_imagery'
        }
    ],
    'pattern': [
        {
            'pattern': 'Creates contrast between different elements',
            'type': 'wrong_device_contrast'
        },
        {
            'pattern': 'Uses {subject} symbolically without repetition',
            'type': 'wrong_device_symbolism'
        },
        {
            'pattern': 'Describes {subject} with sensory details',
            'type': 'wrong_device_imagery'
        }
    ],
    'exaggeration': [
        {
            'pattern': 'Describes {subject} accurately without exaggeration',
            'type': 'opposite_mechanism'
        },
        {
            'pattern': 'Compares {subject} to something else through metaphor',
            'type': 'wrong_device_comparison'
        },
        {
            'pattern': 'Uses {subject} as symbol representing themes',
            'type': 'wrong_device_symbolism'
        }
    ],
    'other': [
        {
            'pattern': 'Creates vivid sensory imagery',
            'type': 'generic_imagery'
        },
        {
            'pattern': 'Establishes symbolic meaning',
            'type': 'generic_symbolism'
        },
        {
            'pattern': 'Shows literal description without literary technique',
            'type': 'generic_literal'
        }
    ]
}

# ============================================================================
# CHRONOLOGICAL SEQUENCING TEMPLATES
# ============================================================================
# Shows HOW effect unfolds during reading (NOT how to analyze it)

SEQUENCING_TEMPLATES = {
    'comparison': [
        'Reader encounters "{quote}" in Chapter {chapter}',
        '{device_name} transfers {quality} from compared element to {subject}',
        'This establishes {subject} as defined by {quality} in {macro_focus}'
    ],
    'human_quality': [
        'Reader sees {subject} described as "{quote}" in Chapter {chapter}',
        '{device_name} attributes human {quality} to non-human {subject}',
        'This creates impression of {subject} as {quality} during {macro_focus}'
    ],
    'sensory': [
        'Reader experiences sensory language: "{quote}" in Chapter {chapter}',
        '{device_name} engages the senses to convey {quality}',
        'This immerses reader in {subject}\'s {quality} within {macro_focus}'
    ],
    'sound': [
        'Reader hears repeated sounds in "{quote}" from Chapter {chapter}',
        '{device_name} creates auditory pattern emphasizing {quality}',
        'This reinforces {subject}\'s {quality} through sound in {macro_focus}'
    ],
    'representation': [
        'Reader notices {subject} presented as "{quote}" in Chapter {chapter}',
        '{device_name} transforms {subject} into representation of {quality}',
        'This layers symbolic {quality} onto literal {subject} in {macro_focus}'
    ],
    'contrast': [
        'Reader observes {subject} juxtaposed in "{quote}" from Chapter {chapter}',
        '{device_name} highlights differences to emphasize {quality}',
        'This sharpens understanding of {subject}\'s {quality} through contrast in {macro_focus}'
    ],
    'pattern': [
        'Reader recognizes repeated element in "{quote}" from Chapter {chapter}',
        '{device_name} accumulates emphasis on {quality} through repetition',
        'This intensifies {subject}\'s {quality} via accumulated pattern in {macro_focus}'
    ],
    'exaggeration': [
        'Reader encounters exaggerated claim: "{quote}" in Chapter {chapter}',
        '{device_name} amplifies {quality} beyond literal reality',
        'This emphasizes {subject}\'s {quality} through deliberate distortion in {macro_focus}'
    ],
    'other': [
        'Reader encounters "{quote}" in Chapter {chapter}',
        '{device_name} emphasizes {quality} in the description',
        'This establishes {subject} through {quality} in {macro_focus}'
    ]
}

# ============================================================================
# EFFECT CATEGORIZATION SYSTEM
# ============================================================================

def categorize_effect(effect_text, explanation_text):
    """
    Categorize an effect into reader_response, meaning_creation, or thematic.
    """
    combined = (effect_text + " " + explanation_text).lower()
    
    # Reader Response: emotional/sensory/experiential
    reader_keywords = [
        'feel', 'sense', 'experience', 'atmosphere', 'mood',
        'evoke', 'immerse', 'draw', 'engage', 'visceral',
        'emotional', 'sensory', 'impression'
    ]
    
    # Thematic Impact: message/theme/larger meaning
    thematic_keywords = [
        'theme', 'reinforce', 'message', 'comment', 'critique',
        'reflect', 'larger', 'universal', 'connect to',
        'represents', 'symbolize', 'allegory'
    ]
    
    # Meaning Creation: reveals/shows/establishes (default)
    meaning_keywords = [
        'show', 'reveal', 'tell', 'establish', 'convey',
        'indicate', 'suggest', 'demonstrate', 'characterize',
        'describe', 'depict', 'portray'
    ]
    
    # Count keyword matches
    reader_score = sum(1 for kw in reader_keywords if kw in combined)
    thematic_score = sum(1 for kw in thematic_keywords if kw in combined)
    meaning_score = sum(1 for kw in meaning_keywords if kw in combined)
    
    # Return highest scoring category
    scores = {
        'reader_response': reader_score,
        'thematic': thematic_score,
        'meaning_creation': meaning_score
    }
    
    return max(scores, key=scores.get)

def build_effect_for_category(category, subject, effect_core, macro_focus):
    """Build a complete effect sentence for a specific category."""
    if category == 'reader_response':
        return f"Makes readers feel {subject}'s {effect_core}"
    elif category == 'meaning_creation':
        return f"Shows {subject} as {effect_core}"
    elif category == 'thematic':
        # Try to connect to larger themes
        theme_hints = {
            'decay': 'decline of tradition',
            'weariness': 'burden of history',
            'strict': 'rigid social order',
            'harsh': 'severity of justice'
        }
        theme = None
        for keyword, theme_phrase in theme_hints.items():
            if keyword in effect_core.lower():
                theme = theme_phrase
                break
        if theme:
            return f"Reinforces theme of {theme} in {macro_focus}"
        else:
            return f"Connects {subject}'s {effect_core} to larger themes in {macro_focus}"
    return f"Shows {subject} as {effect_core}"  # fallback

def simplify_effect(text):
    """Truncate effect to ~10 words"""
    if not text:
        return ''
    words = text.split()
    if len(words) <= 10:
        return text
    return ' '.join(words[:10]) + '...'

def load_template(template_path):
    """Load template file"""
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

# ============================================================================
# HELPER FUNCTIONS FOR EXTRACTION
# ============================================================================

def extract_subject_from_device(text, explanation):
    """Extract subject - PRIORITIZE QUOTE TEXT."""
    # Strategy 1: Common important nouns in quote (places/objects)
    important_subjects = ['courthouse', 'town', 'maycomb', 'house', 'street', 'building', 'square']
    for noun in important_subjects:
        if noun in text.lower():
            return noun.capitalize()
    
    # Strategy 2: Proper nouns in quote
    proper_nouns = re.findall(r'\b[A-Z][a-z]+\b', text)
    if proper_nouns:
        return proper_nouns[0]
    
    # Strategy 3: Possessives in explanation (character names)
    possessive_match = re.search(r"([A-Z][a-z]+)'s", explanation)
    if possessive_match:
        return possessive_match.group(1)
    
    # Strategy 4: Subject at start of explanation
    subject_match = re.search(r'^([A-Z][a-z]+)\s+(?:is|are|given)', explanation)
    if subject_match:
        return subject_match.group(1)
    
    return "the subject"

def extract_quality_from_explanation(explanation):
    """Extract core quality from explanation."""
    patterns = [
        r'suggesting ([^,\.]+)',
        r'emphasizing ([^,\.]+)',
        r'revealing ([^,\.]+)',
        r'conveying ([^,\.]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, explanation.lower())
        if match:
            quality = match.group(1).strip()
            # Remove possessives
            quality = re.sub(r'^(?:her|his|their|its|the)\s+', '', quality)
            return quality
    
    return "this quality"

def extract_comparison_target(explanation):
    """For comparison devices, extract what's being compared to what."""
    # Look for "compared to", "like", "as" patterns
    patterns = [
        r'compared to ([^,\.]+)',
        r'like ([^,\.]+)',
        r'as if ([^,\.]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, explanation.lower())
        if match:
            return match.group(1).strip()
    
    return "something else"

def build_multiple_choice(device_name, device_type, subject, quality, macro_focus):
    """Build MC with correct answer and 3 distractors."""
    # Correct answer (no device name)
    correct_answer = f"Shows {subject} as {quality}"
    
    # Get distractors for this device type
    distractor_templates = MC_DISTRACTOR_TEMPLATES.get(device_type, MC_DISTRACTOR_TEMPLATES['other'])
    
    # Build 3 distractors
    distractors = []
    for template in distractor_templates[:3]:
        distractor = template['pattern'].format(subject=subject, quality=quality)
        distractors.append(distractor)
    
    # Randomize order
    all_options = [correct_answer] + distractors
    random.shuffle(all_options)
    
    # Find correct letter
    correct_letter = chr(65 + all_options.index(correct_answer))
    
    return {
        'question': f"What does {device_name} DO in this text? What is its purpose or function?",
        'options': {
            'A': all_options[0],
            'B': all_options[1],
            'C': all_options[2],
            'D': all_options[3]
        },
        'correct': correct_letter
    }

def build_chronological_sequence(device_name, device_type, subject, quote, chapter, quality, macro_focus):
    """
    Build sequencing steps that show HOW EFFECT UNFOLDS during reading.
    NOT analytical steps - this is the READING EXPERIENCE.
    """
    # Get template for device type
    template = SEQUENCING_TEMPLATES.get(device_type, SEQUENCING_TEMPLATES['other'])
    
    # Truncate long quotes for display
    display_quote = quote[:60] + "..." if len(quote) > 60 else quote
    
    # Fill template with actual content
    steps = []
    for step_template in template:
        step = step_template.format(
            device_name=device_name,
            subject=subject,
            quote=display_quote,
            chapter=chapter,
            quality=quality,
            macro_focus=macro_focus
        )
        steps.append(step)
    
    return steps


def extract_worksheet_data_from_stage1b(device, macro_focus, text_title, chapter_num):
    """
    Extract ALL worksheet content from Stage 1B JSON.
    NO API CALLS - everything extracted from JSON.
    """
    
    device_name = device.get('device_name') or device.get('name', 'Unknown')
    device_type = get_device_type(device_name)
    definition = device.get('definition', '')
    
    # Get examples for the activity chapter
    examples = device.get('examples', [])
    # Handle both string and int chapter numbers
    chapter_examples = [ex for ex in examples if str(ex.get('chapter', '')) == str(chapter_num)]
    
    if not chapter_examples:
        chapter_examples = examples[:2]  # Fallback to first examples
    
    primary_example = chapter_examples[0] if chapter_examples else {}
    quote = primary_example.get('text', primary_example.get('quote_snippet', ''))
    explanation = primary_example.get('explanation', '')
    chapter = primary_example.get('chapter', chapter_num)
    
    # Safety check for empty quote
    if not quote and examples:
        quote = examples[0].get('text', examples[0].get('quote_snippet', ''))
    
    # Extract subject and quality using helper functions
    subject = extract_subject_from_device(quote, explanation)
    quality = extract_quality_from_explanation(explanation)
    
    # ========================================
    # MULTIPLE CHOICE - Using templates
    # ========================================
    
    mc_data = build_multiple_choice(device_name, device_type, subject, quality, macro_focus)
    
    # ========================================
    # CHRONOLOGICAL SEQUENCING - Reading experience
    # ========================================
    
    sequence_steps = build_chronological_sequence(
        device_name=device_name,
        device_type=device_type,
        subject=subject,
        quote=quote,
        chapter=chapter,
        quality=quality,
        macro_focus=macro_focus
    )
    
    # Return steps in correct order - randomization happens in template filling
    seq_data = {
        "item_a": sequence_steps[0] if len(sequence_steps) > 0 else "",
        "item_b": sequence_steps[1] if len(sequence_steps) > 1 else "",
        "item_c": sequence_steps[2] if len(sequence_steps) > 2 else "",
        "correct_order": "A, B, C",  # Will be recalculated after randomization
        "explanation": f"Students see how the effect builds up during reading: first encountering the text, then the device transfers meaning, then the effect is established"
    }
    
    # ========================================
    # EFFECTS - Extract directly from Stage 1B (RANDOMIZED ORDER)
    # ========================================
    
    effects = device.get('effects', [])
    
    # Extract effect texts from Stage 1B
    effect_list = []
    
    if len(effects) >= 6:
        # Extract text from effect objects (handle both dict and string formats)
        for effect_item in effects[:6]:
            if isinstance(effect_item, dict):
                effect_text = effect_item.get('text', str(effect_item))
            else:
                effect_text = str(effect_item)
            effect_list.append(effect_text)
    elif len(effects) >= 3:
        # Use available effects
        for effect_item in effects:
            if isinstance(effect_item, dict):
                effect_text = effect_item.get('text', str(effect_item))
            else:
                effect_text = str(effect_item)
            effect_list.append(effect_text)
        # Fill remaining with simple variations
        for i in range(len(effects), 6):
            effect_list.append(f"Effect {i+1} for {device_name}")
    else:
        # Fallback if effects missing
        for i in range(6):
            effect_list.append(f"Effect {i+1} for {device_name}")
    
    # RANDOMIZE ORDER so it's not obvious (not 1→Reader, 2→Meaning, 3→Thematic)
    randomized_effects = effect_list.copy()
    random.shuffle(randomized_effects)
    
    # Assign to placeholders (first 6 for Step 6)
    effects_data = {}
    for i in range(6):
        effects_data[f"effect_{i+1}_simplified"] = randomized_effects[i]
    
    # Also map to old format for compatibility (use original order for categorization)
    effects_data["reader"] = effect_list[0] if len(effect_list) > 0 else f"Creates sense of {quality} in {subject}"
    effects_data["reader2"] = effect_list[1] if len(effect_list) > 1 else f"Makes readers feel the {quality}"
    effects_data["meaning"] = effect_list[2] if len(effect_list) > 2 else f"Shows {subject} as {quality}"
    effects_data["character"] = effect_list[3] if len(effect_list) > 3 else f"Reveals Scout's view of {subject}"
    effects_data["theme"] = effect_list[4] if len(effect_list) > 4 else f"Reinforces themes of {quality}"
    effects_data["structure"] = effect_list[5] if len(effect_list) > 5 else f"Establishes {subject} as foundation for {macro_focus}"
    
    # ========================================
    # EXAMPLES & TEACHING
    # ========================================
    
    quote_display = quote if len(quote) <= 40 else quote[:37] + "..."
    
    examples_data = {
        "model_example": quote,
        "location_prompt": f"Chapter {chapter}, opening paragraphs describing {subject}",
        "sample_response": f"In Chapter {chapter}, the author uses {device_name.lower()} to describe {subject}",
        "detail_sample": f"shown through the description of {subject} as '{quote_display}'"
    }
    
    teaching_data = {
        "teaching_note": f"Guide students to see how {device_name.lower()} reveals {subject} as {quality} in {macro_focus}",
        "common_error_1": f"Students may identify {device_name.lower()} but miss what it reveals about {subject}",
        "common_error_2": f"Students may paraphrase '{quote_display}' without analyzing its effect",
        "scaffolding_tip": f"Point students to Chapter {chapter} and help them locate '{quote_display}' before analyzing"
    }
    
    return {
        "multiple_choice": mc_data,
        "sequencing": seq_data,
        "effects": effects_data,
        "examples": examples_data,
        "teaching": teaching_data
    }

def fill_worksheet_template(template, week_package, enriched_devices, randomization_states):
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
            # New structure uses 'options' dict
            if 'options' in mc:
                output = output.replace(f"{{{{DEVICE_{i}_OPTION_A}}}}", mc['options'].get('A', ''))
                output = output.replace(f"{{{{DEVICE_{i}_OPTION_B}}}}", mc['options'].get('B', ''))
                output = output.replace(f"{{{{DEVICE_{i}_OPTION_C}}}}", mc['options'].get('C', ''))
                output = output.replace(f"{{{{DEVICE_{i}_OPTION_D}}}}", mc['options'].get('D', ''))
            else:
                # Fallback to old structure
                output = output.replace(f"{{{{DEVICE_{i}_OPTION_A}}}}", mc.get('option_a', ''))
                output = output.replace(f"{{{{DEVICE_{i}_OPTION_B}}}}", mc.get('option_b', ''))
                output = output.replace(f"{{{{DEVICE_{i}_OPTION_C}}}}", mc.get('option_c', ''))
                output = output.replace(f"{{{{DEVICE_{i}_OPTION_D}}}}", mc.get('option_d', ''))
        
        # Sequencing (use stored randomization)
        if 'sequencing' in enriched:
            seq = enriched['sequencing']
            indices = randomization_states[i-1] if i-1 < len(randomization_states) else None
            
            if indices is None:
                indices = [0, 1, 2]
                random.shuffle(indices)
                while indices == [0, 1, 2]:
                    random.shuffle(indices)
            
            items = [
                seq.get('item_a', ''),
                seq.get('item_b', ''),
                seq.get('item_c', '')
            ]
            
            output = output.replace(f"{{{{DEVICE_{i}_SEQUENCE_STEP_RANDOMIZED_1}}}}", items[indices[0]])
            output = output.replace(f"{{{{DEVICE_{i}_SEQUENCE_STEP_RANDOMIZED_2}}}}", items[indices[1]])
            output = output.replace(f"{{{{DEVICE_{i}_SEQUENCE_STEP_RANDOMIZED_3}}}}", items[indices[2]])
            
            # DO NOT include correct answer in student worksheet
            # This line should ONLY be in teacher key, not here
            output = output.replace(f"{{{{DEVICE_{i}_SEQUENCE_CORRECT_ORDER}}}}", "")
        
        # Effects (simplified for v2.2) - extracted directly from Stage 1B
        if 'effects' in enriched:
            eff = enriched['effects']
            
            # Use simplified effects structure (extracted from Stage 1B)
            output = output.replace(f"{{{{DEVICE_{i}_EFFECT_1_SIMPLIFIED}}}}", eff.get('effect_1_simplified', ''))
            output = output.replace(f"{{{{DEVICE_{i}_EFFECT_2_SIMPLIFIED}}}}", eff.get('effect_2_simplified', ''))
            output = output.replace(f"{{{{DEVICE_{i}_EFFECT_3_SIMPLIFIED}}}}", eff.get('effect_3_simplified', ''))
            output = output.replace(f"{{{{DEVICE_{i}_EFFECT_4_SIMPLIFIED}}}}", eff.get('effect_4_simplified', ''))
            output = output.replace(f"{{{{DEVICE_{i}_EFFECT_5_SIMPLIFIED}}}}", eff.get('effect_5_simplified', ''))
            output = output.replace(f"{{{{DEVICE_{i}_EFFECT_6_SIMPLIFIED}}}}", eff.get('effect_6_simplified', ''))
        
        # Examples
        if 'examples' in enriched:
            ex = enriched['examples']
            output = output.replace(f"{{{{DEVICE_{i}_MODEL_EXAMPLE}}}}", ex.get('model_example', ''))
            output = output.replace(f"{{{{DEVICE_{i}_EXAMPLE_LOCATIONS}}}}", ex.get('location_prompt', ''))
    
    return output

def fill_teacher_key_template(template, week_package, enriched_devices, randomization_states):
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
            # New structure uses 'options' dict
            if 'options' in mc:
                output = output.replace(f"{{{{DEVICE_{i}_OPTION_A}}}}", mc['options'].get('A', ''))
                output = output.replace(f"{{{{DEVICE_{i}_OPTION_B}}}}", mc['options'].get('B', ''))
                output = output.replace(f"{{{{DEVICE_{i}_OPTION_C}}}}", mc['options'].get('C', ''))
                output = output.replace(f"{{{{DEVICE_{i}_OPTION_D}}}}", mc['options'].get('D', ''))
                output = output.replace(f"{{{{DEVICE_{i}_CORRECT_OPTION}}}}", mc.get('correct', ''))
            else:
                # Fallback to old structure
                output = output.replace(f"{{{{DEVICE_{i}_OPTION_A}}}}", mc.get('option_a', ''))
                output = output.replace(f"{{{{DEVICE_{i}_OPTION_B}}}}", mc.get('option_b', ''))
                output = output.replace(f"{{{{DEVICE_{i}_OPTION_C}}}}", mc.get('option_c', ''))
                output = output.replace(f"{{{{DEVICE_{i}_OPTION_D}}}}", mc.get('option_d', ''))
                output = output.replace(f"{{{{DEVICE_{i}_CORRECT_OPTION}}}}", mc.get('correct', ''))
                output = output.replace(f"{{{{DEVICE_{i}_DISTRACTOR_1}}}}", mc.get('distractor_1_explanation', ''))
                output = output.replace(f"{{{{DEVICE_{i}_DISTRACTOR_2}}}}", mc.get('distractor_2_explanation', ''))
        
        # Sequencing with answer (must match worksheet randomization)
        if 'sequencing' in enriched:
            seq = enriched['sequencing']
            indices = randomization_states[i-1] if i-1 < len(randomization_states) else None
            
            if indices is None:
                indices = [0, 1, 2]
                random.shuffle(indices)
                while indices == [0, 1, 2]:
                    random.shuffle(indices)
            
            items = [
                seq.get('item_a', ''),
                seq.get('item_b', ''),
                seq.get('item_c', '')
            ]
            
            output = output.replace(f"{{{{DEVICE_{i}_SEQUENCE_STEP_RANDOMIZED_1}}}}", items[indices[0]])
            output = output.replace(f"{{{{DEVICE_{i}_SEQUENCE_STEP_RANDOMIZED_2}}}}", items[indices[1]])
            output = output.replace(f"{{{{DEVICE_{i}_SEQUENCE_STEP_RANDOMIZED_3}}}}", items[indices[2]])
            
            # Calculate correct answer format: "1-B, 2-A, 3-C"
            # indices tells us which original item (0,1,2) is in each position
            # We need to reverse: which letter (A,B,C) is in position 1, 2, 3?
            letters = ['A', 'B', 'C']
            correct_order_parts = []
            for pos in range(3):
                # Find which letter corresponds to the original item at this position
                original_item_idx = indices[pos]
                letter = letters[original_item_idx]
                correct_order_parts.append(f"{pos+1}-{letter}")
            
            correct_order = ', '.join(correct_order_parts)
            
            output = output.replace(f"{{{{DEVICE_{i}_SEQUENCE_ANSWER}}}}", correct_order)
            output = output.replace(f"{{{{DEVICE_{i}_SEQUENCE_EXPLANATION}}}}", seq.get('explanation', ''))
            output = output.replace(f"{{{{DEVICE_{i}_SEQUENCE_CORRECT_ORDER}}}}", f"**Correct Answer:** {correct_order}")
        
        # Effects (simplified for v2.2) - extracted directly from Stage 1B
        if 'effects' in enriched:
            eff = enriched['effects']
            
            # Simplified versions for sorting (from Stage 1B)
            output = output.replace(f"{{{{DEVICE_{i}_EFFECT_1_SIMPLIFIED}}}}", eff.get('effect_1_simplified', ''))
            output = output.replace(f"{{{{DEVICE_{i}_EFFECT_2_SIMPLIFIED}}}}", eff.get('effect_2_simplified', ''))
            output = output.replace(f"{{{{DEVICE_{i}_EFFECT_3_SIMPLIFIED}}}}", eff.get('effect_3_simplified', ''))
            output = output.replace(f"{{{{DEVICE_{i}_EFFECT_4_SIMPLIFIED}}}}", eff.get('effect_4_simplified', ''))
            output = output.replace(f"{{{{DEVICE_{i}_EFFECT_5_SIMPLIFIED}}}}", eff.get('effect_5_simplified', ''))
            output = output.replace(f"{{{{DEVICE_{i}_EFFECT_6_SIMPLIFIED}}}}", eff.get('effect_6_simplified', ''))
            
            # Categorized effects for teacher key answer tables
            # Use first 2 effects for each category (from Stage 1B with synonym variations)
            # Reader response effects (feeling-based)
            output = output.replace(f"{{{{DEVICE_{i}_FELT_EFFECT_1}}}}", eff.get('effect_1_simplified', eff.get('reader', '')))
            output = output.replace(f"{{{{DEVICE_{i}_FELT_EFFECT_2}}}}", eff.get('effect_2_simplified', eff.get('reader2', '')))
            
            # Meaning creation effects (understanding-based)
            output = output.replace(f"{{{{DEVICE_{i}_UNDERSTOOD_EFFECT_1}}}}", eff.get('effect_3_simplified', eff.get('meaning', '')))
            output = output.replace(f"{{{{DEVICE_{i}_UNDERSTOOD_EFFECT_2}}}}", eff.get('effect_4_simplified', eff.get('character', '')))
            
            # Thematic impact effects (big idea)
            output = output.replace(f"{{{{DEVICE_{i}_BIGIDEA_EFFECT_1}}}}", eff.get('effect_5_simplified', eff.get('theme', '')))
            output = output.replace(f"{{{{DEVICE_{i}_BIGIDEA_EFFECT_2}}}}", eff.get('effect_6_simplified', eff.get('structure', '')))
        
        # Examples and teaching
        if 'examples' in enriched:
            ex = enriched['examples']
            output = output.replace(f"{{{{DEVICE_{i}_MODEL_EXAMPLE}}}}", ex.get('model_example', ''))
            output = output.replace(f"{{{{DEVICE_{i}_EXAMPLE_LOCATIONS}}}}", ex.get('location_prompt', ''))
            output = output.replace(f"{{{{DEVICE_{i}_EXAMPLE_LOCATIONS_FULL}}}}", ex.get('location_prompt', ''))
            output = output.replace(f"{{{{DEVICE_{i}_SAMPLE_RESPONSE}}}}", ex.get('sample_response', ''))
            output = output.replace(f"{{{{DEVICE_{i}_DETAIL_SAMPLE}}}}", ex.get('detail_sample', ''))
            
            # Model paragraph placeholder (if needed)
            output = output.replace(f"{{{{DEVICE_{i}_MODEL_PARAGRAPH}}}}", "See TVODE Construction Worksheet for complete model paragraph")
        
        if 'teaching' in enriched:
            teach = enriched['teaching']
            output = output.replace(f"{{{{DEVICE_{i}_TEACHING_NOTE}}}}", teach.get('teaching_note', ''))
    
    return output

def process_week(week_package, template_dir, output_dir):
    """Process one week: extract data from Stage 1B and fill templates"""
    
    week_num = week_package['week']
    macro_focus = week_package['macro_focus']
    activity_chapter = week_package.get('activity_chapter', 'TBD')
    
    print(f"\n📝 Processing Week {week_num}: {macro_focus}")
    print(f"   Activity Chapter: {activity_chapter}")
    print(f"   Devices: {len(week_package['micro_devices'])}")
    
    # Extract worksheet data from Stage 1B (NO API CALLS)
    print(f"\n📊 Extracting worksheet data from Stage 1B...")
    enriched_devices = []
    randomization_states = []
    
    title = week_package.get('text_title', 'Book')
    
    for device in week_package['micro_devices'][:3]:  # Limit to 3 devices per worksheet
        print(f"   - {device['name']}...", end='', flush=True)
        
        # Extract from Stage 1B instead of generating with AI
        enriched = extract_worksheet_data_from_stage1b(
            device, 
            macro_focus, 
            title,
            activity_chapter
        )
        enriched_devices.append(enriched)
        
        # Generate randomization for this device
        if enriched and 'sequencing' in enriched:
            indices = [0, 1, 2]
            random.shuffle(indices)
            while indices == [0, 1, 2]:
                random.shuffle(indices)
            randomization_states.append(indices)
        else:
            randomization_states.append(None)
        
        print(" ✓ (NO API CALL)")
    
    # Load templates
    print(f"\n📄 Filling templates...")
    worksheet_template = load_template(template_dir / "Template_Literary_Analysis_6Step.md")
    teacher_key_template = load_template(template_dir / "Template_Teacher_Key.md")
    
    # Fill templates (now passing randomization states)
    worksheet = fill_worksheet_template(worksheet_template, week_package, enriched_devices, randomization_states)
    teacher_key = fill_teacher_key_template(teacher_key_template, week_package, enriched_devices, randomization_states)
    
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
            files = process_week(week_package, template_dir, output_dir)
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
        worksheet_path, teacher_key_path = process_week(week_package, template_dir, output_dir)
        
        print("\n" + "="*80)
        print("✅ STAGE 2 COMPLETE!")
        print("="*80)
        print(f"\nGenerated files:")
        print(f"  - {worksheet_path}")
        print(f"  - {teacher_key_path}")
    
    print(f"\n📂 All worksheets saved to: {output_dir}")
    print(f"\n💰 API cost: $0.00 (extraction only, no generation)")

if __name__ == "__main__":
    main()
