# Regenerating and Patching TKAM Kernel

## Step 1: Regenerate the Kernel

Run the following command to regenerate the TKAM kernel with all latest fields:

```bash
python create_kernel.py \
  books/TKAM.pdf \
  "To Kill a Mockingbird" \
  "Harper Lee" \
  "Harper Perennial Modern Classics, 2006" \
  31
```

**What this does:**
- Stage 1: Extracts 5 Freytag sections with chapter ranges
- Stage 2A: Tags 84 macro alignment variables
- Stage 2B: Identifies 15-20+ micro devices with examples
- Saves to: `kernels/To_Kill_a_Mockingbird_kernel_v3_4.json`

**Time:** ~5-10 minutes (includes rate limiting delays)
**API Cost:** ~$0.15-0.30 (3 API calls)

---

## Step 2: Patch the Existing Kernel

After regeneration, run the patching script to merge the new data with your existing kernel:

```bash
python patch_tkam_kernel.py \
  kernels/To_Kill_a_Mockingbird_kernel_v3_4.json \
  kernels/To_Kill_a_Mockingbird_kernel_v3_4.json
```

**What this does:**
- **Backs up** your existing kernel (preserves v3.4 for comparison)
- **Preserves** your existing kernel content (text extracts, rationale, etc.)
- **Adds** missing `chapter_range` and `primary_chapter` to extracts
- **Adds** `assigned_section` to each device
- **Adds** device taxonomy fields (`layer`, `function`, `engagement`, etc.)
- **Increments version** (v3.4 → v3.5)
- **Creates new file** with incremented version number

**Result:**
- Backup: `To_Kill_a_Mockingbird_kernel_v3_4.json` (original preserved)
- New: `To_Kill_a_Mockingbird_kernel_v3_5.json` (patched version)

**Time:** < 1 second
**Cost:** Free (no API calls)

---

## Version Control

The patching script automatically handles versioning:

- **Auto-increments**: v3.4 → v3.5 → v3.6
- **Creates backups**: Original version preserved
- **New file created**: Patched version saved with new version number

### Manual Version Control

Specify a target version:
```bash
python patch_tkam_kernel.py \
  kernels/To_Kill_a_Mockingbird_kernel_v3_4.json \
  kernels/To_Kill_a_Mockingbird_kernel_v3_4.json \
  --version 3.6
```

### Skip Backup

If you don't want a backup (not recommended):
```bash
python patch_tkam_kernel.py \
  kernels/To_Kill_a_Mockingbird_kernel_v3_4.json \
  kernels/To_Kill_a_Mockingbird_kernel_v3_4.json \
  --no-backup
```

---

## What Gets Updated

### Extracts
- ✅ Adds `chapter_range` (e.g., "1-3", "4-14")
- ✅ Adds `primary_chapter` (e.g., 1, 8, 15)
- ✅ Preserves existing `text`, `rationale`, `word_count`

### Devices
- ✅ Adds `assigned_section` (exposition/rising_action/climax/falling_action/resolution)
- ✅ Adds `layer` (N/B/R)
- ✅ Adds `function` (Re/Me/Te)
- ✅ Adds `engagement` (T/V/F)
- ✅ Adds `classification` (Layer|Function|Engagement)
- ✅ Adds `position_code` (DIST/CLUST-BEG/etc.)
- ✅ Adds `student_facing_type`
- ✅ Adds `pedagogical_function`
- ✅ Preserves existing `name`, `definition`, `examples`

### Metadata
- ✅ Updates `kernel_version` to next version (3.4 → 3.5)
- ✅ Sets `chapter_aware` to true
- ✅ Adds `patch_date` and `patch_method`
- ✅ Preserves `upgrade_date` from original

---

## Verification

After patching, verify the kernel works with stage files:

```bash
# Test Stage 1A with new version
python run_stage1a.py kernels/To_Kill_a_Mockingbird_kernel_v3_5.json

# Should see:
# ✓ Exposition: Chapters 1-3
# ✓ Rising action: Chapters 4-14
# ✓ Devices with assigned_section: X/Y
```

### Compare Versions

You can compare outputs from different versions:

```bash
# Generate Stage 1A from v3.4
python run_stage1a.py kernels/To_Kill_a_Mockingbird_kernel_v3_4.json

# Generate Stage 1A from v3.5
python run_stage1a.py kernels/To_Kill_a_Mockingbird_kernel_v3_5.json

# Compare outputs
diff outputs/To_Kill_a_Mockingbird_stage1a_v5.0.json \
     outputs/To_Kill_a_Mockingbird_stage1a_v5.0.json
```

---

## Troubleshooting

**Issue:** "New kernel not found"
- Make sure you ran `create_kernel.py` first
- Check the kernel was saved to `kernels/` directory

**Issue:** "Existing kernel not found"
- Check the path to your existing kernel file
- Make sure you're in the project root directory

**Issue:** Devices missing taxonomy fields after patching
- The new kernel might not have all devices matching by name
- Check the new kernel has the same device names
- You may need to manually add some fields



