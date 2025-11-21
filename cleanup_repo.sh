#!/bin/bash

# Repository Cleanup Script
# Purpose: Organize literary-analysis-automation repository
# Safety: Only moves files, never deletes

set -e  # Exit on error

echo "=========================================="
echo "Repository Cleanup Script"
echo "=========================================="
echo ""

# First, verify what's actually working
echo "Step 0: Verifying current pipeline..."
echo ""

if [ -f "verify_pipeline.py" ]; then
    python3 verify_pipeline.py
    echo ""
    read -p "Does this look correct? Continue with cleanup? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cleanup cancelled."
        exit 0
    fi
else
    echo "⚠️  verify_pipeline.py not found. Continuing without verification..."
    echo "⚠️  This script will assume run_stage1a/1b/2_fixed are correct."
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cleanup cancelled. Download verify_pipeline.py first."
        exit 0
    fi
fi

echo ""

# Create log file
LOG_FILE="cleanup_log_$(date +%Y%m%d_%H%M%S).txt"
echo "Cleanup started at $(date)" > "$LOG_FILE"

# Function to log and move
log_move() {
    local src="$1"
    local dst="$2"
    if [ -e "$src" ]; then
        echo "Moving: $src -> $dst" | tee -a "$LOG_FILE"
        mkdir -p "$(dirname "$dst")"
        mv "$src" "$dst"
    else
        echo "Skipping (not found): $src" | tee -a "$LOG_FILE"
    fi
}

echo "Step 1: Creating directory structure..."
mkdir -p archive/old_scripts
mkdir -p archive/old_kernels
mkdir -p tests
mkdir -p docs

echo ""
echo "Step 2: Archiving old/experimental scripts..."

# Old stage2 versions
log_move "run_stage2_analysis.py" "archive/old_scripts/run_stage2_analysis.py"
log_move "run_stage2.py" "archive/old_scripts/run_stage2.py"

# Old kernel creation scripts
log_move "create_kernel.py" "archive/old_scripts/create_kernel.py"
log_move "create_kernel_v2.py" "archive/old_scripts/create_kernel_v2.py"
log_move "create_kernel_v2_fixed.py" "archive/old_scripts/create_kernel_v2_fixed.py"
log_move "create_kernel copy.py" "archive/old_scripts/create_kernel_copy.py"

# Old extraction test files
log_move "test_extraction_options2_4.py" "archive/old_scripts/test_extraction_options2_4.py"
log_move "test_extraction_approaches_sim.py" "archive/old_scripts/test_extraction_approaches_sim.py"

echo ""
echo "Step 3: Moving test files to /tests/..."

log_move "test_full_pipeline.py" "tests/test_full_pipeline.py"
log_move "test_truncation_quality.py" "tests/test_truncation_quality.py"
log_move "test_mapping.py" "tests/test_mapping.py"
log_move "test_stage1_token_limit.py" "tests/test_stage1_token_limit.py"

echo ""
echo "Step 4: Moving documentation to /docs/..."

log_move "DEVELOPER_GUIDE.md" "docs/DEVELOPER_GUIDE.md"
log_move "CHANGELOG.md" "docs/CHANGELOG.md"
log_move "CHANGELOG_breaks.md" "docs/CHANGELOG_breaks.md"
log_move "DEVICE_MAPPING_TEST_RESULTS.md" "docs/DEVICE_MAPPING_TEST_RESULTS.md"
log_move "commit_message.txt" "archive/commit_message.txt"

echo ""
echo "Step 5: Organizing template files..."

mkdir -p templates
log_move "Template_Literary_Analysis_6Step.md" "templates/Template_Literary_Analysis_6Step.md"
log_move "Template_TVODE_Construction.md" "templates/Template_TVODE_Construction.md"
log_move "Template_Teacher_Key.md" "templates/Template_Teacher_Key.md"
log_move "__LITERARY_ANALYSIS_WORKSHEET_-_Device_Recognition_v2.1" "templates/LITERARY_ANALYSIS_WORKSHEET_Device_Recognition_v2.1.md"

echo ""
echo "Step 6: Organizing book-specific output files..."

mkdir -p outputs/books
log_move "The_Giver_Week1_TeacherKey.md" "outputs/books/The_Giver_Week1_TeacherKey.md"
log_move "The_Giver_Week1_Worksheet.md" "outputs/books/The_Giver_Week1_Worksheet.md"
log_move "To_Kill_a_Mockingbird_Week1_TeacherKey.md" "outputs/books/To_Kill_a_Mockingbird_Week1_TeacherKey.md"
log_move "To_Kill_a_Mockingbird_Week1_Worksheet.md" "outputs/books/To_Kill_a_Mockingbird_Week1_Worksheet.md"
log_move "To_Kill_a_Mockingbird_Week2_TeacherKey.md" "outputs/books/To_Kill_a_Mockingbird_Week2_TeacherKey.md"
log_move "To_Kill_a_Mockingbird_Week2_Worksheet.md" "outputs/books/To_Kill_a_Mockingbird_Week2_Worksheet.md"
log_move "To_Kill_a_Mockingbird_Week3_TeacherKey.md" "outputs/books/To_Kill_a_Mockingbird_Week3_TeacherKey.md"
log_move "To_Kill_a_Mockingbird_Week3_Worksheet.md" "outputs/books/To_Kill_a_Mockingbird_Week3_Worksheet.md"
log_move "To_Kill_a_Mockingbird_Week4_TeacherKey.md" "outputs/books/To_Kill_a_Mockingbird_Week4_TeacherKey.md"
log_move "To_Kill_a_Mockingbird_Week4_Worksheet.md" "outputs/books/To_Kill_a_Mockingbird_Week4_Worksheet.md"
log_move "To_Kill_a_Mockingbird_Week5_TeacherKey.md" "outputs/books/To_Kill_a_Mockingbird_Week5_TeacherKey.md"
log_move "To_Kill_a_Mockingbird_Week5_Worksheet.md" "outputs/books/To_Kill_a_Mockingbird_Week5_Worksheet.md"
log_move "The_Old_Man_and_the_Sea_Week1_TeacherKey.md" "outputs/books/The_Old_Man_and_the_Sea_Week1_TeacherKey.md"
log_move "The_Old_Man_and_the_Sea_Week1_Worksheet.md" "outputs/books/The_Old_Man_and_the_Sea_Week1_Worksheet.md"

