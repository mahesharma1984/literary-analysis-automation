# GitHub Version History Implementation Guide

**Purpose:** Guide for implementing version history and releases in GitHub  
**Date:** November 17, 2025

---

## Quick Start

### 1. Initial Setup

```bash
# Add CHANGELOG.md to your repository
git add CHANGELOG.md
git commit -m "docs: Add comprehensive changelog"
git push origin main
```

### 2. Create Git Tags for Existing Versions

```bash
# Kernel Protocols
git tag -a kernel-v3.1 -m "Kernel Validation Protocol v3.1 - Extract Preparation"
git tag -a kernel-v3.2 -m "Kernel Validation Protocol v3.2 - Terminology Clarification"
git tag -a kernel-v3.3 -m "Kernel Validation Protocol v3.3 - Examples Structure"

# Enhancement Protocol
git tag -a enhancement-v3.1 -m "Kernel Protocol Enhancement v3.1 - Device Inventory"
git tag -a enhancement-v3.2 -m "Kernel Protocol Enhancement v3.2 - Terminology Update"
git tag -a enhancement-v3.3 -m "Kernel Protocol Enhancement v3.3 - Examples Format"

# Stage Implementations
git tag -a stage1a-v5.0 -m "Stage 1A v5.0 - Macro-Micro Extraction"
git tag -a stage1a-v5.1 -m "Stage 1A v5.1 - Version Alignment"
git tag -a stage1b-v5.0 -m "Stage 1B v5.0 - Macro-Micro Packages"
git tag -a stage1b-v5.1 -m "Stage 1B v5.1 - Chapter Chronology"
git tag -a stage2-v4.0 -m "Stage 2 v4.0 - Macro-Micro Templates"
git tag -a stage2-v4.1 -m "Stage 2 v4.1 - 6-Step Pedagogy"

# Templates
git tag -a templates-v2.0 -m "Templates v2.0 - MacroMicro Initial Release"
git tag -a templates-v2.1 -m "Template Updates v2.1 - Location Hints"

# Push all tags
git push origin --tags
```

### 3. Create GitHub Releases

Go to your GitHub repository → Releases → Create a new release

---

## Release Creation Guide

### Release Template

For each major version, create a release with:

**Tag:** `[component]-v[version]`  
**Release title:** `[Component] v[Version] - [Short Description]`  
**Release notes:** See templates below

---

## Individual Release Notes

### Kernel Validation Protocol v3.3 (Current)

**Tag:** `kernel-v3.3`  
**Title:** Kernel Validation Protocol v3.3 - Examples Structure Enhancement  
**Release Date:** 2025-11-14

**Release Notes:**

```markdown
## 🎯 What's New

This release adds structured examples to the Kernel Validation Protocol, enabling automated worksheet generation with chapter/page references.

### ✨ Features Added

- Structured examples array format with Freytag section mapping
- Scene identifiers for pedagogical utility
- Chapter and page range references
- Quote snippets (20-100 characters)
- Edition reference requirements in validation metadata

### 📊 Technical Details

**Example Structure:**
```json
{
  "freytag_section": "CLUST-BEG",
  "scene": "Atticus teaches shooting lesson",
  "chapter": 10,
  "page_range": "90-93",
  "quote_snippet": "it's a sin to kill a mockingbird"
}
```

**Specification:**
- 2-3 examples required per device
- Examples must align with position codes
- ~20-30% size reduction vs. full quotes

### 🔄 Migration

**Backward Compatible:** Existing v3.2 JSON can be migrated by adding examples arrays.

### 📦 Dependencies

- Triggers: Kernel Protocol Enhancement v3.3
- Enables: Stage 1A v5.0 automation
- Required for: Template Updates v2.1

### 📚 Documentation

- See CHANGELOG.md for detailed changes
- See Kernel_Validation_Protocol_v3_3.md for full specification

### 🔗 Related Releases

- Enhancement v3.3: [link]
- Stage 1A v5.0: [link]

---

**Files Changed:**
- `Kernel_Validation_Protocol_v3_3.md`

**Breaking Changes:** None (backward compatible)
```

---

### Stage 1A v5.0 (Major Release)

