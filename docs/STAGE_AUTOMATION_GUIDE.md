# STAGE 1A/1B/2 AUTOMATION GUIDE

Complete the education vertical pipeline: Kernel → Packages → Worksheets

---

## OVERVIEW

**You now have 4 automation scripts:**

1. **`create_kernel.py`** - Creates kernel from book PDF (~15 min, ~$1-2)
2. **`run_stage1a.py`** - Extracts macro-micro packages (instant, free)
3. **`run_stage1b.py`** - Creates 5-week teaching packages (instant, free)
4. **`run_stage2.py`** - Generates worksheets (~5 min per week, ~$0.20 per week)

---

## COMPLETE WORKFLOW

### Step 1: Create Kernel (You Already Did This!)

```bash
python3 create_kernel.py \
  books/TheGiver.pdf \
  "The Giver" \
  "Lois Lowry" \
  "Houghton Mifflin, 1993"
```

**Output:** `kernels/The_Giver_kernel_v3.3.json`

---

### Step 2: Run Stage 1A (Extract Packages)

```bash
python3 run_stage1a.py kernels/The_Giver_kernel_v3.3.json
```

**What it does:**
- Extracts macro elements (Exposition, Structure, Voice)
- Categorizes devices by which macro they execute
- Creates 5-week macro-micro packages

**Output:** `outputs/The_Giver_stage1a_v5.0.json`

**Time:** < 1 second
**Cost:** FREE (no API calls)

---

### Step 3: Run Stage 1B (Create Weekly Packages)

```bash
python3 run_stage1b.py outputs/The_Giver_stage1a_v5.0.json
```

**What it does:**
- Packages content into 5 teaching weeks
- Adds pedagogical scaffolding
- Creates teaching sequences
- Adds teaching notes for each device

**Output:** `outputs/The_Giver_stage1b_v5.0.json`

**Time:** < 1 second
**Cost:** FREE (no API calls)

---

### Step 4: Run Stage 2 (Generate Worksheets)

**Option A: Generate Week 1 only (default)**
```bash
python3 run_stage2.py outputs/The_Giver_stage1b_v5.0.json
```

**Option B: Generate specific week**
```bash
python3 run_stage2.py outputs/The_Giver_stage1b_v5.0.json --week 2
```

**Option C: Generate all 5 weeks**
```bash
python3 run_stage2.py outputs/The_Giver_stage1b_v5.0.json --all-weeks
```

**What it does:**
- Calls Claude API to generate worksheet content
- Creates student worksheet (analysis questions, TVODE template)
- Creates teacher answer key (sample answers, teaching notes)

**Output:** 
- `outputs/worksheets/The_Giver_Week1_Worksheet.md`
- `outputs/worksheets/The_Giver_Week1_TeacherKey.md`
- (And Week 2-5 if using --all-weeks)

**Time:** ~3-5 minutes per week
**Cost:** ~$0.20 per week (~$1.00 for all 5 weeks)

---

## QUICK REFERENCE

### Run Everything (One Command Each)

```bash
# Stage 1A
python3 run_stage1a.py kernels/The_Giver_kernel_v3.3.json

# Stage 1B
python3 run_stage1b.py outputs/The_Giver_stage1a_v5.0.json

# Stage 2 (Week 1 only)
python3 run_stage2.py outputs/The_Giver_stage1b_v5.0.json

# Stage 2 (All weeks)
python3 run_stage2.py outputs/The_Giver_stage1b_v5.0.json --all-weeks
```

---

## OUTPUT STRUCTURE

After running everything, your folder looks like:

```
automation-package/
├── books/
│   └── TheGiver.pdf
├── kernels/
│   └── The_Giver_kernel_v3.3.json        ← Kernel (Stage 0)
├── outputs/
│   ├── The_Giver_stage1a_v5.0.json       ← Macro-micro packages (Stage 1A)
│   ├── The_Giver_stage1b_v5.0.json       ← Weekly packages (Stage 1B)
│   └── worksheets/                       ← Worksheets (Stage 2)
│       ├── The_Giver_Week1_Worksheet.md
│       ├── The_Giver_Week1_TeacherKey.md
│       ├── The_Giver_Week2_Worksheet.md
│       ├── The_Giver_Week2_TeacherKey.md
│       ├── The_Giver_Week3_Worksheet.md
│       ├── The_Giver_Week3_TeacherKey.md
│       ├── The_Giver_Week4_Worksheet.md
│       ├── The_Giver_Week4_TeacherKey.md
│       ├── The_Giver_Week5_Worksheet.md
│       └── The_Giver_Week5_TeacherKey.md
```

