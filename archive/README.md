# Archive Directory

This directory contains archived versions of scripts and files from the literary analysis automation project.

## Versioning System

Files in this archive are tracked using a structured versioning system with metadata.

### Naming Convention

Archived files follow this naming pattern:
```
{base_name}_v{version}_{description}.{ext}
```

Examples:
- `run_stage1a_v5_0_taxonomy_fix.py`
- `run_stage2_v4_2_old_template.py`
- `create_kernel_v3_4_FIXED_old.py`

### Metadata Tracking

All archived files are tracked in `archive_metadata.json`, which contains:
- Version number
- Archive date
- Reason for archiving
- What replaced it (if applicable)
- Additional notes

### Usage

#### Archive a File

```bash
# Archive a file with version info
python3 archive_versioning.py run_stage1a.py \
    --version 5.0 \
    --reason "Replaced by v5.1 with taxonomy fixes" \
    --description "taxonomy_fix" \
    --replaced-by "run_stage1a.py v5.1"
```

#### List Archived Versions

```bash
# List all archived versions of a file
python3 archive_versioning.py --list run_stage1a
```

#### View Archive Summary

```bash
# Show metadata summary
python3 archive_versioning.py --show-metadata
```

#### Retroactively Label Existing Files

If you have existing archive files that aren't tracked:

```bash
# Interactively label existing files
python3 archive_versioning.py --retroactive-label
```

### Directory Structure

The archive is organized as follows:

```
archive/
├── README.md                    # This file
├── archive_metadata.json        # Version tracking metadata
├── old_scripts/                 # Older script versions
│   ├── create_kernel_v2.py
│   └── ...
├── broken_automation/           # Scripts that had issues
│   └── ...
└── [other archived files]       # Directly archived files
```

### Best Practices

1. **Always use the versioning script** when archiving files
2. **Provide clear reasons** for why a file was archived
3. **Note what replaced it** if applicable
4. **Use descriptive descriptions** in filenames
5. **Keep metadata up to date** - the system tracks this automatically

### Finding Files

To find a specific archived version:

1. Use `--list` to see all versions of a file
2. Check `archive_metadata.json` for detailed information
3. Search by reason or date in the metadata file

### Example Workflow

```bash
# 1. You've updated run_stage1a.py to v5.1
# 2. Archive the old version
python3 archive_versioning.py run_stage1a.py \
    --version 5.0 \
    --reason "Replaced by v5.1 with improved taxonomy mapping" \
    --description "pre_taxonomy_fix" \
    --replaced-by "run_stage1a.py v5.1"

# 3. Later, find the old version
python3 archive_versioning.py --list run_stage1a

# 4. View all archive info
python3 archive_versioning.py --show-metadata
```




