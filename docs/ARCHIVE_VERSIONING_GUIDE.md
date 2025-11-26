# Archive Versioning Guide

## Quick Start

### Archive a File

When you need to archive an old version of a file:

```bash
python3 archive_versioning.py <file> \
    --version <version> \
    --reason "<reason>" \
    [--description "<description>"] \
    [--replaced-by "<replacement>"] \
    [--notes "<notes>"]
```

**Example:**
```bash
python3 archive_versioning.py run_stage1a.py \
    --version 5.0 \
    --reason "Replaced by v5.1 with taxonomy fixes" \
    --description "pre_taxonomy_fix" \
    --replaced-by "run_stage1a.py v5.1"
```

### Find Archived Versions

```bash
# List all versions of a specific file
python3 archive_versioning.py --list run_stage1a

# Show archive summary
python3 archive_versioning.py --show-metadata
```

### Label Existing Archive Files

If you have files already in the archive that need proper labeling:

```bash
python3 archive_versioning.py --retroactive-label
```

This will interactively guide you through labeling each unlabeled file.

## File Naming Convention

Archived files are automatically named using this pattern:
```
{base_name}_v{version}_{description}.{ext}
```

- `base_name`: The original filename without version info
- `version`: Version number (e.g., `5.0`, `5.1`)
- `description`: Short descriptive label
- `ext`: Original file extension

**Examples:**
- `run_stage1a_v5_0_taxonomy_fix.py`
- `run_stage2_v4_2_old_template.py`
- `create_kernel_v3_4_FIXED_old.py`

## Metadata Structure

All archived files are tracked in `archive/archive_metadata.json`:

```json
{
  "files": {
    "run_stage1a": [
      {
        "archived_name": "run_stage1a_v5_0_taxonomy_fix.py",
        "original_name": "run_stage1a.py",
        "version": "5.0",
        "archived_date": "2025-01-27T10:30:00",
        "reason": "Replaced by v5.1 with taxonomy fixes",
        "description": "taxonomy_fix",
        "replaced_by": "run_stage1a.py v5.1",
        "notes": "Had issues with device categorization",
        "file_size": 12345,
        "source_path": "run_stage1a.py"
      }
    ]
  }
}
```

## Common Use Cases

### 1. Archiving After an Update

```bash
# Before updating run_stage1a.py to v5.1
cp run_stage1a.py run_stage1a_backup.py

# Make your changes...

# Archive the old version
python3 archive_versioning.py run_stage1a_backup.py \
    --version 5.0 \
    --reason "Replaced by v5.1" \
    --replaced-by "run_stage1a.py v5.1"

# Clean up backup
rm run_stage1a_backup.py
```

### 2. Finding an Old Version

```bash
# See all archived versions
python3 archive_versioning.py --list run_stage1a

# Output shows:
# 1. run_stage1a_v5_0_taxonomy_fix.py
#    Version: 5.0
#    Date: 2025-01-27T10:30:00
#    Reason: Replaced by v5.1 with taxonomy fixes
#    ...
```

### 3. Organizing Existing Archive

If you have files already in `archive/` that need proper labeling:

```bash
python3 archive_versioning.py --retroactive-label
```

The script will:
1. Find all files in `archive/` not yet in metadata
2. Ask you to provide version, reason, description for each
3. Update the metadata file automatically

## Benefits

1. **Consistent Naming**: All archived files follow the same pattern
2. **Searchable**: Find files by version, date, or reason
3. **Traceable**: Know what replaced what and when
4. **Organized**: Metadata keeps everything documented
5. **Queryable**: JSON metadata can be searched programmatically

## Integration with Git

The versioning system works well with git:

```bash
# Archive before committing changes
python3 archive_versioning.py old_file.py \
    --version 5.0 \
    --reason "Replaced in commit abc123" \
    --replaced-by "new_file.py v5.1"

# Commit the changes
git add new_file.py archive/
git commit -m "Update to v5.1, archived v5.0"
```

## Tips

- **Be descriptive**: Good descriptions make files easier to find later
- **Note replacements**: Always note what replaced an archived file
- **Use consistent versions**: Match version numbers with your project's versioning scheme
- **Regular cleanup**: Use `--retroactive-label` periodically to organize existing files




