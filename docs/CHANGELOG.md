# Changelog

All notable changes to the Literary Experience Model (LEM) Kernel and Stage protocols will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Kernel Protocol v3.6: Confidence scores for device identifications
- Stage 1A v5.2: Automated macro-micro relationship validation
- Stage 2 v4.2: Differentiated instruction versions
- Template v3.0: Multi-text comparison worksheets

---

### [Stage 1B v5.2] - 2025-11-25

#### Added
- **Effect Synthesis System** for generating device effects
  - Synonym library system with 10+ word clusters (decay/decline, tiredness/exhaustion, strictness/harshness, etc.)
  - Automatic quality extraction from device explanations
  - Subject extraction (characters, places, objects) from device examples
  - Three-effect generation per device using synonym variations
- **Effect format:**
  - Dictionary structure with `text` and `category` keys
  - Three categories: `reader_response`, `meaning_creation`, `thematic_impact`
  - Explicit signal words: "feel", "reveals", "theme" for student categorization
  - Complete sentences ready for worksheet integration
- **Extraction functions:**
  - `extract_subject_from_device()` - Extracts subject with priority (character names > place names > objects)
  - `extract_quality_from_explanation()` - Extracts core quality from device explanations
  - `generate_effects_for_device()` - Synthesizes 3 categorized effects with synonym variations
  - `create_quality_variations()` - Creates 3 quality variations using synonym mapping
  - `get_synonym_for_word()` - Synonym selection based on index

#### Changed
- **Effects field structure:** Plain strings → Dictionaries with text/category
- Each device now has `effects` array with 3 categorized effect objects
- Effects include signal words for pedagogical categorization

#### Benefits
- **No API costs:** All effect generation is rule-based (synonym system)
- **No keyword repetition:** Synonym variations ensure diverse vocabulary
- **Student-ready:** Complete sentences with clear categorization signals
- **Contextual:** Effects reference actual subjects and qualities from device examples

#### Technical Details
- Synonym mapping covers 10+ semantic clusters
- Handles compound qualities ("X and Y" patterns)
- Grammar-aware (removes possessive pronouns, handles subject forms)
- Fallback cases for edge scenarios

#### Dependencies
- Requires Stage 1A v5.0+ output with device examples
- No breaking changes to existing output structure (additive feature)
- Compatible with Stage 2 v4.1+ worksheet generation

---

### [Kernel v3.5] - 2025-11-25

#### Added
- **Book Structure Alignment Protocol v1.1** integration
  - New Stage 0: Structure detection and chapter-to-Freytag alignment
  - Structure detection (NUM/NAME/NEST/UNMARK/HYBRID)
  - Conventional distribution formula with climax refinement
  - Content verification and validation step
  - Protocol file: `protocols/Book_Structure_Alignment_Protocol_v1.md`
- **New kernel fields:**
  - `structure_detection` - Structure type, total units, special elements
  - `chapter_alignment` - Validated chapter-to-Freytag mapping with percentages
  - `structure_alignment_protocol: "v1.1"` in metadata
- **Chapter range format normalization:**
  - Extracts now include `chapter_range` in numeric format ("1-3" not "Chapters 1-3")
  - Fixes compatibility with `run_stage1a.py` parser

#### Changed
- **create_kernel.py:**
  - Added Stage 0 before Stage 1 (structure alignment)
  - Stage 1 now uses validated chapter alignment from Stage 0
  - Reduced Stage 1 token usage (targeted chapter samples instead of full book)
  - Automatic normalization of chapter_range format
  - Kernel version updated to 3.5
- **Updated TKAM kernel to v3.5:**
  - Added structure_detection and chapter_alignment sections
  - Preserved all existing data (backward compatible)

#### Fixed
- Chapter range format inconsistency between `extracts` and `narrative_position_mapping`
- Stage 1 token limit issues (reduced from ~70K to ~8K tokens)

#### Documentation
- Updated README.md with Stage 0 workflow
- Updated QUICKSTART.md with v3.5 examples
- Added integration summary and protocol update documentation

#### Migration Notes
- **Backward compatible:** v3.4 kernels still work with all downstream tools
- **New kernels:** Will be created as v3.5 by default
- **Upgrade path:** Existing kernels can be manually upgraded (see TKAM example)

---

### [v5.1.2] - 2025-11-24

#### Added
- **Archive versioning system** (`archive_versioning.py`)
  - Automated file archiving with version tracking
  - Metadata tracking in `archive/archive_metadata.json`
  - Archive documentation (`docs/ARCHIVE_VERSIONING_GUIDE.md`)
  - Archive directory README with usage instructions
