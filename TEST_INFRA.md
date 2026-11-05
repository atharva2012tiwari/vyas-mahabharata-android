# TEST_INFRA.md — E2E Test Suite Architecture & Specification

## 1. Overview & Objectives

This document defines the End-to-End (E2E) testing architecture and execution infrastructure for the **Vyasa Mahabharata Android Application**. 

The testing framework is built as an executable, automated, opaque-box test harness that strictly validates the system against user requirements specified in `ORIGINAL_REQUEST.md` and architectural interfaces documented in `PROJECT.md`. The suite does not rely on transient internal implementation details; instead, it exercises data assets, Room contracts, FTS5 latency, mathematical typography constraints, color contrast ratios, procedural physics simulations, quote export dimensions, and build configurations.

### Key Metrics & Commitments
- **Total Features Covered**: 21 features across Milestones M1 through M5.
- **Tiers**: 4 systematic tiers (Feature Coverage, Boundary & Corner Cases, Cross-Feature Interactions, Real-World Application Scenarios).
- **Target Test Count**: $\ge 11 \times N + \max(5, \lfloor N/2 \rfloor) = 11 \times 21 + 11 = 242+$ tests.
- **Execution Model**: Zero-dependency standalone Python 3 runner (`python3 tests/e2e/test_runner.py`), enabling instantaneous verification on resource-constrained development machines (4GB RAM) as well as continuous integration environments without requiring an Android emulator.

---

## 2. Testing Tiers & Hierarchy

```
+-----------------------------------------------------------------------------------------+
|                               TEST EXECUTION RUNNER                                     |
|                             tests/e2e/test_runner.py                                    |
+-----------------------------------------------------------------------------------------+
      |                           |                          |                          |
      v                           v                          v                          v
+---------------+          +---------------+          +---------------+          +---------------+
|    TIER 1     |          |    TIER 2     |          |    TIER 3     |          |    TIER 4     |
|    Feature    |          |  Boundary &   |          | Cross-Feature |          |  Real-World   |
|   Coverage    |          | Corner Cases  |          | Combinatorial |          | User Scenarios|
| (≥105 tests)  |          | (≥105 tests)  |          |  (≥16 tests)  |          |  (≥16 tests)  |
+---------------+          +---------------+          +---------------+          +---------------+
  F01 - F21                  F01 - F21                  Pairwise matrix            Full user flows
  ≥5 tests/feat              ≥5 tests/feat              Multi-component            E2E journeys
```

### Tier 1: Core Feature Coverage (≥105 tests, ≥5 per feature)
Verifies the fundamental functional contract of each of the 21 features:
- **F01**: 18 Parvas Master Metadata (IDs, canonical Sanskrit/English/Hindi names, order, color seeds).
- **F02**: Anchor Chapters Alignment (verse-by-verse alignment in Adi Parva Ch 1 & Bhishma Parva Ch 25).
- **F03**: SQLite FTS5 Indexing (virtual table existence, 4-language searchability, trigger consistency).
- **F04**: Room Database & DAOs (schema validity, table creation, foreign key constraints, asset delivery).
- **F05**: App Manifest & Base Resources (package name, exported components, FileProvider configuration).
- **F06**: 1.8x Line Height Typography (Devanagari font padding disablement, 1.8x line-height ratio).
- **F07**: 45-65 CPL Measure Constraint (optimal reading width 600dp centering, character-per-line bounds).
- **F08**: Dual Sacred Soft-Contrast Themes (Warm Papyrus `#FBF8F2` & Dark Espresso `#1B1917` palette).
- **F09**: HorizontalFloatingToolbar & ButtonGroup (language toggles `[संस्कृत]`, `[IAST]`, `[हिन्दी]`, `[English]`).
- **F10**: Animated Verse Cards (verse structure, speaker attribution, multi-script card expansion).
- **F11**: Procedural Harmonic Ripples (damped harmonic oscillator model $y(t) = A_0 e^{-\zeta \omega t} \cos(\omega_d t)$).
- **F12**: Dynamic Shloka Inscription Shader (opening shloka vector calligraphy sweep path mathematics).
- **F13**: Single-Tap Welcome Bypass (tap event listener, transition to explorer, skip state).
- **F14**: 18 Parvas Explorer & Cards (card rendering model, progress pills, Parva navigation).
- **F15**: Chapter Selector Modal Sheet (chapter list retrieval, navigation intent to Reader).
- **F16**: Sub-15ms FTS5 Offline Search (FTS query latency benchmarks across 4 languages).
- **F17**: Reading Progress Resume & Bookmarking (per-Parva position persistence, bookmark CRUD).
- **F18**: High-Res Papyrus Quote Card Exporter (1080x1350 4:5 aspect ratio, styling, FileProvider sharing).
- **F19**: Low-Memory Gradle Configuration (`-Xmx1200m -XX:MaxMetaspaceSize=384m`, `parallel=false`).
- **F20**: GitHub Actions Cloud Compilation (triggers: `push`, `pull_request`, `workflow_dispatch`, APK artifact).
- **F21**: Comprehensive E2E Testing Suite (runner capabilities, test discovery, reporting format).