**Tag:** `stage1a-v5.0`  
**Title:** Stage 1A v5.0 - Macro-Micro Extraction  
**Release Date:** 2025-11-15

**Release Notes:**

```markdown
## 🚀 Major Release: Macro-Micro Integration

This is a **BREAKING CHANGE** release that completely redesigns Stage 1A extraction to support macro-focused pedagogy.

### ⚠️ Breaking Changes

**Cannot migrate from v4.2** - Complete regeneration required.

**What Changed:**
- Output structure: Flat device list → Macro-micro packages
- Extraction logic: Device-only → Integrated macro+micro
- File format: Incompatible with v4.2 processors

### ✨ Features Added

- **Macro-Micro Extraction:** Extract both alignment elements AND devices
- **Relationship Mapping:** Shows which devices execute which macro elements
- **Package Structure:** Organizes as macro-micro pairs
- **Chapter Mapping:** Single chapter focus per package
- **Teaching Context:** Adds `executes_macro` field to devices

### 📊 New Output Structure

```json
{
  "macro_micro_packages": {
    "exposition_package": {
      "macro_focus": "Exposition",
      "macro_variables": {
        "narrative.structure.exposition_method": "Incremental revelation",
        "narrative.voice.distance": "Retrospective intimacy"
      },
      "micro_devices": [
        {
          "device_name": "Indirect Characterization",
          "executes_macro": "Builds character knowledge gradually...",
          "examples": [...]
        }
      ],
      "focus_chapter": 1
    }
  }
}
```

### 🎯 Why This Change?

Education vertical requires teaching macro concepts (exposition, structure, voice) through micro devices. v4.2 only extracted devices without showing their relationship to macro alignment.

### 📦 Dependencies

**Requires:**
- Kernel_Validation_Protocol v3.2+ (terminology)
- Kernel_Protocol_Enhancement v3.3 (examples)

**Enables:**
- Stage 1B v5.0 (macro-micro packages)

**Impacts:**
- Stage 1B v4.2 outputs become invalid
- Stage 2 v3.2 outputs become invalid
- All downstream outputs require regeneration

### 🔄 Migration Guide

1. **Backup v4.2 outputs** (cannot migrate)
2. **Run Stage 1A v5.0** on kernel JSON
3. **Regenerate Stage 1B** with v5.0
4. **Regenerate Stage 2** worksheets with v4.0

Expected time: +30% for relationship mapping

### 📚 Documentation

- `Stage_1A_v5.0_Implementation.md`: Full specification
- `CHANGELOG.md`: Detailed change log
- `COMPLETE_REVISION_HISTORY.md`: Rationale and context

### 🔗 Related Releases

- **Supersedes:** Stage 1A v4.2 (deprecated)
- **Required by:** Stage 1B v5.0
- **Part of:** v5.0 Macro-Micro Integration series

---

**Files Changed:**
- `Stage_1A_v5.0_Implementation.md` (new)
- `Stage_1A_v4.2_Implementation.md` (deprecated)

**Breaking Changes:** Yes - complete output structure redesign
```

---

### Stage 2 v4.1 (Enhancement Release)

**Tag:** `stage2-v4.1`  
**Title:** Stage 2 v4.1 - 6-Step Pedagogical Scaffolding  
**Release Date:** 2025-11-15

**Release Notes:**

```markdown
## 📚 Enhancement: 6-Step Pedagogical Scaffolding

This release adds structured skill progression to worksheet device analysis.

### ✨ Features Added

**6-Step Learning Progression:**

1. **Definition** - Recognition skill
2. **Find** - Matching skill
3. **Identify** - Multiple choice
4. **Analyze** - Sequencing
5. **Detail** - Textual evidence
6. **Effect** - Categorization

### 📊 Example Structure

```markdown
## Device 1: Indirect Characterization

### Step 1: DEFINITION
Read and recognize the definition...

### Step 2: FIND
Find an example in Chapter 1...

### Step 3: IDENTIFY
Which of these is indirect characterization?
[ ] Direct statement about Scout
[ ] Action showing Scout's curiosity ✓
[ ] Author's description

### Step 4: ANALYZE
Order these characterization techniques...

### Step 5: DETAIL
Quote textual evidence...

