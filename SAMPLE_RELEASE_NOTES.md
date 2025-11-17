# Sample Release Notes Files

These are ready-to-use release notes for each major version. Save them in `docs/releases/` or use directly in GitHub releases.

---

## File: kernel-v3.3.md

```markdown
# Kernel Validation Protocol v3.3

**Release Date:** November 14, 2025  
**Status:** Stable  
**Type:** Minor Enhancement

---

## Overview

This release adds structured examples to the Kernel Validation Protocol, enabling automated worksheet generation with chapter/page references.

## What's New

### Structured Examples Array

- **Freytag section mapping** - Links examples to narrative arc positions
- **Scene identifiers** - 10-50 character descriptions for easy location
- **Chapter/page references** - Precise location data for worksheets
- **Quote snippets** - 20-100 character excerpts (replaces full quotes)
- **Edition reference** - ISBN or edition info in validation metadata

### Example Structure

```json
{
  "examples": [
    {
      "freytag_section": "CLUST-BEG",
      "scene": "Atticus teaches shooting lesson",
      "chapter": 10,
      "page_range": "90-93",
      "quote_snippet": "it's a sin to kill a mockingbird"
    }
  ]
}
```

### Specifications

- **2-3 examples required** per device used in education vertical (Weeks 1-4)
- **Examples must align** with position codes (CLUST-BEG, CLUST-MID, etc.)
- **~20-30% size reduction** from using snippets vs. full quotes
- **Validation rules added** to ensure example quality

## Benefits

✅ Automated worksheet population with location hints  
✅ Reduced JSON file size  
✅ Better pedagogical utility  
✅ Reproducibility with edition references  
✅ Efficient location indexing  

## Migration

### Backward Compatible

Existing v3.2 kernel JSON can be migrated by:
1. Adding `examples` array to existing devices
2. Populating with structured format
3. Adding `edition_reference` to validation metadata

### Optional Enhancement

Examples structure is optional unless generating educational worksheets. Kernel analysis can still be performed without examples.

## Dependencies

### Triggers
- **Kernel Protocol Enhancement v3.3** - Must update examples format

### Enables
- **Stage 1A v5.0** - Can use structured examples for automation
- **Template Updates v2.1** - Location hints in worksheets

### Requires
- No new dependencies (backward compatible)

## Files Changed

- `Kernel_Validation_Protocol_v3_3.md` - Updated specification
- `CHANGELOG.md` - Version history updated

## Breaking Changes

**None** - This is a backward-compatible enhancement.

## Related Releases

- [Kernel Protocol Enhancement v3.3](enhancement-v3.3.md)
- [Stage 1A v5.0](stage1a-v5.0.md)
- [Template Updates v2.1](templates-v2.1.md)

## Documentation

- [Full Specification](../../kernel/Kernel_Validation_Protocol_v3_3.md)
- [CHANGELOG](../../CHANGELOG.md#kernel-validation-protocol-v33)
- [Examples Guide](../../docs/guides/examples-structure.md)

## Download

[Download Kernel v3.3](../../releases/kernel-v3.3.zip)

---

**Questions?** See [CHANGELOG.md](../../CHANGELOG.md) or open an issue.
```

---

## File: stage1a-v5.0.md

