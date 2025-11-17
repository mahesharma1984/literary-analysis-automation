#!/bin/bash

# create_all_releases.sh
# Script to create all GitHub releases for LEM project version history
# Requires: GitHub CLI (gh) installed and authenticated
# Run this script from your repository root after creating tags

set -e  # Exit on error

echo "=========================================="
echo "Creating GitHub Releases for LEM"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) is not installed${NC}"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}❌ Not authenticated with GitHub CLI${NC}"
    echo "Run: gh auth login"
    exit 1
fi

echo -e "${GREEN}✅ GitHub CLI is installed and authenticated${NC}"
echo ""

# Check if docs/releases directory exists
if [ ! -d "docs/releases" ]; then
    echo -e "${RED}❌ docs/releases directory not found${NC}"
    echo "Create it and add release note files first"
    exit 1
fi

# Function to create a release
create_release() {
    local tag=$1
    local title=$2
    local notes_file=$3
    local is_breaking=$4
    
    echo -e "${BLUE}Creating release for $tag...${NC}"
    
    # Check if notes file exists
    if [ ! -f "$notes_file" ]; then
        echo -e "${YELLOW}⚠️  Release notes file not found: $notes_file${NC}"
        echo -e "${YELLOW}   Creating release without notes file...${NC}"
        gh release create "$tag" \
            --title "$title" \
            --notes "See CHANGELOG.md for details."
    else
        gh release create "$tag" \
            --title "$title" \
            --notes-file "$notes_file"
    fi
    
    echo -e "${GREEN}✅ Created release: $tag${NC}"
    echo ""
}

echo "Creating releases..."
echo ""

# Kernel Protocol Releases
echo -e "${BLUE}═══ Kernel Validation Protocol ═══${NC}"
create_release "kernel-v3.1" \
    "Kernel Validation Protocol v3.1 - Extract Preparation" \
    "docs/releases/kernel-v3.1.md" \
    false

create_release "kernel-v3.2" \
    "Kernel Validation Protocol v3.2 - Terminology Clarification" \
    "docs/releases/kernel-v3.2.md" \
    false

create_release "kernel-v3.3" \
    "Kernel Validation Protocol v3.3 - Examples Structure" \
    "docs/releases/kernel-v3.3.md" \
    false

echo ""

# Kernel Enhancement Releases
echo -e "${BLUE}═══ Kernel Protocol Enhancement ═══${NC}"
create_release "enhancement-v3.1" \
    "Kernel Protocol Enhancement v3.1 - Device Inventory" \
    "docs/releases/enhancement-v3.1.md" \
    false

create_release "enhancement-v3.2" \
    "Kernel Protocol Enhancement v3.2 - Terminology Update" \
    "docs/releases/enhancement-v3.2.md" \
    false

create_release "enhancement-v3.3" \
    "Kernel Protocol Enhancement v3.3 - Examples Format" \
    "docs/releases/enhancement-v3.3.md" \
    false

echo ""

# Stage 1A Releases
echo -e "${BLUE}═══ Stage 1A Implementation ═══${NC}"
create_release "stage1a-v5.0" \
    "Stage 1A v5.0 - Macro-Micro Extraction ⚠️ BREAKING" \
    "docs/releases/stage1a-v5.0.md" \
    true

create_release "stage1a-v5.1" \
    "Stage 1A v5.1 - Version Alignment" \
    "docs/releases/stage1a-v5.1.md" \
    false

echo ""

# Stage 1B Releases
echo -e "${BLUE}═══ Stage 1B Implementation ═══${NC}"
create_release "stage1b-v5.0" \
    "Stage 1B v5.0 - Macro-Micro Packages ⚠️ BREAKING" \
    "docs/releases/stage1b-v5.0.md" \
    true

create_release "stage1b-v5.1" \
    "Stage 1B v5.1 - Chapter Chronology" \
    "docs/releases/stage1b-v5.1.md" \
    false

echo ""

# Stage 2 Releases
echo -e "${BLUE}═══ Stage 2 Implementation ═══${NC}"
create_release "stage2-v4.0" \
    "Stage 2 v4.0 - Macro-Micro Templates ⚠️ BREAKING" \
    "docs/releases/stage2-v4.0.md" \
    true

create_release "stage2-v4.1" \
    "Stage 2 v4.1 - 6-Step Pedagogy" \
    "docs/releases/stage2-v4.1.md" \
    false

echo ""

# Template Releases
echo -e "${BLUE}═══ Templates ═══${NC}"
create_release "templates-v2.0" \
    "Templates v2.0 - MacroMicro System" \
    "docs/releases/templates-v2.0.md" \
    false

create_release "templates-v2.1" \
    "Template Updates v2.1 - Location Hints" \
    "docs/releases/templates-v2.1.md" \
    false

echo ""
echo "=========================================="
echo -e "${GREEN}✅ All releases created successfully!${NC}"
echo "=========================================="
echo ""
echo "View releases at:"
echo "  https://github.com/$(gh repo view --json owner,name -q '.owner.login + \"/\" + .name')/releases"
echo ""
echo "Or use:"
echo "  gh release list"
echo ""