### Step 6: EFFECT
Categorize the effect...
```

### 🎯 Why This Change?

Need clear skill progression from recognition to application. Provides scaffolding for students at different levels.

### 📦 Dependencies

**Requires:**
- Stage 1B v5.1 packages
- Extends Stage 2 v4.0

**Updates:**
- Template_Literary_Analysis_MacroMicro v2.0

### 🔄 Migration

**Non-Breaking:** Compatible with v4.0 packages
- Existing v4.0 worksheets can be enhanced with 6-step structure
- Recommended: Regenerate worksheets for full 6-step experience

### 📚 Documentation

- `Stage_2_v4_1_Implementation.md`: Full specification
- `Template_Literary_Analysis_MacroMicro.md` v2.0: Updated template

### 🔗 Related Releases

- **Extends:** Stage 2 v4.0
- **Requires:** Stage 1B v5.1

---

**Files Changed:**
- `Stage_2_v4_1_Implementation.md`
- `Template_Literary_Analysis_MacroMicro.md` (v2.0)

**Breaking Changes:** None (enhancement only)
```

---

## GitHub Release Workflow

### For New Versions

1. **Update Files**
   ```bash
   # Update implementation file
   # Update CHANGELOG.md
   git add [files]
   git commit -m "feat: [Component] v[X.X] - [Description]"
   git push origin main
   ```

2. **Create Tag**
   ```bash
   git tag -a [component]-v[X.X] -m "[Component] v[X.X] - [Description]"
   git push origin [component]-v[X.X]
   ```

3. **Create GitHub Release**
   - Go to: `https://github.com/[your-repo]/releases/new`
   - Choose tag: `[component]-v[X.X]`
   - Add release title and notes (use templates above)
   - Attach relevant files if needed
   - Publish release

---

## Commit Message Convention

Use conventional commits format:

```bash
# Features
git commit -m "feat(kernel): Add examples structure to v3.3"
git commit -m "feat(stage1a): Add macro-micro extraction"

# Breaking Changes
git commit -m "feat(stage1a)!: Redesign output structure for macro-micro

BREAKING CHANGE: Output format changed from flat device list to macro-micro packages"

# Documentation
git commit -m "docs: Update CHANGELOG for v3.3 release"
git commit -m "docs(readme): Add migration guide for v5.0"

# Fixes
git commit -m "fix(stage2): Correct template variable names"

# Deprecations
git commit -m "chore: Deprecate Stage 1A v4.2"
```

### Commit Types
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `chore`: Maintenance tasks
- `refactor`: Code restructuring
- `test`: Test additions/changes
- `perf`: Performance improvements

Add `!` after type for breaking changes: `feat(stage1a)!:`

---

## Branch Strategy

### Recommended Structure

```
main (stable releases only)
├── develop (active development)
├── feature/stage1a-v5.1
├── feature/stage2-6step
├── hotfix/kernel-v3.3.1
└── release/v5.0-macro-micro
```

### Workflow

1. **Feature Development**
   ```bash
   git checkout -b feature/[component]-[description]
   # Make changes
   git commit -m "feat([component]): [description]"
   git push origin feature/[component]-[description]
   # Create PR to develop
   ```

2. **Release Preparation**
   ```bash
   git checkout -b release/v[X.X]-[name]
   # Update CHANGELOG.md
   # Update version numbers
   # Test thoroughly
   git commit -m "chore: Prepare v[X.X] release"
   # Create PR to main
   ```

3. **Release Finalization**
   ```bash
   # After PR merged to main
   git checkout main
   git pull
   git tag -a [component]-v[X.X] -m "Release v[X.X]"
   git push origin [component]-v[X.X]
   # Create GitHub release
   ```

---

## Version File Management

### Recommended Structure

```
/
├── CHANGELOG.md
├── COMPLETE_REVISION_HISTORY.md
├── VERSION
├── docs/
│   ├── releases/
│   │   ├── kernel-v3.3.md
│   │   ├── stage1a-v5.0.md
│   │   └── stage2-v4.1.md
│   └── migration/
│       ├── v4.2-to-v5.0.md
│       └── v3.2-to-v3.3.md
├── kernel/
│   ├── Kernel_Validation_Protocol_v3_3.md
│   └── Kernel_Protocol_Enhancement_v3_3.md
├── stages/
│   ├── Stage_1A_v5_1_Implementation.md
│   ├── Stage_1B_v5_1_Implementation.md
│   └── Stage_2_v4_1_Implementation.md
└── templates/
    ├── Template_Literary_Analysis_MacroMicro.md
    ├── Template_TVODE_MacroMicro.md
    └── Template_Teacher_Key_MacroMicro.md
```

