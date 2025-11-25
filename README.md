# Kernel Creation Automation - Version 2

Semi-automated literary analysis kernel creation following the **Kernel Validation Protocol v3.3** and **Book Structure Alignment Protocol v1.1**.

## Overview

This automation script helps you create kernel JSONs (comprehensive literary analysis data structures) from books by:
- Extracting 5 Freytag dramatic structure sections
- Tagging 84 macro alignment variables (narrative + rhetorical elements)
- Identifying 15-20+ micro literary devices with examples
- Assembling everything into a validated kernel JSON

**Version 2 Features:**
- ✅ Automated API calls to Claude
- ✅ Review gates at each stage (you approve before continuing)
- ✅ JSON validation and error handling
- ✅ Saves intermediate outputs
- ✅ Progress tracking

## Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Directory Structure

Create the following directories:

```bash
mkdir -p protocols books kernels outputs
```

### 3. Add Your Protocol Files

Place these files in the `protocols/` directory:
- `Book_Structure_Alignment_Protocol_v1.md` (v1.1)
- `Kernel_Validation_Protocol_v3_3.md`
- `Kernel_Protocol_Enhancement_v3_3.md`
- `Artifact_1_-_Device_Taxonomy_by_Alignment_Function`
- `Artifact_2_-_Text_Tagging_Protocol`
- `LEM_-_Stage_1_-_Narrative-Rhetoric_Triangulation`

### 4. Set Up Anthropic API Key

Get your API key from: https://console.anthropic.com

Set it as an environment variable:

```bash
# On macOS/Linux
export ANTHROPIC_API_KEY="your-api-key-here"

# On Windows
set ANTHROPIC_API_KEY=your-api-key-here

# Or add to your .bashrc / .zshrc for permanent setup
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
```

## Usage

### Basic Command

```bash
python create_kernel.py <book_path> <title> <author> <edition> <total_chapters>
```

**Note:** The `total_chapters` parameter is required for structure alignment (Stage 0).

### Example: To Kill a Mockingbird

```bash
python create_kernel.py \
  books/TKAM.pdf \
  "To Kill a Mockingbird" \
  "Harper Lee" \
  "Harper Perennial Modern Classics, 2006" \
  31
```

### Example: The Giver

```bash
python create_kernel.py \
  books/The_Giver.pdf \
  "The Giver" \
  "Lois Lowry" \
  "Houghton Mifflin, 1993" \
  23
```

## Workflow

The script runs through 5 stages with review gates:

### Stage 0: Book Structure Alignment (NEW in v3.5)
- Detects book structure type (NUM/NAME/NEST/UNMARK/HYBRID)
- Applies conventional distribution formula
- Identifies actual climax chapter(s) through content verification
- Validates chapter-to-Freytag alignment
- You review and approve the alignment

### Stage 1: Freytag Extract Selection
- Uses validated chapter alignment from Stage 0
- Extracts 5 key sections (Exposition, Rising Action, Climax, Falling Action, Resolution)
- Provides text extracts and rationales for each section
- You review and approve the extracts

### Stage 2A: Macro Alignment Tagging
- Claude analyzes the 5 extracts
- Tags 84 macro variables (narrative voice, structure, rhetorical alignment)
- You review and approve the macro variables

### Stage 2B: Micro Device Inventory
- Claude identifies 15-20+ literary devices
- Provides 2-3 examples per device with structured format
- You review and approve the device list

### Final Assembly
- Script assembles everything into kernel JSON
- You review the final kernel
- Kernel is saved to `kernels/` directory

## Review Commands

At each review gate, you have these options:

