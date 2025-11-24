

Statistical Validation of Kernel Reliability Version 3.3 | November 2025

CHANGELOG v3.2 â†’ v3.3
* DEVICE STRUCTURE ENHANCEMENT: Added `examples` array specification for pedagogically relevant devices
* Examples include Freytag section mapping, scene identifiers, chapter/page references, and optional quote snippets
* Specification: 2-3 examples required for devices used in educational vertical (Weeks 1-4)
* Examples leverage existing Freytag-mapped extract structure for efficient location indexing
* Validation rules added: examples must align with position codes (CLUST-BEG, CLUST-MID, etc.)
* No changes to core validation methodology or success criteria

Previous changes (v3.1 â†’ v3.2):
* TERMINOLOGY UPDATE: Clarified distinction between macro alignment elements and micro devices
* "Stage 2: N-R-D Tagging" renamed to "Stage 2A: Macro Alignment Tagging"
* "Devices" now refers exclusively to 50+ micro literary techniques (Artifact 1 taxonomy)
* "Alignment variables" or "narrative/rhetorical elements" refers to 84 core variables
* Updated all references throughout to maintain terminological consistency
* No substantive methodology changes from v3.1

Previous changes (v3.0 â†’ v3.1):
* Added Stage 1.5: Extract Preparation Protocol
* Formalized dual output format requirement (JSON + Reasoning Document)
* Added extract file format specifications
* Clarified that extract preparation is separate step before tagging
* Added guidance for checking existing extract analyses
* Updated Stage 2 to reference prepared extract files
* Minor clarifications throughout based on TKAM pilot experiment

Protocol Overview 

Purpose 
Validate that the kernel's three analytical layers produce statistically reliable and methodologically robust classifications across different processing conditions. 

This protocol tests ONLY kernel reliability. It does NOT test:
* âœ— Vertical integration (see Education Vertical Build & Validation v4.2)
* âœ— API structure (see Education Vertical Build & Validation v4.2)
* âœ— Performance benchmarks (separate engineering concern)
* âœ— TVODE generation (vertical responsibility, not kernel) 

Scope: Kernel internal processing (Layers 1-3: Taxonomy â†’ Tagging â†’ Alignment)

Research Questions 

Core Validation Questions
1. Order Independence: Do different tagging orders produce equivalent alignment scores?
2. Extract Validity: Do Freytag-mapped extracts capture whole-text alignment patterns?
3. Variable Robustness: Which alignment variables show highest/lowest consistency across methods?
4. Model Selection: Does Claude Sonnet 4.5 produce equivalent results to Opus 4? 

Success Criteria 

Kernel is statistically reliable if:
* âœ“ ICC >0.85 for composite alignment across tagging orders (order-independent)
* âœ“ r >0.80 between full-text and extract alignment scores (extracts valid)
* âœ“ >85% agreement on high-priority alignment variables (POV, focalization, reliability)
* âœ“ >80% alignment type agreement across conditions (Reinforcing/Tension/Failed) 

Kernel needs refinement if:
* âš  ICC <0.75 (order-dependent, must standardize processing order)
* âš  r <0.70 (extracts insufficient, must use full texts)
* âš  <75% agreement on critical alignment variables (definitions need improvement) 

Kernel has fundamental issues if:
* âœ— ICC <0.50 (unstable classifications)
* âœ— r <0.50 (extracts completely invalid)
* âœ— <60% alignment type agreement (classification unreliable)

Experimental Design 

Within-subjects factorial design:
* 6 tagging orders Ã— 2 scope conditions (full text vs extracts) Ã— 10 texts
* Total: 70 kernel outputs per text (60 full-text + 10 extract variations)
* Corpus: 10 texts (700 total kernel classifications)

Input Requirements 

Text Corpus (10 texts) 

Selection criteria for diversity: 