---

## WHAT EACH FILE CONTAINS

### Stage 1A Output (JSON)
```json
{
  "macro_elements": {
    "exposition": { "variables": {...} },
    "structure": { "variables": {...} },
    "voice": { "variables": {...} }
  },
  "device_mapping": {
    "week_1_exposition": [...],
    "week_2_literary_devices": [...],
    "week_3_structure": [...],
    "week_4_narrative_voice": [...],
    "week_5_rhetorical_voice": [...]
  },
  "macro_micro_packages": {
    "week_1_exposition": {...},
    "week_2_literary_devices": {...},
    "week_3_structure": {...},
    "week_4_narrative_voice": {...},
    "week_5_rhetorical_voice": {...}
  }
}
```

### Stage 1B Output (JSON)
```json
{
  "week_packages": [
    {
      "week": 1,
      "macro_focus": "Exposition",
      "teaching_goal": "Understanding narrative setup",
      "scaffolding_level": "High",
      "teaching_sequence": [...],
      "micro_devices": [...]
    },
    ...
  ]
}
```

### Stage 2 Output (Markdown)
```markdown
# The Giver - Week 1 Literary Analysis Worksheet

## Introduction
[Explanation of macro concept]

## Device Definitions
[Clear definitions for students]

## Text Analysis Activity
[6 analysis questions]

## TVODE Construction
[Template and examples]

## Reflection
[Synthesis questions]
```

---

## COST BREAKDOWN

**Complete pipeline for one book:**

| Stage | Time | Cost | Notes |
|-------|------|------|-------|
| Kernel Creation | 15 min | $1-2 | One-time, analyzes whole book |
| Stage 1A | <1 sec | FREE | Data transformation |
| Stage 1B | <1 sec | FREE | Data transformation |
| Stage 2 (Week 1) | 3-5 min | $0.20 | Worksheet generation |
| Stage 2 (All weeks) | 10-15 min | $1.00 | All 5 weeks |
| **TOTAL** | ~30 min | **$1.80-2.80** | **Complete analysis + worksheets** |

**For 10 books:** ~$18-28 total (vs. weeks of manual work!)

---

## TIPS

### Speed Up Processing
- Stage 1A/1B are instant - no waiting
- Stage 2 only costs when you need worksheets
- Generate Week 1 first to test, then generate rest

### Save Money
- Stage 1A/1B outputs can be edited manually (no API)
- Only generate worksheets (Stage 2) when you're satisfied with packages
- Generate one week at a time if testing

### Version Control
```bash
git add outputs/
git commit -m "Add The Giver Stage 1A/1B/2 outputs"
```

---

## TROUBLESHOOTING

### "ANTHROPIC_API_KEY not set" (Stage 2 only)
```bash
export ANTHROPIC_API_KEY="your-key-here"
```
Stage 1A/1B don't need API key.

### "File not found"
Make sure you're using the exact output path from previous stage.

### Want to modify packages before generating worksheets?
Edit the Stage 1B JSON file manually, then run Stage 2.

---

## WHAT'S NEXT?

### Process More Books
Repeat for TKAM, Holes, Animal Farm, etc.

### Update Protocols
1. Edit protocol .md files in `protocols/`
2. Regenerate kernel: `python3 create_kernel.py ...`
3. Rerun Stage 1A/1B/2
4. Compare outputs with Git

### Customize Worksheets
- Edit Stage 2 script to change worksheet format
- Add custom teaching notes
- Modify TVODE templates

---

## COMPLETE EXAMPLE

**Process The Giver from start to finish:**

```bash
# Already done: Create kernel
# python3 create_kernel.py books/TheGiver.pdf "The Giver" "Lois Lowry" "1993"

# Run Stage 1A (instant)
python3 run_stage1a.py kernels/The_Giver_kernel_v3.3.json

# Run Stage 1B (instant)  
python3 run_stage1b.py outputs/The_Giver_stage1a_v5.0.json

# Generate all worksheets (~15 min, $1.00)
python3 run_stage2.py outputs/The_Giver_stage1b_v5.0.json --all-weeks

# Done! View worksheets in outputs/worksheets/
```

**Total time:** ~15 minutes  
**Total cost:** ~$2 (kernel + worksheets)  
**Output:** Complete teaching materials for 5 weeks

---

## YOU NOW HAVE A COMPLETE AUTOMATION PIPELINE! 🎉

From book PDF to ready-to-use worksheets in ~30 minutes total.
