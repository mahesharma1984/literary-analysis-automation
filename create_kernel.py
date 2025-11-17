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
        
        # Storage for stage outputs
        self.stage1_extracts = None
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
            if not filepath.exists():
                print(f"⚠️  Warning: {filename} not found, skipping...")
                protocols[key] = ""
                continue
                
            with open(filepath, 'r', encoding='utf-8') as f:
                protocols[key] = f.read()
            print(f"  ✓ Loaded {filename}")
        
        return protocols
    
    def _load_book(self) -> str:
        """Load book text from PDF or txt file"""
        print(f"\n📖 Loading book: {self.book_path.name}")
        
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
            print(f"  📄 Extracting text from {total_pages} pages...")
            
            for i, page in enumerate(pdf_reader.pages):
                text += page.extract_text()
                if (i + 1) % 50 == 0:
                    print(f"    Progress: {i + 1}/{total_pages} pages")
        
        print(f"  ✓ Extracted {len(text):,} characters")
        return text
    
    def _call_claude(self, prompt: str, system_prompt: str = "") -> str:
        """Call Claude API with given prompt"""
        print("\n🤖 Calling Claude API...")
        
        messages = [{"role": "user", "content": prompt}]
        
        response = self.client.messages.create(
            model=Config.MODEL,
            max_tokens=Config.MAX_TOKENS,
            system=system_prompt if system_prompt else None,
            messages=messages
        )
        
        result = response.content[0].text
        print(f"  ✓ Received {len(result):,} characters")
        return result
    
    def _review_and_approve(self, stage_name: str, output: str) -> bool:
        """Present output to user for review"""
        print(f"\n{'='*80}")
        print(f"STAGE COMPLETE: {stage_name}")
        print(f"{'='*80}")
        print("\nOutput preview (first 2000 characters):")
        print(output[:2000])
        if len(output) > 2000:
            print(f"\n... ({len(output) - 2000:,} more characters)")
        
        print(f"\n{'='*80}")
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
    
    def stage1_extract_freytag(self):
        """Stage 1: Extract 5 Freytag sections"""
        print("\n" + "="*80)
        print("STAGE 1: FREYTAG EXTRACT SELECTION")
        print("="*80)
        
        prompt = f"""You are performing Stage 1 of the Kernel Validation Protocol v3.3.

TASK: Extract 5 key sections from the book that map to Freytag's dramatic structure:
1. Exposition (beginning)
2. Rising Action (conflict development)
3. Climax (turning point)
4. Falling Action (aftermath)
5. Resolution (ending)

BOOK METADATA:
- Title: {self.title}
- Author: {self.author}
- Edition: {self.edition}

PROTOCOL TO FOLLOW:
{self.protocols['kernel_validation']}

ADDITIONAL CONTEXT:
{self.protocols['lem']}

BOOK TEXT (full):
{self.book_text}

OUTPUT FORMAT:
Provide a JSON object with this structure:
{{
  "metadata": {{
    "title": "{self.title}",
    "author": "{self.author}",
    "edition": "{self.edition}",
    "extraction_date": "{datetime.now().isoformat()}"
  }},
  "extracts": {{
    "exposition": {{
      "chapter_range": "X-Y",
      "page_range": "X-Y",
      "text": "extracted text here...",
      "rationale": "why this section represents exposition"
    }},
    "rising_action": {{ ... }},
    "climax": {{ ... }},
    "falling_action": {{ ... }},
    "resolution": {{ ... }}
  }}
}}

CRITICAL: Output ONLY valid JSON. No additional text before or after the JSON.
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
            print(f"\n❌ Error: Invalid JSON response from Claude")
            print(f"Error details: {e}")
            return False
        
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
            print("❌ Error: Stage 1 extracts not available")
            return False
        
        extracts_text = ""
        for section, data in self.stage1_extracts['extracts'].items():
            extracts_text += f"\n### {section.upper()}\n{data['text']}\n"
        
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
            print(f"\n❌ Error: Invalid JSON response from Claude")
            print(f"Error details: {e}")
            return False
        
        # Review
        if self._review_and_approve("Stage 2A: Macro Variables", result_formatted):
            self.stage2a_macro = macro_json
            return True
        return False
    
    def stage2b_tag_devices(self):
        """Stage 2B: Tag 15-20+ micro devices with examples"""
        print("\n" + "="*80)
        print("STAGE 2B: MICRO DEVICE INVENTORY")
        print("="*80)
        
        if not self.stage1_extracts:
            print("❌ Error: Stage 1 extracts not available")
            return False
        
        extracts_text = ""
        for section, data in self.stage1_extracts['extracts'].items():
            extracts_text += f"\n### {section.upper()}\n{data['text']}\n"
        
        prompt = f"""You are performing Stage 2B of the Kernel Protocol Enhancement v3.3.