Period distribution:
* 3 texts: 18th-19th century (Austen Emma, Dickens Great Expectations, Eliot Middlemarch)
* 3 texts: Early 20th modernist (Fitzgerald Gatsby, Woolf Mrs Dalloway, Joyce Portrait)
* 2 texts: Mid-late 20th (Nabokov Lolita, Atwood Handmaid's Tale)
* 2 texts: Contemporary/genre (literary fiction + genre novel) 

Rationale: Ensures taxonomy applies across historical periods and stylistic traditions. 

Format requirements:
* Full text available (for full-text tagging conditions)
* Freytag mapping completed (see Stage 1.5: Extract Preparation Protocol)
* Extract files prepared with 5 key sections identified per text
* Extract word count: 20-50 pages per text (4-10 pages per Freytag stage)

Extract Preparation Protocol (v3.1+)

CRITICAL: Extract preparation is now a separate documented stage that must be completed BEFORE tagging experiments begin. Do not identify extracts ad-hoc during analysis.

Tagging Orders (6 conditions) 

Order 1: Nâ†’Râ†’D (Narrative-first)
1. Tag narrative alignment variables (voice + structure)
2. Tag rhetorical alignment variables (voice + structure)
3. Identify micro devices 

Order 2: Râ†’Nâ†’D (Rhetoric-first)
1. Tag rhetorical alignment variables
2. Tag narrative alignment variables
3. Identify micro devices

Order 3: Dâ†’Nâ†’R (Device-first)
1. Identify micro devices
2. Tag narrative alignment variables
3. Tag rhetorical alignment variables

Order 4: Nâ†’Dâ†’R (Narrative-Device)
1. Tag narrative alignment variables
2. Identify micro devices
3. Tag rhetorical alignment variables

Order 5: Râ†’Dâ†’N (Rhetoric-Device)
1. Tag rhetorical alignment variables
2. Identify micro devices
3. Tag narrative alignment variables

Order 6: Dâ†’Râ†’N (Device-Rhetoric)
1. Identify micro devices
2. Tag rhetorical alignment variables
3. Tag narrative alignment variables

Rationale: Tests whether processing order affects final classifications.

---

## DEVICE STRUCTURE SPECIFICATION (NEW IN v3.3)

### Required Device Fields

All devices in the `tagged_profile.devices` array must include:

**Core Classification:**
```json
{
  "name": "Device name",
  "code": "DEVICE-CODE",
  "classification": "Layer|Function|Engagement",
  "layer": "N|R|B",
  "function": "Re|Te|Me",
  "engagement": "T|V|TV",
  "frequency": "Pervasive|High|Moderate|Low",
  "frequency_count": "Quantitative estimate",
  "position": "DIST|CLUST-BEG|CLUST-MID|CLUST-END|FRAME",
  "description": "Brief functional description"
}
```

### Examples Array Specification (NEW IN v3.3)

**For pedagogically relevant devices** (those used in educational vertical Weeks 1-4), add `examples` array:

```json
{
  "name": "Symbolism (Mockingbird)",
  "code": "SYMBOLISM",
  "classification": "B|Me|V",
  "layer": "B",
  "function": "Me",
  "engagement": "V",
  "frequency": "Moderate",
  "frequency_count": "4-5 explicit references",
  "position": "CLUST-BEG+CLUST-END",
  "description": "Mockingbird symbol translates Tom/Boo narratives into moral principle about innocence",
  "examples": [
    {
      "freytag_section": "Exposition",
      "scene": "Atticus teaches shooting lesson",
      "chapter": 10,
      "page_range": "90-93",
      "quote_snippet": "it's a sin to kill a mockingbird"
    },
    {
      "freytag_section": "Climax",
      "scene": "Tom Robinson trial aftermath",
      "chapter": 25,
      "page_range": "240-242",
      "quote_snippet": "Tom was a dead man the minute Mayella Ewell opened her mouth"
    },
    {
      "freytag_section": "Resolution",
      "scene": "Sheriff protects Boo",
      "chapter": 30,
      "page_range": "276-278",
      "quote_snippet": "let the dead bury the dead"
    }
  ]
}
```

### Examples Array Fields

**Required fields:**
- `freytag_section`: "Exposition" | "Rising Action" | "Climax" | "Falling Action" | "Resolution" | "Frame"
- `scene`: Brief scene identifier (10-50 characters)
- `chapter`: Chapter number (integer)
- `page_range`: Page range where device appears (e.g., "90-93" or "240")

**Optional field:**
- `quote_snippet`: Representative quote showing device (20-100 characters, not full quote)

### Specification Guidelines

**Which devices need examples:**
Add examples for devices used in educational vertical Weeks 1-4:
- Week 1: Literary Device Recognition (e.g., Symbolism, Foreshadowing, Dramatic Irony)
- Week 2: Exposition & Characterization (e.g., Dialogue, Characterization)
- Week 3: Structure Analysis (e.g., Scene, Parallelism, Chronology)
- Week 4: Voice Control (e.g., First-Person Narration, Retrospective Narration)

Typically: 6-8 devices per text require examples.

**How many examples per device:**
- 2-3 examples per device
- Distributed across Freytag sections when possible
- At least one example from primary position code section

**Example selection criteria:**
1. **Pedagogically clear:** Examples should be easily identifiable by students
2. **Representative:** Shows typical usage of the device
3. **Accessible:** Located in passages students will read
4. **Freytag-mapped:** Uses existing extract structure for efficiency

### Validation Rules

**Position code alignment:**
- `CLUST-BEG` devices â†’ at least 1 example from "Exposition"
- `CLUST-MID` devices â†’ at least 1 example from "Climax"
- `CLUST-END` devices â†’ at least 1 example from "Resolution"
- `CLUST-BEG+CLUST-END` â†’ examples from both Exposition and Resolution
- `DIST` â†’ examples distributed across multiple sections
- `FRAME` â†’ examples from opening/closing frames

**Freytag section validation:**
All `freytag_section` values must map to prepared extract sections from Stage 1.5.

**Chapter/page validation:**
Chapter and page numbers should correspond to standard editions when possible. Note edition used in `validation_metadata.edition_reference`.

### Size Impact

**Estimated increase per kernel JSON:**
- 6-8 devices with examples
- 2-3 examples per device = 12-24 example objects
- Average 150 characters per example
- **Total addition: ~2-4KB (7-15% size increase)**

This is minimal overhead given the pedagogical value gained.

---

## Output Format Requirements (Updated v3.3)

All tagging experiments must produce TWO deliverables:

### 1. JSON Output (Structured Data) 

Required fields:
* `text_profile`: Metadata about text and analysis
* `tagged_profile`: All variable assignments (narrative elements, rhetorical elements, micro devices with examples)
* `device_analysis`: Micro device statistics and distributions
* `alignment_analysis`: All scores, classification, mechanism
* `quality_assessment`: Consistency, intentionality, rating
* `interpretation_summary`: Meaning production analysis, pedagogical notes
* `validation_metadata`: Analysis scope, model used, conditions, edition reference (NEW)

**NEW IN v3.3:** `validation_metadata` must include:
```json
"validation_metadata": {
  "analysis_scope": "full-text" | "extract",
  "model_used": "claude-sonnet-4-20250514",
  "tagging_order": "Nâ†’Râ†’D",
  "edition_reference": "Harper Perennial Modern Classics, 2006",
  "extract_word_count": 12500
}
```

### 2. Reasoning Document (Analytical Process) 

Required sections:
* Extract identification (if applicable)
* Variable-by-variable decision rationale
* Evidence from text for each classification
* Decision certainty ratings
* Alignment calculation walkthrough
* Interpretation and synthesis
* **NEW IN v3.3:** Example selection justification (for devices with examples)

Purpose: Enables validation of analytical process, not just outputs

File naming convention:
* JSON: [TextTitle]_[Order]_Analysis.json
* Reasoning: [TextTitle]_[Order]_Reasoning_Document.md

---

## Analysis (Unchanged from v3.2)

Analysis 1.1: Intraclass Correlation Coefficient (ICC)

**What ICC measures:** Consistency of alignment scores across 6 tagging orders.

**For each of 10 texts:**
- Calculate ICC(2,1) for:
  - Voice alignment (V_align): 6 values per text
  - Structure alignment (S_align): 6 values per text
  - Device mediation (D_med): 6 values per text
  - Composite alignment (A_total): 6 values per text

**Interpretation:**
- ICC >0.85: Excellent consistency âœ“ (order-independent)
- ICC 0.75-0.85: Good consistency âš  (minor order effects)
- ICC 0.50-0.75: Moderate consistency âš  (order matters)
- ICC <0.50: Poor consistency âœ— (unreliable)

**Primary metric:** ICC for A_total (composite alignment)

Analysis 1.2: Variable-Level Agreement

**For each of 84 alignment variables:**
- Calculate agreement rate across 6 orders
- Agreement = (# orders with same assignment) / 6

**For high-priority variables (POV, focalization, reliability, tone):**
Target: >85% agreement across all 10 texts

Analysis 1.3: Alignment Type Stability

**For each of 10 texts:**
- Count: How many orders produce same alignment type (Reinforcing/Tension/Failed)?

**Target:** >80% of texts show 100% stability (same type across all 6 orders)

Stage 1 Output 

Deliverables:
1. ICC table (4 scores Ã— 10 texts)
2. Variable agreement matrix (84 variables Ã— 10 texts)
3. Alignment type stability report
4. Order effect analysis (which orders diverge? which variables affected?)

Visualization:
* Heatmap: ICC by text and score type
* Bar chart: Variable agreement rates (sorted)
* Stability chart: Alignment type changes

---

## NEW IN v3.3: Examples Validation Analysis

### Analysis 1.4: Example Position Code Alignment

**For each device with examples:**
Validate that examples align with position codes:

**Validation checks:**
1. CLUST-BEG devices have â‰¥1 example from Exposition
2. CLUST-MID devices have â‰¥1 example from Climax
3. CLUST-END devices have â‰¥1 example from Resolution
4. DIST devices have examples from â‰¥2 different sections
5. Combined codes (e.g., CLUST-BEG+CLUST-END) satisfy both requirements

**Metric:** % of devices passing position code validation

**Target:** 100% of devices with examples pass validation

### Analysis 1.5: Example Coverage

**For pedagogically relevant devices:**
- Count: How many devices have examples array?
- Expected: 6-8 devices per text (Week 1-4 relevant devices)

**Metric:** % of pedagogically relevant devices with examples

**Target:** 100% of Week 1-4 devices have 2-3 examples

### Analysis 1.6: Example Quality Check

**Manual review sample (2 texts):**
- Are scene identifiers clear and findable?
- Do quote snippets accurately represent device usage?
- Are chapter/page references correct for specified edition?

**Metric:** Qualitative assessment of example utility

**Target:** Examples are pedagogically useful and accurate

---

## STAGE 2: Extract Validity Testing (Unchanged from v3.2)

Objective: Validate that Freytag-mapped extracts capture whole-text alignment patterns.

Procedure: For each of 10 texts, apply Nâ†’Râ†’D order to full-text and extract conditions.

Analysis:
- 2.1: Alignment Score Correlation (r >0.80 target)
- 2.2: Variable Agreement Rate (>85% for high-priority variables)
- 2.3: Device Detection Consistency
- 2.4: Alignment Type Agreement

---

## STAGE 3: Variable Robustness Analysis (Unchanged from v3.2)

Objective: Identify which alignment variables and micro devices show highest/lowest consistency.

**For each of 84 alignment variables:**
Calculate robustness score across all conditions

**For each of 50+ micro devices:**
Calculate detection consistency

Categorization:
- **Stable devices (>80%):** Consistently identified
- **Moderate devices (70-80%):** Usually identified  
- **Fragile devices (<70%):** Subtle, requires trained eye or specific order

---

## STAGE 4: Model Comparison (Unchanged from v3.2)

Objective: Validate that Claude Sonnet 4.5 produces equivalent results to Opus 4.

Procedure: Run 3 texts through both models using Nâ†’Râ†’D order.

Analysis:
- Alignment score correlation (r target >0.85)
- Variable agreement (>80% for critical variables)
- Device detection overlap
- Qualitative comparison of reasoning

---

## Implementation Notes for v3.3

### During Kernel Creation

**When tagging devices:**
1. Classify device (code, function, layer, etc.) as usual
2. Note Freytag sections where device appears
3. For pedagogically relevant devices, record:
   - 2-3 representative scenes
   - Chapter numbers
   - Page ranges
   - Optional quote snippets
4. Validate examples align with position codes
5. Include edition reference in validation_metadata

**Workflow integration:**
The Freytag extract preparation (Stage 1.5) already identifies key sections. During device tagging, simply note which prepared sections contain the device and record specific chapter/page locations.

**No extra pass needed:** Examples are recorded during normal tagging process.

### Quality Assurance

**Before finalizing kernel JSON:**
1. Check all Week 1-4 devices have examples array
2. Validate position code alignment (Analysis 1.4)
3. Verify chapter/page accuracy against edition
4. Confirm scene identifiers are clear

### Downstream Impact

**Stage 1A (Pure Extraction):**
- Extract examples array from kernel devices
- Pass through to flat structure output

**Stage 1B (Pedagogical Application):**
- Include examples in week packages
- No additional processing needed

**Stage 2 (Workbook Generator):**
- Use examples to populate worksheet prompts
- Show chapter/page references to students

**Templates:**
- Update to include "Find this device in Chapter X, pages Y-Z"
- Scene identifiers help teachers locate passages

---

## Success Criteria Summary (Updated v3.3)

Kernel v3.3 is valid if:
* âœ“ ICC >0.85 for composite alignment (order-independent)
* âœ“ r >0.80 for extract-fulltext correlation (extracts valid)
* âœ“ >85% agreement on high-priority variables
* âœ“ >80% alignment type stability
* âœ“ **NEW:** 100% of Week 1-4 devices have examples
* âœ“ **NEW:** 100% of examples align with position codes
* âœ“ **NEW:** Examples are pedagogically useful (qualitative check)

---

**END OF KERNEL VALIDATION PROTOCOL v3.3**
