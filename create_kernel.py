#!/usr/bin/env python3
"""
KERNEL CREATION AUTOMATION - VERSION 2.1
Semi-automated kernel creation with review gates

This script automates the Kernel Validation Protocol v3.4:
- Stage 1: Extract 5 Freytag sections
- Stage 2A: Tag 84 macro alignment variables
- Stage 2B: Identify 15-20+ micro devices with examples
- Stage 3: Generate reasoning document with alignment pattern derivation

v2.1 Changes:
- Stage 3: Reasoning document derives alignment pattern from code synthesis (CPEA methodology)
- ReasoningDoc output version: v4.1

User reviews and approves each stage before continuing.
"""

import anthropic
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from datetime import datetime
import PyPDF2
from typing import Dict, List, Optional

# Configuration
class Config:
    """Configuration settings"""
    API_KEY = os.getenv("ANTHROPIC_API_KEY")
    MODEL = "claude-sonnet-4-20250514"
    MAX_TOKENS = 16000
    
    # Directories
    PROTOCOLS_DIR = Path("protocols")
    BOOKS_DIR = Path("books")
    KERNELS_DIR = Path("kernels")
    OUTPUTS_DIR = Path("outputs")
    
    # Protocol files
    STRUCTURE_ALIGNMENT = "Book_Structure_Alignment_Protocol_v2.md"
    KERNEL_VALIDATION = "Kernel_Validation_Protocol_v3_4.md"
    KERNEL_ENHANCEMENT = "Kernel_Protocol_Enhancement_v3_3.md"
    ARTIFACT_1 = "Artifact_1_-_Device_Taxonomy_by_Alignment_Function"
    ARTIFACT_2 = "Artifact_2_-_Text_Tagging_Protocol"
    LEM = "LEM_-_Stage_1_-_Narrative-Rhetoric_Triangulation"

# Device tier mapping for pedagogical progression
DEVICE_TIER_MAP = {
    # =========================================================================
    # TIER 1 - Concrete/Sensory → EXPOSITION
    # Easiest to identify, visual/auditory, students can point to examples
    # =========================================================================
    'Imagery': 1,
    'Simile': 1,
    'Hyperbole': 1,
    'Metaphor': 1,
    'Onomatopoeia': 1,
    'Personification': 1,
    'Alliteration': 1,
    'Assonance': 1,
    'Consonance': 1,
    'Sensory Detail': 1,
    
    # =========================================================================
    # TIER 2 - Structural/Pattern → RISING ACTION
    # Pattern recognition, structural elements, how text is organized
    # =========================================================================
    'Dialogue': 2,
    'Repetition': 2,
    'Direct Characterization': 2,
    'Indirect Characterization': 2,
    'Ellipsis': 2,
    'Scene': 2,
    'Summary': 2,
    'Pause': 2,
    'Parallelism': 2,
    'Anaphora': 2,
    'Epistrophe': 2,
    'Polysyndeton': 2,
    'Asyndeton': 2,
    'Linear Chronology': 2,
    'Episodic Structure': 2,
    'Flashback': 2,
    'Analepsis': 2,
    'Flashforward': 2,
    'Prolepsis': 2,
    'In Medias Res': 2,
    
    # =========================================================================
    # TIER 3 - Abstract/Symbolic → CLIMAX
    # Requires inference, abstract connections, symbolic thinking
    # =========================================================================
    'Symbolism': 3,
    'Motif': 3,
    'Foreshadowing': 3,
    'Juxtaposition': 3,
    'Allusion': 3,
    'Allegory': 3,
    'Paradox': 3,
    'Oxymoron': 3,
    'Chiasmus': 3,
    'Circular Structure': 3,
    'Spiral Structure': 3,
    'Understatement': 3,
    'Litotes': 3,
    
    # =========================================================================
    # TIER 4 - Authorial Intent/Irony → FALLING ACTION
    # Requires perspective-taking, understanding author's purpose
    # =========================================================================
    'Verbal Irony': 4,
    'Dramatic Irony': 4,
    'Situational Irony': 4,
    'Structural Irony': 4,
    'Suspense': 4,
    'Satire': 4,
    'Tone': 4,
    'Rhetorical Question': 4,
    'Apostrophe': 4,
    'Ethos Establishment': 4,
    
    # =========================================================================
    # TIER 5 - Narrative Frame/Voice → RESOLUTION
    # Meta-level, narrative perspective, framing devices
    # =========================================================================
    'Third-Person Omniscient': 5,
    'Third-Person Limited': 5,
    'First-Person': 5,
    'First-Person Narration': 5,
    'Second-Person Narration': 5,
    'Internal Monologue': 5,
    'Stream of Consciousness': 5,
    'Unreliable Narrator': 5,
    'Free Indirect Discourse': 5,
    'Frame Narrative': 5,
    'Non-Linear Chronology': 5,
    'Metafiction': 5,
    'Breaking Fourth Wall': 5,
    'Unreliable Chronology': 5,
    'Narrator': 5,
    'Point of View': 5,
}

# Tier 5 devices that need relocation if found in wrong section
TIER5_VOICE_DEVICES = {
    'Third-Person Omniscient', 'Third-Person Limited', 'First-Person',
    'First-Person Narration', 'Second-Person Narration', 'Internal Monologue',
    'Stream of Consciousness', 'Unreliable Narrator', 'Free Indirect Discourse',
    'Frame Narrative', 'Non-Linear Chronology', 'Metafiction',
    'Breaking Fourth Wall', 'Unreliable Chronology', 'Narrator', 'Point of View'
}

# Mutually exclusive POV devices - only ONE can exist in any text
MUTUALLY_EXCLUSIVE_POV = {
    'First-Person', 'First-Person Narration', 'Second-Person Narration',
    'Third-Person Omniscient', 'Third-Person Limited'
}

# Map macro POV codes to device names
POV_CODE_TO_DEVICE = {
    'FP': {'First-Person', 'First-Person Narration'},
    'TPO': {'Third-Person Omniscient'},
    'TPL': {'Third-Person Limited'},
    'SP': {'Second-Person Narration'}
}

TIER_TO_FREYTAG = {
    1: 'exposition',
    2: 'rising_action',
    3: 'climax',
    4: 'falling_action',
    5: 'resolution'
}