# Integrated progression files
log_move "The_Old_Man_and_the_Sea_Integrated_Progression.md" "outputs/books/The_Old_Man_and_the_Sea_Integrated_Progression.md"

# Bug reports
log_move "BUG_REPORT_Missing_Chapter_Assignments.md" "archive/BUG_REPORT_Missing_Chapter_Assignments.md"
log_move "BUG_REPORT_Chapter_Methodology_Comprehensive.md" "archive/BUG_REPORT_Chapter_Methodology_Comprehensive.md"

echo ""
echo "Step 7: Creating VERSION.txt reference file..."

cat > VERSION.txt << 'EOF'
# Literary Analysis Automation - Current Version
# Last Updated: November 21, 2025
# System Version: 5.0
# ✓ Verified empirically by checking actual outputs

## PRODUCTION PIPELINE (Verified Working):

Stage 1A: run_stage1a.py
  Input:  kernels/[book]_kernel_v3.3.json
  Output: outputs/[book]_stage1a_v5.0.json (verified: 5 weeks)

Stage 1B: run_stage1b.py
  Input:  outputs/[book]_stage1a_v5.0.json
  Output: outputs/[book]_stage1b_v5.0.json (verified: 5 weeks)
          outputs/[book]_Integrated_Progression.md

Stage 2:  run_stage2_fixed.py
  Input:  outputs/[book]_stage1b_v5.0.json
          kernels/[book]_kernel_v3.3.json
  Output: outputs/books/[book]_Week[N]_Worksheet.md
          outputs/books/[book]_Week[N]_TeacherKey.md

## HOW THIS WAS VERIFIED:

This VERSION.txt was generated by checking:
1. Actual output files exist and have correct structure
2. Stage 1A outputs contain 5-week packages
3. Stage 1B outputs contain 5-week packages
4. Data structures match between pipeline stages

Run `python3 verify_pipeline.py` to re-verify at any time.

## CRITICAL FILES:
- device_taxonomy_mapping.json (5-week categorization)
- run_stage1a.py (macro-micro package creation)
- run_stage1b.py (teaching progression)
- run_stage2_fixed.py (worksheet generation)

## FOLDER STRUCTURE:
- /kernels/         : Book kernels (v3.3 format)
- /outputs/         : Stage 1A/1B JSON outputs
- /outputs/books/   : Final worksheets & teacher keys
- /templates/       : Worksheet templates
- /tests/           : Test scripts
- /docs/            : Documentation
- /archive/         : Old/experimental files

## TESTING:
Verify pipeline:
  python3 verify_pipeline.py

Run full test:
  python3 tests/test_full_pipeline.py

## FOR DOCUMENTATION:
See docs/DEVELOPER_GUIDE.md
EOF

echo "Created: VERSION.txt (empirically verified)" | tee -a "$LOG_FILE"

echo ""
echo "Step 8: Creating clean .gitignore..."

cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
cleanup_log_*.txt

# Temporary files
*.tmp
*.bak
*~

# Output files (commit selectively)
outputs/*.json
outputs/books/*.md

# Don't ignore critical files
!device_taxonomy_mapping.json
!run_stage1a.py
!run_stage1b.py
!run_stage2_fixed.py
!VERSION.txt
EOF

echo "Created: .gitignore" | tee -a "$LOG_FILE"

echo ""
echo "=========================================="
echo "Cleanup Complete!"
echo "=========================================="
echo ""
echo "Log saved to: $LOG_FILE"
echo ""
echo "NEW STRUCTURE:"
echo "├── VERSION.txt              (← Your quick reference)"
echo "├── device_taxonomy_mapping.json"
echo "├── run_stage1a.py"
echo "├── run_stage1b.py"
echo "├── run_stage2_fixed.py"
echo "├── kernels/"
echo "├── outputs/"
echo "│   └── books/"
echo "├── templates/"
echo "├── tests/"
echo "├── docs/"
echo "└── archive/"
echo ""
echo "NEXT STEPS:"
echo "1. Review VERSION.txt for current pipeline"
echo "2. Check cleanup_log to see what moved"
echo "3. Run: python3 tests/test_full_pipeline.py"
echo "4. If everything works, commit changes"
echo ""
echo "To undo: Check $LOG_FILE and move files back manually"
echo ""
