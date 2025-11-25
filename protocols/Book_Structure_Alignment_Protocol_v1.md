# BOOK STRUCTURE ALIGNMENT PROTOCOL

**Version:** 1.1  
**Date:** November 2025  
**Dependencies:** Runs BEFORE Kernel_Validation_Protocol_v3_3  
**Purpose:** Establish validated alignment between physical book structure and Freytag narrative structure

---

## PURPOSE

This protocol detects a book's physical organization (chapters, parts, sections) and establishes a validated mapping to Freytag narrative stages before kernel creation begins. Strong chapter-narrative alignment is foundational—all downstream analysis (device assignment, example locations, worksheet generation) depends on this mapping being accurate.

---

## CORE CONTENT

### Section 1: Structure Type Definitions

**Physical Structure Types:**

| Code | Type | Description | Example |
|------|------|-------------|---------|
| `NUM` | Numbered Chapters | Sequential chapter numbers (1, 2, 3...) | The Giver, TKAM |
| `NAME` | Named Chapters | Titled chapters without numbers | Matilda, many children's books |
| `NEST` | Nested Structure | Parts/Books containing chapters | Brideshead Revisited, Les Misérables |
| `UNMARK` | Unmarked/Continuous | No chapter divisions | The Old Man and the Sea |
| `HYBRID` | Hybrid | Combination (e.g., numbered + prologue/epilogue) | Many novels with framing |

**Structural Elements:**

| Element | Code | Handling Rule |
|---------|------|---------------|
| Prologue | `PRO` | Treat as Chapter 0 or include in Exposition range |
| Epilogue | `EPI` | Treat as final chapter or include in Resolution range |
| Part/Book divisions | `DIV` | Note but map through to chapter-level |
| Interlude/Intermezzo | `INT` | Include in surrounding chapter range |
| Unnumbered sections | `UNN` | Assign sequential identifiers for mapping |

---

### Section 2: Conventional Distribution Model

**Core Heuristic:**

Traditional narrative structure distributes roughly evenly across the text, with climax at approximate center.

**Standard Distribution (starting assumption):**

| Freytag Stage | Position | Typical % of Book |
|---------------|----------|-------------------|
| Exposition | Beginning | ~10-15% |
| Rising Action | Early-middle | ~30-40% |
| Climax | Center (variable) | ~5-10% (1-3 chapters) |
| Falling Action | Late-middle | ~25-30% |
| Resolution | End | ~10-15% |

**Key Insight:** Climax is typically the shortest stage—often a single pivotal chapter. The formula provides a starting point; verification determines actual boundaries.

**Application Formula:**

For a book with N chapters:
```
Exposition:      Chapters 1 to floor(N × 0.12)
Rising Action:   Chapters floor(N × 0.12)+1 to floor(N × 0.50)-1
Climax:          Chapters floor(N × 0.50) to floor(N × 0.55)  [typically 1-3 chapters]
Falling Action:  Chapters floor(N × 0.55)+1 to floor(N × 0.85)
Resolution:      Chapters floor(N × 0.85)+1 to N
```

**Climax Refinement Rule:**

If formula produces >3 chapters for climax, narrow to:
- Primary climax chapter = floor(N × 0.50)
- Range = primary ±1 chapter maximum

**Adjustment Tolerance:** ±2 chapters at each boundary, except climax which should remain tight (1-3 chapters).

---

### Section 3: Decision Rules

**Step 1: Structure Detection**

```
IF book has numbered chapters → structure_type = NUM
IF book has titled chapters without numbers → structure_type = NAME
IF book has Parts/Books containing chapters → structure_type = NEST
IF book has no chapter divisions → structure_type = UNMARK
IF book has prologue/epilogue + numbered chapters → structure_type = HYBRID
```

**Step 2: Unit Counting**

```
IF structure_type = NUM → count chapters directly
IF structure_type = NAME → count titled sections, assign sequential IDs
IF structure_type = NEST → flatten to chapter-level count (e.g., "Book 1 Ch 1-5, Book 2 Ch 1-4" = 9 units)
IF structure_type = UNMARK → estimate units by page count ÷ ~20 pages OR use natural scene breaks
IF structure_type = HYBRID → count all units including prologue/epilogue
```