- Updated The Giver kernel files:
  - `The_Giver_kernel_v3.3.json` - Updated kernel data
  - `The_Giver_kernel_v3_4.json` - New v3.4 kernel format
  - `The_Giver_ReasoningDoc_v3.3.md` - Updated reasoning document

#### Changed
- Updated device taxonomy protocol (`Artifact_1_-_Device_Taxonomy_by_Alignment_Function.md`)
- Updated The Giver worksheets and integrated progression:
  - `The_Giver_Week1_Worksheet.md`
  - `The_Giver_Week1_TeacherKey.md`
  - `The_Giver_Integrated_Progression.md`
- Updated pipeline scripts:
  - `run_stage1a.py` - Improvements to stage 1A processing
  - `run_stage1b.py` - Improvements to stage 1B processing
  - `create_kernel.py` - Kernel creation enhancements
- Updated `README.md` with latest project information

#### Dependencies
- Archive versioning system enables better file management
- Kernel v3.4 format supports enhanced device tracking
- Updated taxonomy protocol improves device categorization

---

### [v5.1.1] - 2025-11-24

#### Changed
- Repository reorganization and cleanup
- Scripts renamed to clean names:
  - `create_kernel_v3_4_FIXED.py` → `create_kernel.py`
  - `run_stage1a_FIXED.py` → `run_stage1a.py`
  - `run_stage1b_v5_1.py` → `run_stage1b.py`
  - `run_stage2_v5_1.py` → `run_stage2.py`
- Old script versions archived to `/archive` folder
- Feature branches merged and deleted:
  - `feature/two-pass-extraction`
  - `fix/stage2-template-system`
- Repository tagged as v5.1
- Documentation updated for script name changes

#### Note
- No functional changes to pipeline
- All scripts maintain same behavior
- GitHub repository organized and consolidated

---

## Stage Implementations

### [Stage 2 v4.1] - 2025-11-15

#### Added
- 6-step pedagogical scaffolding for device analysis
  - Definition (recognition skill)
  - Find (matching skill)
  - Identify (multiple choice)
  - Analyze (sequencing)
  - Detail (textual evidence)
  - Effect (categorization)
- Step-by-step progression within each device section
- Enhanced scaffolding from simple to complex tasks

#### Changed
- Template_Literary_Analysis_MacroMicro.md updated to v2.0
- Improved learning progression structure

#### Dependencies
- Requires Stage 1B v5.1 week packages
- Extends Stage 2 v4.0

---

### [Stage 1B v5.1] - 2025-11-15

#### Changed
- **BREAKING:** Week order updated to follow chapter chronology
  - Week 1: Exposition (Chapter 1) - moved from Week 2
  - Week 2: Literary Devices Foundation (Chapter 10) - moved from Week 1
  - Week 3: Structure (Chapter 19) - unchanged
  - Week 4: Voice (Chapter 31) - unchanged

#### Rationale
- Better alignment with reading sequence
- Students read Chapter 1 first, so Week 1 should analyze Chapter 1

#### Migration
- Requires worksheet regeneration for correct chapter mapping
- No changes to package data structure

#### Dependencies
- Processes Stage 1A v5.1 output
- Feeds into Stage 2 v4.1

---

### [Stage 1A v5.1] - 2025-11-15

#### Note
- Version number updated for consistency with Stage 1B v5.1
- No actual changes to extraction logic or output format
- All v5.0 functionality maintained

#### Dependencies
- Feeds into Stage 1B v5.1

---

### [Stage 1B v5.0] - 2025-11-15

#### Added
- Macro-micro week package structure
- Pedagogical scaffolding specification (High → Medium → Low)
- Teaching sequence ordering within weeks
- Success criteria per week
- 4-week macro progression (Devices → Exposition → Structure → Voice)
- `teaching_notes` with macro connection explanations
- `executes_macro` field for each device

#### Changed
- **BREAKING:** Complete package structure redesign from v4.2
- Single chapter focus per week (was multiple chapters)

#### Removed
- Simple device-list structure (superseded by macro-micro packages)

#### Migration
- Cannot migrate from v4.2 - requires complete regeneration
- Requires Stage 2 v4.0 to process new structure

#### Dependencies
- Requires Stage 1A v5.0 macro-micro packages
- Enables Stage 2 v4.0 worksheet generation

---

### [Stage 1A v5.0] - 2025-11-15

#### Added
- Macro-micro extraction (both alignment elements AND devices)
- Relationship mapping between macro elements and micro devices
- Package structure organizing as macro-micro pairs
- Single chapter focus per package
- `executes_macro` field showing how devices build macro elements
- Teaching context for educational use

