#!/usr/bin/env python3
"""
KERNEL CREATION AUTOMATION - VERSION 2
Semi-automated kernel creation with review gates

This script automates the Kernel Validation Protocol v3.3:
- Stage 1: Extract 5 Freytag sections
- Stage 2A: Tag 84 macro alignment variables
- Stage 2B: Identify 15-20+ micro devices with examples

User reviews and approves each stage before continuing.
"""

import anthropic
import json
import os
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
    KERNEL_VALIDATION = "Kernel_Validation_Protocol_v3_3.md"
    KERNEL_ENHANCEMENT = "Kernel_Protocol_Enhancement_v3_3.md"
    ARTIFACT_1 = "Artifact_1_-_Device_Taxonomy_by_Alignment_Function"
    ARTIFACT_2 = "Artifact_2_-_Text_Tagging_Protocol"
    LEM = "LEM_-_Stage_1_-_Narrative-Rhetoric_Triangulation"

class KernelCreator:
    """Main class for creating kernel JSONs"""
    
    def __init__(self, book_path: str, title: str, author: str, edition: str, total_chapters: int):
        self.book_path = Path(book_path)
        self.title = title
        self.author = author
        self.edition = edition
        self.total_chapters = total_chapters
        
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
        """Call Claude API with given prompt"""
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
        print("\n" + "="*80)
        print("STAGE 0: BOOK STRUCTURE ALIGNMENT")
        print("="*80)
        
        # Apply conventional distribution formula
        n = self.total_chapters
        
        # Formula from v1.1
        exp_end = max(1, int(n * 0.12))
        ra_end = int(n * 0.50) - 1
        climax_start = int(n * 0.50)
        climax_end = int(n * 0.55)
        
        # Climax refinement: if >3 chapters, narrow to primary ±1
        climax_chapters = climax_end - climax_start + 1
        if climax_chapters > 3:
            primary_climax = int(n * 0.50)
            climax_start = max(1, primary_climax - 1)
            climax_end = min(n, primary_climax + 1)
        
        formula_alignment = {
            'exposition': {
                'start': 1,
                'end': exp_end,
            },
            'rising_action': {
                'start': exp_end + 1,
                'end': ra_end,
            },
            'climax': {
                'start': climax_start,
                'end': climax_end,
            },
            'falling_action': {
                'start': climax_end + 1,
                'end': int(n * 0.85),
            },
            'resolution': {
                'start': int(n * 0.85) + 1,
                'end': n,
            }
        }
        
        print(f"\n📊 Formula-based alignment (N={n}):")
        for stage, ranges in formula_alignment.items():
            count = ranges['end'] - ranges['start'] + 1
            pct = round(count / n * 100)
            print(f"  {stage}: Chapters {ranges['start']}-{ranges['end']} ({count} chapters, {pct}%)")
        
        # Create book sample for climax identification
        book_sample = self._create_book_sample()
        
        # Use Claude to identify actual climax and validate alignment
        prompt = f"""You are performing the Book Structure Alignment Protocol v1.1.

TASK: Identify the actual climax chapter(s) and validate/refine the proposed alignment.

BOOK METADATA:
- Title: {self.title}
- Author: {self.author}
- Edition: {self.edition}
- Total Chapters: {self.total_chapters}

PROTOCOL TO FOLLOW:
{self.protocols['structure_alignment']}

PROPOSED FORMULA ALIGNMENT:
- Exposition: Chapters {formula_alignment['exposition']['start']}-{formula_alignment['exposition']['end']}
- Rising Action: Chapters {formula_alignment['rising_action']['start']}-{formula_alignment['rising_action']['end']}
- Climax: Chapters {formula_alignment['climax']['start']}-{formula_alignment['climax']['end']}
- Falling Action: Chapters {formula_alignment['falling_action']['start']}-{formula_alignment['falling_action']['end']}
- Resolution: Chapters {formula_alignment['resolution']['start']}-{formula_alignment['resolution']['end']}

BOOK SAMPLE (beginning, middle, end):
{book_sample}

CRITICAL TASKS:

1. IDENTIFY THE ACTUAL CLIMAX:
   - Find THE pivotal moment: highest tension, irreversible change, key decision/revelation
   - Determine which chapter(s) contain this moment (1-3 chapters maximum)
   - If climax differs from formula by >3 chapters, note this

2. VALIDATE AND REFINE ALIGNMENT:
   - Check if formula boundaries match narrative content
   - Adjust boundaries if needed (especially for extended rising action)
   - Ensure climax is tight (1-3 chapters)
   - Ensure all chapters 1-{n} are covered with no gaps

3. OUTPUT VALIDATED ALIGNMENT:
   Provide a JSON object with this structure:
   {{
     "structure_detection": {{
       "structure_type": "NUM",
       "total_units": {n},
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
         "chapter_range": "Z+1-{n}",
         "chapters": [...],
         "primary_chapter": {n},
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
✓ All chapters 1-{n} must be included (no gaps, no overlaps)
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
        
        # Validate required fields
        if 'chapter_alignment' not in alignment_json:
            print(f"\n❌ Error: Missing 'chapter_alignment' in response")
            return False
        
        # Validate all chapters are covered
        all_chapters = set()
        for stage, data in alignment_json['chapter_alignment'].items():
            chapters = data.get('chapters', [])
            all_chapters.update(chapters)
        
        expected_chapters = set(range(1, n + 1))
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
            return True
        return False
    
    def stage1_extract_freytag(self):
        """Stage 1: Extract 5 Freytag sections with chapter ranges"""
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
        
        prompt = f"""You are performing Stage 1 of the Kernel Validation Protocol v3.3.

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

