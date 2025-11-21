#!/usr/bin/env python3
"""
KERNEL CREATION AUTOMATION - VERSION 3.4
Chapter-aware kernel creation

NEW IN v3.4:
- Captures chapter numbers for all Freytag sections
- Includes chapter numbers in device examples
- Creates narrative_position_mapping for downstream pipeline
- Enables chapter-based worksheet generation

This script automates the Kernel Validation Protocol v3.3 with chapter awareness:
- Stage 1A: Identify Freytag section boundaries WITH CHAPTER RANGES
- Stage 1B: Extract focused passages and record chapters
- Stage 2A: Tag macro alignment variables
- Stage 2B: Identify devices with chapter-aware examples

User reviews and approves each stage before continuing.
"""

import anthropic
import json
import os
import sys
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
    KERNEL_VALIDATION = "Kernel_Validation_Protocol_v3_3.md"
    KERNEL_ENHANCEMENT = "Kernel_Protocol_Enhancement_v3_3.md"
    ARTIFACT_1 = "Artifact_1_-_Device_Taxonomy_by_Alignment_Function"
    ARTIFACT_2 = "Artifact_2_-_Text_Tagging_Protocol"
    LEM = "LEM_-_Stage_1_-_Narrative-Rhetoric_Triangulation"

class KernelCreator:
    """Main class for creating kernel JSONs with chapter awareness"""
    
    def __init__(self, book_path: str, title: str, author: str, edition: str):
        self.book_path = Path(book_path)
        self.title = title
        self.author = author
        self.edition = edition
        
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
        self.stage1a_boundaries = None
        self.stage1b_extracts = None
        self.stage2a_macro = None
        self.stage2b_devices = None
        self.narrative_position_mapping = None  # NEW: Chapter mapping
        self.kernel = None
        
    def _load_protocols(self) -> Dict[str, str]:
        """Load all protocol markdown files"""
        print("\n📚 Loading protocols...")
        protocols = {}
        
        protocol_files = {
            "kernel_validation": Config.KERNEL_VALIDATION,
            "kernel_enhancement": Config.KERNEL_ENHANCEMENT,
            "artifact_1": Config.ARTIFACT_1,
            "artifact_2": Config.ARTIFACT_2,
            "lem": Config.LEM
        }
        
        for key, filename in protocol_files.items():
            filepath = Config.PROTOCOLS_DIR / filename
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    protocols[key] = f.read()
                print(f"  ✓ Loaded: {filename}")
            else:
                print(f"  ⚠ Missing: {filename}")
        
        return protocols
    
    def _load_book(self) -> str:
        """Extract text from PDF"""
        print(f"\n📖 Loading book: {self.book_path}")
        
        if not self.book_path.exists():
            raise FileNotFoundError(f"Book not found: {self.book_path}")
        
        text = ""
        with open(self.book_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            print(f"  Total pages: {total_pages}")
            
            for i, page in enumerate(pdf_reader.pages):
                if i % 50 == 0 and i > 0:
                    print(f"  Extracting... {i}/{total_pages} pages")
                text += page.extract_text()
        
        word_count = len(text.split())
        print(f"  ✓ Extracted {word_count:,} words")
        
        return text
    
    def _call_claude(self, prompt: str, system_prompt: str) -> str:
        """Call Claude API"""
        messages = [{"role": "user", "content": prompt}]
        
        response = self.client.messages.create(
            model=Config.MODEL,
            max_tokens=Config.MAX_TOKENS,
            system=system_prompt,
            messages=messages
        )
        
        return response.content[0].text
    
    def _review_and_approve(self, stage_name: str, output: str) -> bool:
        """Display output and get user approval"""
        print("\n" + "="*80)
        print(f"REVIEW: {stage_name}")
        print("="*80)
        print(output)
        print("="*80)
        
        while True:
            response = input("\n✓ Approve and continue? [y/n/save/quit]: ").lower().strip()
            
            if response == 'y':
                return True
            elif response == 'n':
                print("❌ Stage rejected. Please restart or modify manually.")
                return False
            elif response == 'save':
                filename = f"{stage_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                save_path = Config.OUTPUTS_DIR / filename
                save_path.parent.mkdir(parents=True, exist_ok=True)
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(output)
                print(f"💾 Saved to: {save_path}")
                continue
            elif response == 'quit':
                print("👋 Exiting...")
                sys.exit(0)
            else:
                print("Invalid response. Please enter y/n/save/quit")
    
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
    
    def stage1a_identify_boundaries(self):
        """Stage 1A: Identify Freytag section boundaries WITH CHAPTER RANGES"""
        print("\n" + "="*80)
        print("STAGE 1A: IDENTIFY FREYTAG BOUNDARIES (WITH CHAPTERS)")
        print("="*80)
        
        book_sample = self._create_book_sample()
        
        # NEW v3.4: Request chapter information
        prompt = f"""You are performing Stage 1A: Identifying Freytag dramatic structure boundaries.

TASK: Analyze this book sample and identify WHERE each Freytag section occurs, INCLUDING CHAPTER NUMBERS.

BOOK METADATA:
- Title: {self.title}
- Author: {self.author}
- Edition: {self.edition}

BOOK SAMPLE (beginning, middle, end):
{book_sample}

INSTRUCTIONS:
Identify the approximate location of each Freytag section:
1. Exposition - Where does the story begin? Character/setting introduction
2. Rising Action - Where does conflict develop and escalate?
3. Climax - What is the turning point / peak tension?
4. Falling Action - What happens immediately after the climax?
5. Resolution - How does the story end?

For each section, provide:
- Approximate word position (e.g., "words 1000-5000")
- Chapter range (e.g., "1-3" or "15" for single chapter) **NEW v3.4**
- Primary chapter (single chapter with densest content) **NEW v3.4**
- Page range if identifiable (e.g., "3-45") **NEW v3.4**
- Brief description of what happens there
- Key characters/events that signal this section

**CRITICAL v3.4:** If the text has no chapters (e.g., novellas), use page ranges instead. 
For page-only texts, use format: "primary_chapter": "pages 1-15"

OUTPUT FORMAT (JSON):
{{
  "text_structure": {{
    "has_chapters": true,
    "total_chapters_estimate": 31,
    "notes": "Chapter breaks clearly visible" or "No chapters, using pages"
  }},
  "exposition": {{
    "word_start": 0,
    "word_end": 5000,
    "chapter_start": 1,
    "chapter_end": 3,
    "primary_chapter": 1,
    "page_range": "3-45",
    "description": "Scout introduces her family and Maycomb...",
    "key_events": ["Introduction of Atticus", "Boo Radley mystery begins"]
  }},
  "rising_action": {{
    "word_start": 5000,
    "word_end": 40000,
    "chapter_start": 4,
    "chapter_end": 14,
    "primary_chapter": 8,
    "page_range": "46-180",
    "description": "...",
    "key_events": [...]
  }},
  "climax": {{
    "word_start": 40000,
    "word_end": 45000,
    "chapter_start": 15,
    "chapter_end": 15,
    "primary_chapter": 15,
    "page_range": "181-195",
    "description": "...",
    "key_events": [...]
  }},
  "falling_action": {{
    "word_start": 45000,
    "word_end": 65000,
    "chapter_start": 16,
    "chapter_end": 25,
    "primary_chapter": 20,
    "page_range": "196-280",
    "description": "...",
    "key_events": [...]
  }},
  "resolution": {{
    "word_start": 65000,
    "word_end": 75000,
    "chapter_start": 26,
    "chapter_end": 31,
    "primary_chapter": 28,
    "page_range": "281-324",
    "description": "...",
    "key_events": [...]
  }}
}}

CRITICAL: Output ONLY valid JSON. The word positions and chapters are estimates based on the sample - that's fine.
Chapter numbers should be your best estimate based on how chapter markers appear in the text.
"""
        
        system_prompt = "You are a literary analysis expert identifying Freytag dramatic structure boundaries with chapter awareness."
        
        print("\n🤖 Calling Claude API...")
        result = self._call_claude(prompt, system_prompt)
        
        # Clean and validate
        result = result.replace('```json\n', '').replace('```\n', '').replace('```', '').strip()
        
        try:
            boundaries_json = json.loads(result)
            result_formatted = json.dumps(boundaries_json, indent=2)
        except json.JSONDecodeError as e:
            print(f"\n❌ Error: Invalid JSON response")
            print(f"Error: {e}")
            return False
        
        # Review
        if self._review_and_approve("Stage 1A: Boundaries with Chapters", result_formatted):
            self.stage1a_boundaries = boundaries_json
            
            # NEW v3.4: Create narrative position mapping
            self._create_narrative_position_mapping()
            return True
        return False
    
    def _create_narrative_position_mapping(self):
        """NEW v3.4: Create chapter mapping from Stage 1A boundaries"""
        print("\n📍 Creating narrative position → chapter mapping...")
        
        if not self.stage1a_boundaries:
            print("⚠️ No boundaries to map")
            return
        
        mapping = {}
        text_structure = self.stage1a_boundaries.get('text_structure', {})
        has_chapters = text_structure.get('has_chapters', True)
        
        for section in ['exposition', 'rising_action', 'climax', 'falling_action', 'resolution']:
            if section in self.stage1a_boundaries:
                data = self.stage1a_boundaries[section]
                
                if has_chapters:
                    # Chapter-based mapping
                    chapter_start = data.get('chapter_start', 'unknown')
                    chapter_end = data.get('chapter_end', 'unknown')
                    primary_chapter = data.get('primary_chapter', 'unknown')
                    
                    if chapter_start == chapter_end:
                        chapter_range = str(chapter_start)
                    else:
                        chapter_range = f"{chapter_start}-{chapter_end}"
                    
                    mapping[section] = {
                        "chapter_range": chapter_range,
                        "primary_chapter": primary_chapter,
                        "pages": data.get('page_range', 'unknown')
                    }
                else:
                    # Page-based mapping (for novellas)
                    mapping[section] = {
                        "chapter_range": "N/A",
                        "primary_chapter": data.get('primary_chapter', data.get('page_range', 'unknown')),
                        "pages": data.get('page_range', 'unknown')
                    }
        
        self.narrative_position_mapping = mapping
        
        print("✓ Narrative position mapping created:")
        print(json.dumps(mapping, indent=2))
    
    def stage1b_extract_passages(self):
        """Stage 1B: Extract focused passages from each section"""
        print("\n" + "="*80)
        print("STAGE 1B: EXTRACT FOCUSED PASSAGES")
        print("="*80)
        
        if not self.stage1a_boundaries:
            print("❌ Error: Stage 1A boundaries not available")
            return False
        
        extracts = {}
        
        # Extract each section
        for section in ['exposition', 'rising_action', 'climax', 'falling_action', 'resolution']:
            if section not in self.stage1a_boundaries:
                continue
                
            boundaries = self.stage1a_boundaries[section]
            word_start = boundaries.get('word_start', 0)
            word_end = boundaries.get('word_end', len(self.book_words))
            
            # Get target region
            target_words = self.book_words[word_start:word_end]
            target_text = ' '.join(target_words)
            
            # Truncate if too long (keep first 3000 words for context)
            if len(target_words) > 3000:
                target_text = ' '.join(target_words[:3000]) + "\n\n[... section continues ...]"
            
            print(f"\n📝 Extracting {section}...")
            print(f"   Word range: {word_start:,} - {word_end:,}")
            print(f"   Sample size: {min(len(target_words), 3000):,} words")
            
            # NEW v3.4: Include chapter info in prompt
            chapter_info = ""
            if section in self.stage1a_boundaries:
                sect_data = self.stage1a_boundaries[section]
                if 'chapter_start' in sect_data:
                    chapter_info = f"\nLOCATION: Chapters {sect_data.get('chapter_start')}-{sect_data.get('chapter_end')}, Pages {sect_data.get('page_range', 'unknown')}"
            
            prompt = f"""Extract a focused 500-800 word passage from this {section} section.

BOOK: {self.title} by {self.author}
SECTION: {section.upper()}{chapter_info}

CONTEXT:
{boundaries.get('description', 'No description')}

KEY EVENTS:
{', '.join(boundaries.get('key_events', ['None']))}

TEXT SAMPLE:
{target_text}

TASK: Select a focused 500-800 word passage that:
1. Best represents this narrative stage
2. Contains rich literary devices
3. Is coherent and self-contained
4. Shows character development or plot progression

OUTPUT FORMAT (JSON):
{{
  "passage": "The selected text passage (500-800 words)",
  "rationale": "Why this passage was selected",
  "word_count": 650,
  "key_devices_visible": ["metaphor", "imagery", "dialogue"],
  "chapter_location": "Chapter X, pages Y-Z"
}}

CRITICAL: Output ONLY valid JSON.
"""
            
            system_prompt = f"You are extracting a focused literary passage from the {section} of a novel."
            
            print(f"🤖 Calling Claude API for {section}...")
            result = self._call_claude(prompt, system_prompt)
            
            # Clean and validate
            result = result.replace('```json\n', '').replace('```\n', '').replace('```', '').strip()
            
            try:
                extract_json = json.loads(result)
                extracts[section] = {
                    "text": extract_json.get('passage', ''),
                    "rationale": extract_json.get('rationale', ''),
                    "word_count": extract_json.get('word_count', 0),
                    "key_devices": extract_json.get('key_devices_visible', []),
                    "chapter_location": extract_json.get('chapter_location', 'unknown'),
                    # Include original boundary info
                    "word_range": f"{word_start}-{word_end}",
                    "chapter_range": f"{boundaries.get('chapter_start', '?')}-{boundaries.get('chapter_end', '?')}",
                    "primary_chapter": boundaries.get('primary_chapter', '?')
                }
            except json.JSONDecodeError as e:
                print(f"\n❌ Error parsing {section}: {e}")
                return False
        
        # Compile results
        result = {
            "text_structure": self.stage1a_boundaries.get('text_structure', {}),
            "extracts": extracts
        }
        
        result_formatted = json.dumps(result, indent=2)
        
        # Review
        if self._review_and_approve("Stage 1B: Extracted Passages", result_formatted):
            self.stage1b_extracts = result
            return True
        return False
    
    def stage2a_tag_macro(self):
        """Stage 2A: Tag macro alignment variables"""
        print("\n" + "="*80)
        print("STAGE 2A: MACRO ALIGNMENT VARIABLES")
        print("="*80)
        
        if not self.stage1b_extracts:
            print("❌ Error: Stage 1B extracts not available")
            return False
        
        # Build extracts text
        extracts_text = ""
        for section, data in self.stage1b_extracts['extracts'].items():
            extracts_text += f"\n### {section.upper()}\n{data['text']}\n"
        
        prompt = f"""You are performing Stage 2A: Macro Alignment Variable Tagging.

TASK: Analyze these extracts and tag the macro alignment variables.

BOOK METADATA:
- Title: {self.title}
- Author: {self.author}
- Edition: {self.edition}

PROTOCOL TO FOLLOW:
{self.protocols['kernel_enhancement']}

TAGGING PROTOCOL:
{self.protocols['artifact_2']}

FREYTAG EXTRACTS:
{extracts_text}

OUTPUT FORMAT:
Provide a JSON object with these sections:
{{
  "narrative": {{
    "pov": "FIRST/THIRD_LIMITED/THIRD_OMNI/etc",
    "focalization": "INTERNAL/EXTERNAL/VARIABLE",
    "tense": "PAST/PRESENT/MIXED",
    "temporality": "LINEAR/NONLINEAR/etc",
    "narrative_distance": "CLOSE/MEDIUM/FAR",
    "reliability": "RELIABLE/UNRELIABLE/etc"
  }},
  "rhetoric": {{
    "diction_register": "FORMAL/INFORMAL/etc",
    "syntax_complexity": "SIMPLE/MODERATE/COMPLEX",
    "tone": "description",
    "voice_consistency": "STABLE/VARIABLE",
    "rhetorical_appeals": ["logos", "pathos", "ethos"]
  }},
  "alignment": {{
    "alignment_type": "CODE from taxonomy",
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

CRITICAL: Output ONLY valid JSON. Use the codes from the protocol.
"""
        
        system_prompt = "You are a literary analysis expert tagging macro alignment variables."
        
        print("\n🤖 Calling Claude API...")
        result = self._call_claude(prompt, system_prompt)
        
        # Clean and validate
        result = result.replace('```json\n', '').replace('```\n', '').replace('```', '').strip()
        
        try:
            macro_json = json.loads(result)
            result_formatted = json.dumps(macro_json, indent=2)
        except json.JSONDecodeError as e:
            print(f"\n❌ Error: Invalid JSON response")
            print(f"Error: {e}")
            return False
        
        # Review
        if self._review_and_approve("Stage 2A: Macro Variables", result_formatted):
            self.stage2a_macro = macro_json
            return True
        return False
    
    def stage2b_tag_devices(self):
        """Stage 2B: Tag micro devices WITH CHAPTER-AWARE EXAMPLES"""
        print("\n" + "="*80)
        print("STAGE 2B: MICRO DEVICE INVENTORY (WITH CHAPTERS)")
        print("="*80)
        
        if not self.stage1b_extracts:
            print("❌ Error: Stage 1B extracts not available")
            return False
        
        # Build extracts text with chapter info
        extracts_text = ""
        for section, data in self.stage1b_extracts['extracts'].items():
            chapter_info = f"[Chapters {data.get('chapter_range', '?')}, Primary: {data.get('primary_chapter', '?')}]"
            extracts_text += f"\n### {section.upper()} {chapter_info}\n{data['text']}\n"
        
        # NEW v3.4: Show narrative position mapping
        mapping_text = json.dumps(self.narrative_position_mapping, indent=2) if self.narrative_position_mapping else "Not available"
        
        prompt = f"""You are performing Stage 2B: Micro Device Inventory with CHAPTER AWARENESS.

TASK: Identify 15-20+ micro literary devices in these extracts with quoted examples INCLUDING CHAPTER LOCATIONS.

REQUIREMENTS:
- Minimum 15 devices (target: 20+)
- At least 3 figurative language devices
- At least 1 sound device
- At least 2 irony/contrast devices
- 2-3 examples per device with structured format
- **NEW v3.4:** Each example MUST include chapter number or page range

BOOK METADATA:
- Title: {self.title}
- Author: {self.author}
- Edition: {self.edition}

NARRATIVE POSITION → CHAPTER MAPPING:
{mapping_text}

PROTOCOL TO FOLLOW:
{self.protocols['kernel_enhancement']}

DEVICE TAXONOMY:
{self.protocols['artifact_1']}

FREYTAG EXTRACTS (with chapter locations):
{extracts_text}

OUTPUT FORMAT:
Provide a JSON array of devices:
[
  {{
    "name": "Device Name",
    "definition": "Brief definition",
    "examples": [
      {{
        "text": "Quoted example from text",
        "explanation": "How this exemplifies the device",
        "narrative_position": "exposition",
        "chapter": 1,
        "page": 5
      }}
    ]
  }}
]

**CRITICAL v3.4:** Every example MUST include:
- "narrative_position": one of [exposition, rising_action, climax, falling_action, resolution]
- "chapter": number (or "pages X-Y" for texts without chapters)
- "page": number if identifiable (can be null if unknown)

Use the narrative position mapping above to determine chapter numbers based on which extract the example came from.

CRITICAL: Output ONLY valid JSON. Include at least 15 devices with chapter-aware examples.
"""
        
        system_prompt = "You are a literary analysis expert identifying micro literary devices with chapter-level precision."
        
        print("\n🤖 Calling Claude API...")
        result = self._call_claude(prompt, system_prompt)
        
        # Clean and validate
        result = result.replace('```json\n', '').replace('```\n', '').replace('```', '').strip()
        
        try:
            devices_json = json.loads(result)
            device_count = len(devices_json)
            print(f"\n✓ Identified {device_count} devices")
            
            # NEW v3.4: Validate chapter info present
            missing_chapters = 0
            for device in devices_json:
                for example in device.get('examples', []):
                    if 'chapter' not in example:
                        missing_chapters += 1
            
            if missing_chapters > 0:
                print(f"⚠️ Warning: {missing_chapters} examples missing chapter info")
            
            result_formatted = json.dumps(devices_json, indent=2)
        except json.JSONDecodeError as e:
            print(f"\n❌ Error: Invalid JSON response")
            print(f"Error: {e}")
            return False
        
        # Review
        if self._review_and_approve("Stage 2B: Devices with Chapters", result_formatted):
            self.stage2b_devices = devices_json
            return True
        return False
    
    def assemble_kernel(self):
        """Assemble final kernel JSON WITH NARRATIVE POSITION MAPPING"""
        print("\n" + "="*80)
        print("FINAL ASSEMBLY (v3.4 with Chapter Mapping)")
        print("="*80)
        
        if not all([self.stage1b_extracts, self.stage2a_macro, self.stage2b_devices]):
            print("❌ Error: Not all stages completed")
            return False
        
        # Combine all stages into final kernel
        self.kernel = {
            "metadata": {
                "title": self.title,
                "author": self.author,
                "edition": self.edition,
                "creation_date": datetime.now().isoformat(),
                "protocol_version": "3.3",
                "kernel_version": "3.4",  # NEW
                "chapter_aware": True  # NEW
            },
            "text_structure": self.stage1b_extracts.get('text_structure', {}),  # NEW
            "narrative_position_mapping": self.narrative_position_mapping,  # NEW
            "extracts": self.stage1b_extracts['extracts'],
            "macro_variables": self.stage2a_macro,
            "micro_devices": self.stage2b_devices
        }
        
        result_formatted = json.dumps(self.kernel, indent=2)
        
        # Review
        if self._review_and_approve("Final Kernel v3.4", result_formatted):
            return True
        return False
    
    def save_kernel(self):
        """Save kernel to file"""
        if not self.kernel:
            print("❌ Error: No kernel to save")
            return False
        
        # Create filename with v3.4 version
        safe_title = self.title.replace(' ', '_').replace('/', '_')
        filename = f"{safe_title}_kernel_v3_4.json"
        filepath = Config.KERNELS_DIR / filename
        
        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Save
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.kernel, indent=2, fp=f)
        
        print(f"\n✅ Kernel v3.4 saved to: {filepath}")
        print(f"   Size: {filepath.stat().st_size:,} bytes")
        
        # Print summary
        print("\n📊 KERNEL SUMMARY:")
        print(f"   - Chapter-aware: {self.kernel['metadata']['chapter_aware']}")
        print(f"   - Has chapters: {self.kernel['text_structure'].get('has_chapters', 'unknown')}")
        print(f"   - Total devices: {len(self.kernel['micro_devices'])}")
        
        if self.narrative_position_mapping:
            print("\n📍 CHAPTER MAPPING:")
            for section, mapping in self.narrative_position_mapping.items():
                print(f"   {section}: Chapters {mapping['chapter_range']}, Primary: {mapping['primary_chapter']}")
        
        return True
    
    def run(self):
        """Run the full pipeline"""
        print("\n" + "="*80)
        print("KERNEL CREATION PIPELINE v3.4")
        print("="*80)
        print(f"Book: {self.title} by {self.author}")
        print(f"Edition: {self.edition}")
        print(f"Book size: {len(self.book_words):,} words")
        print("\n🆕 NEW IN v3.4: Chapter-aware kernel creation")
        
        # Stage 1A: Identify boundaries with chapters
        if not self.stage1a_identify_boundaries():
            print("\n❌ Pipeline failed at Stage 1A")
            return False
        
        # Stage 1B: Extract passages
        if not self.stage1b_extract_passages():
            print("\n❌ Pipeline failed at Stage 1B")
            return False
        
        # Stage 2A: Tag macro variables
        if not self.stage2a_tag_macro():
            print("\n❌ Pipeline failed at Stage 2A")
            return False
        
        # Stage 2B: Tag devices with chapters
        if not self.stage2b_tag_devices():
            print("\n❌ Pipeline failed at Stage 2B")
            return False
        
        # Assemble kernel
        if not self.assemble_kernel():
            print("\n❌ Pipeline failed at assembly")
            return False
        
        # Save
        if not self.save_kernel():
            print("\n❌ Pipeline failed at save")
            return False
        
        print("\n" + "="*80)
        print("✅ PIPELINE COMPLETE - v3.4 KERNEL CREATED")
        print("="*80)
        print("\n🎯 Next steps:")
        print("1. Verify kernel has chapter info: cat <kernel>.json | grep narrative_position_mapping")
        print("2. Run Stage 1A with new kernel to test propagation")
        print("3. Generate worksheets and verify chapter references")
        
        return True

def main():
    if len(sys.argv) < 5:
        print("Usage: python3 create_kernel_v3_4.py <pdf_path> <title> <author> <edition>")
        print("\nExample:")
        print('  python3 create_kernel_v3_4.py books/The_Giver.pdf "The Giver" "Lois Lowry" "1993"')
        print("\nNEW IN v3.4:")
        print("  - Captures chapter numbers for all narrative sections")
        print("  - Includes chapter info in device examples")
        print("  - Creates narrative_position_mapping for downstream use")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    title = sys.argv[2]
    author = sys.argv[3]
    edition = sys.argv[4]
    
    try:
        creator = KernelCreator(pdf_path, title, author, edition)
        success = creator.run()
        sys.exit(0 if success else 1)
    
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