- **`y`** - Approve and continue to next stage
- **`n`** - Reject (exit, you'll need to restart or edit manually)
- **`save`** - Save current output to `outputs/` for later review
- **`quit`** - Exit the script

## Output Files

### Kernel JSON Structure

```json
{
  "text_metadata": {
    "title": "Book Title",
    "author": "Author Name",
    "edition": "Publisher, Year",
    "protocol_version": "Kernel Validation Protocol v3.3"
  },
  "extracts": {
    "exposition": { "text": "...", "chapter_range": "..." },
    "rising_action": { ... },
    "climax": { ... },
    "falling_action": { ... },
    "resolution": { ... }
  },
  "narrative": {
    "voice": { "pov": "FP", "focalization": "INT", ... },
    "structure": { "plot_architecture": "ARIST", ... }
  },
  "rhetoric": {
    "alignment_type": "CODE",
    "dominant_mechanism": "CODE"
  },
  "devices": [
    {
      "name": "Symbolism",
      "layer": "B",
      "function": "Me",
      "examples": [...]
    }
  ]
}
```

### File Naming

Kernels are automatically saved as:
```
kernels/<Title>_kernel_v3_5.json
```

Example: `kernels/To_Kill_a_Mockingbird_kernel_v3_5.json`

**Note:** Kernel version 3.5 includes structure alignment protocol integration. Older v3.4 kernels remain compatible.

## Version Control with Git

### Initial Setup

```bash
git init
git add protocols/ create_kernel.py requirements.txt README.md
git commit -m "Initial setup: Kernel creation automation"
```

### After Creating a Kernel

```bash
git add kernels/TKAM_kernel_v3.3.json
git commit -m "Add TKAM kernel v3.3"
git push
```

### When Updating Protocols

```bash
# Update protocol file
vim protocols/Kernel_Validation_Protocol_v3_4.md

# Regenerate kernels
python create_kernel.py books/TKAM.pdf "To Kill a Mockingbird" "Harper Lee" "..."
python create_kernel.py books/The_Giver.pdf "The Giver" "Lois Lowry" "..."

# Compare versions
git diff kernels/TKAM_kernel_v3.3.json kernels/TKAM_kernel_v3.4.json

# Commit changes
git add protocols/ kernels/
git commit -m "Updated to Kernel Protocol v3.4, regenerated all kernels"
```

## Troubleshooting

### API Key Error
```
ValueError: ANTHROPIC_API_KEY environment variable not set
```
**Solution:** Set your API key (see Setup step 4)

### PDF Extraction Issues
```
Error loading PDF
```
**Solution:** Ensure PDF is not encrypted/password-protected. Try converting to .txt first.

### JSON Parse Error
```
❌ Error: Invalid JSON response from Claude
```
**Solution:** This is rare but can happen. Claude will retry on next run. If persistent, check your protocol files for formatting issues.

### Device Count Warning
```
⚠️  Warning: Only 12 devices found (minimum 15 required)
```
**Solution:** You can still approve and continue, but the kernel may need manual review to add more devices later.

## Cost Estimation

Using Claude Sonnet 4.5 via API:

- **Stage 1 (Extracts):** ~$0.50-1.00 (processes full book)
- **Stage 2A (Macro):** ~$0.20-0.40 (processes extracts)
- **Stage 2B (Devices):** ~$0.30-0.50 (processes extracts)

**Total per book:** ~$1.00-2.00

Much cheaper than using Claude Pro credits in chat!

## Complete Pipeline

This repository contains a complete automation pipeline for literary analysis:

1. **Kernel Creation** (`create_kernel.py`) - Create kernel JSONs from book PDFs
2. **Stage 1A** (`run_stage1a.py`) - Extract macro-micro packages (5 weeks)
3. **Stage 1B** (`run_stage1b.py`) - Create weekly teaching packages
4. **Stage 2** (`run_stage2.py`) - Generate worksheets and teacher keys

### Quick Start

```bash
# 1. Create kernel (now includes Stage 0: Structure Alignment)
python3 create_kernel.py books/TKAM.pdf "To Kill a Mockingbird" "Harper Lee" "1960" 31

# 2. Run Stage 1A (instant, free)
python3 run_stage1a.py kernels/To_Kill_a_Mockingbird_kernel_v3_5.json

# 3. Run Stage 1B (instant, free)
python3 run_stage1b.py outputs/To_Kill_a_Mockingbird_stage1a_v5.0.json

# 4. Generate worksheets (requires API key)
python3 run_stage2.py outputs/To_Kill_a_Mockingbird_stage1b_v5.0.json --all-weeks
```

**Total time:** ~30 minutes  
**Total cost:** ~$2-3 per book (kernel + worksheets)

## Documentation

- **[Stage Automation Guide](docs/STAGE_AUTOMATION_GUIDE.md)** - Complete workflow for Stages 1A/1B/2
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - How to modify the codebase safely
- **[Archive Versioning Guide](docs/ARCHIVE_VERSIONING_GUIDE.md)** - Properly label and track archived file versions
- **[Changelog](docs/CHANGELOG.md)** - Version history and migration guides
- **[Quick Start](QUICKSTART.md)** - Get running in 5 minutes
- **[Version Info](VERSION.txt)** - Current system version (5.1.2)

## System Version

**Current Version:** 5.1.2 (November 2025)

- 5-week pedagogical progression
- Macro-micro integration
- Device taxonomy mapping system
- Automated worksheet generation

See [VERSION.txt](VERSION.txt) for detailed pipeline information.

## Support

For issues or questions:
- Check documentation in `docs/` folder
- Review [Developer Guide](docs/DEVELOPER_GUIDE.md) for making changes
- Check [Changelog](docs/CHANGELOG.md) for version compatibility
- Review example kernels in `kernels/`
- Verify your protocol versions match (Kernel Validation v3.3, Structure Alignment v1.1)

## License

Your literary analysis framework - use as needed for research/teaching.
