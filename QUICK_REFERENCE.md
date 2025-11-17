# GitHub Version History - Quick Reference

**Last Updated:** November 17, 2025

---

## ✅ Setup Checklist

### Initial Setup (One-Time)

- [ ] **Add CHANGELOG.md to repository**
  ```bash
  cp CHANGELOG.md /path/to/repo/
  git add CHANGELOG.md
  git commit -m "docs: Add comprehensive changelog"
  git push origin main
  ```

- [ ] **Create docs/releases/ directory**
  ```bash
  mkdir -p docs/releases
  ```

- [ ] **Add release notes files**
  ```bash
  # Copy sample release notes from SAMPLE_RELEASE_NOTES.md
  # Customize for your project
  cp sample-releases/*.md docs/releases/
  git add docs/releases/
  git commit -m "docs: Add release notes"
  ```

- [ ] **Update README.md with version section**
  ```bash
  # Add version table from README_VERSION_SECTION.md
  # Commit changes
  git commit -m "docs: Add version history to README"
  ```

- [ ] **Create VERSION file (optional)**
  ```bash
  echo "KERNEL_VALIDATION_PROTOCOL=3.3" > VERSION
  echo "STAGE_1A=5.1" >> VERSION
  # ... add other components
  git add VERSION
  git commit -m "chore: Add VERSION file"
  ```

---

## 🏷️ Tagging Existing Versions

### Kernel Protocols

```bash
git tag -a kernel-v3.1 -m "Kernel v3.1 - Extract Preparation Protocol"
git tag -a kernel-v3.2 -m "Kernel v3.2 - Terminology Clarification"
git tag -a kernel-v3.3 -m "Kernel v3.3 - Examples Structure" 

git tag -a enhancement-v3.1 -m "Enhancement v3.1 - Device Inventory"
git tag -a enhancement-v3.2 -m "Enhancement v3.2 - Terminology Update"
git tag -a enhancement-v3.3 -m "Enhancement v3.3 - Examples Format"
```

### Stage Implementations

```bash
git tag -a stage1a-v5.0 -m "Stage 1A v5.0 - Macro-Micro Extraction"
git tag -a stage1a-v5.1 -m "Stage 1A v5.1 - Version Alignment"

git tag -a stage1b-v5.0 -m "Stage 1B v5.0 - Macro-Micro Packages"
git tag -a stage1b-v5.1 -m "Stage 1B v5.1 - Chapter Chronology"

git tag -a stage2-v4.0 -m "Stage 2 v4.0 - Macro-Micro Templates"
git tag -a stage2-v4.1 -m "Stage 2 v4.1 - 6-Step Pedagogy"
```

### Templates

```bash
git tag -a templates-v2.0 -m "Templates v2.0 - MacroMicro System"
git tag -a templates-v2.1 -m "Template Updates v2.1 - Location Hints"
```

### Push All Tags

```bash
git push origin --tags
```

---

## 📝 Release Creation Workflow

### For Each Release

#### 1. Update Documentation
```bash
# Update CHANGELOG.md
# Update version numbers in files
# Update README.md version table
git add CHANGELOG.md README.md [version-files]
git commit -m "chore: Prepare [component] v[X.X] release"
git push origin main
```

#### 2. Create Git Tag
```bash
git tag -a [component]-v[X.X] -m "[Component] v[X.X] - [Description]"
git push origin [component]-v[X.X]
```

#### 3. Create GitHub Release
```bash
# Option A: Using GitHub web interface
# 1. Go to: https://github.com/[user]/[repo]/releases/new
# 2. Choose tag: [component]-v[X.X]
# 3. Add title: "[Component] v[X.X] - [Description]"
# 4. Copy release notes from docs/releases/[component]-v[X.X].md
# 5. Publish release

# Option B: Using GitHub CLI
gh release create [component]-v[X.X] \
  --title "[Component] v[X.X] - [Description]" \
  --notes-file docs/releases/[component]-v[X.X].md
```

---

## 🔄 For New Versions Going Forward

### When Creating a New Version

#### Step 1: Make Changes
```bash
git checkout -b feature/[component]-[description]
# Make your changes
git commit -m "feat([component]): [description]"
git push origin feature/[component]-[description]
```

#### Step 2: Update Documentation
```bash
# 1. Add entry to CHANGELOG.md under [Unreleased]
# 2. Update implementation file with version number
# 3. Create release notes in docs/releases/
# 4. Update README.md version table
```

#### Step 3: Release
```bash
# Merge to main
git checkout main
git merge feature/[component]-[description]

# Create tag
git tag -a [component]-v[X.X] -m "[Description]"
git push origin main --tags

# Create GitHub release (see above)
```

---

## 📋 Files Included

### Core Documentation
- ✅ **CHANGELOG.md** - Standard format changelog
- ✅ **COMPLETE_REVISION_HISTORY.md** - Detailed version history
- ✅ **GITHUB_IMPLEMENTATION_GUIDE.md** - Complete setup guide
- ✅ **README_VERSION_SECTION.md** - README templates
- ✅ **SAMPLE_RELEASE_NOTES.md** - Individual release templates

### In Your Repository (After Setup)
```
/
├── CHANGELOG.md ← Standard changelog
├── README.md ← With version section
├── VERSION ← Optional version file
├── docs/
│   ├── releases/
│   │   ├── kernel-v3.3.md
│   │   ├── stage1a-v5.0.md
│   │   ├── stage2-v4.1.md
│   │   └── ... (other releases)
│   └── migration/
│       ├── v4.2-to-v5.1.md
│       └── ... (other migrations)
└── [your implementation files]
```

---

## 🎯 Quick Commands Reference

### View All Tags
```bash
git tag -l
```