**Step 3: Apply Conventional Distribution**

```
1. Calculate initial chapter ranges using Standard Distribution formula
2. Round to whole chapter numbers
3. Ensure no gaps (ranges must be contiguous 1 to N)
4. Ensure complete coverage (all chapters assigned)
```

**Step 4: Verify Against Text**

```
FOR each Freytag stage:
  Sample text at assigned chapter boundaries
  CHECK: Does content match expected narrative function?
  
  Exposition: Character/setting establishment, status quo
  Rising Action: Conflict introduction, tension building, complications
  Climax: Peak tension, major turning point, irreversible change
  Falling Action: Consequences unfold, movement toward resolution
  Resolution: Final outcome, new equilibrium, closure

IF match_rate ≥ 90% → PROCEED with alignment
IF match_rate < 90% → FLAG for manual review or adjust boundaries
```

**Step 4b: Climax Identification (Required)**

The climax is not simply "middle of book"—it's the narrative turning point. Before finalizing alignment:

```
1. Identify THE pivotal moment:
   - Point of highest tension/conflict
   - Irreversible change occurs
   - Character's key decision or revelation
   
2. Locate which chapter contains this moment

3. Set climax range:
   - If pivotal moment is single scene → climax = that chapter only
   - If pivotal moment spans chapters → climax = those chapters (max 3)
   
4. Adjust other stages around confirmed climax:
   - Rising Action ends at chapter before climax
   - Falling Action begins at chapter after climax
```

**Override Rule:** If identified climax chapter differs from formula by >3 chapters, use identified climax and recalculate other stages proportionally.

**Step 5: Handle Mismatches**

```
IF boundary falls mid-chapter:
  → Assign chapter to stage where majority of content belongs
  → Note in rationale: "Chapter X contains transition"

IF stage is unusually short/long:
  → Acceptable if content matches function
  → Flag if distribution is extreme (any stage <5% or >40%)

IF structure doesn't fit conventional model:
  → Flag as NON_CONVENTIONAL
  → Document actual structure in notes
  → Proceed with best-fit mapping + explicit caveats
```

---

### Section 4: Examples

**Example 1: The Giver (23 chapters, NUM structure)**

Detection:
- Structure type: `NUM`
- Total units: 23
- Special elements: None

Formula application (N=23):
```
Exposition:      Ch 1-2   (floor(23 × 0.12) = 2)
Rising Action:   Ch 3-10  (ends at floor(23 × 0.50)-1 = 10)
Climax:          Ch 11-12 (floor(23 × 0.50) to floor(23 × 0.55) = 11-12)
Falling Action:  Ch 13-19 
Resolution:      Ch 20-23
```

Climax verification:
- Actual climax: Chapter 15-16 (warfare memory, peak emotional intensity)
- Formula climax: Chapter 11-12
- **Adjustment needed:** Climax is later than formula suggests

Adjusted alignment:
```
Exposition:      Ch 1-4   (17%) - extended setup of Jonas's world
Rising Action:   Ch 5-14  (43%) - extended training period with The Giver
Climax:          Ch 15-16 (9%)  - warfare memory, peak revelation
Falling Action:  Ch 17-22 (26%) - escape planning, release discovery
Resolution:      Ch 23    (4%)  - escape journey, ambiguous ending
```

Result: Adjustment required due to extended rising action. Final alignment validated at ~95% fit.

---

**Example 2: Brideshead Revisited (NEST structure)**

Detection:
- Structure type: `NEST`
- Organization: Prologue + Book One (5 ch) + Book Two (3 ch) + Book Three (5 ch) + Epilogue
- Total units: 15 (counting Prologue and Epilogue as units)

Flattened mapping:
```
Unit 1: Prologue
Units 2-6: Book One, Chapters 1-5
Units 7-9: Book Two, Chapters 1-3
Units 10-14: Book Three, Chapters 1-5
Unit 15: Epilogue
```

