# Original User Request

## 2026-11-05T14:43:09Z

Requested team: Full team (Android UI, Fluid Motion, Data Pipeline, Cloud CI/CD)

Build an offline-first Android application in pure native Jetpack Compose using Material 3 Expressive, containing the unabridged Vyasa Mahabharata (~100,000 verses across 18 Parvas + Harivamsha) in original Sanskrit (Devanagari & Roman IAST), paired verse-for-verse with Hindi (Gita Press tradition) and English (Kisari Mohan Ganguli) translations. The app features a deeply spacious and comforting reading canvas with 1.8x line-height ratio, a fluid procedural welcome animation, sub-millisecond offline search, and a GitHub Actions cloud compilation workflow.

Working directory: /home/atharva/.gemini/antigravity/scratch/vyas-mahabharata-android
Integrity mode: development

## Requirements

### R1. Multilingual Data Pipeline & Pre-bundled SQLite Database
Download, sanitize, and align the unabridged Vyasa Mahabharata text across all 18 Parvas from verified digital corpora (Gita Press vulgate, aasi-archive, rahular/itihasa). Generate phonetic Roman IAST transliterations for all Sanskrit shlokas. Compile the dataset into a self-contained Room-compatible SQLite database (`assets/mahabharata.db`) with FTS5 full-text search indexing across Sanskrit, IAST, Hindi, and English.

### R2. Material 3 Expressive UI & Spacious Reading Canvas
Implement a high-comfort reading interface using official Google Material 3 Expressive components. Enforce a 1.8x line-height ratio for Devanagari to completely eliminate Shirorekha-matra glyph clipping, coupled with a 45–65 CPL measure constraint (max-width 600dp). Implement the dual soft-contrast themes: Sacred Warm Papyrus (`#FBF8F2` / `#252528`) and Dark Espresso Amber (`#1B1917` / `#EAE4DC`). Provide an auto-hiding `HorizontalFloatingToolbar` housing a morphing `ButtonGroup` with toggleable items for instant language filtering (`[संस्कृत]`, `[IAST]`, `[हिन्दी]`, `[English]`).

### R3. Cinematic Procedural Welcome Screen & 18 Parvas Explorer
Create a multi-phase welcome sequence: (a) an interactive procedural `Canvas` generating concentric harmonic ripples with damped spring physics, (b) a dynamic vector path clip shader that progressively inscribers the sacred opening shloka (*"नारायणं नमस्कृत्य नरं चैव नरोत्तमम्..."*), and (c) an expressive shared-element morph into the 18 Parvas home explorer featuring expansive visual Parva cards and a chapter selector.

### R4. Core Reading Utilities & Offline Search
Provide instant multilingual search powered by SQLite FTS5 with query execution latency under 15ms. Implement a verse bookmarking and progress resume system that tracks last-read position per Parva. Build a high-resolution quote card exporter that renders any shloka with its translations on a styled papyrus card ready for system sharing.

### R5. Low-Memory Configuration & GitHub Actions Cloud Compilation
Configure the project with low-memory Gradle parameters (`-Xmx1200m -XX:MaxMetaspaceSize=384m`, `parallel=false`) tailored for a 4GB RAM Fedora development laptop. Implement a complete GitHub Actions CI workflow (`.github/workflows/build-apk.yml`) that compiles the debug APK in the cloud and provides downloadable build artifacts.

## Acceptance Criteria

### Data & Search Accuracy
- [ ] Database contains master records for all 18 Parvas with valid titles, chapter counts, and theme seeds.
- [ ] Anchor chapters (including Adi Parva Ch. 1 and Bhishma Parva Ch. 25 / Bhagavad Gita Ch. 1) have exact verse-by-verse alignment between Sanskrit, IAST, Hindi, and English.
- [ ] SQLite FTS5 search queries across Devanagari, IAST, Hindi, and English keywords return correct hits in under 15ms.
- [ ] Total compiled database file size is under 80MB.