class KernelCreator:
    """Main class for creating kernel JSONs"""
    
    def __init__(self, book_path: str, title: str, author: str, edition: str):
        self.book_path = Path(book_path)
        self.title = title
        self.author = author
        self.edition = edition
        self.total_chapters = None  # Will be set by Stage 0
        
        # Initialize API client
        if not Config.API_KEY:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = anthropic.Anthropic(api_key=Config.API_KEY)
        
        # Load protocols
        self.protocols = self._load_protocols()
        
        # Load book text
        self.book_text = self._load_book()
        self.book_words = self.book_text.split()
        
        # Storage for stage outputs
        self.structure_alignment = None
        self.stage1_extracts = None
        self.stage2a_macro = None
        self.stage2b_devices = None
        self.kernel = None
    
    def _get_checkpoint_path(self, stage_name: str) -> Path:
        """Get checkpoint file path for a stage."""
        safe_title = "".join(c for c in self.title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')
        return Config.OUTPUTS_DIR / f"{safe_title}_{stage_name}.json"
    
    def _save_checkpoint(self, stage_name: str, data: dict):
        """Save stage output as checkpoint."""
        path = self._get_checkpoint_path(stage_name)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"  💾 Checkpoint saved: {path.name}")
    
    def _load_checkpoint(self, stage_name: str) -> dict | None:
        """Load checkpoint if exists and valid."""
        path = self._get_checkpoint_path(stage_name)
        if not path.exists():
            return None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"  ✅ Loaded checkpoint: {path.name}")
            return data
        except json.JSONDecodeError:
            print(f"  ⚠️ Invalid checkpoint, will regenerate: {path.name}")
            return None
    
    def _clear_checkpoints_from(self, stage_name: str):
        """Clear this and all later checkpoints (for force restart)."""
        stages = ['kernel_stage0', 'kernel_stage1', 'kernel_stage2a', 'kernel_stage2b']
        start_idx = stages.index(stage_name) if stage_name in stages else 0
        for stage in stages[start_idx:]:
            path = self._get_checkpoint_path(stage)
            if path.exists():
                path.unlink()
                print(f"  🗑️ Cleared checkpoint: {path.name}")
        
    def _load_protocols(self) -> Dict[str, str]:
        """Load all protocol markdown files"""
        print("\nðŸ“š Loading protocols...")
        protocols = {}
        
        protocol_files = {
            "structure_alignment": Config.STRUCTURE_ALIGNMENT,
            "kernel_validation": Config.KERNEL_VALIDATION,
            "kernel_enhancement": Config.KERNEL_ENHANCEMENT,
            "artifact_1": Config.ARTIFACT_1,
            "artifact_2": Config.ARTIFACT_2,
            "lem": Config.LEM
        }
        
        for key, filename in protocol_files.items():
            filepath = Config.PROTOCOLS_DIR / filename
            if not filepath.exists():
                print(f"âš ï¸  Warning: {filename} not found, skipping...")
                protocols[key] = ""
                continue
                
            with open(filepath, 'r', encoding='utf-8') as f:
                protocols[key] = f.read()
            print(f"  âœ“ Loaded {filename}")
        
        return protocols
    
    def _load_book(self) -> str:
        """Load book text from PDF or txt file"""
        print(f"\nðŸ“– Loading book: {self.book_path.name}")
        
        if self.book_path.suffix.lower() == '.pdf':
            return self._load_pdf()
        elif self.book_path.suffix.lower() == '.txt':
            with open(self.book_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported file type: {self.book_path.suffix}")
    
    def _load_pdf(self) -> str:
        """Extract text from PDF"""
        text = ""
        with open(self.book_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            total_pages = len(pdf_reader.pages)
            print(f"  ðŸ“„ Extracting text from {total_pages} pages...")
            
            for i, page in enumerate(pdf_reader.pages):
                text += page.extract_text()
                if (i + 1) % 50 == 0:
                    print(f"    Progress: {i + 1}/{total_pages} pages")
        
        print(f"  âœ“ Extracted {len(text):,} characters")
        return text
    
    def _call_claude(self, prompt: str, system_prompt: str = "") -> str:
        """Call Claude API with given prompt, with automatic retry on rate limit"""
        print("\nðŸ¤– Calling Claude API...")
        
        messages = [{"role": "user", "content": prompt}]
        
        response = self.client.messages.create(
            model=Config.MODEL,
            max_tokens=Config.MAX_TOKENS,
            system=system_prompt if system_prompt else None,
            messages=messages
        )
        
        result = response.content[0].text
        print(f"  âœ“ Received {len(result):,} characters")
        return result
    
    def _validate_tier_alignment(self, devices):
        """Check that device examples are in tier-appropriate Freytag sections."""
        misaligned = []
        unmapped = []
        
        for device in devices:
            name = device.get('name', '')
            tier = DEVICE_TIER_MAP.get(name, None)
            
            if tier is None:
                unmapped.append(name)
                continue
                
            expected_section = TIER_TO_FREYTAG.get(tier, None)
            
            for example in device.get('examples', []):
                actual_section = example.get('freytag_section', '')
                if expected_section and actual_section != expected_section:
                    misaligned.append({
                        'device': name,
                        'tier': tier,
                        'expected': expected_section,
                        'actual': actual_section
                    })
        
        if unmapped:
            print(f"\n⚠️  Warning: {len(unmapped)} device(s) not in DEVICE_TIER_MAP (assigned Tier 0):")
            for name in unmapped:
                print(f"    - {name}")
        
        return misaligned
    
    def _relocate_tier5_devices(self, devices):
        """
        Tier 5 (Voice) devices are pervasive - they exist throughout the text.
        If API placed them in wrong section, relocate to resolution.
        """
        for device in devices:
            name = device.get('name', '')
            if name in TIER5_VOICE_DEVICES:
                assigned = device.get('assigned_section', '')
                if assigned != 'resolution':
                    print(f"  ⚠️ Relocating {name} from {assigned} to resolution (Tier 5 device)")
                    device['assigned_section'] = 'resolution'
                    # Update example freytag_section too
                    for example in device.get('examples', []):
                        example['freytag_section'] = 'resolution'
        
        return devices
    
    def _deduplicate_devices(self, devices):
        """
        If same device appears multiple times, keep only the tier-appropriate one.
        """
        seen = {}
        result = []
        
        for device in devices:
            name = device.get('name', '')
            tier = DEVICE_TIER_MAP.get(name, 0)
            expected_section = TIER_TO_FREYTAG.get(tier, None)
            actual_section = device.get('assigned_section', '')
            
            if name not in seen:
                seen[name] = device
                result.append(device)
            else:
                # Keep the one in correct section
                if actual_section == expected_section:
                    # Replace previous with this one
                    result = [d for d in result if d.get('name') != name]
                    result.append(device)
                    seen[name] = device
                    print(f"  ⚠️ Deduplicating {name}: keeping {actual_section} (correct tier)")
        
        return result
    
    def _filter_contradictory_pov_devices(self, devices, macro_pov):
        """
        Remove POV devices that contradict the text's actual POV.
        A text can only have ONE narrative POV - can't be both first-person and third-person.
        """
        allowed_pov_devices = POV_CODE_TO_DEVICE.get(macro_pov, set())
        
        filtered = []
        for device in devices:
            name = device.get('name', '')
            if name in MUTUALLY_EXCLUSIVE_POV:
                if name in allowed_pov_devices:
                    filtered.append(device)
                else:
                    print(f"  ⚠️ Removing {name} (contradicts text's {macro_pov} POV)")
            else:
                filtered.append(device)
        
        return filtered
    
    def _review_and_approve(self, stage_name: str, output: str) -> bool:
        """Present output to user for review (automatically approved)"""
        print(f"\n{'='*80}")
        print(f"STAGE COMPLETE: {stage_name}")
        print(f"{'='*80}")
        print("\nOutput preview (first 2000 characters):")
        print(output[:2000])
        if len(output) > 2000:
            print(f"\n... ({len(output) - 2000:,} more characters)")
        
        print(f"\n{'='*80}")
        print("Automatically approved and continuing...")
        return True


    def _create_book_sample(self) -> str:
        """Create strategic sample of book for boundary identification"""
        total_words = len(self.book_words)
        
        # Sample: 15K from beginning + 15K from middle + 15K from end = 45K words
        beginning = ' '.join(self.book_words[:15000])
        
        middle_start = (total_words // 2) - 7500
        middle_end = (total_words // 2) + 7500
        middle = ' '.join(self.book_words[middle_start:middle_end])
        
        ending = ' '.join(self.book_words[-15000:])
        
        sample = f"{beginning}\n\n[... middle sections omitted ...]\n\n{middle}\n\n[... later sections omitted ...]\n\n{ending}"
        
        return sample
    
    def _create_chapter_samples(self) -> str:
        """Create targeted samples from validated chapter alignment (Stage 0)
        
        Instead of beginning/middle/end, extract ~1000 words from each 
        of the 5 primary chapters identified in Stage 0.
        Total: ~5K words instead of 45K words
        """
        if not self.structure_alignment:
            return self._create_book_sample()  # Fallback
        
        chapter_alignment = self.structure_alignment.get('chapter_alignment', {})
        samples = []
        
        for stage_name, data in chapter_alignment.items():
            primary_chapter = data.get('primary_chapter', 1)
            extract = self._extract_text_from_chapter_range(
                str(primary_chapter), 
                primary_chapter, 
                word_count=1000
            )
            samples.append(f"=== {stage_name.upper()} (Chapter {primary_chapter}) ===\n{extract}")
        
        return "\n\n".join(samples)
    
    def _extract_text_from_chapter_range(self, chapter_range: str, primary_chapter: int, word_count: int = None) -> str:
        """Extract full chapter text for primary chapter.
        
        Changed from 400-word sample to full chapter to prevent hallucination.
        See ISSUE_001 for details.
        
        Args:
            chapter_range: Chapter range string (unused, kept for compatibility)
            primary_chapter: The primary chapter to extract
            word_count: Ignored (kept for backward compatibility)
            
        Returns:
            String of full chapter text
        """
        total_words = len(self.book_words)
        words_per_chapter = total_words / self.total_chapters
        
        # Calculate chapter boundaries
        chapter_start = int((primary_chapter - 1) * words_per_chapter)
        chapter_end = int(primary_chapter * words_per_chapter)
        
        # Extract full chapter
        extracted_text = ' '.join(self.book_words[chapter_start:chapter_end])
        return extracted_text
    
    def _extract_devices_from_section(self, section: str, chapter_range: str, 
                                       primary_chapter: int, chapter_text: str) -> list:
        """Extract devices from a single section's full chapter.
        
        ISSUE_001 fix: Process one section at a time with full chapter text
        to prevent hallucination of quotes.
        ISSUE_003 fix: Include device taxonomy in prompt to prevent invented device names.
        """
        
        # Get device taxonomy
        device_taxonomy = self.protocols.get('artifact_1', '')
        
        prompt = f"""You are analyzing Chapter {primary_chapter} of {self.title} for the {section.upper()} section.

CHAPTER TEXT:
{chapter_text}

DEVICE TAXONOMY (you MUST choose devices from this list):
{device_taxonomy}

TASK: Identify 6-8 literary devices from the taxonomy above that appear in this chapter and demonstrate {section} narrative function.

For each device, provide:
- name: Device name (MUST be from the taxonomy above - e.g., "Metaphor", "Foreshadowing", "Dramatic Irony")
- anchor_phrase: EXACT 5-10 word quote from the chapter above
- location_percent: Where in chapter (0-100%)
- scene: Brief scene description
- effect: What this device accomplishes

CRITICAL CONSTRAINTS:
1. Device name MUST match exactly one from the taxonomy (not invented names)
2. anchor_phrase MUST be exact text from the chapter above
3. Do NOT use your training knowledge of this book
4. Do NOT paraphrase or invent quotes
5. If you cannot find a good example, skip that device

Valid device names include:
- Metaphor, Simile, Personification, Symbolism
- Foreshadowing, Flashback, Dramatic Irony, Verbal Irony, Situational Irony
- First-Person Narration, Third-Person Limited, Unreliable Narrator
- Imagery, Dialogue, Juxtaposition, Motif
- Alliteration, Parallelism, Hyperbole, Understatement

Return ONLY a JSON array:
[
  {{
    "name": "Foreshadowing",
    "anchor_phrase": "exact words from chapter",
    "location_percent": 35,
    "scene": "brief scene description", 
    "effect": "what device accomplishes"
  }}
]"""

        system_prompt = "You are a literary analysis expert. Only quote exact text from the provided chapter. Never hallucinate quotes."
        
        result = self._call_claude(prompt, system_prompt)
        
        if result:
            try:
                # Clean JSON if wrapped in markdown
                result = result.strip()
                if result.startswith("```"):
                    result = result.split("```")[1]
                    if result.startswith("json"):
                        result = result[4:]
                
                devices = json.loads(result)
                
                # Add section metadata
                for d in devices:
                    d['assigned_section'] = section
                    d['chapter'] = primary_chapter
                    d['chapter_range'] = chapter_range
                    
                return devices
                
            except json.JSONDecodeError as e:
                print(f"  Failed to parse devices for {section}: {e}")
                return []
        return []
    
    def stage0_structure_alignment(self):
        """Stage 0: Book Structure Alignment Protocol v1.1"""
        # Check for existing checkpoint
        cached = self._load_checkpoint('kernel_stage0')
        if cached:
            self.structure_alignment = cached
            if 'structure_detection' in cached and 'total_units' in cached['structure_detection']:
                self.total_chapters = cached['structure_detection']['total_units']
            return True
        
        print("\n" + "="*80)
        print("STAGE 0: BOOK STRUCTURE ALIGNMENT")
        print("="*80)
        
        # Create book sample for structure detection
        book_sample = self._create_book_sample()
        
        # Use Claude to detect structure and identify actual climax
        prompt = f"""You are performing the Book Structure Alignment Protocol v1.1.

TASK: Detect the book structure (total chapters) and identify the actual climax chapter(s), then create a validated alignment.

BOOK METADATA:
- Title: {self.title}
- Author: {self.author}
- Edition: {self.edition}

PROTOCOL TO FOLLOW:
{self.protocols['structure_alignment']}

BOOK SAMPLE (beginning, middle, end):
{book_sample}

CRITICAL TASKS:

1. DETECT BOOK STRUCTURE:
   - Analyze the book sample to determine the total number of chapters
   - Identify the structure type (numbered chapters, parts, etc.)
   - Set total_units to the total chapter count

2. IDENTIFY THE ACTUAL CLIMAX:
   - Find THE pivotal moment: highest tension, irreversible change, key decision/revelation
   - Determine which chapter(s) contain this moment (1-3 chapters maximum)

3. CREATE VALIDATED ALIGNMENT:
   - Apply conventional distribution formula based on detected total chapters
   - Adjust boundaries if needed (especially for extended rising action)
   - Ensure climax is tight (1-3 chapters)
   - Ensure all chapters are covered with no gaps

4. OUTPUT VALIDATED ALIGNMENT:
   Provide a JSON object with this structure:
   {{
     "structure_detection": {{
       "structure_type": "NUM",
       "total_units": <detected_total_chapters>,
       "special_elements": [],
       "notes": "Numbered chapters detected"
     }},
     "chapter_alignment": {{
       "exposition": {{
         "chapter_range": "1-X",
         "chapters": [1, 2, ...],
         "primary_chapter": 1,
         "percentage": 15
       }},
       "rising_action": {{
         "chapter_range": "X-Y",
         "chapters": [...],
         "primary_chapter": X,
         "percentage": 35
       }},
       "climax": {{
         "chapter_range": "Y",
         "chapters": [Y],
         "primary_chapter": Y,
         "percentage": 5
       }},
       "falling_action": {{
         "chapter_range": "Y+1-Z",
         "chapters": [...],
         "primary_chapter": X,
         "percentage": 30
       }},
       "resolution": {{
         "chapter_range": "Z+1-<total_chapters>",
         "chapters": [...],
         "primary_chapter": <total_chapters>,
         "percentage": 15
       }}
     }},
     "validation": {{
       "method": "conventional_distribution_with_verification",
       "fit_score": 95,
       "status": "VERIFIED",
       "notes": "Climax identified at chapter X. Alignment adjusted for extended rising action."
     }}
   }}

VERIFICATION REQUIREMENTS:
✓ All chapters must be included (no gaps, no overlaps)
✓ Climax must be 1-3 chapters
✓ Chapter ranges must be sequential
✓ Each stage must have primary_chapter specified
✓ Fit score must be ≥90% for VERIFIED status

CRITICAL: Output ONLY valid JSON. No additional text before or after.
"""
        
        system_prompt = "You are a literary analysis expert following the Book Structure Alignment Protocol v1.1 to establish validated chapter-to-Freytag mapping."
        
        result = self._call_claude(prompt, system_prompt)
        
        # Clean markdown formatting if present
        result = result.replace('```json\n', '').replace('```\n', '').replace('```', '').strip()
        
        # Validate JSON
        try:
            alignment_json = json.loads(result)
        except json.JSONDecodeError as e:
            print(f"\n❌ Error: Invalid JSON response from Claude")
            print(f"Error details: {e}")
            return False
        
        # Extract total_units and set as total_chapters
        if 'structure_detection' in alignment_json and 'total_units' in alignment_json['structure_detection']:
            self.total_chapters = alignment_json['structure_detection']['total_units']
            print(f"✓ Detected {self.total_chapters} chapters from book structure")
        else:
            raise ValueError("Stage 0 failed to detect total_units")
        
        # Validate required fields
        if 'chapter_alignment' not in alignment_json:
            print(f"\n❌ Error: Missing 'chapter_alignment' in response")
            return False
        
        # Validate all chapters are covered
        all_chapters = set()
        for stage, data in alignment_json['chapter_alignment'].items():
            chapters = data.get('chapters', [])
            all_chapters.update(chapters)
        
        expected_chapters = set(range(1, self.total_chapters + 1))
        missing = expected_chapters - all_chapters
        extra = all_chapters - expected_chapters
        
        if missing:
            print(f"\n⚠️  Warning: Missing chapters: {sorted(missing)}")
        if extra:
            print(f"\n⚠️  Warning: Extra chapters: {sorted(extra)}")
        
        # Review
        result_formatted = json.dumps(alignment_json, indent=2)
        if self._review_and_approve("Stage 0: Structure Alignment", result_formatted):
            self.structure_alignment = alignment_json
            self._save_checkpoint('kernel_stage0', self.structure_alignment)
            return True
        return False
    
    def stage1_extract_freytag(self):
        """Stage 1: Extract 5 Freytag sections with chapter ranges"""
        # Check for existing checkpoint
        cached = self._load_checkpoint('kernel_stage1')
        if cached:
            self.stage1_extracts = cached
            return True
        
        print("\n" + "="*80)
        print("STAGE 1: FREYTAG EXTRACT SELECTION (with chapter mapping)")
        print("="*80)
        
        if not self.structure_alignment:
            print("❌ Error: Stage 0 structure alignment not completed")
            return False
        
        # Get validated chapter alignment
        chapter_alignment = self.structure_alignment.get('chapter_alignment', {})
        
        book_sample = self._create_chapter_samples()
        
        # Build chapter range context from validated alignment
        alignment_context = ""
        for stage, data in chapter_alignment.items():
            chapter_range = data.get('chapter_range', '')
            primary_chapter = data.get('primary_chapter', 1)
            alignment_context += f"- {stage}: {chapter_range} (primary: {primary_chapter})\n"
        
        prompt = f"""You are performing Stage 1 of the Kernel Validation Protocol v3.4.

IMPORTANT: Use the VALIDATED chapter alignment from Stage 0 (Book Structure Alignment Protocol).
Do NOT create new chapter ranges - use the provided alignment.

TASK: Extract the 5 Freytag dramatic structure sections from this book:
1. Exposition - Initial character/setting establishment
2. Rising Action - Conflict development
3. Climax - Turning point/peak tension
4. Falling Action - Consequences unfold
5. Resolution - Final outcome/thematic closure

BOOK METADATA:
- Title: {self.title}
- Author: {self.author}
- Edition: {self.edition}
- Total Chapters: {self.total_chapters}

==================================================================================
VALIDATED CHAPTER ALIGNMENT (from Stage 0):
==================================================================================
{alignment_context}
==================================================================================

CRITICAL: You MUST use these exact chapter ranges. Do NOT create new ranges.
The alignment has been validated through the Book Structure Alignment Protocol v1.1.

PROTOCOL REFERENCE: Kernel Validation Protocol v3.4 - Stage 1 (Freytag Section Identification)

The chapter alignment has already been validated. Your task is to:
1. Use the EXACT chapter ranges provided above
2. Provide rationale for each section (2-3 sentences)
3. Extract representative text (400-600 words) from each primary chapter

BOOK SAMPLE (extracts from primary chapters):
{book_sample}

OUTPUT FORMAT:
Provide a JSON object with this structure:
{{
  "metadata": {{
    "title": "{self.title}",
    "author": "{self.author}",
    "edition": "{self.edition}",
    "total_chapters": {self.total_chapters},
    "extraction_date": "{datetime.now().isoformat()}"
  }},
  "extracts": {{
    "exposition": {{
      "chapter_range": "[use validated range from Stage 0]",
      "primary_chapter": [use validated primary from Stage 0],
      "rationale": "why this represents exposition (2-3 sentences)"
    }},
    "rising_action": {{
      "chapter_range": "[use validated range from Stage 0]",
      "primary_chapter": [use validated primary from Stage 0],
      "rationale": "why this represents rising action (2-3 sentences)"
    }},
    "climax": {{
      "chapter_range": "[use validated range from Stage 0]",
      "primary_chapter": [use validated primary from Stage 0],
      "rationale": "why this represents climax (2-3 sentences)"
    }},
    "falling_action": {{
      "chapter_range": "[use validated range from Stage 0]",
      "primary_chapter": [use validated primary from Stage 0],
      "rationale": "why this represents falling action (2-3 sentences)"
    }},
    "resolution": {{
      "chapter_range": "[use validated range from Stage 0]",
      "primary_chapter": [use validated primary from Stage 0],
      "rationale": "why this represents resolution (2-3 sentences)"
    }}
  }}
}}

VERIFICATION CHECKLIST:
✓ Chapter ranges match the validated alignment from Stage 0 exactly
✓ Each section has primary_chapter matching Stage 0 alignment
✓ Each section has a clear, specific rationale
✓ Chapter ranges use numeric-only format: "1-3" NOT "Chapters 1-3"

CRITICAL FORMAT REQUIREMENT:
- chapter_range MUST be numeric-only: "1-3", "15", "4-14"
- Do NOT include "Chapters " prefix in chapter_range values
- Example: "chapter_range": "1-3" ✅ NOT "chapter_range": "Chapters 1-3" ❌

CRITICAL: Output ONLY valid JSON. No additional text before or after the JSON.
DO NOT extract or reproduce any text passages from the book.
"""
        
        system_prompt = "You are a literary analysis expert following the Kernel Validation Protocol v3.4 for extracting Freytag dramatic structure sections from novels."
        
        result = self._call_claude(prompt, system_prompt)
        
        # Clean markdown formatting if present
        result = result.replace('```json\n', '').replace('```\n', '').replace('```', '').strip()
        
        # Validate JSON
        try:
            extracts_json = json.loads(result)
            result_formatted = json.dumps(extracts_json, indent=2)
        except json.JSONDecodeError as e:
            print(f"\nâŒ Error: Invalid JSON response from Claude")
            print(f"Error details: {e}")
            return False
        
        # Validate required fields
        narrative_sections = extracts_json.get('extracts', {})
        if not narrative_sections:
            print(f"\n❌ Error: Missing 'extracts' in response")
            return False
        
        missing_fields = []
        for section_name, section_data in narrative_sections.items():
            if 'chapter_range' not in section_data:
                missing_fields.append(f"{section_name}: missing chapter_range")
            if 'primary_chapter' not in section_data:
                missing_fields.append(f"{section_name}: missing primary_chapter")
        
        if missing_fields:
            print(f"\n❌ Error: Missing required fields:")
            for field in missing_fields:
                print(f"  - {field}")
            print("\nStage 1 must include chapter_range and primary_chapter for each section.")
            return False
        
        # Normalize chapter_range format: remove "Chapters " prefix if present
        # Expected format: "1-3" not "Chapters 1-3"
        normalized = False
        for section_name, section_data in narrative_sections.items():
            chapter_range = section_data.get('chapter_range', '')
            if chapter_range:
                original = chapter_range
                # Remove "Chapters " prefix if present
                if chapter_range.startswith('Chapters '):
                    chapter_range = chapter_range.replace('Chapters ', '', 1).strip()
                    normalized = True
                elif chapter_range.startswith('Chapter '):
                    chapter_range = chapter_range.replace('Chapter ', '', 1).strip()
                    normalized = True
                # Update the normalized value
                if chapter_range != original:
                    section_data['chapter_range'] = chapter_range
                    normalized = True
        
        if normalized:
            print("\n✓ Normalized chapter_range format (removed 'Chapters ' prefix)")
            # Re-format JSON with normalized values
            result_formatted = json.dumps(extracts_json, indent=2)
        
        # Review
        if self._review_and_approve("Stage 1: Freytag Extracts", result_formatted):
            self.stage1_extracts = extracts_json
            self._save_checkpoint('kernel_stage1', self.stage1_extracts)
            return True
        return False
    
    def stage2a_tag_macro(self):
        """Stage 2A: Tag 84 macro alignment variables"""
        # Check for existing checkpoint
        cached = self._load_checkpoint('kernel_stage2a')
        if cached:
            self.stage2a_macro = cached
            return True
        
        print("\n" + "="*80)
        print("STAGE 2A: MACRO ALIGNMENT TAGGING")
        print("="*80)
        
        if not self.stage1_extracts:
            print("âŒ Error: Stage 1 extracts not available")
            return False
        
        # Extract text from book using chapter ranges
        extracts_text = ""
        for section, data in self.stage1_extracts.get('extracts', {}).items():
            chapter_range = data.get('chapter_range', '')
            primary_chapter = data.get('primary_chapter', 1)
            
            # Extract text from this section
            section_text = self._extract_text_from_chapter_range(
                chapter_range, 
                primary_chapter, 
                word_count=400
            )
            extracts_text += f"\n### {section.upper()}\n{section_text}\n"
        
        prompt = f"""You are performing Stage 2A of the Kernel Validation Protocol v3.4.\n\nTASK: Analyze the 5 Freytag extracts and tag all 84 macro alignment variables:\n- Narrative variables (voice, structure, etc.)\n- Rhetorical variables (alignment type, mechanisms, etc.)\n\nBOOK METADATA:\n- Title: {self.title}\n- Author: {self.author}\n\nPROTOCOL TO FOLLOW:\n{self.protocols['kernel_validation']}\n\nTAGGING PROTOCOL:\n{self.protocols['artifact_2']}\n\nFREYTAG EXTRACTS:\n{extracts_text}\n\nOUTPUT FORMAT:\nProvide a JSON object with this structure:\n{{"narrative": {{"voice": {{"pov": "CODE", ...}}, "structure": {{...}}}}, "rhetoric": {{...}}, "device_mediation": {{...}}}}\n\nCRITICAL: Output ONLY valid JSON. Use the exact codes from the protocol.\n"""
        
        system_prompt = "You are a literary analysis expert tagging macro alignment variables according to Kernel Validation Protocol v3.4."
        
        result = self._call_claude(prompt, system_prompt)
        
        # Clean and validate
        result = result.replace('```json\n', '').replace('```\n', '').replace('```', '').strip()
        
        try:
            macro_json = json.loads(result)
            result_formatted = json.dumps(macro_json, indent=2)
        except json.JSONDecodeError as e:
            print(f"\n❌ Error: Invalid JSON response from Claude")
            print(f"Error details: {e}")
            return False
        
        # Review
        if self._review_and_approve("Stage 2A: Macro Variables", result_formatted):
            self.stage2a_macro = macro_json
            self._save_checkpoint('kernel_stage2a', self.stage2a_macro)
            return True
        return False
    
    def stage2b_tag_devices(self):
        """Stage 2B: Tag micro devices with examples.\n        \n        ISSUE_001 fix: Process one section at a time with full chapter\n        instead of single call with 400-word samples.\n        """
        # Check for existing checkpoint
        cached = self._load_checkpoint('kernel_stage2b')
        if cached:
            self.stage2b_devices = cached
            return True
        
        print("\n" + "="*80)
        print("STAGE 2B: MICRO DEVICE INVENTORY")
        print("="*80)
        
        if not self.stage1_extracts:
            print("❌ Error: Stage 1 extracts not available")
            return False
        
        all_devices = []
        
        for section, data in self.stage1_extracts.get('extracts', {}).items():
            chapter_range = data.get('chapter_range', '')
            primary_chapter = data.get('primary_chapter', 1)
            
            print(f"  Processing {section} (Chapter {primary_chapter})...")
            
            # Extract FULL chapter text
            chapter_text = self._extract_text_from_chapter_range(
                chapter_range, 
                primary_chapter
            )
            
            # Call API for this section
            devices = self._extract_devices_from_section(
                section, 
                chapter_range, 
                primary_chapter,
                chapter_text
            )
            
            if devices:
                all_devices.extend(devices)
                print(f"    Found {len(devices)} devices")
            else:
                print(f"    ⚠ No devices found for {section}")
        
        # Store results
        self.stage2b_devices = all_devices
        
        print(f"  Total devices: {len(all_devices)}")
        
        # Relocate Tier 5 devices to resolution (they're pervasive but should be taught last)
        all_devices = self._relocate_tier5_devices(all_devices)
        
        # Remove duplicate devices, keeping tier-appropriate ones
        all_devices = self._deduplicate_devices(all_devices)
        
        # Filter out POV devices that contradict the text's actual POV
        if self.stage2a_macro:
            macro_pov = self.stage2a_macro.get('narrative', {}).get('voice', {}).get('pov', 'TPO')
            all_devices = self._filter_contradictory_pov_devices(all_devices, macro_pov)
        
        # Add pedagogical_tier to each device
        for device in all_devices:
            device_name = device.get("name", "")
            device["pedagogical_tier"] = DEVICE_TIER_MAP.get(device_name, 0)
        
        # Update stored devices
        self.stage2b_devices = all_devices
        result_formatted = json.dumps(all_devices, indent=2)
        
        # Review
        if self._review_and_approve("Stage 2B: Micro Devices", result_formatted):
            self._save_checkpoint('kernel_stage2b', self.stage2b_devices)
            return len(all_devices) > 0
        return False
    
    def assemble_kernel(self):
        """Assemble final kernel JSON"""
        print("\n" + "="*80)
        print("ASSEMBLING FINAL KERNEL")
        print("="*80)
        
        if not all([self.stage1_extracts, self.stage2a_macro, self.stage2b_devices]):
            print("âŒ Error: Not all stages completed")
            return False
        
        # Create narrative_position_mapping from extracts
        narrative_position_mapping = {}
        for section, data in self.stage1_extracts.get('extracts', {}).items():
            narrative_position_mapping[section] = {
                "chapter_range": data.get('chapter_range', ''),
                "primary_chapter": data.get('primary_chapter', 1),
                "pages": ""  # Pages would need to be determined from PDF if available
            }
        
        kernel = {
            "metadata": {
                "title": self.title,
                "author": self.author,
                "edition": self.edition,
                "creation_date": datetime.now().isoformat(),
                "protocol_version": "3.3",
                "kernel_version": "4.0",
                "chapter_aware": True,
                "structure_alignment_protocol": "v1.1"
            },
            "text_structure": {
                "has_chapters": True,
                "total_chapters_estimate": self.total_chapters,
                "notes": "Chapter breaks identified during kernel creation"
            },
            "structure_detection": self.structure_alignment.get('structure_detection', {}) if self.structure_alignment else {},
            "chapter_alignment": self.structure_alignment.get('chapter_alignment', {}) if self.structure_alignment else {},
            "narrative_position_mapping": narrative_position_mapping,
            "extracts": self.stage1_extracts.get('extracts', {}),
            "macro_variables": {
                "narrative": self.stage2a_macro.get('narrative', {}),
                "rhetoric": self.stage2a_macro.get('rhetoric', {}),
                "device_mediation": self.stage2a_macro.get('device_mediation', {})
            },
            "micro_devices": self.stage2b_devices
        }
        
        self.kernel = kernel
        kernel_formatted = json.dumps(kernel, indent=2)
        
        # Review
        if self._review_and_approve("Final Kernel Assembly", kernel_formatted):
            return True
        return False
    
    def save_kernel(self, output_path: Optional[Path] = None):
        """Save kernel JSON to file"""
        if not self.kernel:
            print("âŒ Error: No kernel to save")
            return False
        
        if not output_path:
            # Generate default filename
            safe_title = "".join(c for c in self.title if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title.replace(' ', '_')
            filename = f"{safe_title}_kernel_v4_0.json"
            output_path = Config.KERNELS_DIR / filename
        
        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.kernel, f, indent=2)
        
        print(f"\nâœ… Kernel saved to: {output_path}")
        print(f"   Size: {output_path.stat().st_size:,} bytes")
        return True

    def save_reasoning_document(self, output_path: Optional[Path] = None):
        """Generate reasoning document following Stage 3 protocol (CPEA methodology)."""
        if not self.kernel:
            print("âŒ Error: No kernel to save reasoning for")
            return False
    
        if not output_path:
            safe_title = "".join(c for c in self.title if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title.replace(' ', '_')
            filename = f"{safe_title}_ReasoningDoc_v4_1.md"
            output_path = Config.KERNELS_DIR / filename
    
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
        # Format kernel data
        macro_text = self._format_macro_for_prompt(self.kernel.get('macro_variables', {}))
        devices_text = self._format_devices_for_prompt(self.kernel.get('micro_devices', []))
        chapter_text = self._format_chapter_alignment(self.kernel.get('chapter_alignment', {}))

        prompt = f"""Create a reasoning document for "{self.title}" by {self.author}.

KERNEL DATA:

{chapter_text}

{macro_text}

{devices_text}

---

CRITICAL: Derive the alignment pattern from code synthesis. Do not invent a thematic frame separately.

Examples:

- TPL + INT + RETRO + OBJ + SIT → "Stoic Retrospection"

- TPO + ZERO + HEAVY + ADV + VERB → "Intrusive Advocacy"

STRUCTURE:

## 1. Alignment Pattern

**Pattern**: [2-3 word name derived from codes]

**Core Dynamic**: [One sentence: how narrative access + rhetorical intent combine]

**Reader Effect**: [One sentence: what this produces for the reader]

## 2. Macro Variable Justifications

Explain WHY each code fits this text:

**Narrative Voice**: POV, Focalization, Reliability, Temporal, Intrusion

**Narrative Structure**: Chronology, Architecture, Pacing, Beginning

**Rhetorical Voice**: Stance, Tone, Register, Irony

**Rhetorical Structure**: Alignment type, N-R relationship, Mechanism, Mediation

## 3. Device Selections by Freytag Section

For each section, explain how devices EXECUTE the pattern:

**Exposition**: [devices] — establish the pattern

**Rising Action**: [devices] — develop it

**Climax**: [devices] — intensify it

**Falling Action**: [devices] — pivot/resolve

**Resolution**: [devices] — complete it

## 4. Alignment Effect

One paragraph: What does this alignment achieve? How do codes + devices combine to produce the reader experience?

Reference actual codes and device names throughout."""

        system_prompt = "You are documenting literary analysis using CPEA methodology. Derive patterns from code synthesis—do not invent frames independently."
        result = self._call_claude(prompt, system_prompt)
    
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
    
        print(f"\nâœ… Reasoning document saved: {output_path}")
        print(f"   Size: {output_path.stat().st_size:,} bytes")
        return True
    
    def _format_macro_for_prompt(self, macro_vars: dict) -> str:
        """Format macro variables for Stage 3 prompt."""
        lines = []
        
        nv = macro_vars.get('narrative', {}).get('voice', {})
        lines.append("NARRATIVE VOICE:")
        lines.append(f"  POV: {nv.get('pov')} - {nv.get('pov_description', '')}")
        lines.append(f"  Focalization: {nv.get('focalization')} - {nv.get('focalization_description', '')}")
        lines.append(f"  Reliability: {nv.get('reliability')}")
        lines.append(f"  Temporal Distance: {nv.get('temporal_distance')}")
        lines.append(f"  Intrusion: {nv.get('narrative_intrusion')}")
        
        ns = macro_vars.get('narrative', {}).get('structure', {})
        lines.append("\nNARRATIVE STRUCTURE:")
        lines.append(f"  Chronology: {ns.get('chronology')}")
        lines.append(f"  Architecture: {ns.get('plot_architecture')} - {ns.get('plot_architecture_description', '')}")
        lines.append(f"  Pacing: {ns.get('pacing')}")
        lines.append(f"  Beginning: {ns.get('beginning_type')}")
        lines.append(f"  Ending: {ns.get('ending_type')}")
        
        rv = macro_vars.get('rhetoric', {}).get('voice', {})
        lines.append("\nRHETORICAL VOICE:")
        lines.append(f"  Stance: {rv.get('stance')}")
        lines.append(f"  Tone: {rv.get('tone')}")
        lines.append(f"  Register: {rv.get('register')}")
        lines.append(f"  Irony: {rv.get('irony')}")
        lines.append(f"  Pathos: {rv.get('pathos')}")
        
        rs = macro_vars.get('rhetoric', {}).get('structure', {})
        lines.append("\nRHETORICAL STRUCTURE:")
        lines.append(f"  Alignment: {rs.get('alignment_type')}")
        lines.append(f"  N-R Relationship: {rs.get('narrative_rhetoric_relationship')}")
        lines.append(f"  Mechanism: {rs.get('primary_mechanism')}")
        lines.append(f"  Mediation: {rs.get('mediation_strategy')}")
        
        return "\n".join(lines)

    def _format_devices_for_prompt(self, devices: list) -> str:
        """Format micro devices for Stage 3 prompt."""
        lines = [f"MICRO DEVICES ({len(devices)} total):"]
        
        by_section = {}
        for d in devices:
            section = d.get('assigned_section', 'unknown')
            if section not in by_section:
                by_section[section] = []
            by_section[section].append(d)
        
        for section in ['exposition', 'rising_action', 'climax', 'falling_action', 'resolution']:
            if section in by_section:
                lines.append(f"\n{section.upper().replace('_', ' ')}:")
                for d in by_section[section]:
                    lines.append(f"  - {d['name']} ({d.get('classification', '')})")
        
        return "\n".join(lines)

    def _format_chapter_alignment(self, chapter_align: dict) -> str:
        """Format chapter alignment for Stage 3 prompt."""
        lines = ["CHAPTER ALIGNMENT:"]
        for section in ['exposition', 'rising_action', 'climax', 'falling_action', 'resolution']:
            if section in chapter_align:
                data = chapter_align[section]
                lines.append(f"  {section.upper().replace('_', ' ')}: Ch.{data.get('chapter_range')} (primary: {data.get('primary_chapter')})")
        return "\n".join(lines)
    
    def run(self):
        """Run the complete kernel creation pipeline"""
        print("\n" + "="*80)
        print(f"KERNEL CREATION PIPELINE - {self.title}")
        print("="*80)
        print(f"Book: {self.book_path.name}")
        print(f"Author: {self.author}")
        print(f"Edition: {self.edition}")
        
        # Stage 0: Structure Alignment
        if not self.stage0_structure_alignment():
            print("\n❌ Pipeline failed at Stage 0")
            return False
        
        # Rate limit protection: wait between API calls
        print("\n⏳ Waiting 60 seconds (rate limit protection)...")
        time.sleep(60)
        
        # Stage 1
        if not self.stage1_extract_freytag():
            print("\nâŒ Pipeline failed at Stage 1")
            return False
        
        print("\n⏳ Waiting 60 seconds (rate limit protection)...")
        time.sleep(60)

        # Stage 2A
        if not self.stage2a_tag_macro():
            print("\nâŒ Pipeline failed at Stage 2A")
            return False
        
        print("\n⏳ Waiting 60 seconds (rate limit protection)...")
        time.sleep(60)

        # Stage 2B
        if not self.stage2b_tag_devices():
            print("\nâŒ Pipeline failed at Stage 2B")
            return False
        
        print("\n⏳ Waiting 60 seconds (rate limit protection)...")
        time.sleep(60)
        
        # Assemble (no API call - no delay needed)
        if not self.assemble_kernel():
            print("\nâŒ Pipeline failed at assembly")
            return False
        
        # Save (no API call - no delay needed)
        if not self.save_kernel():
            print("\nâŒ Pipeline failed at save")
            return False

        # ReasoningDoc generation (final API call)
        if not self.save_reasoning_document():
            print("\nÃ¢Å’ Pipeline failed at reasoning document")
            return False
        
        print("\n" + "="*80)
        print("âœ… KERNEL CREATION COMPLETE!")
        print("="*80)
        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Create kernel JSON for literary analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python create_kernel.py books/TKAM.pdf 'To Kill a Mockingbird' 'Harper Lee' 'Harper Perennial Modern Classics, 2006'
  python create_kernel.py books/TKAM.pdf 'To Kill a Mockingbird' 'Harper Lee' 'Harper Perennial Modern Classics, 2006' --from-stage kernel_stage2b
  python create_kernel.py books/TKAM.pdf 'To Kill a Mockingbird' 'Harper Lee' 'Harper Perennial Modern Classics, 2006' --fresh
  
Note: Chapter count is now auto-detected in Stage 0
        """
    )
    parser.add_argument('book_path', help='Path to book PDF or text file')
    parser.add_argument('title', help='Book title')
    parser.add_argument('author', help='Book author')
    parser.add_argument('edition', help='Book edition')
    parser.add_argument('--from-stage', type=str, choices=['kernel_stage0', 'kernel_stage1', 'kernel_stage2a', 'kernel_stage2b'],
                        help='Force restart from this stage (clears later checkpoints)')
    parser.add_argument('--fresh', action='store_true',
                        help='Clear all checkpoints and start fresh')
    
    args = parser.parse_args()
    
    # Create kernel creator
    creator = KernelCreator(args.book_path, args.title, args.author, args.edition)
    
    # Clear checkpoints if --fresh or --from-stage specified
    if args.fresh:
        creator._clear_checkpoints_from('kernel_stage0')
    elif args.from_stage:
        creator._clear_checkpoints_from(args.from_stage)
    
    # Run pipeline
    success = creator.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