### Tier 2: Boundary, Limit & Corner Cases (≥105 tests, ≥5 per feature)
Stresses the system under extreme, degenerate, and boundary inputs:
- Empty, whitespace-only, and special character queries in FTS5 (`'`, `"`, `*`, `OR`, `NOT`, `AND`).
- Mathematical verification of line-height ratio: $\frac{lineHeight}{fontSize} = 1.8 \pm 0.001$.
- 45–65 CPL bounds on Devanagari verse sample lengths across screen widths.
- Database asset file size ceiling: `file_size < 80 MB`.
- Search query latency threshold: $t_{query} < 15.0 \text{ ms}$ under repeated burst stress.
- WCAG 2.1 AA and AAA contrast ratio verification: $\frac{L_1 + 0.05}{L_2 + 0.05} \ge 4.5$ and $\ge 7.0$.
- Damped oscillator boundary conditions: critical damping $\zeta = 1.0$, underdamped $\zeta \in (0, 1)$, $t = 0$, $t \to \infty$.
- Zero-length bookmarks, note length boundaries, rapid toggle idempotency.
- Extreme chapter / verse navigation bounds (first verse `1.1.1`, last verse of anchor chapter, nonexistent IDs).

### Tier 3: Cross-Feature Interactions & Combinatorial Matrix (≥16 tests)
Validates multi-component interaction and state transitions:
- Toggling language buttons while maintaining reading scroll offset.
- Switching between Warm Papyrus and Dark Espresso themes while exporting a quote card.
- FTS5 search query leading directly to chapter reader navigation with highlight term.
- Reading position update reflected in Parva Explorer progress pill.
- Adding a bookmark on a verse card and querying it from the bookmarks collection.
- Rapid theme switching during procedural welcome animation lifecycle.
- Quote card exporter rendering across all 4 script combinations (Devanagari only, Devanagari+IAST, All 4 languages).

### Tier 4: Real-World End-to-End Application Scenarios (≥16 tests)
Simulates end-to-end user journeys through the application:
1. **Journey 1: First Launch & Reading Genesis** (Welcome screen animation -> tap to bypass -> 18 Parvas Explorer -> Select Adi Parva Ch 1 -> Reader opens with 1.8x line-height Devanagari).
2. **Journey 2: Gita Inquirer** (Search query "धर्मक्षेत्रे" -> FTS5 returns hit in <15ms -> Navigate to Bhishma Parva Ch 25 -> Read Gita verse 1 in Devanagari + Hindi + English).
3. **Journey 3: Multilingual Scholar** (Open chapter -> Enable `[IAST]` and `[English]` toggles -> Disable `[हिन्दी]` -> Verify card content updates smoothly).
4. **Journey 4: Sacred Verse Bookmarking** (Navigate to verse 1.1.1 -> Toggle bookmark with note "Invocation to Narayana" -> Verify bookmark stored -> Retrieve bookmarks list).
5. **Journey 5: Reading Session Resume** (Read Adi Parva Ch 1 to verse 10 -> Background app -> Resume -> Verify last-read position loaded).
6. **Journey 6: High-Res Quote Sharing** (Select Bhishma Parva 25.1 -> Open Quote Export Dialog -> Select Warm Papyrus theme -> Render 1080x1350 card -> Verify FileProvider cache URI).
7. **Journey 7: Cloud CI Delivery** (Verify GitHub Actions workflow trigger, Gradle low-memory parameters, and debug APK artifact output configuration).

---

## 3. Directory Layout

The E2E test suite is located in `tests/e2e/`:

```
tests/e2e/
├── __init__.py
├── test_runner.py                  # Core CLI test runner with tier selection, timing, reporting
├── test_context.py                 # Shared context, DB helper, color math, oscillator models
├── tier1_feature_coverage.py       # Tier 1: Features 1-21 (≥105 test cases)
├── tier2_boundary_corner.py        # Tier 2: Boundaries for Features 1-21 (≥105 test cases)
├── tier3_cross_feature.py          # Tier 3: Pairwise & combinatorial tests (≥16 test cases)
└── tier4_real_world.py             # Tier 4: End-to-end real-world user flows (≥16 test cases)
```

---

## 4. Execution & CLI Options

The test suite is runnable with standard Python 3 (no third-party dependencies required):

```bash
# Run the complete test suite (all tiers)
python3 tests/e2e/test_runner.py

# Run a specific tier
python3 tests/e2e/test_runner.py --tier 1
python3 tests/e2e/test_runner.py --tier 2
python3 tests/e2e/test_runner.py --tier 3
python3 tests/e2e/test_runner.py --tier 4

# Run tests for a specific feature
python3 tests/e2e/test_runner.py --feature 3

# Run with verbose output (prints all test names and timings)
python3 tests/e2e/test_runner.py -v

# Export results to JSON
python3 tests/e2e/test_runner.py --json test_report.json

# Fail fast on first error
python3 tests/e2e/test_runner.py --failfast
```

---

## 5. Authoritative Sources of Truth

All expected outputs are derived from:
1. `ORIGINAL_REQUEST.md`: System requirements R1 to R5 and Acceptance Criteria.
2. `PROJECT.md`: Architecture layers, 21-feature inventory, milestone boundaries, and interface contracts.
3. `app/src/main/assets/mahabharata.db`: Compiled SQLite Room database asset.
4. `gradle.properties`: Low-memory JVM tuning for 4GB RAM environment.
5. `.github/workflows/build-apk.yml`: GitHub Actions cloud compilation pipeline.
6. W3C WCAG 2.1 Specification: Relative luminance and contrast ratio formulas.
7. Classical Damped Harmonic Motion Physics: Second-order differential equation $m\ddot{y} + c\dot{y} + ky = 0$.
