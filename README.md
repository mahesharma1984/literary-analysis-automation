# Kernel Creation Automation - Version 2

Semi-automated literary analysis kernel creation following the **Kernel Validation Protocol v3.3**.

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
python create_kernel.py <book_path> <title> <author> <edition>
```

### Example: To Kill a Mockingbird

```bash
python create_kernel.py \
  books/TKAM.pdf \
  "To Kill a Mockingbird" \
  "Harper Lee" \
  "Harper Perennial Modern Classics, 2006"
```

### Example: The Giver

```bash
python create_kernel.py \
  books/The_Giver.pdf \
  "The Giver" \
  "Lois Lowry" \
  "Houghton Mifflin, 1993"
```

## Workflow

The script runs through 4 stages with review gates:

### Stage 1: Freytag Extract Selection
- Claude analyzes the full book
- Extracts 5 key sections (Exposition, Rising Action, Climax, Falling Action, Resolution)
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
kernels/<Title>_kernel_v3.3.json
```

Example: `kernels/To_Kill_a_Mockingbird_kernel_v3.3.json`

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

## Next Steps

Once you have a kernel JSON, you can:

1. **Run Stage 1A:** Extract macro-micro packages
   ```bash
   python run_stage1a.py kernels/TKAM_kernel_v3.3.json
   ```

2. **Run Stage 1B:** Package into 4 weeks
   ```bash
   python run_stage1b.py outputs/TKAM_stage1a_v5.0.json
   ```

3. **Run Stage 2:** Generate worksheets
   ```bash
   python run_stage2.py outputs/TKAM_stage1b_v5.0.json
   ```

## Support

For issues or questions:
- Check protocol documentation in `protocols/`
- Review example kernels in `kernels/`
- Verify your protocol versions match (v3.3)

## License

Your literary analysis framework - use as needed for research/teaching.
