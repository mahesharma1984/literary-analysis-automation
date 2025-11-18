# Changelog

All notable changes to the Literary Experience Model (LEM) Kernel and Stage protocols will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Kernel Protocol v3.4: Confidence scores for device identifications
- Stage 1A v5.2: Automated macro-micro relationship validation
- Stage 2 v4.2: Differentiated instruction versions
- Template v3.0: Multi-text comparison worksheets

---

# CHANGELOG

All notable changes to the Literary Analysis Automation System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [5.0.0] - 2025-11-18

### Major Release: 5-Week Progression with Device Taxonomy Mapping

This release fundamentally restructures the pedagogical progression from 4 weeks to 5 weeks and replaces fragile keyword-based device categorization with an explicit taxonomy mapping system.

### ⚠️ BREAKING CHANGES

#### Function Signature Changes

**`categorize_device()` in `run_stage1a.py`:**
- **Old:** `categorize_device(device) -> str`
  - Returns: `category` (string: "exposition", "structure", "voice", or "devices_general")
- **New:** `categorize_device(device_name: str, classification: str) -> tuple`
  - Returns: `(week_key, week_label)` tuple
  - Example: `('week_2_literary_devices', 'Week 2: Literary Devices')`

**Impact:** All code calling `categorize_device()` must be updated to:
1. Pass two arguments instead of one
2. Unpack two return values instead of one
3. Use `week_key` instead of `category`

#### Data Structure Changes

**Week Structure:**
- **Old:** 4 weeks
  - Week 1: Foundation/Devices General
  - Week 2: Exposition
  - Week 3: Structure
  - Week 4: Voice
- **New:** 5 weeks
  - Week 1: Exposition
  - Week 2: Literary Devices
  - Week 3: Structure
  - Week 4: Narrative Voice
  - Week 5: Rhetorical Voice

**Week Keys:**
- **Old:** `devices_general`, `exposition`, `structure`, `voice`
- **New:** `week_1_exposition`, `week_2_literary_devices`, `week_3_structure`, `week_4_narrative_voice`, `week_5_rhetorical_voice`

**Loop Ranges:**
- **Old:** `range(1, 5)` for 4 weeks
- **New:** `range(1, 6)` for 5 weeks

#### Device Data Fields

**Removed:**
- `executes_macro` (replaced by `week_label`)

**Added:**
- `week_label` - Human-readable week label (e.g., "Week 2: Literary Devices")

### ✨ Added

#### New Files

1. **`device_taxonomy_mapping.json`** - Core mapping file
   - Explicit device-to-week categorization for 50+ devices
   - Classification codes (Layer|Function|Engagement) for each device
   - Rationale statements explaining categorization decisions
   - Fallback heuristics for unmapped devices
   - Week definitions with pedagogical focus

2. **`test_mapping.py`** - Device mapping validation script
   - Tests device categorization against kernels
   - Reports device distribution across weeks
   - Identifies unmapped devices
   - Provides summary statistics

3. **`test_full_pipeline.py`** - Full pipeline integration test
   - Runs Stage 1A → 1B → 2 on a kernel
   - Validates JSON structure at each stage
   - Checks for 5 weeks in all outputs
   - Reports pass/fail for each stage

4. **`DEVELOPER_GUIDE.md`** - Developer documentation
   - Architecture overview
   - Dependency mapping
   - Change assessment framework
   - Testing protocols
   - Communication guidelines
   - Lessons learned from migration

5. **`DEVICE_MAPPING_USAGE_GUIDE.md`** - Mapping system documentation
   - 5-week structure explanation
   - How to use the mapping file
   - Integration instructions
   - Ambiguous case resolutions
   - Maintenance procedures

6. **`DEVICE_MAPPING_TEST_RESULTS.md`** - Test validation report
   - Results from The Giver (20/20 devices mapped)
   - Results from The Old Man and the Sea (15/15 devices mapped)
   - Edge case analysis
   - Production readiness assessment

