# Version History Section for README.md

Add this section to your project's main README.md file:

---

## 📋 Version History

This project uses semantic versioning across multiple components. Each component (Kernel, Stage implementations, Templates) has independent version numbers.

### Current Versions

| Component | Version | Status | Release Date |
|-----------|---------|--------|--------------|
| Kernel Validation Protocol | v3.3 | ✅ Stable | 2025-11-14 |
| Kernel Protocol Enhancement | v3.3 | ✅ Stable | 2025-11-14 |
| Stage 1A Implementation | v5.1 | ✅ Stable | 2025-11-15 |
| Stage 1B Implementation | v5.1 | ✅ Stable | 2025-11-15 |
| Stage 2 Implementation | v4.1 | ✅ Stable | 2025-11-15 |
| Templates (MacroMicro) | v2.0 | ✅ Stable | 2025-11-15 |

### Quick Links

- **[CHANGELOG.md](CHANGELOG.md)** - Complete version history with migration guides
- **[Releases](../../releases)** - GitHub releases with downloadable assets
- **[Migration Guides](docs/migration/)** - Step-by-step upgrade instructions

### Major Versions

#### v5.0 Series - Macro-Micro Integration (November 2025)
Complete redesign of Stage implementations to support macro-focused pedagogy. Teaches literary alignment concepts through device analysis.

**Key Changes:**
- Stage 1A: Macro-micro extraction
- Stage 1B: Pedagogical week packages
- Stage 2: 6-step scaffolded worksheets

**Breaking Changes:** Requires complete regeneration of all outputs.

[View v5.0 Release Notes →](releases/v5.0-macro-micro.md)

#### v3.3 - Examples Structure (November 2025)
Added structured examples to kernel output with chapter/page references for automated worksheet generation.

**Key Changes:**
- Freytag section mapping
- Scene identifiers
- Quote snippets

**Compatible with:** All v3.x versions

[View v3.3 Release Notes →](releases/kernel-v3.3.md)

### Recent Updates

See [CHANGELOG.md](CHANGELOG.md) for detailed release notes.

### Deprecated Versions

⚠️ The following versions are deprecated and should not be used for new projects:

- Stage 1A v4.2 → Use v5.1
- Stage 1B v4.2 → Use v5.1  
- Stage 2 v3.2 → Use v4.1

See [migration guides](docs/migration/) for upgrade instructions.

---

## Alternative Compact Version

For a more concise README section:

---

## 📋 Versions

**Current:** Kernel v3.3 | Stage 1A/1B v5.1 | Stage 2 v4.1 | Templates v2.0

- **[CHANGELOG](CHANGELOG.md)** - Full version history
- **[Releases](../../releases)** - Download versions
- **[Docs](docs/)** - Implementation guides

**Latest:** v5.1 (2025-11-15) - Macro-micro integration with 6-step pedagogy

---

## Alternative Table Format

For detailed component tracking:

---

## 📋 Component Versions

### Kernel Protocols

| Component | Current | Previous | Status |
|-----------|---------|----------|--------|
| Validation Protocol | [v3.3](kernel/Kernel_Validation_Protocol_v3_3.md) | v3.2, v3.1, v3.0 | Stable |
| Protocol Enhancement | [v3.3](kernel/Kernel_Protocol_Enhancement_v3_3.md) | v3.2, v3.1 | Stable |

**Latest:** v3.3 (2025-11-14) - Examples structure for worksheet automation

### Stage Implementations

| Stage | Current | Previous | Status |
|-------|---------|----------|--------|
| Stage 1A | [v5.1](stages/Stage_1A_v5_1_Implementation.md) | v5.0, ~~v4.2~~ | Stable |
| Stage 1B | [v5.1](stages/Stage_1B_v5_1_Implementation.md) | v5.0, ~~v4.2~~ | Stable |
| Stage 2 | [v4.1](stages/Stage_2_v4_1_Implementation.md) | v4.0, ~~v3.2~~ | Stable |

**Latest:** v5.1 (2025-11-15) - Chapter chronology and 6-step pedagogy

### Templates

| Template | Current | Previous | Status |
|----------|---------|----------|--------|
| Literary Analysis | [v2.0](templates/Template_Literary_Analysis_MacroMicro.md) | v1.0 | Stable |
| TVODE Construction | [v1.0](templates/Template_TVODE_MacroMicro.md) | - | Stable |
| Teacher Key | [v1.0](templates/Template_Teacher_Key_MacroMicro.md) | - | Stable |