### VERSION File

Create a simple VERSION file in root:

```
KERNEL_VALIDATION_PROTOCOL=3.3
KERNEL_PROTOCOL_ENHANCEMENT=3.3
STAGE_1A=5.1
STAGE_1B=5.1
STAGE_2=4.1
TEMPLATE_LITERARY_ANALYSIS=2.0
TEMPLATE_TVODE=1.0
TEMPLATE_TEACHER_KEY=1.0
```

---

## Release Checklist

### Pre-Release

- [ ] All changes committed and pushed
- [ ] CHANGELOG.md updated
- [ ] Version numbers updated in all files
- [ ] Documentation updated
- [ ] Tests passing (if applicable)
- [ ] Breaking changes clearly documented
- [ ] Migration guide written (if breaking)
- [ ] Dependencies verified

### Release

- [ ] Create git tag
- [ ] Push tag to GitHub
- [ ] Create GitHub release
- [ ] Add release notes
- [ ] Attach relevant files
- [ ] Link related releases
- [ ] Update VERSION file

### Post-Release

- [ ] Notify team/users of release
- [ ] Update project board/issues
- [ ] Deprecate old versions (if applicable)
- [ ] Archive old documentation
- [ ] Create migration issues (if breaking)

---

## Deprecation Policy

### Marking Versions as Deprecated

1. **In CHANGELOG.md:**
   ```markdown
   ### [Stage 1A v4.2] - DEPRECATED
   
   **Deprecated:** 2025-11-15  
   **Superseded by:** v5.0  
   **Reason:** Cannot support macro-focused pedagogy
   ```

2. **In GitHub:**
   - Add `deprecated` label to release
   - Add warning to release notes
   - Create deprecation issue

3. **In Documentation:**
   - Add deprecation warning to file headers
   - Link to replacement version
   - Set removal timeline

### Example Deprecation Notice

```markdown
# ⚠️ DEPRECATED: Stage 1A v4.2

**This version is deprecated as of 2025-11-15.**

**Superseded by:** [Stage 1A v5.0](link)  
**Reason:** Cannot support macro-focused pedagogy  
**Migration:** See [migration guide](link)

This documentation is maintained for historical reference only.
Use [Stage 1A v5.1](link) for new projects.
```

---

## Automation (Optional)

### GitHub Actions for Release

Create `.github/workflows/release.yml`:

```yaml
name: Create Release

on:
  push:
    tags:
      - '*-v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Extract version info
        id: version
        run: |
          TAG=${GITHUB_REF#refs/tags/}
          COMPONENT=${TAG%-v*}
          VERSION=${TAG#*-v}
          echo "component=$COMPONENT" >> $GITHUB_OUTPUT
          echo "version=$VERSION" >> $GITHUB_OUTPUT
      
      - name: Create Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: ${{ steps.version.outputs.component }} v${{ steps.version.outputs.version }}
          body_path: docs/releases/${{ steps.version.outputs.component }}-v${{ steps.version.outputs.version }}.md
          draft: false
          prerelease: false
```

---

## Quick Reference Commands

```bash
# Create and push tag
git tag -a [component]-v[X.X] -m "[Description]"
git push origin [component]-v[X.X]

# List all tags
git tag -l

# Delete tag (if mistake)
git tag -d [component]-v[X.X]
git push origin :refs/tags/[component]-v[X.X]

# View tag details
git show [component]-v[X.X]

# Create release from tag
gh release create [component]-v[X.X] --notes-file docs/releases/[component]-v[X.X].md

# List releases
gh release list
```

---

## Support

For questions about version control or release process:
- Review CHANGELOG.md for version history
- Check COMPLETE_REVISION_HISTORY.md for detailed rationale
- See migration guides in docs/migration/

---

**Last Updated:** 2025-11-17  
**Maintainer:** Project Documentation System