```markdown
# Stage 1A v5.0 - Macro-Micro Extraction

**Release Date:** November 15, 2025  
**Status:** Stable  
**Type:** Major Release (Breaking Changes)

---

## ⚠️ BREAKING CHANGES

**This is a major release with breaking changes. Cannot migrate from v4.2.**

### What Breaks

- **Output format completely redesigned** - Flat device list → Macro-micro packages
- **Incompatible with v4.2 processors** - Stage 1B v4.2 cannot read v5.0 output
- **All downstream outputs invalid** - Stage 1B and Stage 2 must be regenerated
- **Requires complete regeneration** - Cannot convert v4.2 outputs to v5.0

## Overview

Complete redesign of Stage 1A extraction to support macro-focused pedagogy. Now extracts both macro alignment elements and micro devices, showing their relationship.

## What's New

### Macro-Micro Extraction

Extract **both** alignment elements (macro) and devices (micro):
- Identifies which macro concepts are present (Exposition, Structure, Voice)
- Maps which devices execute those concepts
- Creates explicit teaching relationships

### Package Structure

Organizes output as integrated macro-micro packages:

```json
{
  "macro_micro_packages": {
    "exposition_package": {
      "macro_focus": "Exposition",
      "macro_variables": {
        "narrative.structure.exposition_method": "Incremental revelation",
        "narrative.voice.distance": "Retrospective intimacy"
      },
      "micro_devices": [
        {
          "device_name": "Indirect Characterization",
          "executes_macro": "Builds character knowledge gradually through actions and dialogue",
          "examples": [...]
        }
      ],
      "focus_chapter": 1
    }
  }
}
```

### New Fields

- **`executes_macro`** - Explains how each device builds the macro concept
- **`macro_focus`** - The primary alignment element for this package
- **`macro_variables`** - Specific alignment variables and their values
- **`focus_chapter`** - Single chapter per package for focused analysis

### Chapter Mapping

- Single chapter focus per package
- Deep analysis vs. scattered examples
- Better alignment with reading sequence

## Why This Change?

### Problem with v4.2
- Only extracted devices without context
- No connection to macro alignment concepts
- Couldn't support macro-focused pedagogy
- Devices taught in isolation

### Solution in v5.0
- Teaches macro concepts (exposition, structure, voice)
- Shows how devices execute those concepts
- Enables "what + how" teaching model
- Supports educational vertical goals

## Benefits

✅ Macro concepts explicitly taught  
✅ Devices connected to their function  
✅ Single chapter focus  
✅ Teaching context included  
✅ Enables pedagogical progression  

## Migration Guide

### From v4.2 to v5.0

**Step 1: Backup**
```bash
# Save your v4.2 outputs
cp TKAM_Stage1A_v4.2_Extraction_Output.json backups/
```

**Step 2: Regenerate Stage 1A**
```bash
# Run Stage 1A v5.0 on kernel JSON
python stage1a_v5.0.py TKAM_N-R-D_Analysis_v3.3.json
# Output: TKAM_Stage1A_v5.0_Extraction_Output.json
```

**Step 3: Regenerate Stage 1B**
```bash
# Must use Stage 1B v5.0+ to process new format
python stage1b_v5.0.py TKAM_Stage1A_v5.0_Extraction_Output.json
```

**Step 4: Regenerate Stage 2**
```bash
# Must use Stage 2 v4.0+ for new templates
python stage2_v4.0.py TKAM_Stage1B_v5.0_Week_Packages.json
```

### Expected Time

- Stage 1A regeneration: +30% time (relationship mapping)
- Stage 1B regeneration: ~Same time
- Stage 2 regeneration: +2-3 hours (new templates)
- **Total:** Plan 1 full day for complete regeneration

### No Migration Path

**Cannot convert v4.2 outputs to v5.0 format** because:
- Macro-micro relationships not present in v4.2
- Teaching context not captured
- Chapter mapping not structured
- Must re-extract from kernel JSON

## Dependencies

### Requires

- **Kernel Validation Protocol v3.2+** - Terminology clarification
- **Kernel Protocol Enhancement v3.3** - Examples structure
- **Python 3.8+** - Implementation language

### Enables

- **Stage 1B v5.0** - Processes macro-micro packages
- **Macro-focused education** - Teaching model support

### Impacts

- **Stage 1B v4.2** - Outputs become invalid
- **Stage 2 v3.2** - Outputs become invalid
- **All worksheets** - Must be regenerated

## Files Changed

### New
- `Stage_1A_v5.0_Implementation.md` - Full specification

### Deprecated
- `Stage_1A_v4.2_Implementation.md` - Superseded, no longer supported

### Updated
- `CHANGELOG.md` - Version history

## Breaking Changes Summary

| What | v4.2 | v5.0 | Migration |
|------|------|------|-----------|
| Output format | Flat list | Packages | None - regenerate |
| Macro elements | ❌ None | ✅ Included | Requires v5.0 |
| Device context | ❌ Isolated | ✅ Mapped | Requires v5.0 |
| Chapter focus | ❌ Scattered | ✅ Single | Requires v5.0 |

## Related Releases

- **Part of:** v5.0 Macro-Micro Integration series
- **Supersedes:** [Stage 1A v4.2](stage1a-v4.2.md) (deprecated)
- **Required by:** [Stage 1B v5.0](stage1b-v5.0.md)
- **Enables:** [Stage 2 v4.0](stage2-v4.0.md)

## Documentation

- [Implementation Spec](../../stages/Stage_1A_v5_0_Implementation.md)
- [Migration Guide](../../docs/migration/v4.2-to-v5.0.md)
- [CHANGELOG](../../CHANGELOG.md#stage-1a-v50)
- [Complete Revision History](../../COMPLETE_REVISION_HISTORY.md)

## Download

[Download Stage 1A v5.0](../../releases/stage1a-v5.0.zip)

---

**Questions?** See [migration guide](../../docs/migration/v4.2-to-v5.0.md) or open an issue.

**Warning:** This release requires complete regeneration. Budget 1 full day for transition.
```

