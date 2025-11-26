# Kernel Versioning Guide

## Version Numbering

Kernels use **semantic versioning** with format: `MAJOR.MINOR`

- **Major version (3)**: Protocol version (currently 3.x)
- **Minor version (.4, .5, .6...)**: Increments with each update/regeneration

### Examples
- `v3.4` → First v3.4 kernel
- `v3.5` → Patched/regenerated v3.4 kernel
- `v3.6` → Further updates to v3.5 kernel

## File Naming Convention

Kernels follow this naming pattern:
```
<Book_Title>_kernel_v<MAJOR>_<MINOR>.json
```

**Format:** Underscores in filename, dots in metadata
- Filename: `To_Kill_a_Mockingbird_kernel_v3_4.json`
- Metadata: `"kernel_version": "3.4"`

### Examples
```
To_Kill_a_Mockingbird_kernel_v3_4.json  → version 3.4
To_Kill_a_Mockingbird_kernel_v3_5.json  → version 3.5
The_Giver_kernel_v3_4.json              → version 3.4
```

## Version Progression

### When You Regenerate a Kernel

1. **Regenerate** using `create_kernel.py`:
   ```bash
   python create_kernel.py books/TKAM.pdf "To Kill a Mockingbird" "Harper Lee" "Harper Perennial Modern Classics, 2006" 31
   ```
   - Creates: `To_Kill_a_Mockingbird_kernel_v3_4.json` (if starting fresh)
   - Or overwrites existing if same version

2. **Patch** using `patch_tkam_kernel.py`:
   ```bash
   python patch_tkam_kernel.py \
     kernels/To_Kill_a_Mockingbird_kernel_v3_4.json \
     kernels/To_Kill_a_Mockingbird_kernel_v3_4.json
   ```
   - **Backs up**: `To_Kill_a_Mockingbird_kernel_v3_4.json` (original preserved)
   - **Creates**: `To_Kill_a_Mockingbird_kernel_v3_5.json` (patched version)
   - **Updates**: Metadata `kernel_version` to `"3.5"`

### Auto-Increment Behavior

The patching script automatically increments the version:
- `v3.4` → `v3.5`
- `v3.5` → `v3.6`
- `v3.6` → `v3.7`

### Manual Version Control

You can specify a target version:
```bash
python patch_tkam_kernel.py \
  kernels/To_Kill_a_Mockingbird_kernel_v3_4.json \
  kernels/To_Kill_a_Mockingbird_kernel_v3_4.json \
  --version 3.6
```

## Backup Strategy

### Automatic Backups

When patching, the script automatically:
1. **Creates backup** of existing kernel with current version number
2. **Saves new version** with incremented version number
3. **Preserves both** for comparison

### Backup Naming

- **First backup**: `To_Kill_a_Mockingbird_kernel_v3_4.json`
- **If backup exists**: `To_Kill_a_Mockingbird_kernel_v3_4_20250125_143022.json` (with timestamp)

### Example Workflow

```bash
# You have: To_Kill_a_Mockingbird_kernel_v3_4.json

# Regenerate kernel
python create_kernel.py books/TKAM.pdf "To Kill a Mockingbird" "Harper Lee" "Harper Perennial Modern Classics, 2006" 31
# Creates: To_Kill_a_Mockingbird_kernel_v3_4.json (overwrites)

# Patch it
python patch_tkam_kernel.py \
  kernels/To_Kill_a_Mockingbird_kernel_v3_4.json \
  kernels/To_Kill_a_Mockingbird_kernel_v3_4.json

# Result:
# - Backup: To_Kill_a_Mockingbird_kernel_v3_4.json (original)
# - New:    To_Kill_a_Mockingbird_kernel_v3_5.json (patched)
```

## Version Comparison

### Keeping Versions for Comparison

All versions are preserved:
- `v3_4.json` - Original/backup
- `v3_5.json` - First patch
- `v3_6.json` - Second patch
- etc.

### Comparing Versions

You can compare kernels using:
```bash
# View differences
diff kernels/To_Kill_a_Mockingbird_kernel_v3_4.json \
     kernels/To_Kill_a_Mockingbird_kernel_v3_5.json

# Or use JSON diff tools
jq . kernels/To_Kill_a_Mockingbird_kernel_v3_4.json > v3_4.txt
jq . kernels/To_Kill_a_Mockingbird_kernel_v3_5.json > v3_5.txt
diff v3_4.txt v3_5.txt
```

## Metadata Version Fields

Each kernel includes version tracking in metadata:

```json
{
  "metadata": {
    "kernel_version": "3.5",
    "protocol_version": "3.3",
    "chapter_aware": true,
    "patch_date": "2025-01-25T14:30:22.123456",
    "patch_method": "regenerated_and_patched",
    "upgrade_date": "2025-01-25T14:30:22.123456"
  }
}
```

### Version Fields Explained

- **`kernel_version`**: Current kernel version (3.4, 3.5, etc.)
- **`protocol_version`**: Protocol used (currently 3.3)
- **`patch_date`**: When this version was created
- **`patch_method`**: How it was created (`regenerated_and_patched`, `manual`, etc.)
- **`upgrade_date`**: First upgrade date (preserved from original)

## Best Practices

1. **Always backup before patching** (automatic by default)
2. **Keep all versions** for comparison and rollback
3. **Use consistent naming** (underscores in filenames)
4. **Document major changes** in version notes or CHANGELOG
5. **Test stage files** with new versions before deleting old ones

## Stage File Compatibility

Stage files (`run_stage1a.py`, etc.) work with any version, but:
- **v3.4+** kernels have full compatibility (all fields present)
- **v3.3** kernels use fallback logic (less optimal)

Always test stage files after patching:
```bash
python run_stage1a.py kernels/To_Kill_a_Mockingbird_kernel_v3_5.json
```