Conventional distribution applied:
```
Exposition:      Units 1-2   (Prologue + Book One Ch 1)
Rising Action:   Units 3-6   (Book One Ch 2-5)
Climax:          Units 7-9   (Book Two Ch 1-3)
Falling Action:  Units 10-12 (Book Three Ch 1-3)
Resolution:      Units 13-15 (Book Three Ch 4-5 + Epilogue)
```

Verification required at boundaries.

---

**Example 3: The Old Man and the Sea (UNMARK structure)**

Detection:
- Structure type: `UNMARK`
- Total units: No chapters
- Approach: Use page-based sections OR natural scene breaks

Handling:
```
Option A: Page-based (127 pages ÷ ~25 = 5 sections)
  Section 1: pp. 1-25 (Exposition)
  Section 2: pp. 26-50 (Rising Action)
  Section 3: pp. 51-75 (Climax)
  Section 4: pp. 76-100 (Falling Action)
  Section 5: pp. 101-127 (Resolution)

Option B: Scene-based
  Identify major scene breaks (going out, hooking fish, fighting fish, return)
  Map scenes to Freytag stages
```

Note: For UNMARK texts, page references replace chapter references in downstream outputs.

---

**Example 4: Matilda (NAME structure)**

Detection:
- Structure type: `NAME`
- Chapters: "The Reader of Books", "Mr Wormwood the Great Car Dealer", etc.
- Total units: 21 named chapters

Handling:
```
Assign sequential IDs:
  Chapter 1: "The Reader of Books"
  Chapter 2: "Mr Wormwood the Great Car Dealer"
  ...
  Chapter 21: "A New Home"
```

Apply conventional distribution using IDs, but preserve names for output.

---

### Section 5: Output Format

**Structure Detection Output:**

```json
{
  "structure_detection": {
    "structure_type": "NUM|NAME|NEST|UNMARK|HYBRID",
    "total_units": <integer>,
    "special_elements": ["PRO", "EPI"] | [],
    "unit_list": [
      {"id": 1, "label": "Chapter 1", "type": "chapter"},
      {"id": 2, "label": "Chapter 2", "type": "chapter"}
    ],
    "notes": "string describing any unusual features"
  }
}
```

**Alignment Mapping Output:**

```json
{
  "chapter_alignment": {
    "exposition": {
      "chapter_range": "1-4",
      "chapters": [1, 2, 3, 4],
      "primary_chapter": 1,
      "percentage": 17
    },
    "rising_action": {
      "chapter_range": "5-10",
      "chapters": [5, 6, 7, 8, 9, 10],
      "primary_chapter": 8,
      "percentage": 26
    },
    "climax": {
      "chapter_range": "11-14",
      "chapters": [11, 12, 13, 14],
      "primary_chapter": 13,
      "percentage": 17
    },
    "falling_action": {
      "chapter_range": "15-20",
      "chapters": [15, 16, 17, 18, 19, 20],
      "primary_chapter": 18,
      "percentage": 26
    },
    "resolution": {
      "chapter_range": "21-23",
      "chapters": [21, 22, 23],
      "primary_chapter": 23,
      "percentage": 13
    }
  },
  "validation": {
    "method": "conventional_distribution",
    "fit_score": 95,
    "status": "VERIFIED|FLAGGED",
    "notes": "string with any boundary adjustments or concerns"
  }
}
```

---

### Section 6: Edge Cases

**Prologue/Epilogue Handling:**
```
IF prologue contains exposition content → include in Exposition range
IF prologue is frame narrative only → note separately, start Exposition at Ch 1
IF epilogue resolves plot → include in Resolution range
IF epilogue is distant future/frame → note separately, end Resolution before it
```

**Extremely Short/Long Stages:**
```
IF any stage < 5% of book → FLAG, verify content justifies brevity
IF any stage > 40% of book → FLAG, consider splitting or verify structure
IF climax > 20% of book → likely misidentified, reassess turning point
```