---

## File: stage2-v4.1.md

```markdown
# Stage 2 v4.1 - 6-Step Pedagogical Scaffolding

**Release Date:** November 15, 2025  
**Status:** Stable  
**Type:** Minor Enhancement

---

## Overview

This release adds structured 6-step pedagogical scaffolding to worksheet device analysis, providing clear skill progression from recognition to application.

## What's New

### 6-Step Learning Progression

**Step 1: DEFINITION (Recognition)**
- Read and understand device definition
- Recognize device characteristics
- Basic comprehension skill

**Step 2: FIND (Matching)**
- Locate examples in text
- Match definition to textual evidence
- Application of recognition

**Step 3: IDENTIFY (Multiple Choice)**
- Distinguish device from alternatives
- Test understanding through choice
- Differentiation skill

**Step 4: ANALYZE (Sequencing)**
- Order techniques or effects
- Understand relationships
- Higher-order thinking

**Step 5: DETAIL (Textual Evidence)**
- Quote specific examples
- Provide evidence and context
- Precision and citation skills

**Step 6: EFFECT (Categorization)**
- Classify the impact of device
- Connect to reader experience
- Synthesis and evaluation

### Example Worksheet Structure

```markdown
## DEVICE 1: Indirect Characterization

### Step 1: DEFINITION
Indirect characterization reveals character traits through actions,
dialogue, thoughts, and interactions rather than direct statements.

Read the definition above. Indirect characterization shows us who
a character is rather than telling us directly.

### Step 2: FIND
Find an example of indirect characterization in Chapter 1 (pages 3-24).

**Where to look:**
Chapter 1 (pages 5-10): Scout's interactions with Dill

**My Example:**
_____________________________________________________________

### Step 3: IDENTIFY
Which of these is an example of indirect characterization?

[ ] "Scout was a curious child."
[ ] "Scout asked questions about everything she encountered."  ✓
[ ] The author describes Scout as inquisitive.

### Step 4: ANALYZE
Put these characterization techniques in order from direct to indirect:

[ ] Author statement about personality
[ ] Character's actions revealing traits
[ ] Character's dialogue showing values

### Step 5: DETAIL
Quote textual evidence of indirect characterization:

"_____________________________________________________________"

### Step 6: EFFECT
How does this characterization affect your understanding of Scout?