#### New Pedagogical Week

**Week 5: Rhetorical Voice**
- **Macro Element:** Irony, persuasion, and interpretive control
- **Teaching Goal:** Understanding rhetorical strategies
- **Scaffolding:** Low - Independent application
- **Devices:** Dramatic Irony, Situational Irony, Verbal Irony, Euphemism, Understatement, Juxtaposition, Repetition, Tone, Diction, Rhetorical Question, Sarcasm

#### New Macro Elements

**Added to `extract_macro_elements()`:**
- `literary_devices` - Foundational figurative language (Week 2)
- `narrative_voice` - POV and consciousness (Week 4, renamed from `voice`)
- `rhetorical_voice` - Irony and persuasion (Week 5)

### 🔄 Changed

#### Stage 1A (`run_stage1a.py`)

**Device Categorization:**
- Replaced keyword-based heuristics with explicit mapping lookup
- Added `fallback_categorization()` function for unmapped devices
- Changed categorization to return both `week_key` and `week_label`

**Device Mapping Initialization:**
```python
# Old
device_mapping = {
    'devices_general': [],
    'exposition': [],
    'structure': [],
    'voice': []
}

# New
device_mapping = {
    'week_1_exposition': [],
    'week_2_literary_devices': [],
    'week_3_structure': [],
    'week_4_narrative_voice': [],
    'week_5_rhetorical_voice': []
}
```

**Macro-Micro Packages:**
- Changed from 4 packages to 5 packages
- Updated package keys to match new week structure
- Added scaffolding levels to each package

**Print Statements:**
- Updated to show 5 weeks with new labels
- Changed device count reporting to match new week keys

#### Stage 1B (`run_stage1b.py`)

**Week Processing:**
- Changed loop from `range(1, 5)` to `range(1, 6)`
- Updated week key lookup to handle 5 weeks
- Added Week 5 to all dictionaries

**Scaffolding Levels:**
```python
scaffolding_levels = {
    1: "High - Teacher models everything",
    2: "Medium-High - Co-construction with students",
    3: "Medium - Students lead with support",
    4: "Medium-Low - Independent work with feedback",
    5: "Low - Independent application"  # NEW
}
```

**Teaching Sequences:**
- Added Week 5 teaching sequence
- Updated Week 2-4 sequences to reflect new progression

**Teaching Approaches:**
```python
teaching_approaches = {
    1: "Here are devices. Let's identify them.",
    2: "Literary devices create meaning through figurative language.",  # CHANGED
    3: "Structure UNFOLDS through devices that create pacing.",
    4: "Narrative voice OPERATES through perspective devices.",  # CHANGED
    5: "Rhetorical voice CONTROLS interpretation through irony and persuasion."  # NEW
}
```

**Progression Summary:**
- Changed `total_weeks` from 4 to 5
- Updated skill progression to 5 steps
- Updated TVODE evolution to 5 weeks
- Added Week 5 scaffolding level

**Markdown Output:**
- Changed header from "4-Week" to "5-Week"
- Updated curriculum overview table to 5 rows
- Added Week 5 section with full details
- Updated progression summary for 5 weeks

#### Device Field Names

**In device data objects:**
- Replaced `executes_macro` with `week_label`
- Updated all references in Stage 1B packaging
- Updated teaching notes to use `week_label`

### 🐛 Fixed

#### Path Handling
- Fixed kernel paths to use relative paths instead of absolute `/mnt/project/`
- Updated test scripts to handle Mac filesystem paths
- Fixed file name format: `v3.3` instead of `v3_3`

#### Device Categorization Errors
- Fixed Interior Monologue incorrectly categorized to Week 1 (now Week 4)
- Fixed Repetition incorrectly categorized to Week 2 (now Week 5)
- Fixed Third-Person Limited confusion with structure devices (now Week 4)
- Fixed Direct Dialogue ambiguity (Week 1 for exposition, not Week 4 for voice)