TASK: Identify 15-20+ micro literary devices in the text with quoted examples.

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
    "layer": "CODE (N/B/R)",
    "function": "CODE (Re/Me/Dr)",
    "engagement": "CODE (Pa/Ac/Sy)",
    "classification": "Layer|Function|Engagement",
    "definition": "student-facing definition",
    "student_facing_type": "Figurative Language/Sound Device/etc.",
    "pedagogical_function": "what it does for reader/theme",
    "position_code": "DIST/CLUST-BEG/etc.",
    "examples": [
      {{
        "freytag_section": "exposition/rising_action/etc.",
        "scene": "brief scene identifier",
        "chapter": X,
        "page_range": "X-Y",
        "quote_snippet": "20-100 character quote excerpt"
      }}
    ]
  }}
]

CRITICAL: 
- Output ONLY valid JSON array
- Include 2-3 examples per device
- Use structured example format (v3.3)
- Ensure examples align with position codes
"""
        
        system_prompt = "You are a literary analysis expert identifying and cataloging micro literary devices according to Kernel Protocol Enhancement v3.3."
        
        result = self._call_claude(prompt, system_prompt)
        
        # Clean and validate
        result = result.replace('```json\n', '').replace('```\n', '').replace('```', '').strip()
        
        try:
            devices_json = json.loads(result)
            result_formatted = json.dumps(devices_json, indent=2)
        except json.JSONDecodeError as e:
            print(f"\n❌ Error: Invalid JSON response from Claude")
            print(f"Error details: {e}")
            return False
        
        # Validate minimum requirements
        device_count = len(devices_json)
        if device_count < 15:
            print(f"\n⚠️  Warning: Only {device_count} devices found (minimum 15 required)")
        
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
            print("❌ Error: Not all stages completed")
            return False
        
        kernel = {
            "text_metadata": {
                "title": self.title,
                "author": self.author,
                "edition": self.edition,
                "analysis_date": datetime.now().isoformat(),
                "protocol_version": "Kernel Validation Protocol v3.3",
                "enhancement_version": "Kernel Protocol Enhancement v3.3"
            },
            "extracts": self.stage1_extracts['extracts'],
            "narrative": self.stage2a_macro.get('narrative', {}),
            "rhetoric": self.stage2a_macro.get('rhetoric', {}),
            "device_mediation": self.stage2a_macro.get('device_mediation', {}),
            "devices": self.stage2b_devices,
            "validation_metadata": {
                "total_devices": len(self.stage2b_devices),
                "examples_provided": True,
                "examples_format": "v3.3 (freytag_section, scene, chapter, page_range, quote_snippet)",
                "education_vertical_ready": True,
                "model_used": Config.MODEL
            }
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
            print("❌ Error: No kernel to save")
            return False
        
        if not output_path:
            # Generate default filename
            safe_title = "".join(c for c in self.title if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title.replace(' ', '_')
            filename = f"{safe_title}_kernel_v3.3.json"
            output_path = Config.KERNELS_DIR / filename
        
        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.kernel, f, indent=2)
        
        print(f"\n✅ Kernel saved to: {output_path}")
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
        
        # Stage 1
        if not self.stage1_extract_freytag():
            print("\n❌ Pipeline failed at Stage 1")
            return False
        
        # Stage 2A
        if not self.stage2a_tag_macro():
            print("\n❌ Pipeline failed at Stage 2A")
            return False
        
        # Stage 2B
        if not self.stage2b_tag_devices():
            print("\n❌ Pipeline failed at Stage 2B")
            return False
        
        # Assemble
        if not self.assemble_kernel():
            print("\n❌ Pipeline failed at assembly")
            return False
        
        # Save
        if not self.save_kernel():
            print("\n❌ Pipeline failed at save")
            return False
        
        print("\n" + "="*80)
        print("✅ KERNEL CREATION COMPLETE!")
        print("="*80)
        return True


def main():
    """Main entry point"""
    if len(sys.argv) < 5:
        print("Usage: python create_kernel.py <book_path> <title> <author> <edition>")
        print("Example: python create_kernel.py books/TKAM.pdf 'To Kill a Mockingbird' 'Harper Lee' 'Harper Perennial Modern Classics, 2006'")
        sys.exit(1)
    
    book_path = sys.argv[1]
    title = sys.argv[2]
    author = sys.argv[3]
    edition = sys.argv[4]
    
    # Create kernel creator
    creator = KernelCreator(book_path, title, author, edition)
    
    # Run pipeline
    success = creator.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
