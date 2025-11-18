# PROJECT DIRECTORY STRUCTURE

```
literary-analysis-automation/
│
├── create_kernel.py          # Main kernel creation script
├── setup.py                  # Setup and verification script
├── requirements.txt          # Python dependencies
├── README.md                 # Full documentation
├── QUICKSTART.md            # Quick start guide
├── .gitignore               # Git ignore patterns
│
├── protocols/               # Protocol documentation (v3.3)
│   ├── Kernel_Validation_Protocol_v3_3.md
│   ├── Kernel_Protocol_Enhancement_v3_3.md
│   ├── Artifact_1_-_Device_Taxonomy_by_Alignment_Function
│   ├── Artifact_2_-_Text_Tagging_Protocol
│   └── LEM_-_Stage_1_-_Narrative-Rhetoric_Triangulation
│
├── books/                   # Source book files
│   ├── TKAM.pdf
│   ├── The_Giver.pdf
│   └── Holes.txt
│
├── kernels/                 # Generated kernel JSONs
│   ├── To_Kill_a_Mockingbird_kernel_v3.3.json
│   ├── The_Giver_kernel_v3.3.json
│   └── Holes_kernel_v3.3.json
│
└── outputs/                 # Intermediate outputs (for review)
    ├── Stage_1_Freytag_Extracts_20251117_143022.txt
    ├── Stage_2A_Macro_Variables_20251117_144531.txt
    └── Stage_2B_Micro_Devices_20251117_150142.txt
```

## File Descriptions

### Scripts
- **create_kernel.py** - Main automation script with review gates
- **setup.py** - Initializes directories and verifies setup

### Documentation
- **README.md** - Complete documentation with setup, usage, troubleshooting
- **QUICKSTART.md** - 5-minute getting started guide
- **requirements.txt** - Python package dependencies

### Protocols (Input)
These are your framework documents that define the analysis methodology.
Place these in `protocols/` before running the script.

### Books (Input)
Your source texts in PDF or .txt format.
Place in `books/` directory.

### Kernels (Output - Track in Git)
The final validated kernel JSONs containing complete literary analysis.
**These should be committed to Git** for version control.

### Outputs (Temporary - Don't Track)
Intermediate outputs saved during review process.
Useful for debugging but not needed in Git.

## Git Workflow Example

```bash
# Initial setup
git init
git add create_kernel.py setup.py requirements.txt README.md QUICKSTART.md .gitignore
git add protocols/
git commit -m "Initial commit: Kernel creation automation v2"

# After creating TKAM kernel
git add kernels/To_Kill_a_Mockingbird_kernel_v3.3.json
git commit -m "Add TKAM kernel v3.3"

# After updating protocols to v3.4
git add protocols/Kernel_Validation_Protocol_v3_4.md
python create_kernel.py books/TKAM.pdf "To Kill a Mockingbird" "Harper Lee" "..."
git add kernels/To_Kill_a_Mockingbird_kernel_v3.4.json
git commit -m "Update to Kernel Protocol v3.4, regenerate TKAM kernel"

# Compare versions
git diff kernels/To_Kill_a_Mockingbird_kernel_v3.3.json kernels/To_Kill_a_Mockingbird_kernel_v3.4.json
```

## What to Track in Git

**DO track:**
- ✅ Scripts (create_kernel.py, setup.py)
- ✅ Documentation (README.md, QUICKSTART.md)
- ✅ Protocols (all .md files in protocols/)
- ✅ Kernels (all .json files in kernels/)
- ✅ Configuration examples

**DON'T track:**
- ❌ API keys (.env files)
- ❌ Book PDFs (large files - use Git LFS if needed)
- ❌ Temporary outputs (outputs/ directory)
- ❌ Python cache (__pycache__)

## Storage Size Estimates

- **Protocols:** ~200 KB total
- **Scripts:** ~50 KB total
- **Kernel JSON:** ~20-50 KB each
- **Book PDF:** 1-5 MB each (don't commit)

**Repository size without books:** < 1 MB
**Repository size with 10 kernels:** ~1-2 MB