**Latest:** v2.0 (2025-11-15) - 6-step scaffolding integration

### Core Artifacts (Stable - No Versions)

- [Device Taxonomy](artifacts/Artifact_1_Device_Taxonomy.md) - 50+ literary devices
- [Text Tagging Protocol](artifacts/Artifact_2_Text_Tagging_Protocol.md) - Tagging methodology
- [Alignment Algorithm](artifacts/Artifact_3_Alignment_Algorithm.md) - Measurement formulas
- [LEM Theory](theory/LEM_Narrative_Rhetoric_Triangulation.md) - Foundational model

---

## 🔄 Upgrade Paths

```
Current v4.2 → v5.1
├── Stage 1A: Complete regeneration required
├── Stage 1B: Complete regeneration required
└── Stage 2: New templates required

Current v3.2 → v3.3
└── Kernel: Add examples structure (optional, backward compatible)
```

See [CHANGELOG.md](CHANGELOG.md) for detailed migration instructions.

---

## 📚 Documentation

- **[CHANGELOG.md](CHANGELOG.md)** - Detailed version history
- **[Releases](../../releases)** - GitHub releases with notes
- **[Migration Guides](docs/migration/)** - Version upgrade instructions
- **[Implementation Docs](docs/)** - Component specifications

---

## Alternative Badge Style

For visual version indicators:

---

## 📋 Versions

![Kernel](https://img.shields.io/badge/Kernel-v3.3-blue)
![Stage 1A](https://img.shields.io/badge/Stage_1A-v5.1-green)
![Stage 1B](https://img.shields.io/badge/Stage_1B-v5.1-green)
![Stage 2](https://img.shields.io/badge/Stage_2-v4.1-green)
![Templates](https://img.shields.io/badge/Templates-v2.0-green)

- **[View Changelog](CHANGELOG.md)** | **[View Releases](../../releases)** | **[Docs](docs/)**

**Latest Release:** v5.1 (2025-11-15) - Macro-micro integration with 6-step pedagogy

---

## Usage Examples

### In Your README.md

1. **Choose a format** from the templates above
2. **Add after your project description** (before installation/usage)
3. **Update links** to match your repository structure
4. **Add badges** if desired for visual clarity

### Maintaining It

When you release a new version:

1. Update the version table/badges
2. Add a note under "Recent Updates" or "Latest Release"
3. Update "Current" version in relevant sections
4. Move old versions to "Previous" column
5. Add deprecation warnings if needed

### Example Full Section

```markdown
# Literary Experience Model (LEM)

Educational toolkit for teaching literary analysis through narrative-rhetoric alignment.

## 📋 Versions

**Current:** Kernel v3.3 | Stage 1A/1B v5.1 | Stage 2 v4.1

![Kernel](https://img.shields.io/badge/Kernel-v3.3-blue)
![Stages](https://img.shields.io/badge/Stages-v5.1-green)
![Templates](https://img.shields.io/badge/Templates-v2.0-green)

| Component | Version | Release Date | Status |
|-----------|---------|--------------|--------|
| Kernel Validation Protocol | v3.3 | 2025-11-14 | ✅ Stable |
| Stage 1A Implementation | v5.1 | 2025-11-15 | ✅ Stable |
| Stage 1B Implementation | v5.1 | 2025-11-15 | ✅ Stable |
| Stage 2 Implementation | v4.1 | 2025-11-15 | ✅ Stable |

**Latest:** v5.1 (2025-11-15) - Macro-micro integration with 6-step pedagogy

- **[📋 CHANGELOG](CHANGELOG.md)** - Full version history and migration guides
- **[🏷️ Releases](../../releases)** - Download versions with release notes
- **[📚 Documentation](docs/)** - Implementation specifications

### Major Changes in v5.1

- Macro-micro extraction and packaging
- Chapter chronology week ordering
- 6-step pedagogical scaffolding
- Complete worksheet generation system

⚠️ **Breaking Changes:** v5.0+ requires complete regeneration from kernel JSON.

See [migration guide](docs/migration/v4.2-to-v5.1.md) for upgrade instructions.

## Installation

[... rest of your README ...]
```

---

## Tips

1. **Keep it concise** in README - detailed history goes in CHANGELOG.md
2. **Use tables** for easy scanning of current versions
3. **Link to releases** so users can download specific versions
4. **Highlight breaking changes** prominently
5. **Update regularly** when releasing new versions
6. **Use badges** for visual version indicators (optional)
7. **Include migration links** for users on old versions

---

**Template Updated:** 2025-11-17