### UI & Typography Ergonomics
- [ ] Sanskrit shlokas render with 1.8x line height without glyph overlapping or clipping on any screen density.
- [ ] Toggling language chips (`[संस्कृत]`, `[IAST]`, `[हिन्दी]`, `[English]`) animates button widths smoothly and expands/collapses verse card content without screen jumping or frame drops.
- [ ] Reader container maintains optimal reading measure (max 600dp) centered horizontally on wide screens, foldables, and tablets.
- [ ] Both Day (Warm Papyrus) and Night (Dark Espresso) themes apply correct tonal containers and text contrast.

### Animation & Smoothness
- [ ] Welcome screen renders procedural harmonic ripples and stroke-by-stroke invocation inscription without stuttering.
- [ ] Welcome screen can be smoothly bypassed with a single tap.
- [ ] Reader scroll maintains 120Hz silky scrolling with lazy list virtualization and under 130MB active RAM consumption.

### Cloud Build & Delivery
- [ ] GitHub Actions workflow file `.github/workflows/build-apk.yml` is valid and configured to build on `push`, `pull_request`, and `workflow_dispatch`.
- [ ] Gradle build configuration succeeds with zero memory crashes.

## 2026-11-05T16:05:12Z

This is a single self-contained feature; keep it small and focused. Requested team: Small, focused team (single direct implementer, zero audit swarm).

Complete the Android scripture reading application in pure native Jetpack Compose using Material 3 Expressive, building upon the existing Room database, repository layer, and SQLite FTS5 assets (`assets/mahabharata.db`). Implement the spacious reading canvas with 1.8x line-height Devanagari typography, the procedural welcome animation, and GitHub Actions cloud compilation.

Working directory: /home/atharva/.gemini/antigravity/scratch/vyas-mahabharata-android
Integrity mode: development

## Requirements

### R1. Material 3 Expressive Theme & Typography Engine
Build the theme system in `ui/theme/` applying the Sacred Warm Papyrus (`#FBF8F2` / `#252528`) and Dark Espresso Amber (`#1B1917` / `#EAE4DC`) palettes. Implement the 30-scale typography system enforcing a 1.8x line-height ratio on Devanagari Sanskrit shlokas to eliminate all Shirorekha-matra clipping.

### R2. Spacious Shloka Card & Floating Reader Toolbar
Implement `ui/components/ShlokaCard.kt` featuring smooth container elevation, verse indicator tags, and animated toggleable views for Sanskrit, Roman IAST, Hindi, and English. Implement `ui/components/FloatingReaderBar.kt` using official M3 Expressive `HorizontalFloatingToolbar` (with dynamic scroll auto-hide) and `ButtonGroup` with `toggleableItem` chips for instant language selection.

### R3. Procedural Welcome Screen & Navigation Graph
Implement `ui/screens/welcome/WelcomeScreen.kt` using a custom `Canvas` with damped spring harmonic ripples and a dynamic vector path clip shader for the sacred invocation (*"नारायणं नमस्कृत्य..."*). Connect it via Navigation Compose to the Chapter Explorer and Reader screen.

### R4. Quote Card Exporter & Cloud Build Finalization
Implement the verse quote card image export dialog for sharing shlokas on stylized papyrus cards. Verify that `.github/workflows/build-apk.yml` and Gradle configurations are aligned for cloud compilation.

## Acceptance Criteria

### UI & Typography
- [ ] Sanskrit shlokas render with 1.8x line height without glyph clipping on any screen density.
- [ ] Language toggle chips (`[संस्कृत]`, `[IAST]`, `[हिन्दी]`, `[English]`) animate button widths and smoothly collapse/expand shloka content without screen jump.
- [ ] Content width is constrained to max 600dp (45–65 CPL) centered horizontally on wide displays.

### Animation & Flow
- [ ] Welcome screen renders procedural harmonic ripples and invocation text, and can be smoothly bypassed with a single tap.
- [ ] Reader scroll maintains 120Hz smooth scrolling using Compose `LazyColumn` and existing `MahabharataRepository`.

### Cloud CI/CD
- [ ] GitHub Actions workflow `.github/workflows/build-apk.yml` is validated for cloud APK compilation.