PROTOCOL REFERENCE: Kernel Validation Protocol v3.3 - Stage 1 (Freytag Section Identification)

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
      "rationale": "why this represents exposition (2-3 sentences)",
      "text": "extract 400-600 words from primary chapter"
    }},
    "rising_action": {{
      "chapter_range": "[use validated range from Stage 0]",
      "primary_chapter": [use validated primary from Stage 0],
      "rationale": "why this represents rising action (2-3 sentences)",
      "text": "extract 400-600 words from primary chapter"
    }},
    "climax": {{
      "chapter_range": "[use validated range from Stage 0]",
      "primary_chapter": [use validated primary from Stage 0],
      "rationale": "why this represents climax (2-3 sentences)",
      "text": "extract 400-600 words from primary chapter"
    }},
    "falling_action": {{
      "chapter_range": "[use validated range from Stage 0]",
      "primary_chapter": [use validated primary from Stage 0],
      "rationale": "why this represents falling action (2-3 sentences)",
      "text": "extract 400-600 words from primary chapter"
    }},
    "resolution": {{
      "chapter_range": "[use validated range from Stage 0]",
      "primary_chapter": [use validated primary from Stage 0],
      "rationale": "why this represents resolution (2-3 sentences)",
      "text": "extract 400-600 words from primary chapter"
    }}
  }}
}}

VERIFICATION CHECKLIST:
✓ Chapter ranges match the validated alignment from Stage 0 exactly
✓ Each section has primary_chapter matching Stage 0 alignment
✓ Each section has text extract (400-600 words) from primary chapter
✓ Each section has a clear, specific rationale
✓ Chapter ranges use numeric-only format: "1-3" NOT "Chapters 1-3"

CRITICAL FORMAT REQUIREMENT:
- chapter_range MUST be numeric-only: "1-3", "15", "4-14"
- Do NOT include "Chapters " prefix in chapter_range values
- Example: "chapter_range": "1-3" ✅ NOT "chapter_range": "Chapters 1-3" ❌

CRITICAL: Output ONLY valid JSON. No additional text before or after the JSON.
DO NOT extract or reproduce any text passages from the book.
"""
        
        system_prompt = "You are a literary analysis expert following the Kernel Validation Protocol v3.3 for extracting Freytag dramatic structure sections from novels."
        
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
            return True
        return False
    
    def stage2a_tag_macro(self):
        """Stage 2A: Tag 84 macro alignment variables"""
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
        
        prompt = f"""You are performing Stage 2A of the Kernel Validation Protocol v3.3.

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
        
        system_prompt = "You are a literary analysis expert tagging macro alignment variables according to Kernel Validation Protocol v3.3."
        
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
            return True
        return False
    
    def stage2b_tag_devices(self):
        """Stage 2B: Tag 8-12 micro devices with examples"""
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

BOOK METADATA:

- Title: {self.title}

- Author: {self.author}

- Edition: {self.edition}

DEVICE TAXONOMY (Use ONLY these devices):

{self.protocols['artifact_1']}

FREYTAG EXTRACTS:

{extracts_text}

OUTPUT FORMAT:

Provide a JSON array of devices. Each device must be from the taxonomy above:

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

"""
        
        system_prompt = "You are a literary analysis expert identifying and cataloging micro literary devices according to Kernel Protocol Enhancement v3.3."
        
        result = self._call_claude(prompt, system_prompt)
        
        # Clean and validate
        result = result.replace('```json\n', '').replace('```\n', '').replace('```', '').strip()
        
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
        

        # Review
        if self._review_and_approve("Stage 2B: Micro Devices", result_formatted):
            self.stage2b_devices = devices_json
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
                "kernel_version": "3.5",
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
            filename = f"{safe_title}_kernel_v3_5.json"
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
        """Generate narrative reasoning document"""
        if not self.kernel:
            print("âŒ Error: No kernel to save reasoning for")
            return False
    
        if not output_path:
            safe_title = "".join(c for c in self.title if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title.replace(' ', '_')
            filename = f"{safe_title}_ReasoningDoc_v3.5.md"
            output_path = Config.KERNELS_DIR / filename
    
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
        # Generate reasoning doc
        prompt = f"""Create a narrative reasoning document explaining the literary analysis decisions for "{self.title}" by {self.author}.

    STRUCTURE:
    1. Overview of text and alignment pattern
    2. Justification for macro variable selections (Stage 2A)
    3. Explanation of device selections and their alignment functions (Stage 2B)
    4. Summary of how devices mediate the macro alignment
    
    Be clear and pedagogical - explain WHY these analytical choices were made."""
    
        system_prompt = "You are documenting literary analysis decisions."
        result = self._call_claude(prompt, system_prompt)
    
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
    
        print(f"\nâœ… Reasoning document saved: {output_path}")
        print(f"   Size: {output_path.stat().st_size:,} bytes")
        return True
    
    def run(self):
        """Run the complete kernel creation pipeline"""
        print("\n" + "="*80)
        print(f"KERNEL CREATION PIPELINE - {self.title}")
        print("="*80)
        print(f"Book: {self.book_path.name}")
        print(f"Author: {self.author}")
        print(f"Edition: {self.edition}")
        
        # Stage 0: Structure Alignment (NEW)
        if not self.stage0_structure_alignment():
            print("\n❌ Pipeline failed at Stage 0")
            return False
        
        # Rate limit protection: wait 60 seconds before Stage 1
        print("\n⏳ Waiting 60 seconds to avoid rate limits...")
        time.sleep(60)
        
        # Stage 1
        if not self.stage1_extract_freytag():
            print("\nâŒ Pipeline failed at Stage 1")
            return False
        
        # Rate limit protection: wait 60 seconds before Stage 2A
        print("\n⏳ Waiting 60 seconds to avoid rate limits...")
        time.sleep(60)

        # Stage 2A
        if not self.stage2a_tag_macro():
            print("\nâŒ Pipeline failed at Stage 2A")
            return False
        
        # Rate limit protection: wait 60 seconds before Stage 2B
        print("\n⏳ Waiting 60 seconds to avoid rate limits...")
        time.sleep(60)

        # Stage 2B
        if not self.stage2b_tag_devices():
            print("\nâŒ Pipeline failed at Stage 2B")
            return False
        
        # Assemble
        if not self.assemble_kernel():
            print("\nâŒ Pipeline failed at assembly")
            return False
        
        # Save
        if not self.save_kernel():
            print("\nâŒ Pipeline failed at save")
            return False

        if not self.save_reasoning_document():
            print("\nÃ¢Å’ Pipeline failed at reasoning document")
            return False
        
        print("\n" + "="*80)
        print("âœ… KERNEL CREATION COMPLETE!")
        print("="*80)
        return True


def main():
    """Main entry point"""
    if len(sys.argv) < 6:
        print("Usage: python create_kernel.py <book_path> <title> <author> <edition> <total_chapters>")
        print("Example: python create_kernel.py books/TKAM.pdf 'To Kill a Mockingbird' 'Harper Lee' 'Harper Perennial Modern Classics, 2006' 31")
        sys.exit(1)
    
    book_path = sys.argv[1]
    title = sys.argv[2]
    author = sys.argv[3]
    edition = sys.argv[4]
    total_chapters = int(sys.argv[5])
    
    # Create kernel creator
    creator = KernelCreator(book_path, title, author, edition, total_chapters)
    
    # Run pipeline
    success = creator.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
