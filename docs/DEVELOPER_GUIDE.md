# DEVELOPER GUIDE: Making Changes to the Literary Analysis Automation System

**Purpose:** Instructions for AI assistants (Claude) or developers on how to safely modify this codebase without creating cascading errors.

**Last Updated:** November 25, 2025  
**System Version:** 5.1 (5-week progression with device taxonomy mapping)  
**Kernel Version:** 3.5 (includes Book Structure Alignment Protocol v1.1)

---

## SYSTEM ARCHITECTURE

### Pipeline Overview

```
Kernel JSON (v3.5)
    ↓
[Stage 1A] run_stage1a.py
    ↓
Stage 1A JSON output
    ↓
[Stage 1B] run_stage1b.py
    ↓
Stage 1B JSON output + Integrated Progression MD
    ↓
[Stage 2] run_stage2.py
    ↓
Weekly worksheets (Literary Analysis + TVODE + Teacher Key)
```

### Critical Files

| File | Purpose | Dependencies | Output Format |
|------|---------|--------------|---------------|
| `device_taxonomy_mapping.json` | Device→Week categorization | None | JSON mapping structure |
| `run_stage1a.py` | Extract macro-micro packages | kernel, mapping | JSON with 5 week packages |
| `run_stage1b.py` | Create weekly teaching progression | Stage 1A JSON | JSON + Markdown document |
| `run_stage2.py` | Generate worksheets | Stage 1B JSON, kernel | Markdown worksheets |

### Key Data Structures

**Week Structure (5 weeks):**
```python
week_keys = [
    'week_1_exposition',
    'week_2_literary_devices',
    'week_3_structure',
    'week_4_narrative_voice',
    'week_5_rhetorical_voice'
]
```

**Device Categorization Returns:**
```python
categorize_device(name, classification) -> (week_key, week_label)
# Returns: ('week_2_literary_devices', 'Week 2: Literary Devices')
```

**Device Data Structure:**
```python
{
    "name": str,
    "layer": str,  # N, R, or B
    "function": str,  # Re, Te, or Me
    "classification": str,  # "N|Re|T"
    "definition": str,
    "examples": list,
    "week_label": str,
    "tvode_components": dict
}
```

---

## BEFORE MAKING ANY CHANGES

### Step 1: Understand the Change Type

**Ask the user these questions:**

1. **What's changing?**
   - Adding/removing weeks? (High impact)
   - Changing device categorization logic? (Medium impact)
   - Changing worksheet format? (Low impact, Stage 2 only)
   - Adding new devices? (Low impact, mapping file only)

2. **Which files will this affect?**
   - Mapping only? Safe, test with `test_mapping.py`
   - Stage 1A only? Medium risk, affects downstream
   - Multiple stages? High risk, plan carefully

3. **Is the data structure changing?**
   - Number of weeks? (Critical - touches everything)
   - Function return values? (Critical - breaks callers)
   - JSON field names? (High impact - breaks parsing)
   - Display formatting only? (Low impact)

### Step 2: Map Dependencies

**Before changing any file, create a dependency map:**

```
If you change X, then Y breaks:

device_taxonomy_mapping.json
  ↓ breaks if structure changes
run_stage1a.py (categorize_device function)
  ↓ breaks if return values change
run_stage1a.py (categorize_devices function)
  ↓ breaks if week_keys change
run_stage1a.py (create_macro_micro_packages function)
  ↓ output format breaks
run_stage1b.py (create_week_package function)
  ↓ markdown format breaks
run_stage2.py
```

**Use this checklist:**
- [ ] What function signatures are changing?
- [ ] What data structures are changing?
- [ ] What loops need new ranges?
- [ ] What hardcoded values need updating?
- [ ] What print statements reference old structure?

### Step 3: Search for Hardcoded Assumptions

**Before coding, grep for these patterns:**

```bash
# Find hardcoded week counts
grep -n "range(1, 5)" *.py
grep -n "total_weeks.*4" *.py
grep -n "4-week" *.py

# Find old variable names
grep -n "category" *.py
grep -n "executes_macro" *.py
grep -n "devices_general" *.py

# Find hardcoded week references
grep -n "week4" *.py
grep -n "week_4" *.py
```

**Tell the user:** "I found X places that assume 4 weeks. This will require updating all of them."

---

## MAKING CHANGES SAFELY

### Rule 1: Rewrite Complete Files, Don't Patch

**❌ DON'T DO THIS:**
```
"Change line 105 from X to Y"
"Update the categorize_device function"
"Add this code after line 50"
```

**✅ DO THIS:**
```
"I'm going to rewrite the entire run_stage1a.py file 
with the mapping integrated. Here's the complete new version."
```