#### Changed
- **BREAKING:** Complete output structure redesign from v4.2
- Output format: macro-micro packages instead of flat device list

#### Removed
- Flat device-only extraction (superseded by integrated approach)

#### Migration
- Cannot migrate from v4.2 - requires complete regeneration
- All Stage 1B and Stage 2 outputs must be regenerated

#### Dependencies
- Requires Kernel_Validation_Protocol v3.2+ (terminology)
- Requires Kernel_Protocol_Enhancement v3.3 (examples)
- Enables Stage 1B v5.0

---

### [Stage 2 v4.0] - 2025-11-14

#### Added
- Three new macro-micro templates:
  - `Template_Literary_Analysis_MacroMicro.md`
  - `Template_TVODE_MacroMicro.md`
  - `Template_Teacher_Key_MacroMicro.md`
- Macro teaching section in worksheets
- Macro-micro TVODE construction framework
- Teacher keys with macro concept explanations

#### Changed
- **BREAKING:** Template system redesigned for macro-focused pedagogy
- Worksheets now teach macro concepts through micro devices

#### Removed
- Device-only templates (superseded by macro-micro versions)

#### Migration
- Cannot migrate from v3.2 - requires new templates
- All worksheets must be regenerated

#### Dependencies
- Requires Stage 1B v5.0 week packages
- Creates 3 new template types

---

## Kernel Protocols

### [Kernel Protocol Enhancement v3.3] - 2025-11-14

#### Added
- Structured examples array format:
  - `freytag_section`: Narrative arc position
  - `scene`: Scene identifier (10-50 chars)
  - `chapter`: Chapter number
  - `page_range`: Page references
  - `quote_snippet`: Short quote (20-100 chars)
- `edition_reference` requirement in validation_metadata
- Scene identifiers for pedagogical utility

#### Changed
- Examples format: `{quote, location, analysis}` → `{freytag_section, scene, chapter, page_range, quote_snippet}`
- Maximum examples per device: 5 → 3 (reduce bloat)
- Quote snippets replace full quotes (~20-30% size reduction)

#### Removed
- `analysis` field from examples (belongs in reasoning document)

#### Migration
- Backward compatible with migration path from v3.2
- Existing v3.2 JSON can be converted to v3.3 format

#### Dependencies
- Aligns with Kernel_Validation_Protocol v3.3
- Enables Stage 1A v5.0 efficiency improvements
- Required for Template_Updates v2.1 location hints

---

### [Kernel Validation Protocol v3.3] - 2025-11-14

#### Added
- Examples array specification for pedagogically relevant devices
- Freytag section mapping in examples
- Scene identifiers, chapter/page references
- Optional quote snippets
- Validation rules: examples must align with position codes

#### Changed
- Examples specification: 2-3 examples required for educational vertical devices
- Examples leverage Freytag-mapped extract structure

#### Migration
- Backward compatible
- Existing v3.2 analyses can add examples structure

#### Dependencies
- Triggers Kernel Protocol Enhancement v3.3
- Enables Stage 1A v5.0 automation

---

### [Kernel Protocol Enhancement v3.2] - 2025-11-14

#### Changed
- **TERMINOLOGY UPDATE:** Aligned with Kernel Protocol v3.2 terminology
- "Stage 2A: Macro Alignment Tagging" replaces "N-R-D Tagging"
- "Devices" now exclusively refers to 50+ micro literary techniques
- "Alignment variables" refers to 84 macro variables
- Added explicit WHAT (macro) vs HOW (micro) relationship explanation

#### Note
- No substantive methodology changes from v3.1
- Terminology clarification only

#### Dependencies
- Triggered by Kernel_Validation_Protocol v3.2

---

### [Kernel Validation Protocol v3.2] - 2025-11-14

#### Changed
- **TERMINOLOGY UPDATE:** Clarified macro vs micro distinction
- "Stage 2: N-R-D Tagging" renamed to "Stage 2A: Macro Alignment Tagging"
- "Devices" now exclusively means 50+ micro literary techniques (Artifact 1)
- "Alignment variables" or "narrative/rhetorical elements" means 84 core variables

#### Note
- No substantive methodology changes from v3.1
- Critical terminology clarification for vertical integration

#### Dependencies
- Triggers Kernel Protocol Enhancement v3.2 update
- Required Stage implementation terminology updates (v5.0)

---

### [Kernel Protocol Enhancement v3.1] - 2025-11-13

#### Added
- Stage 2B: Comprehensive Micro Device Inventory
- Systematic application of full Artifact 1 taxonomy
- Minimum 15-20 devices per text requirement
- Quoted examples mandatory for devices

