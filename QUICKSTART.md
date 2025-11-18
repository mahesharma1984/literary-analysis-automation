# QUICK START GUIDE
## Get Running in 5 Minutes

### Step 1: Install Dependencies (1 min)

```bash
pip install -r requirements.txt
```

### Step 2: Set API Key (1 min)

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Get your key from: https://console.anthropic.com

### Step 3: Run Setup (1 min)

```bash
python setup.py
```

This creates directories and checks everything is ready.

### Step 4: Add Your Files (2 min)

**Add protocol files to `protocols/` folder:**
- Kernel_Validation_Protocol_v3_3.md
- Kernel_Protocol_Enhancement_v3_3.md
- Artifact_1_-_Device_Taxonomy_by_Alignment_Function
- Artifact_2_-_Text_Tagging_Protocol
- LEM_-_Stage_1_-_Narrative-Rhetoric_Triangulation

**Add your book to `books/` folder:**
- TKAM.pdf (or .txt)

### Step 5: Create Your First Kernel (30 min)

```bash
python create_kernel.py \
  books/TKAM.pdf \
  "To Kill a Mockingbird" \
  "Harper Lee" \
  "Harper Perennial Modern Classics, 2006"
```

**The script will:**
1. Extract 5 Freytag sections → You review & approve
2. Tag 84 macro variables → You review & approve
3. Tag 15-20 micro devices → You review & approve
4. Assemble kernel JSON → You review & approve
5. Save to `kernels/To_Kill_a_Mockingbird_kernel_v3.3.json`

**Done!** Your kernel is ready.

---

## Review Commands

During the workflow, you'll be asked to approve each stage:

- **y** = approve and continue
- **n** = reject and exit
- **save** = save current output for review
- **quit** = exit script

---

## What You Get

A complete kernel JSON with:
- ✅ 5 Freytag extracts (Exposition, Rising Action, Climax, Falling Action, Resolution)
- ✅ 84 macro alignment variables (narrative voice, structure, rhetoric)
- ✅ 15-20+ micro literary devices with examples
- ✅ Validated structure ready for Stage 1A/1B/2

---

## Cost

~$1-2 per book using Claude API (much cheaper than chat credits!)

---

## Next Steps

Once you have a kernel, you can:
1. Run Stage 1A to extract macro-micro packages
2. Run Stage 1B to package into 4 weeks
3. Run Stage 2 to generate worksheets

See README.md for full documentation.