**Why:** Incremental patches lead to 8-10 error cycles. Complete rewrites let you test mentally first.

### Rule 2: Change One File at a Time

**Process:**
1. Rewrite Stage 1A completely
2. Test: `python3 run_stage1a.py kernels/test.json`
3. Commit: `git commit -m "Update Stage 1A for 5 weeks"`
4. Then rewrite Stage 1B
5. Test: `python3 run_stage1b.py outputs/test_stage1a.json`
6. Commit again

**Don't:** Change 1A, 1B, and 2 simultaneously. Debug one at a time.

### Rule 3: Provide Testing Instructions

**After giving code, always add:**

```
To test this:
1. Run: python3 run_stage1a.py kernels/The_Giver_kernel_v3.3.json
2. Expected output: 5 weeks with X, Y, Z devices
3. If you see error about 'category', that means I missed a spot
4. If you see only 4 weeks, the loop range is wrong
```

### Rule 4: Warn About Error Sequences

**If you know changes will cause cascading errors:**

```
⚠️ WARNING: This change touches function signatures.
You'll likely see 5-8 errors in sequence. Here's the order:

1. First error: "missing positional argument 'classification'"
   → This is expected, I'm fixing it now
2. Second error: "too many values to unpack"
   → Also expected, keep going
3. Third error: "KeyError: 'category'"
   → Expected, here's the fix

I'm providing the complete rewritten file to avoid this cycle.
```

---

## COMMON CHANGE PATTERNS

### Adding a Device to the Mapping

**Impact:** Low - only mapping file changes  
**Steps:**
1. Edit `device_taxonomy_mapping.json`
2. Add device to appropriate week array
3. Test with `test_mapping.py`
4. No other files need changes

**Example:**
```json
"week_2_literary_devices": [
  {
    "device_name": "Onomatopoeia",
    "classification": "R|Re|V",
    "rationale": "Sound device creating sensory effect",
    "student_facing_type": "Sound Device"
  }
]
```

### Changing Device Categorization

**Impact:** Low - only mapping file changes  
**Steps:**
1. Move device from one week array to another
2. Update rationale
3. Test against all kernels
4. No pipeline changes needed

### Adding a Week (e.g., 5→6 weeks)

**Impact:** CRITICAL - touches everything  
**Files to update:**
1. `device_taxonomy_mapping.json` - add week_6_* array
2. `run_stage1a.py`:
   - `device_mapping` initialization
   - `create_macro_micro_packages()` - add week6 entry
   - Print statements
   - Loop ranges: `range(1, 5)` → `range(1, 7)`
3. `run_stage1b.py`:
   - `scaffolding_levels` dict
   - `teaching_sequences` dict
   - `teaching_approaches` dict
   - Loop ranges: `range(1, 6)` → `range(1, 7)`
   - Progression summary
4. `run_stage2.py`:
   - Week lookup logic (if hardcoded)

**Recommendation:** DON'T add weeks without careful planning. This is a major refactor.

### Changing Function Return Values

**Impact:** HIGH - breaks all callers  
**Process:**
1. Find all places function is called
2. Update function signature first
3. Update ALL call sites in same commit
4. Provide complete rewritten file

**Example from our pain:**
```python
# Old (broke everything):
def categorize_device(device) -> str:
    return category

# New (had to update 5+ call sites):
def categorize_device(device_name: str, classification: str) -> tuple:
    return week_key, week_label
```

### Changing Worksheet Format Only

**Impact:** Low - Stage 2 only  
**Steps:**
1. Edit `run_stage2.py` only
2. Update template strings
3. Test output format
4. No upstream changes needed

---

## TESTING PROTOCOLS

### Test Before Providing Code

**Mental execution checklist:**
- [ ] Trace through main() function
- [ ] Check all variable names match
- [ ] Verify all imports exist
- [ ] Check all function signatures match call sites
- [ ] Ensure all loops have correct ranges
- [ ] Verify all dict keys exist

### Provide Test Cases

**Always include:**
```
Test with:
python3 run_stage1a.py kernels/The_Giver_kernel_v3.3.json

Expected output:
✓ Week 1 (Exposition): 3 devices
✓ Week 2 (Literary Devices): 5 devices
✓ Week 3 (Structure): 4 devices
✓ Week 4 (Narrative Voice): 2 devices
✓ Week 5 (Rhetorical Voice): 6 devices

If you see only 4 weeks → I missed updating the loop range
If you see KeyError → I missed updating a dict key
```

### Integration Testing