#### Impact
- High: Adds new analysis stage
- Approximately 2-3 hours additional analysis time
- Significantly enriches kernel output

#### Dependencies
- Requires Kernel_Validation_Protocol v3.0+
- Requires Artifact 1 Device Taxonomy

---

### [Kernel Validation Protocol v3.1] - 2025-11-13

#### Added
- Stage 1.5: Extract Preparation Protocol
- Dual output format requirement (JSON + Reasoning Document)
- Extract file format specifications
- Guidance for checking existing extract analyses

#### Changed
- Extract preparation is now separate step before tagging
- Stage 2 references prepared extract files
- Minor clarifications based on TKAM pilot experiment

#### Rationale
- TKAM pilot revealed need for formal extract specification
- Improved process clarity and repeatability

#### Dependencies
- Foundational protocol (no dependencies)

---

## Templates

### [Template_Literary_Analysis_MacroMicro v2.0] - 2025-11-15

#### Added
- Full 6-step scaffolding per device
- Integrated location hints from v2.1 template updates
- Enhanced teacher guidance notes

#### Changed
- Improved macro-micro TVODE guidance

#### Dependencies
- Required for Stage 2 v4.1
- Integrates Template_Updates v2.1

---

### [Template_Updates v2.1] - 2025-11-14

#### Added
- `{{EXAMPLE_LOCATIONS}}` variable for templates
- Chapter/page hints in worksheets
- Graceful degradation if examples unavailable

#### Example
```markdown
**Where to look:**
**Chapter 10** (pages 90-93): Atticus teaches shooting lesson
```

#### Dependencies
- Requires Kernel_Protocol_Enhancement v3.3 examples
- Compatible with all MacroMicro templates

---

### [Template_Literary_Analysis_MacroMicro v1.0] - 2025-11-14

#### Added
- Initial macro-micro template structure
- Section 1: Macro teaching
- Section 2: Device analysis
- Section 3: TVODE construction

#### Changed
- **BREAKING:** Replaces Template_Literary_Analysis_6Step.md
- New focus on macro-focused pedagogy

#### Dependencies
- Requires Stage 1B v5.0 packages
- Enables Stage 2 v4.0

---

### [Template_TVODE_MacroMicro v1.0] - 2025-11-14

#### Added
- TVODE construction guide connecting macro to micro
- Sentence frames for integration
- Example TVODEs

---

### [Template_Teacher_Key_MacroMicro v1.0] - 2025-11-14

#### Added
- Answer keys with teaching guidance
- Macro concept explanations for teachers
- Sample TVODEs with analysis
- Device identification answers

---

## Core Artifacts (Stable - No Changes)

### [Artifact 1: Device Taxonomy] - Stable
- 50+ literary devices organized by function
- Classification: Layer | Function | Engagement
- No version changes

### [Artifact 2: Text Tagging Protocol] - Stable
- Tagging methodology for texts
- Device identification guidelines
- No version changes

### [Artifact 3: Alignment Measurement Algorithm] - Stable
- Algorithm for calculating alignment scores
- Mathematical formulas and weights
- Version 1.0 (operational specification)

### [LEM: Narrative-Rhetoric Triangulation] - Stable
- Literary Experience Model core theory
- Stage 1 triangulation methodology
- Foundational theoretical document

---

## Version Status Summary

### ✓ Current Active Versions

**Kernel Protocols:**
- Kernel_Validation_Protocol v3.3
- Kernel_Protocol_Enhancement v3.3

**Stage Implementations:**
- Stage_1A v5.1 (functionally identical to v5.0)
- Stage_1B v5.1
- Stage_2 v4.1

**Templates:**
- Template_Literary_Analysis_MacroMicro v2.0
- Template_TVODE_MacroMicro v1.0
- Template_Teacher_Key_MacroMicro v1.0

**Stable Artifacts:**
- Artifact_1: Device Taxonomy v1.0
- Artifact_2: Text Tagging Protocol v1.0
- Artifact_3: Alignment Measurement Algorithm v1.0
- LEM: Narrative-Rhetoric Triangulation v1.0

---

## ✗ Deprecated Versions

**Superseded Stage Implementations:**
- Stage_1A v4.2 → Use v5.1
- Stage_1B v4.2 → Use v5.1
- Stage_2 v3.2 → Use v4.1

**Superseded Templates:**
- Template_Literary_Analysis_6Step → Use Template_Literary_Analysis_MacroMicro v2.0

---

## Migration Guides

### From Stage 1A v4.2 to v5.1
**Breaking Change - No Migration Path**

