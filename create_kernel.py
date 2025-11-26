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
    STRUCTURE_ALIGNMENT = "Book_Structure_Alignment_Protocol_v1.md"
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
    
    def _extract_text_from_chapter_range(self, chapter_range: str, primary_chapter: int, word_count: int = 400) -> str:
        """Extract representative text from a chapter range
        
        Args:
            chapter_range: Chapter range string (e.g., "1-3", "15", "8-14")
            primary_chapter: The most representative chapter in the range
            word_count: Approximate words to extract (default: 400)
            
        Returns:
            String of extracted text from the book
        """
        total_words = len(self.book_words)
        words_per_chapter = total_words / self.total_chapters
        
        # Calculate word position for primary chapter
        # Center the extract around the primary chapter
        primary_start_word = int((primary_chapter - 1) * words_per_chapter)
        primary_end_word = int(primary_chapter * words_per_chapter)
        primary_middle = (primary_start_word + primary_end_word) // 2
        
        # Extract word_count words centered on primary chapter middle
        extract_start = max(0, primary_middle - (word_count // 2))
        extract_end = min(total_words, primary_middle + (word_count // 2))
        
        # Ensure we get at least word_count words if possible
        if extract_end - extract_start < word_count and extract_end < total_words:
            extract_end = min(total_words, extract_start + word_count)
        if extract_end - extract_start < word_count and extract_start > 0:
            extract_start = max(0, extract_end - word_count)
        
        extracted_text = ' '.join(self.book_words[extract_start:extract_end])
        return extracted_text
    
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
        
        prompt = f"""You are performing Stage 2A of the Kernel Validation Protocol v3.4.

TASK: Analyze the 5 Freytag extracts and tag all 84 macro alignment variables:
- Narrative variables (voice, structure, etc.)
- Rhetorical variables (alignment type, mechanisms, etc.)

BOOK METADATA:
- Title: {self.title}
- Author: {self.author}

PROTOCOL TO FOLLOW:
{self.protocols['kernel_validation']}

TAGGING PROTOCOL:
{self.protocols['artifact_2']}

FREYTAG EXTRACTS:
{extracts_text}

OUTPUT FORMAT:
Provide a JSON object with this structure:
{{
  "narrative": {{
    "voice": {{
      "pov": "CODE",
      "pov_description": "explanation",
      "focalization": "CODE",
      "focalization_description": "explanation",
      "reliability": "CODE",
      "temporal_distance": "CODE",
      "mode_dominance": "CODE",
      "character_revelation": "CODE"
    }},
    "structure": {{
      "plot_architecture": "CODE",
      "plot_architecture_description": "explanation",
      "chronology": "CODE",
      "causation": "CODE",
      "pacing_dominance": "CODE"
    }}
  }},
  "rhetoric": {{
    "alignment_type": "CODE",
    "alignment_type_description": "explanation",
    "dominant_mechanism": "CODE",
    "secondary_mechanism": "CODE",
    "alignment_strength": "STRONG/MODERATE/WEAK"
  }},
  "device_mediation": {{
    "score": 0.0,
    "description": "how devices mediate alignment"
  }}
}}

CRITICAL: Output ONLY valid JSON. Use the exact codes from the protocol.
"""
        
        system_prompt = "You are a literary analysis expert tagging macro alignment variables according to Kernel Validation Protocol v3.4."
        
        result = self._call_claude(prompt, system_prompt)
        
        # Clean and validate
        result = result.replace('```json\n', '').replace('```\n', '').replace('```', '').strip()
        
        try:
            macro_json = json.loads(result)
            result_formatted = json.dumps(macro_json, indent=2)
        except json.JSONDecodeError as e:
            print(f"\nâŒ Error: Invalid JSON response from Claude")
            print(f"Error details: {e}")
            return False
        
        # Review
        if self._review_and_approve("Stage 2A: Macro Variables", result_formatted):
            self.stage2a_macro = macro_json
            self._save_checkpoint('kernel_stage2a', self.stage2a_macro)
            return True
        return False
    
    def stage2b_tag_devices(self):
        """Stage 2B: Tag 8-12 micro devices with examples"""
        # Check for existing checkpoint
        cached = self._load_checkpoint('kernel_stage2b')
        if cached:
            self.stage2b_devices = cached
            return True
        
        print("\n" + "="*80)
        print("STAGE 2B: MICRO DEVICE INVENTORY")
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
        
        prompt = f"""You are performing Stage 2B of the Kernel Protocol Enhancement v3.3.

TASK: Identify micro literary devices FOR EACH NARRATIVE SECTION with quoted examples.

CRITICAL CONSTRAINT - VALID DEVICES ONLY:

You must ONLY use devices from the Device Taxonomy (Artifact 1). Do NOT invent new device names.

Valid devices include:

- Narrative Structure: Linear Chronology, Non-Linear Chronology, Frame Narrative, In Medias Res, Circular Structure, Episodic Structure, Climactic Structure

- Narrative Voice: First-Person Narration, Third-Person Omniscient, Third-Person Limited, Unreliable Narrator, Free Indirect Discourse, Stream of Consciousness, Internal Monologue

- Dialogue/Speech: Dialogue, Dialect

- Temporal: Foreshadowing, Flashback, Flashforward

- Pacing: Scene, Summary, Pause, Ellipsis

- Figurative Language: Metaphor, Simile, Personification, Hyperbole, Understatement, Imagery, Euphemism, Allusion

- Symbolic: Symbolism, Allegory, Motif

- Irony (MUST specify type): Verbal Irony, Situational Irony, Dramatic Irony, Structural Irony

- Sound/Rhythm: Alliteration, Rhythm, Onomatopoeia

- Structural Repetition: Parallelism, Anaphora, Epistrophe, Chiasmus, Repetition

- Contrast: Juxtaposition, Paradox, Oxymoron, Foil

- Character: Direct Characterization, Indirect Characterization

- Atmosphere: Pathetic Fallacy, Setting as Symbol

- Tension: Suspense, Cliffhanger, Red Herring

- Rhetorical: Apostrophe, Rhetorical Question, Pathos

NAMING RULES:

- Use base names only (e.g., "Motif" not "Hope Motif")

- Always specify irony type (e.g., "Dramatic Irony" not "Irony")

- Match taxonomy names exactly

- Do NOT invent new device names

If a section has limited device variety, the SAME device may appear in multiple sections with DIFFERENT examples. For instance, Symbolism can appear in exposition AND resolution if both sections contain symbolic elements.

SECTION REQUIREMENTS:

You must identify 3-4 devices PER FREYTAG SECTION with examples from that section's chapters:

- Exposition: 3-4 devices with examples from chapters {self.stage1_extracts['extracts']['exposition']['chapter_range']}

- Rising Action: 3-4 devices with examples from chapters {self.stage1_extracts['extracts']['rising_action']['chapter_range']}

- Climax: 3-4 devices with examples from chapters {self.stage1_extracts['extracts']['climax']['chapter_range']}

- Falling Action: 3-4 devices with examples from chapters {self.stage1_extracts['extracts']['falling_action']['chapter_range']}

- Resolution: 3-4 devices with examples from chapters {self.stage1_extracts['extracts']['resolution']['chapter_range']}

Total: 15-20 devices across all sections.

DEVICE SELECTION CRITERIA:

For each section, choose devices that BEST demonstrate the macro-micro alignment for that narrative stage:

- Exposition devices: How character/setting are established

- Rising Action devices: How tension builds

- Climax devices: How the turning point is created

- Falling Action devices: How consequences unfold

- Resolution devices: How closure is achieved

TIER-BASED EXAMPLE LOCATION:

When finding examples for each device, locate them in the Freytag section that matches their pedagogical tier:

- Tier 1 devices (Imagery, Simile, Hyperbole, Metaphor): find in EXPOSITION chapters
- Tier 2 devices (Dialogue, Repetition, Direct Characterization): find in RISING ACTION chapters
- Tier 3 devices (Symbolism, Motif, Foreshadowing, Juxtaposition): find in CLIMAX chapters
- Tier 4 devices (Verbal Irony, Dramatic Irony, Suspense): find in FALLING ACTION chapters
- Tier 5 devices (Third-Person Omniscient, Third-Person Limited, First-Person, First-Person Narration, Internal Monologue, Stream of Consciousness, Unreliable Narrator, Free Indirect Discourse, Frame Narrative, Narrator, Point of View): find in RESOLUTION chapters

CRITICAL FOR TIER 5: Voice/narrative devices exist throughout the text, but you MUST find examples from RESOLUTION chapters specifically. These devices frame the entire narrative, so find where they are most evident in the story's conclusion. Do NOT use exposition examples for Tier 5 devices.

This ensures pedagogical progression from concrete to abstract, matching device complexity to narrative development.

BOOK METADATA:

- Title: {self.title}

- Author: {self.author}

- Edition: {self.edition}

DEVICE TAXONOMY (Use ONLY these devices):

{self.protocols['artifact_1']}

FREYTAG EXTRACTS:

{extracts_text}

CRITICAL: STRUCTURED DEVICE ANALYSIS REQUIRED

For EACH device you identify, you must provide:

1. **worksheet_context** - Contextual data for worksheet generation:

   a) **subject**: What does this device operate on in THIS specific text?
      - NOT a generic object like "characters" or "setting"
      - BUT a specific concept/theme/element from THIS book
      - Examples: "parental delusion", "Matilda's intellectual isolation", "Miss Trunchbull's tyranny"
      - Extract from the actual scenes/quotes where the device appears

   b) **scene_description**: Brief description of where this device appears
      - Will be used in worksheet "Where to look" prompts
      - Should reference specific scene/moment
      - Examples: "opening commentary on parents' blind admiration", "description of Miss Trunchbull's office", "Matilda's first library visit"

   c) **specific_function**: What does this device DO in this text?
      - NOT the generic definition of the device
      - BUT its specific purpose/role in THIS narrative
      - Start with action verbs: "establishes", "reveals", "creates", "emphasizes", "contrasts"
      - Examples: "establishes narrator's satirical perspective on parental bias", "creates immediate threat through vivid sensory detail"

2. **effects** - Three concrete effects (one per category):

   a) **reader_response** (category): How does this device affect what readers FEEL or EXPERIENCE?
      - Focus on emotional/sensory/experiential impact
      - Examples: "Makes readers recognize the absurdity of parental bias", "Creates visceral discomfort at institutional cruelty"

   b) **meaning_creation** (category): How does this device build UNDERSTANDING or reveal IDEAS?
      - Focus on what readers learn/understand/perceive
      - Examples: "Reveals how universal parental delusion blinds judgment", "Shows the systematic nature of educational abuse"

   c) **thematic_impact** (category): How does this device connect to the text's BIGGER MESSAGE or THEME?
      - Focus on thematic significance and broader meaning
      - Examples: "Establishes theme of adults systematically failing children", "Reinforces message about intellectual empowerment"

ANALYSIS QUALITY REQUIREMENTS:

- All analysis must be TEXT-SPECIFIC (not generic device descriptions)
- Subject must be a concrete concept/element from THIS book
- Function must describe THIS device's role in THIS narrative
- Effects must be substantive (not vague like "creates meaning" or "affects reader")
- Draw from actual examples in the text
- Be pedagogically clear (students will read these)

OUTPUT FORMAT:

Provide a JSON array of devices. Each device must be from the taxonomy above AND include structured analysis:

[

  {{

    "name": "Device Name (MUST match taxonomy exactly)",

    "layer": "CODE (N/B/R)",

    "function": "CODE (Re/Me/Te)",

    "engagement": "CODE (T/V/F)",

    "classification": "Layer|Function|Engagement",

    "definition": "student-facing definition",

    "student_facing_type": "Figurative Language/Sound Device/Narrative Technique/etc.",

    "pedagogical_function": "what it does for reader/theme",

    "position_code": "DIST/CLUST-BEG/CLUST-MID/CLUST-END",

    "assigned_section": "exposition/rising_action/climax/falling_action/resolution",

    "worksheet_context": {{
      "subject": "What this device operates on in THIS text (e.g., 'parental delusion', 'Matilda's genius', 'institutional cruelty')",
      "scene_description": "Brief scene description for worksheet 'Where to look' prompts (e.g., 'opening commentary on parents' blind admiration')",
      "specific_function": "What this device SPECIFICALLY does in this text (NOT generic definition - e.g., 'establishes narrator's satirical perspective on parental bias')"
    }},

    "effects": [
      {{
        "text": "Specific reader response effect (e.g., 'Makes readers recognize the absurdity of parental bias')",
        "category": "reader_response"
      }},
      {{
        "text": "Specific meaning creation effect (e.g., 'Reveals how universal parental delusion blinds judgment')",
        "category": "meaning_creation"
      }},
      {{
        "text": "Specific thematic impact effect (e.g., 'Establishes theme of adults systematically failing children')",
        "category": "thematic_impact"
      }}
    ],

    "examples": [

      {{

        "freytag_section": "must match assigned_section",

        "scene": "brief scene identifier",

        "chapter": X,

        "page_range": "X-Y",

        "quote_snippet": "20-100 character exact quote from text"

      }}

    ]

  }}

]

CRITICAL RULES:

1. Output ONLY valid JSON array

2. Device names MUST match the taxonomy exactly - no invented names

3. Every device must have assigned_section field

4. Examples must come from the assigned section's chapters only

5. Include 2-3 examples per device from that section

6. ALL 5 sections must have 3-4 devices each

7. Use base device names (not "Hope Motif", just "Motif")

8. Always specify irony type (Verbal/Situational/Dramatic/Structural)

9. EVERY device must have complete worksheet_context with subject, scene_description, and specific_function

10. EVERY device must have 3 effects (one per category: reader_response, meaning_creation, thematic_impact)

11. All analysis fields must be TEXT-SPECIFIC (not generic device descriptions)

12. Subject must reference actual concepts/themes/elements from THIS book

"""
        
        system_prompt = "You are a literary analysis expert identifying and cataloging micro literary devices with structured pedagogical analysis according to Kernel Protocol Enhancement v3.3. For each device, provide text-specific contextual analysis including subject, function, and concrete effects."
        
        result = self._call_claude(prompt, system_prompt)
        
        # Clean and validate
        result = result.replace('```json\n', '').replace('```\n', '').replace('```', '').strip()
        
        # Comprehensive JSON sanitization
        def clean_json_string(match):
            content = match.group(1)
            content = content.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
            content = re.sub(r'(?<!\\)"', '\\"', content)  # escape unescaped quotes
            return f'"{content}"'
        
        result = re.sub(r'"((?:[^"\\]|\\.)*?)"', clean_json_string, result)
        
        try:
            devices_json = json.loads(result)
            result_formatted = json.dumps(devices_json, indent=2)
        except json.JSONDecodeError as e:
            print(f"\nâŒ Error: Invalid JSON response from Claude")
            print(f"Error details: {e}")
            # Save problematic response for debugging
            debug_path = Config.OUTPUTS_DIR / "stage2b_debug_response.json"
            with open(debug_path, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"Debug: Saved problematic response to {debug_path}")
            print(f"Response length: {len(result)} characters")
            print(f"First 500 characters: {result[:500]}")
            return False
        
        # Validate minimum requirements
        device_count = len(devices_json)
        if device_count < 15:
            print(f"\nâš ï¸  Warning: Only {device_count} devices found (minimum 15 required, target: 20)")
        
        # Validate section distribution
        section_counts = {
            "exposition": 0,
            "rising_action": 0,
            "climax": 0,
            "falling_action": 0,
            "resolution": 0
        }
        
        missing_assigned_section = []
        for device in devices_json:
            assigned_section = device.get("assigned_section")
            if not assigned_section:
                missing_assigned_section.append(device.get("name", "Unknown"))
            elif assigned_section in section_counts:
                section_counts[assigned_section] += 1
        
        if missing_assigned_section:
            print(f"\n⚠️  Warning: {len(missing_assigned_section)} device(s) missing 'assigned_section' field")
        
        # Validate structured analysis fields
        missing_worksheet_context = []
        missing_effects = []
        incomplete_worksheet_context = []
        incomplete_effects = []
        
        for device in devices_json:
            device_name = device.get("name", "Unknown")
            
            # Check worksheet_context
            worksheet_context = device.get("worksheet_context")
            if not worksheet_context:
                missing_worksheet_context.append(device_name)
            else:
                required_fields = ["subject", "scene_description", "specific_function"]
                missing_fields = [field for field in required_fields if not worksheet_context.get(field)]
                if missing_fields:
                    incomplete_worksheet_context.append(f"{device_name}: missing {', '.join(missing_fields)}")
            
            # Check effects
            effects = device.get("effects")
            if not effects:
                missing_effects.append(device_name)
            else:
                if len(effects) < 3:
                    incomplete_effects.append(f"{device_name}: only {len(effects)} effect(s) (need 3)")
                else:
                    categories = [e.get("category") for e in effects]
                    required_categories = ["reader_response", "meaning_creation", "thematic_impact"]
                    missing_categories = [cat for cat in required_categories if cat not in categories]
                    if missing_categories:
                        incomplete_effects.append(f"{device_name}: missing categories {', '.join(missing_categories)}")
        
        if missing_worksheet_context:
            print(f"\n⚠️  Warning: {len(missing_worksheet_context)} device(s) missing 'worksheet_context' field")
        if incomplete_worksheet_context:
            print(f"\n⚠️  Warning: Incomplete worksheet_context:")
            for info in incomplete_worksheet_context:
                print(f"  - {info}")
        if missing_effects:
            print(f"\n⚠️  Warning: {len(missing_effects)} device(s) missing 'effects' field")
        if incomplete_effects:
            print(f"\n⚠️  Warning: Incomplete effects:")
            for info in incomplete_effects:
                print(f"  - {info}")
        
        # Check section distribution
        sections_with_few_devices = []
        for section, count in section_counts.items():
            if count < 3:
                sections_with_few_devices.append(f"{section}: {count} devices (need 3-4)")
        
        if sections_with_few_devices:
            print(f"\n⚠️  Warning: Some sections have insufficient devices:")
            for section_info in sections_with_few_devices:
                print(f"  - {section_info}")
        
        print(f"\n✓ Device distribution by section:")
        for section, count in section_counts.items():
            print(f"  - {section}: {count} devices")
        
        # Relocate Tier 5 devices to resolution (they're pervasive but should be taught last)
        devices_json = self._relocate_tier5_devices(devices_json)
        
        # Remove duplicate devices, keeping tier-appropriate ones
        devices_json = self._deduplicate_devices(devices_json)
        
        # Filter out POV devices that contradict the text's actual POV
        macro_pov = self.stage2a_macro.get('narrative', {}).get('voice', {}).get('pov', 'TPO')
        devices_json = self._filter_contradictory_pov_devices(devices_json, macro_pov)
        
        # Validate tier alignment
        misaligned = self._validate_tier_alignment(devices_json)
        if misaligned:
            print(f"\n⚠️  Warning: {len(misaligned)} device example(s) not in tier-appropriate section:")
            for item in misaligned[:5]:
                print(f"  - {item['device']} (Tier {item['tier']}): expected {item['expected']}, found in {item['actual']}")
            if len(misaligned) > 5:
                print(f"  ... and {len(misaligned) - 5} more")
        
        # Add pedagogical_tier to each device
        for device in devices_json:
            device_name = device.get("name", "")
            device["pedagogical_tier"] = DEVICE_TIER_MAP.get(device_name, 0)
        
        # Update result_formatted with pedagogical_tier added
        result_formatted = json.dumps(devices_json, indent=2)

        # Review
        if self._review_and_approve("Stage 2B: Micro Devices", result_formatted):
            self.stage2b_devices = devices_json
            self._save_checkpoint('kernel_stage2b', self.stage2b_devices)
            return True
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