[ ] Shows her personality through actions ✓
[ ] Tells you directly what she's like
[ ] Summarizes her character traits
```

## Benefits

✅ Clear skill progression  
✅ Scaffolding for different ability levels  
✅ Multiple skill types (recognition → application → synthesis)  
✅ Improved learning outcomes  
✅ Better student engagement  

## Migration

### Non-Breaking Enhancement

**Compatible with v4.0** - Can enhance existing worksheets or regenerate.

### Two Options

**Option 1: Enhance Existing**
- Add 6-step structure to current v4.0 worksheets
- Manual addition of steps
- Preserves existing content

**Option 2: Regenerate (Recommended)**
- Use Stage 2 v4.1 to regenerate all worksheets
- Automatic 6-step structure
- Full integration with templates

### Recommended Approach

Regenerate worksheets using v4.1 for full 6-step experience:

```bash
python stage2_v4.1.py TKAM_Stage1B_v5.1_Week_Packages.json
```

## Dependencies

### Requires
- **Stage 1B v5.1** - Week packages with macro-micro structure
- **Template_Literary_Analysis_MacroMicro v2.0** - Updated template

### Extends
- **Stage 2 v4.0** - Non-breaking enhancement

### Updates
- **Templates** - Literary Analysis template updated to v2.0

## Files Changed

### New
- None (enhancement of existing)

### Updated
- `Stage_2_v4_1_Implementation.md` - Updated specification
- `Template_Literary_Analysis_MacroMicro.md` - v2.0 with 6-step structure
- `CHANGELOG.md` - Version history

## Breaking Changes

**None** - This is a non-breaking enhancement.

Existing v4.0 worksheets remain valid. 6-step structure is additive.

## Pedagogy Details

### Scaffolding Levels

| Step | Skill Level | Bloom's Taxonomy | Student Action |
|------|-------------|------------------|----------------|
| 1. Definition | Basic | Remember | Read, recognize |
| 2. Find | Basic-Medium | Understand | Locate, match |
| 3. Identify | Medium | Apply | Choose, distinguish |
| 4. Analyze | Medium-High | Analyze | Order, relate |
| 5. Detail | High | Evaluate | Quote, justify |
| 6. Effect | High | Create | Synthesize, assess |

### Learning Outcomes

Students who complete 6-step analysis will be able to:
- Define literary devices accurately
- Locate devices in complex texts
- Distinguish devices from similar techniques
- Analyze device relationships and effects
- Cite textual evidence precisely
- Evaluate device impact on reader experience

## Related Releases

- **Extends:** [Stage 2 v4.0](stage2-v4.0.md)
- **Requires:** [Stage 1B v5.1](stage1b-v5.1.md)
- **Updates:** [Templates v2.0](templates-v2.0.md)

## Documentation

- [Implementation Spec](../../stages/Stage_2_v4_1_Implementation.md)
- [Template Spec](../../templates/Template_Literary_Analysis_MacroMicro.md)
- [CHANGELOG](../../CHANGELOG.md#stage-2-v41)
- [Pedagogy Guide](../../docs/guides/6-step-pedagogy.md)

## Download

[Download Stage 2 v4.1](../../releases/stage2-v4.1.zip)

---

**Questions?** See [CHANGELOG.md](../../CHANGELOG.md) or open an issue.
```

---

## File: v5.0-macro-micro.md (Series Overview)