Required: Complete regeneration from kernel JSON
1. Run Stage 1A v5.1 extraction on kernel JSON
2. Regenerate all downstream Stage 1B and Stage 2 outputs

### From Stage 1B v4.2 to v5.1
**Breaking Change - No Migration Path**

Required: Complete regeneration from Stage 1A v5.1 output
1. Must have Stage 1A v5.1 output first
2. Run Stage 1B v5.1 on new Stage 1A data
3. Regenerate all Stage 2 worksheets

### From Stage 2 v3.2 to v4.1
**Breaking Change - No Migration Path**

Required: New template system
1. Must have Stage 1B v5.1 packages
2. Apply new MacroMicro templates
3. Regenerate all worksheets and teacher keys

### From Kernel Enhancement v3.2 to v3.3
**Backward Compatible with Migration**

Optional: Add structured examples
1. Add examples array to existing devices
2. Populate with {freytag_section, scene, chapter, page_range, quote_snippet}
3. Add edition_reference to validation_metadata

---

## Dependency Chart

```
Kernel_Validation_Protocol v3.3
├── Triggers → Kernel_Protocol_Enhancement v3.3
├── Enables → Stage_1A v5.0/v5.1
└── Required by → All downstream stages

Kernel_Protocol_Enhancement v3.3
├── Triggered by → Kernel_Validation_Protocol v3.3
├── Enables → Stage_1A v5.0 automation
└── Required by → Template_Updates v2.1

Stage_1A v5.1
├── Requires → Kernel_Validation_Protocol v3.2+
├── Requires → Kernel_Protocol_Enhancement v3.3
└── Enables → Stage_1B v5.1

Stage_1B v5.1
├── Requires → Stage_1A v5.1 output
└── Enables → Stage_2 v4.1

Stage_2 v4.1
├── Requires → Stage_1B v5.1 packages
├── Requires → Template_Literary_Analysis_MacroMicro v2.0
└── Generates → Final worksheets and teacher keys
```

---

## Release Notes

### Major Releases

#### v5.0 - Macro-Micro Integration (2025-11-15)
**Major Breaking Changes**

Complete redesign of Stage 1A, 1B, and Stage 2 to support macro-focused pedagogy. Worksheets now teach macro alignment concepts (exposition, structure, voice) through micro literary devices.

**Highlights:**
- Macro-micro extraction and packaging
- Pedagogical scaffolding integration
- Single chapter focus per week
- Teaching notes and context

**Migration:** Requires complete regeneration of all outputs from kernel JSON.

---

#### v3.2 - Terminology Clarification (2025-11-14)
**Non-Breaking Clarification**

Critical terminology distinction between 84 macro alignment variables and 50+ micro devices. No methodology changes, but improved clarity across all documentation.

**Highlights:**
- "Devices" now exclusively means micro techniques
- "Alignment variables" means macro elements
- Stage 2 renamed to "Stage 2A: Macro Alignment Tagging"

**Migration:** Update terminology in documentation. No regeneration required.

---

#### v3.1 - Extract Preparation Protocol (2025-11-13)
**Non-Breaking Addition**

Formalized extract preparation as separate protocol step based on TKAM pilot findings.

**Highlights:**
- Stage 1.5 added
- Dual output format (JSON + Reasoning Document)
- Extract file format specifications

**Migration:** Apply to new analyses. Existing analyses compatible.

---

## Contributing

When updating versions:

1. Follow semantic versioning: MAJOR.MINOR.PATCH
2. Update this CHANGELOG.md with:
   - Version number and date
   - Changes categorized as Added/Changed/Deprecated/Removed/Fixed/Security
   - Migration notes for breaking changes
   - Dependency updates
3. Update version numbers in implementation files
4. Document rationale for major changes
5. Create git tags: `git tag -a vX.X.X -m "Version X.X.X"`

---

## Version Numbering

### Kernel Protocols
- Format: `vX.X` (Major.Minor)
- Major: Breaking changes, methodology updates
- Minor: Additive features, clarifications

### Stage Implementations
- Format: `vX.X` (Major.Minor)
- Major: Breaking output structure changes
- Minor: Non-breaking enhancements

### Templates
- Format: `vX.X` (Major.Minor)
- Major: Breaking template structure
- Minor: Variable additions, improvements

---

## Support

For questions about version compatibility or migration:
- Review dependency chart above
- Check migration guides for your version path
- Refer to COMPLETE_REVISION_HISTORY.md for detailed rationale

---

**Last Updated:** 2025-11-24 (v5.1.2)  
**Changelog Maintainer:** Project Documentation System