**Non-Conventional Structures:**
```
IF climax is not near center → FLAG as NON_CONVENTIONAL
IF multiple climaxes exist → identify PRIMARY climax for mapping
IF structure is episodic → use episode-based mapping, note in output
IF structure resists Freytag → document limitations, provide best-fit mapping
```

**Chapter Transitions:**
```
IF narrative transition occurs mid-chapter:
  → Assign chapter to dominant stage
  → Note: "Chapter X contains [Stage A → Stage B] transition"
  → Use chapter start for stage assignment if unclear
```

**Late or Early Climax:**
```
IF climax occurs before 40% of book:
  → Compress Exposition and Rising Action proportionally
  → Expand Falling Action
  → Note: "Early climax structure"

IF climax occurs after 70% of book:
  → Expand Rising Action
  → Compress Falling Action and Resolution
  → Note: "Late climax structure"
```

**Extended Rising Action:**
```
IF rising_action content extends well past formula boundary:
  → This is common (e.g., The Giver training sequence)
  → Expand Rising Action to match content
  → Climax may occur later than 50%
  → Note: "Extended rising action structure"
```

---

## VALIDATION

**Alignment Accuracy Target:** ≥90% of chapter content matches assigned Freytag stage

**Validation is Mandatory, Not Optional:**

The formula produces a *hypothesis*. Verification determines actual fit. Do not skip validation—proceed only after confirming boundaries match narrative content.

**Validation Sequence:**
1. Apply formula to get initial ranges
2. Identify actual climax chapter(s) from content
3. If climax differs from formula → adjust all boundaries
4. Sample text at adjusted boundaries
5. Calculate fit score
6. If fit ≥90% → proceed
7. If fit <90% → flag for manual adjustment

**Verification Method:**
1. Sample opening paragraph of each boundary chapter
2. Confirm narrative function matches assigned stage
3. Document any mismatches with rationale

**Flagging Criteria:**
- Fit score <90% → requires manual review
- Structure type UNMARK → requires user confirmation of unit divisions
- Non-conventional distribution → requires explicit user approval

---

## INTEGRATION WITH KERNEL CREATION

**Execution Order:**
```
1. Book Structure Alignment Protocol (this document) ← FIRST
2. Kernel Validation Protocol Stage 1 (Freytag rationales)
3. Kernel Validation Protocol Stage 2A (84 macro variables)
4. Kernel Protocol Enhancement Stage 2B (15-20 micro devices)
```

**Handoff to Kernel Validation:**

This protocol outputs validated `chapter_alignment` structure. Kernel Validation Protocol Stage 1 uses this to:
- Assign devices to correct Freytag stages
- Reference correct chapters for examples
- Build `narrative_position_mapping` in kernel

**User Confirmation Gate:**

After structure detection and alignment mapping, present to user:
```
BOOK STRUCTURE DETECTED:
- Type: [structure_type]
- Total units: [N]
- Special elements: [list]

PROPOSED ALIGNMENT:
- Exposition: Chapters [range] ([%])
- Rising Action: Chapters [range] ([%])
- Climax: Chapters [range] ([%])
- Falling Action: Chapters [range] ([%])
- Resolution: Chapters [range] ([%])

Verification: [fit_score]% match with conventional structure

Proceed with this alignment? [y/n/adjust]
```

---

## APPENDIX: Validation Test Results (November 2025)

Protocol tested against existing kernels:

| Book | Formula Match | Issue | Resolution |
|------|--------------|-------|------------|
| TKAM (31 ch) | 0% exact | Climax too broad (5 ch vs 1 ch) | Narrowed climax rule added |
| The Giver (23 ch) | 0% exact | Climax too early, rising action underestimated | Extended rising action rule added |

**Key Learnings:**

1. Climax should be 1-3 chapters, not 15% of book
2. Rising action often extends beyond 40% for training/development narratives
3. Formula is starting point; content verification is mandatory

**Status:** Protocol v1.1 incorporates these refinements.

---

**END OF PROTOCOL**