### View Specific Tag
```bash
git show [component]-v[X.X]
```

### Delete Tag (If Mistake)
```bash
# Local
git tag -d [component]-v[X.X]

# Remote
git push origin :refs/tags/[component]-v[X.X]
```

### Create Release (GitHub CLI)
```bash
gh release create [component]-v[X.X] \
  --title "[Component] v[X.X]" \
  --notes-file docs/releases/[component]-v[X.X].md \
  [optional: --draft or --prerelease]
```

### List Releases
```bash
gh release list
```

### View Release
```bash
gh release view [component]-v[X.X]
```

---

## 🔍 Version Naming Convention

### Format: `[component]-v[X.X]`

**Components:**
- `kernel` - Kernel Validation Protocol
- `enhancement` - Kernel Protocol Enhancement
- `stage1a` - Stage 1A Implementation
- `stage1b` - Stage 1B Implementation
- `stage2` - Stage 2 Implementation
- `templates` - Template System

**Version Numbers:**
- `X.X` - Major.Minor (e.g., v5.1)
- Major: Breaking changes
- Minor: Non-breaking additions

**Examples:**
- `kernel-v3.3` ✓
- `stage1a-v5.1` ✓
- `templates-v2.0` ✓

---

## ⚠️ Common Mistakes to Avoid

### ❌ Don't
- Use generic version numbers (v1.0, v2.0) without component prefix
- Create tags without annotation messages
- Skip CHANGELOG.md updates
- Forget to push tags (`git push origin --tags`)
- Create releases without release notes

### ✅ Do
- Use component-specific tags (`kernel-v3.3`, not just `v3.3`)
- Write descriptive annotation messages
- Update CHANGELOG.md with each version
- Push tags after creating them
- Include detailed release notes
- Link related releases
- Document breaking changes clearly

---

## 📚 Documentation References

| File | Purpose | When to Use |
|------|---------|-------------|
| CHANGELOG.md | Version history | Every release |
| COMPLETE_REVISION_HISTORY.md | Detailed context | Understanding decisions |
| GITHUB_IMPLEMENTATION_GUIDE.md | Setup instructions | Initial setup, reference |
| README_VERSION_SECTION.md | README templates | Updating project README |
| SAMPLE_RELEASE_NOTES.md | Release note templates | Creating releases |

---

## 🆘 Troubleshooting

### Tag Already Exists
```bash
# Delete and recreate
git tag -d [component]-v[X.X]
git push origin :refs/tags/[component]-v[X.X]
git tag -a [component]-v[X.X] -m "New message"
git push origin [component]-v[X.X]
```

### Wrong Version Number in Files
```bash
# Before creating tag
git add [corrected-files]
git commit --amend
git push origin main

# After creating tag - create new patch version
git tag -a [component]-v[X.X.1] -m "Fix version number"
```

### Forgot to Push Tags
```bash
git push origin --tags
```

### Need to Update Release Notes
```bash
# Using GitHub CLI
gh release edit [component]-v[X.X] --notes-file docs/releases/[component]-v[X.X].md

# Or edit directly on GitHub web interface
```

---

## 📊 Version Status Dashboard

### Current Stable Versions

| Component | Version | Date | Status |
|-----------|---------|------|--------|
| Kernel | v3.3 | 2025-11-14 | ✅ Stable |
| Enhancement | v3.3 | 2025-11-14 | ✅ Stable |
| Stage 1A | v5.1 | 2025-11-15 | ✅ Stable |
| Stage 1B | v5.1 | 2025-11-15 | ✅ Stable |
| Stage 2 | v4.1 | 2025-11-15 | ✅ Stable |
| Templates | v2.0 | 2025-11-15 | ✅ Stable |

### Deprecated Versions

| Component | Version | Deprecated | Superseded By |
|-----------|---------|------------|---------------|
| Stage 1A | v4.2 | 2025-11-15 | v5.1 |
| Stage 1B | v4.2 | 2025-11-15 | v5.1 |
| Stage 2 | v3.2 | 2025-11-14 | v4.1 |

---

## 🎯 Next Steps After Setup

1. ✅ **Verify all tags are pushed**
   ```bash
   git tag -l
   ```

2. ✅ **Check GitHub releases page**
   Visit: `https://github.com/[user]/[repo]/releases`

3. ✅ **Update README with links**
   Add links to CHANGELOG and releases

4. ✅ **Test a workflow**
   Create a test tag and release to verify process

5. ✅ **Document your process**
   Add team-specific notes to this checklist

6. ✅ **Set up automation (optional)**
   Implement GitHub Actions for automated releases

---

## 📞 Support

**Issues?** 
- Check [GITHUB_IMPLEMENTATION_GUIDE.md](GITHUB_IMPLEMENTATION_GUIDE.md)
- Review [CHANGELOG.md](CHANGELOG.md)
- See [COMPLETE_REVISION_HISTORY.md](COMPLETE_REVISION_HISTORY.md)

**Questions about versions?**
- Check version dependencies in COMPLETE_REVISION_HISTORY.md
- Review migration guides for your version path

---

**Quick Reference Version:** 1.0  
**Last Updated:** November 17, 2025

---

## 🚀 Ready to Start?

```bash
# 1. Copy files to your repo
cp CHANGELOG.md /path/to/repo/

# 2. Create releases directory
mkdir -p /path/to/repo/docs/releases

# 3. Add version section to README
# (Use templates from README_VERSION_SECTION.md)

# 4. Create all tags
./create_all_tags.sh  # Or manually using commands above

# 5. Push everything
git push origin main --tags

# 6. Create GitHub releases
# Use GitHub web interface or gh CLI

# Done! 🎉
```