#### Week Distribution Issues
- Fixed unbalanced device distribution (now 1-6 devices per week)
- Fixed missing Week 5 in output documents
- Fixed inconsistent week labeling across stages

### 🗑️ Removed

**Deprecated Functions:**
- Old keyword-based categorization logic in `run_stage1a.py`

**Deprecated Dictionary Keys:**
- `devices_general` (replaced by `week_2_literary_devices`)
- Old week keys: `exposition`, `structure`, `voice`

**Deprecated Variables:**
- `category` variable (replaced by `week_key`)
- `executes_macro` field (replaced by `week_label`)

### 📊 Testing

#### Validated Against Kernels
- ✅ The Giver (20 devices) - 100% mapped
- ✅ The Old Man and the Sea (15 devices) - 100% mapped
- ⏭️ To Kill a Mockingbird - Pending

#### Integration Tests
- ✅ Stage 1A produces valid 5-week JSON
- ✅ Stage 1B consumes Stage 1A and produces 5-week progression
- ✅ Stage 2 generates worksheets for all 5 weeks
- ✅ Full pipeline runs without errors

### 📝 Documentation

**New Documentation:**
- DEVELOPER_GUIDE.md - How to modify the system safely
- DEVICE_MAPPING_USAGE_GUIDE.md - How to use the mapping system
- DEVICE_MAPPING_TEST_RESULTS.md - Validation results
- CHANGELOG.md - This file

**Updated Documentation:**
- README.md - Updated to reflect 5-week structure (if exists)
- REBUILD_INSTRUCTIONS.md - Updated for new mapping system (if exists)

### 🔧 Migration Guide

#### For Existing Kernels

1. No kernel changes required - kernels are unchanged
2. Re-run Stage 1A with new mapping: `python3 run_stage1a.py kernels/your_kernel.json`
3. Re-run Stage 1B: `python3 run_stage1b.py outputs/your_stage1a.json`
4. Validate 5 weeks are present in output

#### For Custom Code

If you have custom scripts calling `categorize_device()`:

**Before:**
```python
category = categorize_device(device)
if category == "exposition":
    # ...
```

**After:**
```python
week_key, week_label = categorize_device(device['name'], device.get('classification', ''))
if week_key == "week_1_exposition":
    # ...
```

#### For Week References

**Before:**
```python
for week_num in range(1, 5):  # 4 weeks
    # ...
```

**After:**
```python
for week_num in range(1, 6):  # 5 weeks
    # ...
```

### 🎯 Future Work

**Planned Enhancements:**
- Test against TKAM kernel (larger device set)
- Add more narrative voice variations to mapping
- Expand Week 3 with temporal manipulation devices
- Add metafictional devices for advanced texts
- Create review interface for manual categorization approval
- Add versioning system for mapping file changes

**Known Limitations:**
- Fallback heuristics still use keyword matching (should be rarely needed)
- Macro variables often empty in kernels (depends on kernel creation)
- Stage 2 may need updates for Week 5 worksheet templates

### 👥 Contributors

- System design: Original curriculum framework
- 5.0 Implementation: Migration to 5-week structure with mapping system
- Testing: Validation against The Giver and The Old Man and the Sea

---

## [4.x] - Previous Versions

### [4.1] - 2025-11-XX
- 4-week structure with keyword-based categorization
- Stage 1A, 1B, 2 pipeline established
- TVODE construction templates

### [4.0] - 2025-XX-XX
- Initial macro-micro curriculum design
- Kernel format v3.3
- Device taxonomy framework

---

## Version Numbering

**Format:** MAJOR.MINOR.PATCH

- **MAJOR:** Breaking changes to data structures or APIs
- **MINOR:** New features, backward compatible
- **PATCH:** Bug fixes, documentation updates

**Current Version:** 5.0.0
- Major version bump due to breaking changes in function signatures and data structures
- Introduces 5-week structure (breaking change)
- New mapping system (new feature)

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

**Last Updated:** 2025-11-17  
**Changelog Maintainer:** Project Documentation System
