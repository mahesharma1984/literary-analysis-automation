#!/bin/bash

# create_all_tags.sh
# Script to create all git tags for LEM project version history
# Run this script from your repository root

set -e  # Exit on error

echo "=========================================="
echo "Creating Git Tags for LEM Version History"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to create a tag
create_tag() {
    local tag=$1
    local message=$2
    
    if git rev-parse "$tag" >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Tag $tag already exists, skipping...${NC}"
    else
        git tag -a "$tag" -m "$message"
        echo -e "${GREEN}✅ Created tag: $tag${NC}"
    fi
}

echo -e "${BLUE}Creating Kernel Protocol tags...${NC}"
create_tag "kernel-v3.1" "Kernel Validation Protocol v3.1 - Extract Preparation Protocol"
create_tag "kernel-v3.2" "Kernel Validation Protocol v3.2 - Terminology Clarification"
create_tag "kernel-v3.3" "Kernel Validation Protocol v3.3 - Examples Structure Enhancement"
echo ""

echo -e "${BLUE}Creating Kernel Enhancement tags...${NC}"
create_tag "enhancement-v3.1" "Kernel Protocol Enhancement v3.1 - Comprehensive Device Inventory"
create_tag "enhancement-v3.2" "Kernel Protocol Enhancement v3.2 - Terminology Update"
create_tag "enhancement-v3.3" "Kernel Protocol Enhancement v3.3 - Examples Format Standardization"
echo ""

echo -e "${BLUE}Creating Stage 1A tags...${NC}"
create_tag "stage1a-v5.0" "Stage 1A v5.0 - Macro-Micro Extraction (Breaking Change)"
create_tag "stage1a-v5.1" "Stage 1A v5.1 - Version Alignment"
echo ""

echo -e "${BLUE}Creating Stage 1B tags...${NC}"
create_tag "stage1b-v5.0" "Stage 1B v5.0 - Macro-Micro Week Packages (Breaking Change)"
create_tag "stage1b-v5.1" "Stage 1B v5.1 - Chapter Chronology Update"
echo ""

echo -e "${BLUE}Creating Stage 2 tags...${NC}"
create_tag "stage2-v4.0" "Stage 2 v4.0 - Macro-Micro Template System (Breaking Change)"
create_tag "stage2-v4.1" "Stage 2 v4.1 - 6-Step Pedagogical Scaffolding"
echo ""

echo -e "${BLUE}Creating Template tags...${NC}"
create_tag "templates-v2.0" "Templates v2.0 - MacroMicro System Initial Release"
create_tag "templates-v2.1" "Template Updates v2.1 - Location Hints Integration"
echo ""

echo "=========================================="
echo -e "${GREEN}✅ All tags created successfully!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Review tags with: git tag -l"
echo "2. Push tags with: git push origin --tags"
echo "3. Create GitHub releases using the web interface or gh CLI"
echo ""
echo "Commands:"
echo "  View all tags:     git tag -l"
echo "  View tag details:  git show [tag-name]"
echo "  Push all tags:     git push origin --tags"
echo "  Create release:    gh release create [tag-name] --notes-file docs/releases/[tag-name].md"
echo ""
