#!/usr/bin/env python3
"""
KERNEL CREATION AUTOMATION - TWO-PASS EXTRACTION

Proper implementation with two-phase Stage 1:
- Stage 1A: Identify Freytag section boundaries (chapter/page ranges)
- Stage 1B: Extract focused 500-800 word passages from each section
- Stage 2A: Tag macro alignment variables
- Stage 2B: Identify micro devices

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
    """Main class for creating kernel JSONs"""
    
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
        """Stage 1A: Identify Freytag section boundaries"""
        print("\n" + "="*80)
        print("STAGE 1A: IDENTIFY FREYTAG BOUNDARIES")
        print("="*80)
        
        book_sample = self._create_book_sample()
        
        prompt = f"""You are performing Stage 1A: Identifying Freytag dramatic structure boundaries.

TASK: Analyze this book sample and identify WHERE each Freytag section occurs.

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
- Brief description of what happens there
- Key characters/events that signal this section

OUTPUT FORMAT (JSON):
{{
  "exposition": {{
    "word_start": 0,
    "word_end": 5000,
    "description": "Scout introduces her family and Maycomb...",
    "key_events": ["Introduction of Atticus", "Boo Radley mystery begins"]
  }},
  "rising_action": {{
    "word_start": 5000,
    "word_end": 40000,
    "description": "...",
    "key_events": [...]
  }},
  "climax": {{...}},
  "falling_action": {{...}},
  "resolution": {{...}}
}}

CRITICAL: Output ONLY valid JSON. The word positions are estimates - that's fine.
"""
        
        system_prompt = "You are a literary analysis expert identifying Freytag dramatic structure boundaries in novels."
        
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
        if self._review_and_approve("Stage 1A: Boundaries", result_formatted):
            self.stage1a_boundaries = boundaries_json
            return True
        return False
    
    def stage1b_extract_passages(self):
        """Stage 1B: Extract focused 500-800 word passages from each section"""
        print("\n" + "="*80)
        print("STAGE 1B: EXTRACT FOCUSED PASSAGES")
        print("="*80)
        
        if not self.stage1a_boundaries:
            print("❌ Error: Stage 1A boundaries not available")
            return False
        
        extracts = {}
        
        sections = ['exposition', 'rising_action', 'climax', 'falling_action', 'resolution']
        
        for section in sections:
            print(f"\n📝 Extracting {section}...")
            
            boundary = self.stage1a_boundaries.get(section, {})
            word_start = boundary.get('word_start', 0)
            word_end = boundary.get('word_end', len(self.book_words))
            
            # Extract the section text from full book
            section_words = self.book_words[word_start:word_end]
            section_word_count = len(section_words)
            
            print(f"  Section size: {section_word_count:,} words")
            
            # If section is too large, sample it strategically
            if section_word_count > 15000:
                print(f"  Section too large, sampling 15K words strategically...")
                # Take beginning + middle + end
                beginning = section_words[:5000]
                middle_start = len(section_words) // 2 - 2500
                middle_end = len(section_words) // 2 + 2500
                middle = section_words[middle_start:middle_end]
                ending = section_words[-5000:]
                section_text = ' '.join(beginning) + '\n\n[... middle omitted ...]\n\n' + ' '.join(middle) + '\n\n[... later part omitted ...]\n\n' + ' '.join(ending)
            else:
                section_text = ' '.join(section_words)
            
            print(f"  Extracting most narratively dense 500-800 words...")
            
            prompt = f"""Extract the most narratively dense 500-800 word passage from this section.

SECTION: {section.replace('_', ' ').title()}
CONTEXT: {boundary.get('description', '')}

SECTION TEXT:
{section_text}

INSTRUCTIONS:
1. Identify the MOST IMPORTANT narrative moment in this section
2. Extract exactly 500-800 words centered on that moment
3. Ensure clear beginning and ending to the passage
4. Choose the passage that best represents this Freytag section

OUTPUT FORMAT (JSON):
{{
  "text": "the extracted 500-800 word passage here...",
  "rationale": "why this passage represents {section}",
  "word_count": 650
}}

CRITICAL: Output ONLY valid JSON. The passage must be 500-800 words.
"""
            
            system_prompt = f"You are extracting the most narratively important passage from the {section} section."
            
            print("  🤖 Calling Claude API...")
            result = self._call_claude(prompt, system_prompt)
            
            # Clean and parse
            result = result.replace('```json\n', '').replace('```\n', '').replace('```', '').strip()
            
            try:
                extract_json = json.loads(result)
                extracts[section] = extract_json
                
                actual_words = len(extract_json['text'].split())
                print(f"  ✓ Extracted {actual_words} words")
                
            except json.JSONDecodeError as e:
                print(f"  ❌ Error parsing JSON for {section}: {e}")
                return False
            
            # Add delay to avoid rate limits (except for last section)
            if section != sections[-1]:
                print("  ⏳ Waiting 10 seconds before next section...")
                import time
                time.sleep(10)
        
        # Combine all extracts
        full_result = {
            "metadata": {
                "title": self.title,
                "author": self.author,
                "edition": self.edition,
                "extraction_date": datetime.now().isoformat()
            },
            "extracts": extracts
        }
        
        result_formatted = json.dumps(full_result, indent=2)
        
        # Review
        if self._review_and_approve("Stage 1B: Extracts", result_formatted):
            self.stage1b_extracts = full_result
            return True
        return False
    
    def stage2a_tag_macro(self):
        """Stage 2A: Tag macro alignment variables"""
        print("\n" + "="*80)
        print("STAGE 2A: MACRO ALIGNMENT TAGGING")
        print("="*80)
        
        if not self.stage1b_extracts:
            print("❌ Error: Stage 1B extracts not available")
            return False
        
        # Build extracts text
        extracts_text = ""
        for section, data in self.stage1b_extracts['extracts'].items():
            extracts_text += f"\n### {section.upper()}\n{data['text']}\n"
        
        prompt = f"""You are performing Stage 2A: Macro Alignment Tagging.