```markdown
# v5.0 Macro-Micro Integration Series

**Release Date:** November 15, 2025  
**Type:** Major Release Series (Breaking Changes)

---

## Series Overview

The v5.0 series represents a complete redesign of Stage implementations to support macro-focused pedagogy. This is the largest architectural change since project inception.

## What Changed

### Complete Paradigm Shift

**Before (v4.2):** Device-focused analysis
- Extracted devices in isolation
- Taught devices as individual techniques
- No connection to macro alignment concepts

**After (v5.0):** Macro-micro integrated analysis
- Extracts macro alignment elements + micro devices
- Shows how devices execute macro concepts
- Teaches literary alignment through device analysis

### The Big Idea

**Teach WHAT (macro) through HOW (micro)**

- **WHAT** - Macro alignment elements: Exposition, Structure, Voice
- **HOW** - Micro devices: The techniques that build those elements

Example:
- **Macro:** "Exposition is how readers learn about characters and setting"
- **Micro:** "Lee builds exposition through indirect characterization, setting imagery, and dialect"

## Releases in This Series

### [Stage 1A v5.0](stage1a-v5.0.md)
**Macro-Micro Extraction**

- Extracts both macro elements and micro devices
- Maps relationship between them
- Creates integrated packages
- **Breaking:** Complete output redesign

### [Stage 1B v5.0](stage1b-v5.0.md)
**Pedagogical Week Packages**

- Structures 4-week progression
- Each week teaches one macro concept
- Scaffolded difficulty (High → Low)
- **Breaking:** New package structure

### [Stage 1B v5.1](stage1b-v5.1.md)
**Chapter Chronology**

- Reordered weeks to follow chapter sequence
- Week 1: Exposition (Chapter 1)
- Week 2: Devices (Chapter 10)
- Minor: Week order only

### [Stage 2 v4.0](stage2-v4.0.md)
**Macro-Micro Templates**

- New template system for macro-focused worksheets
- Three new templates (Analysis, TVODE, Teacher Key)
- **Breaking:** New template structure required

### [Stage 2 v4.1](stage2-v4.1.md)
**6-Step Pedagogy**

- Added scaffolded skill progression
- Definition → Find → Identify → Analyze → Detail → Effect
- Enhancement: Non-breaking addition

## Impact

### What This Means for Users

**If you're on v4.2:**
- ⚠️ Must regenerate all outputs
- ⚠️ Plan 1 full day for migration
- ⚠️ No automatic migration path
- ✅ Significantly better educational outcomes
- ✅ Macro-focused pedagogy support
- ✅ Scaffolded learning progression

**If you're starting fresh:**
- ✅ Use v5.1 directly
- ✅ Full macro-micro integration
- ✅ Complete pedagogical framework
- ✅ 6-step scaffolded analysis

## Educational Benefits

### For Students

✅ **Clearer learning objectives** - Know what macro concept they're learning  
✅ **Better skill progression** - Scaffolded from simple to complex  
✅ **Deeper understanding** - See how techniques build bigger concepts  
✅ **Practical application** - Connect devices to their actual function  

### For Teachers

✅ **Macro-focused lessons** - Teach conceptual understanding  
✅ **Teaching context provided** - Know how to explain macro-micro connection  
✅ **Progressive difficulty** - 4-week scaffold built-in  
✅ **Complete materials** - Worksheets + teacher keys  

## Migration Guide

### Complete Series Migration

**Time Required:** 1 full day

**Prerequisites:**
- Kernel JSON v3.3 (with examples)
- Python 3.8+
- All v5.0+ implementations

**Steps:**

1. **Backup v4.2 outputs**
   ```bash
   mkdir backups
   cp *_v4.2_*.json backups/
   ```

2. **Regenerate Stage 1A (2-3 hours)**
   ```bash
   python stage1a_v5.1.py TKAM_N-R-D_Analysis_v3.3.json
   # Output: TKAM_Stage1A_v5.1_Extraction_Output.json
   ```

3. **Regenerate Stage 1B (1-2 hours)**
   ```bash
   python stage1b_v5.1.py TKAM_Stage1A_v5.1_Extraction_Output.json
   # Output: TKAM_Stage1B_v5.1_Week_Packages.json
   ```

4. **Regenerate Stage 2 (3-4 hours)**
   ```bash
   python stage2_v4.1.py TKAM_Stage1B_v5.1_Week_Packages.json
   # Outputs: 4 weeks of worksheets + teacher keys
   ```

5. **Review and validate**
   - Check macro-micro connections
   - Verify chapter/page references
   - Test with sample students

### Why No Migration Tool?

Cannot automate because:
- Macro-micro relationships not in v4.2 data
- Teaching context not captured
- Chapter mapping not structured
- Pedagogical scaffolding not present

Must re-extract from kernel JSON to capture all required information.

## Breaking Changes Summary

| Component | What Breaks | Why | Fix |
|-----------|-------------|-----|-----|
| Stage 1A | Output format | New macro-micro structure | Regenerate from kernel |
| Stage 1B | Package format | Pedagogical scaffolding | Regenerate from 1A v5.0 |
| Stage 2 | Templates | Macro-focused teaching | Use new templates |
| Worksheets | All outputs | New structure | Regenerate all |

## Dependencies

### This Series Requires

- **Kernel Validation Protocol v3.2+** - Terminology clarification
- **Kernel Protocol Enhancement v3.3** - Examples structure
- **All previous artifacts** - Taxonomy, tagging protocol, LEM theory

### This Series Enables

- Macro-focused pedagogy
- Scaffolded learning progression
- Complete educational vertical
- 6-step skill development

## Technical Details

### New Data Structures

```json
{
  "macro_micro_packages": {
    "package_name": {
      "macro_focus": "Concept",
      "macro_variables": {...},
      "micro_devices": [
        {
          "device_name": "...",
          "executes_macro": "...",
          "teaching_notes": {...}
        }
      ]
    }
  }
}
```

### New Template Variables

- `{{MACRO_FOCUS}}` - The macro concept for the week
- `{{MACRO_EXPLANATION}}` - How the concept works
- `{{EXECUTES_MACRO}}` - How this device builds the concept
- `{{TEACHING_SEQUENCE}}` - Ordered device progression
- `{{SCAFFOLDING_LEVEL}}` - Current difficulty level

## Testing

### Validation Checklist

Before finalizing v5.0 migration:

- [ ] All Stage 1A packages have macro focus
- [ ] All devices have `executes_macro` field
- [ ] Single chapter focus per package
- [ ] Teaching notes present for educators
- [ ] Stage 1B has scaffolding levels
- [ ] Stage 1B weeks in correct order
- [ ] Stage 2 worksheets use macro-micro templates
- [ ] All 6 steps present in v4.1 worksheets
- [ ] Teacher keys include macro explanations

### Known Issues

None currently. Report issues at [GitHub Issues](../../issues).

## Documentation

- [Individual Release Notes](#releases-in-this-series)
- [Complete Migration Guide](../../docs/migration/v4.2-to-v5.1.md)
- [CHANGELOG](../../CHANGELOG.md)
- [Complete Revision History](../../COMPLETE_REVISION_HISTORY.md)

## Downloads

- [Stage 1A v5.1](../../releases/stage1a-v5.1.zip)
- [Stage 1B v5.1](../../releases/stage1b-v5.1.zip)
- [Stage 2 v4.1](../../releases/stage2-v4.1.zip)
- [Complete v5.1 Bundle](../../releases/v5.1-complete.zip)

---

**Questions?** See [complete migration guide](../../docs/migration/v4.2-to-v5.1.md) or open an issue.

**Support:** For migration assistance, see [support resources](../../docs/support.md).
```

---

## Usage Instructions

1. **Save these files** in your `docs/releases/` directory
2. **Use in GitHub releases** - Copy-paste content when creating releases
3. **Link from CHANGELOG** - Reference these detailed notes from CHANGELOG.md
4. **Update as needed** - Customize for your specific project details

## File Naming Convention

```
docs/releases/
├── kernel-v3.3.md
├── enhancement-v3.3.md
├── stage1a-v5.0.md
├── stage1a-v5.1.md
├── stage1b-v5.0.md
├── stage1b-v5.1.md
├── stage2-v4.0.md
├── stage2-v4.1.md
├── templates-v2.0.md
├── templates-v2.1.md
└── v5.0-macro-micro.md (series overview)
```

---

**These are templates** - Customize paths, links, and details for your repository.