**Full pipeline test:**
```bash
# Test complete pipeline
python3 run_stage1a.py kernels/The_Giver_kernel_v3.3.json
python3 run_stage1b.py outputs/The_Giver_stage1a_v5.0.json
python3 run_stage2.py outputs/The_Giver_stage1b_v5.0.json kernels/The_Giver_kernel_v3.3.json --week 1

# Should produce:
# - Stage 1A JSON with 5 week packages
# - Stage 1B JSON + Integrated Progression MD with 5 weeks
# - Week 1 worksheet set (3 markdown files)
```

---

## SPECIFIC GOTCHAS FOR THIS PROJECT

### 1. File Path Issues
- User is on Mac, you're simulating Linux
- Kernels are in `./kernels/` not `/mnt/project/`
- Outputs go to `./outputs/` not `/mnt/user-data/outputs/`
- File names have periods not underscores: `v3.3` not `v3_3`

### 2. Week Structure is Sacred
- 5 weeks is now hardcoded in multiple places
- Changing this requires updating 10+ locations
- Always search for `range(1, 6)` before claiming something works

### 3. Device Data Has Multiple Names
```python
device['name']  # Canonical name
device['device_name']  # Sometimes used
device_data['name']  # In processed data
```
Make sure you use the right one in context.

### 4. Macro Variables Can Be Empty
```python
macro_variables = {
    "pov": "",  # Often empty in kernels
    "focalization": ""
}
```
Don't assume they're populated. Check with `.get()`.

### 5. JSON vs. Markdown Output
- Stage 1A: JSON only
- Stage 1B: JSON + Markdown
- Stage 2: Markdown only

Don't assume formats carry through stages.

---

## COMMUNICATION PROTOCOL

### When the User Asks for Changes

**Your response format:**

```
I understand you want to [describe change].

This will affect:
- File X: [specific changes]
- File Y: [specific changes]

Impact level: [Low/Medium/High/Critical]

Potential breaking points:
1. [Specific thing that might break]
2. [Another thing]

My approach:
1. [Step 1]
2. [Step 2]
3. [Step 3]

Testing plan:
[How to verify it works]

Estimated error cycles: [1-2 / 3-5 / 8-10]

Do you want me to proceed?
```

### When Providing Fixed Code

**Always include:**
1. What you changed (bullet list)
2. Why it was necessary
3. How to test it
4. What errors to expect (if any)
5. Complete file, not patches

### When Errors Occur

**Your response:**
```
This error means: [plain English explanation]

It happened because: [root cause]

Fix: [complete file or specific change]

This is [expected/unexpected] because [reason]
```

**Don't:**
- Say "just change line X" without checking what else breaks
- Blame the user for running it wrong
- Give incremental fixes without warning about cascades

---

## LESSONS FROM THE 5-WEEK MIGRATION

### What Went Wrong
1. Gave incremental patches instead of complete files
2. Didn't anticipate function signature changes breaking callers
3. Didn't warn about error cascade (8 errors in sequence)
4. Didn't test mental execution before providing code
5. Blamed user for not asking better questions

### What Should Have Happened
1. Recognize this as "HIGH IMPACT" change (data structure + logic)
2. Map all dependencies first
3. Provide complete rewritten files for 1A and 1B
4. Warn: "You'll see 5-8 errors, I'm giving complete files to avoid this"
5. Include full testing instructions
6. Take responsibility when things break

### Apply This Next Time
- **Scope assessment** before coding
- **Complete files** not patches
- **Honest warnings** about complexity
- **Clear testing** instructions
- **Own mistakes** when debugging

---

## QUICK REFERENCE

### Safe Changes (Low Risk)
- Adding devices to mapping
- Changing device categorizations
- Updating worksheet text/format
- Adding examples to devices

### Medium Risk Changes
- Changing categorization logic
- Adding macro variables
- Modifying teaching sequences
- Updating progression summaries

### High Risk Changes (Requires Full Analysis)
- Changing function signatures
- Modifying data structures
- Updating JSON schema
- Changing week structure

### Critical Changes (Plan Carefully)
- Adding/removing weeks
- Changing pipeline flow
- Modifying kernel format
- Restructuring macro-micro relationship

---

## FINAL CHECKLIST

Before providing any code:
- [ ] Assessed impact level
- [ ] Mapped dependencies
- [ ] Searched for hardcoded assumptions
- [ ] Mentally traced execution
- [ ] Prepared complete files (not patches)
- [ ] Written test instructions
- [ ] Warned about potential errors
- [ ] Included "what to do if X breaks" instructions

If you checked all boxes, proceed. If not, get more information first.

---

**END OF DEVELOPER GUIDE**

*When in doubt: ask questions, map dependencies, provide complete files, test thoroughly.*