TASK: Analyze these 5 Freytag extracts and tag all macro alignment variables.

BOOK METADATA:
- Title: {self.title}
- Author: {self.author}

TAGGING PROTOCOL:
{self.protocols['artifact_2']}

FREYTAG EXTRACTS:
{extracts_text}

OUTPUT FORMAT:
Provide a JSON object with macro variables:
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
        """Stage 2B: Tag micro devices"""
        print("\n" + "="*80)
        print("STAGE 2B: MICRO DEVICE INVENTORY")
        print("="*80)
        
        if not self.stage1b_extracts:
            print("❌ Error: Stage 1B extracts not available")
            return False
        
        # Build extracts text
        extracts_text = ""
        for section, data in self.stage1b_extracts['extracts'].items():
            extracts_text += f"\n### {section.upper()}\n{data['text']}\n"
        
        prompt = f"""You are performing Stage 2B: Micro Device Inventory.

TASK: Identify 15-20+ micro literary devices in these extracts with quoted examples.

REQUIREMENTS:
- Minimum 15 devices (target: 20+)
- At least 3 figurative language devices
- At least 1 sound device
- At least 2 irony/contrast devices
- 2-3 examples per device with structured format

BOOK METADATA:
- Title: {self.title}
- Author: {self.author}
- Edition: {self.edition}

PROTOCOL TO FOLLOW:
{self.protocols['kernel_enhancement']}

DEVICE TAXONOMY:
{self.protocols['artifact_1']}

FREYTAG EXTRACTS:
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
        "location": "exposition/rising_action/climax/falling_action/resolution"
      }}
    ]
  }}
]

CRITICAL: Output ONLY valid JSON. Include at least 15 devices.
"""
        
        system_prompt = "You are a literary analysis expert identifying micro literary devices."
        
        print("\n🤖 Calling Claude API...")
        result = self._call_claude(prompt, system_prompt)
        
        # Clean and validate
        result = result.replace('```json\n', '').replace('```\n', '').replace('```', '').strip()
        
        try:
            devices_json = json.loads(result)
            device_count = len(devices_json)
            print(f"\n✓ Identified {device_count} devices")
            
            result_formatted = json.dumps(devices_json, indent=2)
        except json.JSONDecodeError as e:
            print(f"\n❌ Error: Invalid JSON response")
            print(f"Error: {e}")
            return False
        
        # Review
        if self._review_and_approve("Stage 2B: Devices", result_formatted):
            self.stage2b_devices = devices_json
            return True
        return False
    
    def assemble_kernel(self):
        """Assemble final kernel JSON"""
        print("\n" + "="*80)
        print("FINAL ASSEMBLY")
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
                "protocol_version": "3.3"
            },
            "extracts": self.stage1b_extracts['extracts'],
            "macro_variables": self.stage2a_macro,
            "micro_devices": self.stage2b_devices
        }
        
        result_formatted = json.dumps(self.kernel, indent=2)
        
        # Review
        if self._review_and_approve("Final Kernel", result_formatted):
            return True
        return False
    
    def save_kernel(self):
        """Save kernel to file"""
        if not self.kernel:
            print("❌ Error: No kernel to save")
            return False
        
        # Create filename
        safe_title = self.title.replace(' ', '_').replace('/', '_')
        filename = f"{safe_title}_kernel_v3_3.json"
        filepath = Config.KERNELS_DIR / filename
        
        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Save
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.kernel, indent=2, fp=f)
        
        print(f"\n✅ Kernel saved to: {filepath}")
        return True
    
    def run(self):
        """Run the full pipeline"""
        print("\n" + "="*80)
        print("KERNEL CREATION PIPELINE")
        print("="*80)
        print(f"Book: {self.title} by {self.author}")
        print(f"Edition: {self.edition}")
        print(f"Book size: {len(self.book_words):,} words")
        
        # Stage 1A: Identify boundaries
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
        
        # Stage 2B: Tag devices
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
        print("✅ PIPELINE COMPLETE")
        print("="*80)
        
        return True

def main():
    if len(sys.argv) < 5:
        print("Usage: python3 create_kernel.py <pdf_path> <title> <author> <edition>")
        print("\nExample:")
        print('  python3 create_kernel.py books/tkam.pdf "To Kill a Mockingbird" "Harper Lee" "1960"')
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
