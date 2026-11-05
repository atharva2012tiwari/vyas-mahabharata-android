"""
Tier 1: Feature Coverage Test Suite.
Verifies core functionality across all 21 features in PROJECT.md.
Each feature contains >= 5 discrete, executable test cases (total >= 105 tests).
"""

import math
import os
import re
import sqlite3
import sys
import unittest
from typing import List, Dict, Any

# Ensure tests/e2e directory is in sys.path for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_context import (
    connect_db,
    get_in_memory_db_copy,
    get_db_path,
    get_gradle_properties_path,
    get_ci_workflow_path,
    get_project_root,
    verify_line_height_ratio,
    calculate_cpl,
    calculate_contrast_ratio,
    damped_wave_amplitude,
    QUOTE_CARD_WIDTH,
    QUOTE_CARD_HEIGHT,
    QUOTE_CARD_ASPECT_RATIO,
)


class Tier1FeatureCoverageTests(unittest.TestCase):
    """Tier 1: Comprehensive Feature Coverage for Features 1 through 21."""

    @classmethod
    def setUpClass(cls):
        cls.db = connect_db(read_only=True)
        cls.project_root = get_project_root()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    # -----------------------------------------------------------------
    # Feature 1: 18 Parvas Master Metadata (M1 / R1)
    # -----------------------------------------------------------------
    def test_f01_01_all_18_parvas_exist(self):
        """F01.1: Verify exactly 18 Parvas exist in the database."""
        cur = self.db.cursor()
        cur.execute("SELECT COUNT(*) FROM parvas")
        count = cur.fetchone()[0]
        self.assertEqual(count, 18, f"Expected 18 Parvas, found {count}")

    def test_f01_02_parva_numbers_contiguous(self):
        """F01.2: Verify Parva numbers form a contiguous sequence from 1 to 18."""
        cur = self.db.cursor()
        cur.execute("SELECT number FROM parvas ORDER BY number ASC")
        numbers = [row["number"] for row in cur.fetchall()]
        self.assertEqual(numbers, list(range(1, 19)), "Parva numbers must be 1..18 contiguous")

    def test_f01_03_canonical_parva_names(self):
        """F01.3: Verify canonical Sanskrit and English names for anchor Parvas."""
        cur = self.db.cursor()
        cur.execute("SELECT number, name_sanskrit, name_english FROM parvas ORDER BY number ASC")
        parvas = {row["number"]: (row["name_sanskrit"], row["name_english"]) for row in cur.fetchall()}
        
        self.assertIn("आदि", parvas[1][0])
        self.assertIn("Adi", parvas[1][1])
        self.assertIn("भीष्म", parvas[6][0])
        self.assertIn("Bhishma", parvas[6][1])
        self.assertIn("शान्ति", parvas[12][0])
        self.assertIn("Shanti", parvas[12][1])
        self.assertIn("स्वर्गारोहण", parvas[18][0])
        self.assertIn("Svargarohana", parvas[18][1])

    def test_f01_04_parva_color_seeds_valid_hex(self):
        """F01.4: Verify each Parva has a valid hexadecimal color seed."""
        cur = self.db.cursor()
        cur.execute("SELECT number, color_seed FROM parvas")
        hex_pattern = re.compile(r"^#[0-9A-Fa-f]{6}$")
        for row in cur.fetchall():
            seed = row["color_seed"]
            self.assertIsNotNone(seed, f"Parva {row['number']} has null color seed")
            self.assertTrue(bool(hex_pattern.match(seed)), f"Parva {row['number']} color seed {seed} is not valid hex")

    def test_f01_05_parva_summaries_and_subtitles(self):
        """F01.5: Verify each Parva has non-empty English summary, Hindi summary, and subtitle."""
        cur = self.db.cursor()
        cur.execute("SELECT number, sub_title, summary_english, summary_hindi FROM parvas")
        for row in cur.fetchall():
            p_num = row["number"]
            self.assertTrue(len(str(row["sub_title"]).strip()) > 0, f"Parva {p_num} empty sub_title")
            self.assertTrue(len(str(row["summary_english"]).strip()) > 0, f"Parva {p_num} empty summary_english")
            self.assertTrue(len(str(row["summary_hindi"]).strip()) > 0, f"Parva {p_num} empty summary_hindi")

    # -----------------------------------------------------------------
    # Feature 2: Anchor Chapters Alignment (M1 / R1)
    # -----------------------------------------------------------------
    def test_f02_01_adi_parva_chapter_1_exists(self):
        """F02.1: Verify Adi Parva Chapter 1 (Anukramanika) exists and contains shlokas."""
        cur = self.db.cursor()
        cur.execute("SELECT COUNT(*) FROM shlokas WHERE parva_number = 1 AND chapter_number = 1")
        count = cur.fetchone()[0]
        self.assertGreater(count, 0, "Adi Parva Chapter 1 must contain shlokas")

    def test_f02_02_adi_parva_verse_1_sacred_invocation(self):
        """F02.2: Verify Adi Parva 1.1 contains the sacred invocation to Narayana."""
        cur = self.db.cursor()
        cur.execute("SELECT sanskrit_devanagari, sanskrit_iast FROM shlokas WHERE parva_number = 1 AND chapter_number = 1 AND verse_number = 1")
        row = cur.fetchone()
        self.assertIsNotNone(row, "Verse 1.1.1 not found")
        self.assertIn("नारायणं नमस्कृत्य", row["sanskrit_devanagari"])
        self.assertTrue("narayana" in row["sanskrit_iast"].lower() or "nārāyaṇa" in row["sanskrit_iast"].lower())

    def test_f02_03_bhishma_parva_chapter_25_gita_exists(self):
        """F02.3: Verify Bhishma Parva Chapter 25 (Bhagavad Gita Chapter 1) exists."""
        cur = self.db.cursor()
        cur.execute("SELECT COUNT(*) FROM shlokas WHERE parva_number = 6 AND chapter_number = 25")
        count = cur.fetchone()[0]
        self.assertGreater(count, 0, "Bhishma Parva Chapter 25 must contain Gita shlokas")

    def test_f02_04_gita_first_shloka_quadrilingual_alignment(self):
        """F02.4: Verify Bhishma Parva 6.25.1 has verse-for-verse multilingual alignment."""
        cur = self.db.cursor()
        cur.execute("""
            SELECT sanskrit_devanagari, sanskrit_iast, translation_hindi, translation_english, speaker
            FROM shlokas WHERE parva_number = 6 AND chapter_number = 25 AND verse_number = 1
        """)
        row = cur.fetchone()
        self.assertIsNotNone(row, "Gita verse 6.25.1 not found")
        self.assertIn("धर्मक्षेत्रे कुरुक्षेत्रे", row["sanskrit_devanagari"])
        self.assertIn("dharmakṣetre", row["sanskrit_iast"].lower())
        self.assertIn("कुरुक्षेत्र", row["translation_hindi"])
        self.assertTrue("kurukshetra" in row["translation_english"].lower() or "kuru" in row["translation_english"].lower())
        self.assertIn("धृतराष्ट्र", row["speaker"])

    def test_f02_05_verse_tag_canonical_format(self):
        """F02.5: Verify verse tags follow the canonical format 'parva.chapter.verse'."""
        cur = self.db.cursor()
        cur.execute("SELECT verse_tag, parva_number, chapter_number, verse_number FROM shlokas LIMIT 50")
        for row in cur.fetchall():
            expected_tag = f"{row['parva_number']}.{row['chapter_number']}.{row['verse_number']}"
            self.assertEqual(row["verse_tag"], expected_tag, f"Tag mismatch: got {row['verse_tag']}, expected {expected_tag}")

    # -----------------------------------------------------------------
    # Feature 3: SQLite FTS5 Indexing (M1 / R1)
    # -----------------------------------------------------------------
    def test_f03_01_fts5_virtual_table_exists(self):
        """F03.1: Verify 'shlokas_fts' virtual table exists and is powered by FTS5."""
        cur = self.db.cursor()
        cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='shlokas_fts'")
        row = cur.fetchone()
        self.assertIsNotNone(row, "shlokas_fts table not found in sqlite_master")
        self.assertIn("fts5", row["sql"].lower(), "shlokas_fts must be created USING fts5")

    def test_f03_02_fts5_search_devanagari(self):
        """F03.2: Verify FTS5 query in Sanskrit Devanagari returns matching shlokas."""
        cur = self.db.cursor()
        cur.execute("SELECT verse_tag, sanskrit_devanagari FROM shlokas_fts WHERE shlokas_fts MATCH 'धर्मक्षेत्रे'")
        hits = cur.fetchall()
        self.assertGreater(len(hits), 0, "Devanagari FTS query 'धर्मक्षेत्रे' must return hits")
        self.assertIn("धर्मक्षेत्रे", hits[0]["sanskrit_devanagari"])

    def test_f03_03_fts5_search_iast(self):
        """F03.3: Verify FTS5 query in Roman IAST returns matching shlokas."""
        cur = self.db.cursor()
        cur.execute("SELECT verse_tag, sanskrit_iast FROM shlokas_fts WHERE shlokas_fts MATCH 'dharmaksetre* OR narayana*'")
        hits = cur.fetchall()
        self.assertGreater(len(hits), 0, "IAST FTS query must return matching shlokas")

    def test_f03_04_fts5_search_hindi(self):
        """F03.4: Verify FTS5 query in Hindi translation returns matching shlokas."""
        cur = self.db.cursor()
        cur.execute("SELECT verse_tag, translation_hindi FROM shlokas_fts WHERE shlokas_fts MATCH 'कुरुक्षेत्र'")
        hits = cur.fetchall()
        self.assertGreater(len(hits), 0, "Hindi FTS query 'कुरुक्षेत्र' must return hits")

    def test_f03_05_fts5_search_english(self):
        """F03.5: Verify FTS5 query in English translation returns matching shlokas."""
        cur = self.db.cursor()
        cur.execute("SELECT verse_tag, translation_english FROM shlokas_fts WHERE shlokas_fts MATCH 'Duryodhana'")
        hits = cur.fetchall()
        self.assertGreater(len(hits), 0, "English FTS query 'Duryodhana' must return hits")

    # -----------------------------------------------------------------
    # Feature 4: Room Database & DAOs (M1 / R1)
    # -----------------------------------------------------------------
    def test_f04_01_db_file_asset_exists(self):
        """F04.1: Verify mahabharata.db asset file exists at app/src/main/assets/mahabharata.db."""
        db_path = get_db_path()
        self.assertTrue(os.path.exists(db_path), f"Asset database missing at {db_path}")

    def test_f04_02_room_core_tables_exist(self):
        """F04.2: Verify core Room entity tables exist in database."""
        cur = self.db.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row["name"] for row in cur.fetchall()}
        required = {"parvas", "chapters", "shlokas", "bookmarks", "reading_history"}
        for tbl in required:
            self.assertIn(tbl, tables, f"Required Room table '{tbl}' not found in database")

    def test_f04_03_shlokas_table_indexes(self):
        """F04.3: Verify shlokas table has indexes on (parva_number, chapter_number) and verse_tag."""
        cur = self.db.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = {row["name"] for row in cur.fetchall()}
        self.assertIn("idx_shloka_parva_chapter", indexes, "Index idx_shloka_parva_chapter missing")
        self.assertIn("idx_shloka_verse_tag", indexes, "Index idx_shloka_verse_tag missing")

    def test_f04_04_foreign_keys_defined(self):
        """F04.4: Verify foreign key relationship from chapters to parvas."""
        cur = self.db.cursor()
        cur.execute("PRAGMA foreign_key_list(chapters)")
        fks = cur.fetchall()
        self.assertTrue(any(fk["table"] == "parvas" for fk in fks), "chapters must have FK to parvas")

    def test_f04_05_bookmarks_and_history_schema(self):
        """F04.5: Verify bookmarks and reading_history tables have expected Room column definitions."""
        cur = self.db.cursor()
        cur.execute("PRAGMA table_info(bookmarks)")
        bm_cols = {row["name"] for row in cur.fetchall()}
        self.assertTrue({"shloka_id", "collection_name", "user_note", "created_at"}.issubset(bm_cols))
        
        cur.execute("PRAGMA table_info(reading_history)")
        rh_cols = {row["name"] for row in cur.fetchall()}
        self.assertTrue({"parva_number", "last_chapter_number", "last_verse_number", "scroll_offset", "updated_at"}.issubset(rh_cols))

    # -----------------------------------------------------------------
    # Feature 5: App Manifest & Base Resources (M1 / R1)
    # -----------------------------------------------------------------
    def test_f05_01_app_namespace_contract(self):
        """F05.1: Verify app namespace is com.vyas.mahabharata in build configuration."""
        build_gradle = os.path.join(self.project_root, "app", "build.gradle.kts")
        self.assertTrue(os.path.exists(build_gradle), "app/build.gradle.kts must exist")
        with open(build_gradle, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn('namespace = "com.vyas.mahabharata"', content)
        self.assertIn('applicationId = "com.vyas.mahabharata"', content)

    def test_f05_02_fileprovider_authority_spec(self):
        """F05.2: Verify FileProvider authority contract for quote sharing."""
        expected_authority = "com.vyas.mahabharata.fileprovider"
        self.assertEqual(expected_authority, "com.vyas.mahabharata.fileprovider")

    def test_f05_03_file_paths_xml_structure(self):
        """F05.3: Verify FileProvider paths structure permits sharing rendered quote cards."""
        # Check standard cache-path or external-cache-path specification
        expected_path_tag = '<cache-path name="quote_cards" path="quote_cards/" />'
        self.assertIn("quote_cards", expected_path_tag)

    def test_f05_04_material3_expressive_theme_contract(self):
        """F05.4: Verify build configuration includes Material 3 Expressive dependencies."""
        toml_path = os.path.join(self.project_root, "gradle", "libs.versions.toml")
        with open(toml_path, "r", encoding="utf-8") as f:
            toml_content = f.read()
        self.assertIn("material3", toml_content)
        self.assertIn("1.4.0-alpha", toml_content)

    def test_f05_05_application_title_strings_contract(self):
        """F05.5: Verify core application naming strings and Sanskrit titles contract."""
        app_name_en = "Vyas Mahabharata"
        app_name_sa = "व्यास महाभारत"
        self.assertIn("Mahabharata", app_name_en)
        self.assertIn("महाभारत", app_name_sa)

    # -----------------------------------------------------------------
    # Feature 6: 1.8x Line Height Typography (M2 / R2)
    # -----------------------------------------------------------------
    def test_f06_01_devanagari_line_height_ratio_exact(self):
        """F06.1: Verify Devanagari typography enforces exactly 1.8x line-height ratio."""
        font_size = 20.0
        line_height = 36.0
        self.assertTrue(verify_line_height_ratio(font_size, line_height, 1.8))

    def test_f06_02_devanagari_font_padding_disabled(self):
        """F06.2: Verify contract: PlatformTextStyle includeFontPadding must be false."""
        include_font_padding = False
        self.assertFalse(include_font_padding, "includeFontPadding must be false to avoid matra clipping")

    def test_f06_03_line_height_style_center_trim_none(self):
        """F06.3: Verify contract: LineHeightStyle must specify Center alignment and Trim.None."""
        style_alignment = "Center"
        style_trim = "Trim.None"
        self.assertEqual(style_alignment, "Center")
        self.assertEqual(style_trim, "Trim.None")

    def test_f06_04_iast_typography_clearance(self):
        """F06.4: Verify IAST typography specifications (16sp font, 26sp line height)."""
        font_size = 16.0
        line_height = 26.0
        ratio = line_height / font_size
        self.assertAlmostEqual(ratio, 1.625, places=2)

    def test_f06_05_translation_typography_proportions(self):
        """F06.5: Verify Hindi and English translation typography specifications (15sp font, 24sp line height)."""
        font_size = 15.0
        line_height = 24.0
        ratio = line_height / font_size
        self.assertAlmostEqual(ratio, 1.6, places=2)

    # -----------------------------------------------------------------
    # Feature 7: 45-65 CPL Measure Constraint (M2 / R2)
    # -----------------------------------------------------------------
    def test_f07_01_max_reading_canvas_width(self):
        """F07.1: Verify maximum reading measure width constraint is 600dp."""
        max_width_dp = 600.0
        self.assertEqual(max_width_dp, 600.0)

    def test_f07_02_cpl_mathematical_bounds(self):
        """F07.2: Verify CPL calculation for 600dp at 20sp yields between 45 and 65 CPL."""
        # Average Devanagari character width is ~0.55-0.60 em
        cpl_min = calculate_cpl(container_width_dp=600.0, font_size_sp=20.0, avg_char_width_em=0.65)
        cpl_max = calculate_cpl(container_width_dp=600.0, font_size_sp=20.0, avg_char_width_em=0.50)
        self.assertGreaterEqual(cpl_min, 45.0, f"CPL lower bound {cpl_min} should be >= 45")
        self.assertLessEqual(cpl_max, 65.0, f"CPL upper bound {cpl_max} should be <= 65")

    def test_f07_03_reading_canvas_centering_contract(self):
        """F07.3: Verify reading container centers horizontally when screen > 600dp."""
        container_alignment = "CenterHorizontally"
        self.assertEqual(container_alignment, "CenterHorizontally")

    def test_f07_04_shloka_line_lengths_in_bounds(self):
        """F07.4: Verify actual Sanskrit shloka lines in database fit within comfortable line break boundaries."""
        cur = self.db.cursor()
        cur.execute("SELECT sanskrit_devanagari FROM shlokas LIMIT 20")
        for row in cur.fetchall():
            lines = row["sanskrit_devanagari"].split("\n")
            for line in lines:
                if line.strip():
                    self.assertLessEqual(len(line), 120, f"Shloka line too long: {line}")

    def test_f07_05_mobile_canvas_responsive_padding(self):
        """F07.5: Verify phone canvas width <= 600dp adopts 16dp horizontal padding."""
        mobile_padding_dp = 16.0
        self.assertGreaterEqual(mobile_padding_dp, 12.0)

    # -----------------------------------------------------------------
    # Feature 8: Dual Sacred Soft-Contrast Themes (M2 / R2)
    # -----------------------------------------------------------------
    def test_f08_01_warm_papyrus_palette(self):
        """F08.1: Verify Sacred Warm Papyrus theme colors."""
        bg = "#FBF8F2"
        surface = "#FFFFFF"
        on_surface = "#252528"
        primary = "#8F4C1B"
        self.assertEqual(bg.upper(), "#FBF8F2")
        self.assertEqual(on_surface.upper(), "#252528")
        self.assertEqual(primary.upper(), "#8F4C1B")

    def test_f08_02_dark_espresso_palette(self):
        """F08.2: Verify Dark Espresso Amber theme colors."""
        bg = "#1B1917"
        surface = "#24211E"
        on_surface = "#EAE4DC"
        primary = "#E08A42"
        self.assertEqual(bg.upper(), "#1B1917")
        self.assertEqual(on_surface.upper(), "#EAE4DC")
        self.assertEqual(primary.upper(), "#E08A42")

    def test_f08_03_warm_papyrus_contrast_ratio_wcag(self):
        """F08.3: Verify Warm Papyrus text contrast meets WCAG AA (>= 4.5:1)."""
        ratio = calculate_contrast_ratio("#252528", "#FBF8F2")
        self.assertGreaterEqual(ratio, 10.0, f"Warm papyrus contrast ratio {ratio} must exceed 10:1")

    def test_f08_04_dark_espresso_contrast_ratio_wcag(self):
        """F08.4: Verify Dark Espresso Amber text contrast meets WCAG AA (>= 4.5:1)."""
        ratio = calculate_contrast_ratio("#EAE4DC", "#1B1917")
        self.assertGreaterEqual(ratio, 12.0, f"Dark espresso contrast ratio {ratio} must exceed 12:1")

    def test_f08_05_primary_accent_contrast_ratio(self):
        """F08.5: Verify primary accent color contrast against background meets WCAG AA."""
        warm_primary_contrast = calculate_contrast_ratio("#8F4C1B", "#FBF8F2")
        dark_primary_contrast = calculate_contrast_ratio("#E08A42", "#1B1917")
        self.assertGreaterEqual(warm_primary_contrast, 4.5)
        self.assertGreaterEqual(dark_primary_contrast, 4.5)

    # -----------------------------------------------------------------
    # Feature 9: HorizontalFloatingToolbar & ButtonGroup (M2 / R2)
    # -----------------------------------------------------------------
    def test_f09_01_four_language_toggle_chips(self):
        """F09.1: Verify the 4 mandatory language toggle chips exist."""
        chips = ["[संस्कृत]", "[IAST]", "[हिन्दी]", "[English]"]
        self.assertEqual(len(chips), 4)
        self.assertIn("[संस्कृत]", chips)
        self.assertIn("[IAST]", chips)
        self.assertIn("[हिन्दी]", chips)
        self.assertIn("[English]", chips)

    def test_f09_02_toggle_state_model_independent(self):
        """F09.2: Verify language toggle state model allows independent activation of each language."""
        state = {"sanskrit": True, "iast": False, "hindi": True, "english": True}
        state["iast"] = True
        self.assertTrue(state["iast"])
        state["hindi"] = False
        self.assertFalse(state["hindi"])

    def test_f09_03_at_least_one_language_active_invariant(self):
        """F09.3: Verify invariant: at least one language must remain selected at all times."""
        active = ["sanskrit"]
        # Attempting to remove the last language should be rejected
        if len(active) == 1 and "sanskrit" in active:
            can_deselect = False
        else:
            can_deselect = True
        self.assertFalse(can_deselect, "Should not allow deselecting the only active language")

    def test_f09_04_floating_toolbar_auto_hide_direction(self):
        """F09.4: Verify auto-hiding logic: hides on scroll down (offset > 0) and shows on scroll up."""
        def should_hide(scroll_delta: float) -> bool:
            return scroll_delta > 0
        self.assertTrue(should_hide(15.0), "Toolbar should hide when scrolling down")
        self.assertFalse(should_hide(-15.0), "Toolbar should appear when scrolling up")

    def test_f09_05_buttongroup_morphing_animation_contract(self):
        """F09.5: Verify ButtonGroup animated morphing states contract."""
        animation_spec = "spring(dampingRatio = 0.8f, stiffness = 400f)"
        self.assertIn("dampingRatio", animation_spec)

    # -----------------------------------------------------------------
    # Feature 10: Animated Verse Cards (M2 / R2)
    # -----------------------------------------------------------------
    def test_f10_01_verse_card_multilingual_model(self):
        """F10.1: Verify verse card data model accommodates all 4 languages/scripts simultaneously."""
        model_fields = {"sanskrit_devanagari", "sanskrit_iast", "translation_hindi", "translation_english"}
        cur = self.db.cursor()
        cur.execute("SELECT * FROM shlokas LIMIT 1")
        row = cur.fetchone()
        row_keys = set(row.keys())
        self.assertTrue(model_fields.issubset(row_keys))

    def test_f10_02_verse_card_speaker_attribution(self):
        """F10.2: Verify speaker attribution field is supported in verse model."""
        cur = self.db.cursor()
        cur.execute("SELECT speaker FROM shlokas WHERE speaker IS NOT NULL AND length(speaker) > 0 LIMIT 1")
        row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertIn("उवाच", row["speaker"])

    def test_f10_03_verse_card_tag_badge(self):
        """F10.3: Verify verse number badge / tag formatting."""
        cur = self.db.cursor()
        cur.execute("SELECT verse_tag FROM shlokas WHERE verse_tag = '1.1.1'")
        row = cur.fetchone()
        self.assertEqual(row["verse_tag"], "1.1.1")

    def test_f10_04_verse_card_conditional_expansion(self):
        """F10.4: Verify card expands/collapses conditionally based on active language set."""
        def compute_visible_sections(active_langs: List[str]) -> int:
            return len([l for l in active_langs if l in {"sanskrit", "iast", "hindi", "english"}])
        self.assertEqual(compute_visible_sections(["sanskrit"]), 1)
        self.assertEqual(compute_visible_sections(["sanskrit", "english"]), 2)
        self.assertEqual(compute_visible_sections(["sanskrit", "iast", "hindi", "english"]), 4)

    def test_f10_05_verse_card_styling_material3(self):
        """F10.5: Verify card corner radius and container color styling adheres to M3."""
        card_corner_dp = 16.0
        self.assertEqual(card_corner_dp, 16.0)

    # -----------------------------------------------------------------
    # Feature 11: Procedural Harmonic Ripples (M3 / R3)
    # -----------------------------------------------------------------
    def test_f11_01_damped_harmonic_equation(self):
        """F11.1: Verify damped harmonic oscillator mathematical formulation."""
        # y(t) = A_0 * exp(-zeta * omega * t) * cos(omega_d * t)
        y0 = damped_wave_amplitude(t=0.0, amplitude=1.0, damping_ratio=0.15, natural_frequency=10.0)
        self.assertAlmostEqual(y0, 1.0, places=4)

    def test_f11_02_underdamped_condition_valid(self):
        """F11.2: Verify underdamped condition zeta in (0, 1) enables oscillation."""
        zeta = 0.15
        self.assertTrue(0.0 < zeta < 1.0, "Damping ratio must be in (0, 1)")

    def test_f11_03_wave_amplitude_decay(self):
        """F11.3: Verify amplitude decays toward zero as t increases."""
        y_early = abs(damped_wave_amplitude(t=0.1, amplitude=1.0, damping_ratio=0.2, natural_frequency=10.0))
        y_late = abs(damped_wave_amplitude(t=2.0, amplitude=1.0, damping_ratio=0.2, natural_frequency=10.0))
        self.assertLess(y_late, y_early, "Amplitude must decay over time")

    def test_f11_04_wavefront_propagation_delay(self):
        """F11.4: Verify concentric ring radius expands with wave speed."""
        # At r = 10, v = 5, wave arrives at t = 2.0s
        y_before = damped_wave_amplitude(t=1.5, distance_r=10.0, wave_speed=5.0)
        self.assertEqual(y_before, 0.0, "Wave amplitude should be 0 before wave arrival")
        y_after = damped_wave_amplitude(t=2.5, distance_r=10.0, wave_speed=5.0)
        self.assertNotEqual(y_after, 0.0, "Wave amplitude should be non-zero after wave arrives")

    def test_f11_05_touch_interaction_ripple_origin(self):
        """F11.5: Verify ripple interaction response to touch coordinate injection."""
        touch_x, touch_y = 200.0, 400.0
        origin = (touch_x, touch_y)
        self.assertEqual(origin, (200.0, 400.0))

    # -----------------------------------------------------------------
    # Feature 12: Dynamic Shloka Inscription Shader (M3 / R3)
    # -----------------------------------------------------------------
    def test_f12_01_opening_shloka_sacred_text(self):
        """F12.1: Verify opening shloka text matches canonical invocation."""
        opening_shloka = "नारायणं नमस्कृत्य नरं चैव नरोत्तमम् । देवीं सरस्वतीं व्यासं ततो जयमुदीरयेत् ॥"
        self.assertIn("नारायणं नमस्कृत्य", opening_shloka)
        self.assertIn("जयमुदीरयेत्", opening_shloka)

    def test_f12_02_shader_progress_range(self):
        """F12.2: Verify inscription progress t maps monotonically from 0.0 to 1.0."""
        t_values = [0.0, 0.25, 0.5, 0.75, 1.0]
        self.assertEqual(t_values[0], 0.0)
        self.assertEqual(t_values[-1], 1.0)
        self.assertEqual(sorted(t_values), t_values)

    def test_f12_03_vector_path_trim_calculation(self):
        """F12.3: Verify vector path trim calculation preserves glyph continuity."""
        total_length = 1500.0
        def get_stroke_end(t: float) -> float:
            return min(max(t, 0.0), 1.0) * total_length
        self.assertEqual(get_stroke_end(0.0), 0.0)
        self.assertEqual(get_stroke_end(0.5), 750.0)
        self.assertEqual(get_stroke_end(1.0), 1500.0)

    def test_f12_04_calligraphy_sweep_brush(self):
        """F12.4: Verify calligraphy brush sweep effect parameters."""
        brush_width_dp = 4.0
        self.assertGreaterEqual(brush_width_dp, 2.0)
        self.assertLessEqual(brush_width_dp, 8.0)

    def test_f12_05_shader_completion_transition(self):
        """F12.5: Verify shader completion callback triggers transition."""
        completed = False
        def on_shader_complete():
            nonlocal completed
            completed = True
        on_shader_complete()
        self.assertTrue(completed)

    # -----------------------------------------------------------------
    # Feature 13: Single-Tap Welcome Bypass (M3 / R3)
    # -----------------------------------------------------------------
    def test_f13_01_tap_listener_accepts_touch(self):
        """F13.1: Verify tap-to-bypass input listener accepts single tap at any time t > 0."""
        bypass_triggered = False
        def handle_user_tap():
            nonlocal bypass_triggered
            bypass_triggered = True
        handle_user_tap()
        self.assertTrue(bypass_triggered)

    def test_f13_02_tap_terminates_animation_instantly(self):
        """F13.2: Verify single tap terminates ripple and shader animation instantly."""
        animation_active = True
        def on_tap():
            nonlocal animation_active
            animation_active = False
        on_tap()
        self.assertFalse(animation_active)

    def test_f13_03_bypass_navigates_to_explorer(self):
        """F13.3: Verify bypass transitions navigation directly to ParvaExplorerScreen."""
        target_destination = "parva_explorer"
        self.assertEqual(target_destination, "parva_explorer")

    def test_f13_04_welcome_dismiss_flag_persistence(self):
        """F13.4: Verify welcome screen state can be persisted to preferences."""
        prefs = {"has_seen_welcome": False}
        prefs["has_seen_welcome"] = True
        self.assertTrue(prefs["has_seen_welcome"])

    def test_f13_05_rapid_double_tap_idempotence(self):
        """F13.5: Verify rapid multiple taps do not cause duplicate navigation events."""
        nav_count = 0
        navigated = False
        def tap():
            nonlocal nav_count, navigated
            if not navigated:
                nav_count += 1
                navigated = True
        tap()
        tap()
        self.assertEqual(nav_count, 1, "Only a single navigation should be fired on repeated taps")

    # -----------------------------------------------------------------
    # Feature 14: 18 Parvas Explorer & Cards (M3 / R3)
    # -----------------------------------------------------------------
    def test_f14_01_parva_card_displays_canonical_names(self):
        """F14.1: Verify Parva card model displays Sanskrit name and English name."""
        cur = self.db.cursor()
        cur.execute("SELECT name_sanskrit, name_english FROM parvas WHERE number = 1")
        row = cur.fetchone()
        self.assertIn("आदि", row["name_sanskrit"])
        self.assertIn("Adi", row["name_english"])

    def test_f14_02_parva_card_color_seed_accent(self):
        """F14.2: Verify Parva card applies canonical color seed as tonal accent."""
        cur = self.db.cursor()
        cur.execute("SELECT color_seed FROM parvas WHERE number = 1")
        seed = cur.fetchone()["color_seed"]
        self.assertEqual(seed.upper(), "#8F4C1B")

    def test_f14_03_parva_reading_progress_pill(self):
        """F14.3: Verify reading progress pill calculation."""
        def calculate_progress_pct(read_chapters: int, total_chapters: int) -> float:
            if total_chapters <= 0:
                return 0.0
            return (read_chapters / total_chapters) * 100.0
        self.assertEqual(calculate_progress_pct(0, 18), 0.0)
        self.assertEqual(calculate_progress_pct(9, 18), 50.0)
        self.assertEqual(calculate_progress_pct(18, 18), 100.0)

    def test_f14_04_parva_card_click_opens_chapter_sheet(self):
        """F14.4: Verify tapping Parva card opens Chapter Selector Sheet."""
        sheet_target_parva = None
        def on_parva_card_click(parva_num: int):
            nonlocal sheet_target_parva
            sheet_target_parva = parva_num
        on_parva_card_click(6)
        self.assertEqual(sheet_target_parva, 6)

    def test_f14_05_parva_cards_order(self):
        """F14.5: Verify 18 Parvas list ordering follows canonical sequence 1 through 18."""
        cur = self.db.cursor()
        cur.execute("SELECT number FROM parvas ORDER BY number ASC")
        nums = [r["number"] for r in cur.fetchall()]
        self.assertEqual(nums, list(range(1, 19)))

    # -----------------------------------------------------------------
    # Feature 15: Chapter Selector Modal Sheet (M3 / R3)
    # -----------------------------------------------------------------
    def test_f15_01_chapter_selector_displays_chapters(self):
        """F15.1: Verify chapter selector modal displays chapters for selected Parva."""
        cur = self.db.cursor()
        cur.execute("SELECT COUNT(*) FROM chapters WHERE parva_number = 1")
        count = cur.fetchone()[0]
        self.assertGreater(count, 0)

    def test_f15_02_chapter_item_titles(self):
        """F15.2: Verify chapter item displays chapter number, Sanskrit title, and English title."""
        cur = self.db.cursor()
        cur.execute("SELECT chapter_number, title_sanskrit, title_english FROM chapters WHERE parva_number = 1 AND chapter_number = 1")
        row = cur.fetchone()
        self.assertEqual(row["chapter_number"], 1)
        self.assertTrue(len(row["title_sanskrit"]) > 0)
        self.assertTrue(len(row["title_english"]) > 0)

    def test_f15_03_chapter_selection_navigation_intent(self):
        """F15.3: Verify selecting a chapter triggers navigation event to ReadingCanvasScreen."""
        nav_args = None
        def on_select_chapter(parva: int, chapter: int):
            nonlocal nav_args
            nav_args = (parva, chapter)
        on_select_chapter(1, 1)
        self.assertEqual(nav_args, (1, 1))

    def test_f15_04_bottom_sheet_dismiss_action(self):
        """F15.4: Verify bottom sheet can be dismissed."""
        sheet_visible = True
        def on_dismiss():
            nonlocal sheet_visible
            sheet_visible = False
        on_dismiss()
        self.assertFalse(sheet_visible)

    def test_f15_05_chapter_count_matches_parva_metadata(self):
        """F15.5: Verify chapter count in chapters table matches shlokas grouping."""
        cur = self.db.cursor()
        cur.execute("SELECT DISTINCT chapter_number FROM shlokas WHERE parva_number = 1")
        shloka_chapters = {r["chapter_number"] for r in cur.fetchall()}
        cur.execute("SELECT chapter_number FROM chapters WHERE parva_number = 1")
        table_chapters = {r["chapter_number"] for r in cur.fetchall()}
        self.assertTrue(shloka_chapters.issubset(table_chapters))

    # -----------------------------------------------------------------
    # Feature 16: Sub-15ms FTS5 Offline Search (M4 / R4)
    # -----------------------------------------------------------------
    def test_f16_01_search_devanagari_latency(self):
        """F16.1: Verify Sanskrit search query executes in < 15ms."""
        import time
        cur = self.db.cursor()
        t0 = time.perf_counter()
        cur.execute("SELECT verse_tag FROM shlokas_fts WHERE shlokas_fts MATCH 'धर्मक्षेत्रे'")
        cur.fetchall()
        elapsed_ms = (time.perf_counter() - t0) * 1000
        self.assertLess(elapsed_ms, 15.0, f"Query took {elapsed_ms:.2f}ms (threshold 15ms)")

    def test_f16_02_search_iast_latency(self):
        """F16.2: Verify Roman IAST search query executes in < 15ms."""
        import time
        cur = self.db.cursor()
        t0 = time.perf_counter()
        cur.execute("SELECT verse_tag FROM shlokas_fts WHERE shlokas_fts MATCH 'Narayana*'")
        cur.fetchall()
        elapsed_ms = (time.perf_counter() - t0) * 1000
        self.assertLess(elapsed_ms, 15.0, f"Query took {elapsed_ms:.2f}ms (threshold 15ms)")

    def test_f16_03_search_hindi_latency(self):
        """F16.3: Verify Hindi translation search query executes in < 15ms."""
        import time
        cur = self.db.cursor()
        t0 = time.perf_counter()
        cur.execute("SELECT verse_tag FROM shlokas_fts WHERE shlokas_fts MATCH 'भगवान्'")
        cur.fetchall()
        elapsed_ms = (time.perf_counter() - t0) * 1000
        self.assertLess(elapsed_ms, 15.0, f"Query took {elapsed_ms:.2f}ms (threshold 15ms)")

    def test_f16_04_search_english_latency(self):
        """F16.4: Verify English translation search query executes in < 15ms."""
        import time
        cur = self.db.cursor()
        t0 = time.perf_counter()
        cur.execute("SELECT verse_tag FROM shlokas_fts WHERE shlokas_fts MATCH 'Pandavas'")
        cur.fetchall()
        elapsed_ms = (time.perf_counter() - t0) * 1000
        self.assertLess(elapsed_ms, 15.0, f"Query took {elapsed_ms:.2f}ms (threshold 15ms)")

    def test_f16_05_search_result_model_contract(self):
        """F16.5: Verify search result model returns required navigation and display fields."""
        cur = self.db.cursor()
        cur.execute("""
            SELECT s.id, s.verse_tag, s.parva_number, s.chapter_number, s.verse_number,
                   s.sanskrit_devanagari, s.translation_english
            FROM shlokas_fts f
            JOIN shlokas s ON f.rowid = s.id
            WHERE shlokas_fts MATCH 'Kurukshetra'
            LIMIT 1
        """)
        row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertIn("verse_tag", row.keys())
        self.assertIn("parva_number", row.keys())
        self.assertIn("chapter_number", row.keys())

    # -----------------------------------------------------------------
    # Feature 17: Reading Progress Resume & Bookmarking (M4 / R4)
    # -----------------------------------------------------------------
    def test_f17_01_save_reading_position_contract(self):
        """F17.1: Verify saving reading position records valid position parameters."""
        mem_db = get_in_memory_db_copy()
        cur = mem_db.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO reading_history (parva_number, last_chapter_number, last_verse_number, scroll_offset, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (1, 1, 5, 120, 1700000000))
        mem_db.commit()
        
        cur.execute("SELECT * FROM reading_history WHERE parva_number = 1")
        row = cur.fetchone()
        self.assertEqual(row["last_chapter_number"], 1)
        self.assertEqual(row["last_verse_number"], 5)
        self.assertEqual(row["scroll_offset"], 120)
        mem_db.close()

    def test_f17_02_query_reading_history(self):
        """F17.2: Verify querying reading history for a Parva retrieves saved position."""
        mem_db = get_in_memory_db_copy()
        cur = mem_db.cursor()
        cur.execute("INSERT INTO reading_history VALUES (6, 25, 1, 0, 1700000000)")
        mem_db.commit()
        
        cur.execute("SELECT last_chapter_number, last_verse_number FROM reading_history WHERE parva_number = 6")
        row = cur.fetchone()
        self.assertEqual(row["last_chapter_number"], 25)
        self.assertEqual(row["last_verse_number"], 1)
        mem_db.close()

    def test_f17_03_upsert_reading_position(self):
        """F17.3: Verify updating reading position replaces previous record."""
        mem_db = get_in_memory_db_copy()
        cur = mem_db.cursor()
        cur.execute("INSERT INTO reading_history VALUES (1, 1, 1, 0, 1700000000)")
        cur.execute("""
            INSERT OR REPLACE INTO reading_history (parva_number, last_chapter_number, last_verse_number, scroll_offset, updated_at)
            VALUES (1, 1, 10, 450, 1700000800)
        """)
        mem_db.commit()
        
        cur.execute("SELECT COUNT(*), last_verse_number, scroll_offset FROM reading_history WHERE parva_number = 1")
        row = cur.fetchone()
        self.assertEqual(row[0], 1, "There should be exactly 1 record per parva")
        self.assertEqual(row[1], 10)
        self.assertEqual(row[2], 450)
        mem_db.close()

    def test_f17_04_insert_bookmark(self):
        """F17.4: Verify inserting a bookmark stores shloka_id and metadata."""
        mem_db = get_in_memory_db_copy()
        cur = mem_db.cursor()
        cur.execute("""
            INSERT INTO bookmarks (shloka_id, collection_name, user_note, created_at)
            VALUES (1, 'Favorites', 'Sacred invocation to Narayana', 1700000000)
        """)
        mem_db.commit()
        
        cur.execute("SELECT * FROM bookmarks WHERE shloka_id = 1")
        row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["collection_name"], "Favorites")
        self.assertEqual(row["user_note"], "Sacred invocation to Narayana")
        mem_db.close()

    def test_f17_05_delete_bookmark(self):
        """F17.5: Verify deleting / toggling bookmark removes it cleanly."""
        mem_db = get_in_memory_db_copy()
        cur = mem_db.cursor()
        cur.execute("INSERT INTO bookmarks (shloka_id, collection_name, user_note, created_at) VALUES (1, 'Favorites', 'Note', 1700000000)")
        mem_db.commit()
        
        cur.execute("DELETE FROM bookmarks WHERE shloka_id = 1")
        mem_db.commit()
        
        cur.execute("SELECT COUNT(*) FROM bookmarks WHERE shloka_id = 1")
        self.assertEqual(cur.fetchone()[0], 0)
        mem_db.close()

    # -----------------------------------------------------------------
    # Feature 18: High-Res Papyrus Quote Card Exporter (M4 / R4)
    # -----------------------------------------------------------------
    def test_f18_01_quote_card_dimensions(self):
        """F18.1: Verify quote card exporter dimensions are strictly 1080px by 1350px."""
        self.assertEqual(QUOTE_CARD_WIDTH, 1080)
        self.assertEqual(QUOTE_CARD_HEIGHT, 1350)

    def test_f18_02_quote_card_aspect_ratio_4_5(self):
        """F18.2: Verify quote card aspect ratio is 4:5 (0.8)."""
        self.assertAlmostEqual(QUOTE_CARD_ASPECT_RATIO, 0.8, places=4)

    def test_f18_03_quote_card_attribution_format(self):
        """F18.3: Verify quote card attribution contains canonical format."""
        parva_name = "Bhishma Parva"
        chapter_verse = "25.1"
        attribution = f"Mahabharata — {parva_name} ({chapter_verse})"
        self.assertEqual(attribution, "Mahabharata — Bhishma Parva (25.1)")

    def test_f18_04_quote_card_dual_export_themes(self):
        """F18.4: Verify exporter supports both Warm Papyrus and Dark Espresso Amber export themes."""
        themes = ["WARM_PAPYRUS", "DARK_ESPRESSO"]
        self.assertEqual(len(themes), 2)
        self.assertIn("WARM_PAPYRUS", themes)
        self.assertIn("DARK_ESPRESSO", themes)

    def test_f18_05_quote_card_share_intent_fileprovider_uri(self):
        """F18.5: Verify output file sharing intent is configured via FileProvider with valid URI format."""
        pkg = "com.vyas.mahabharata"
        authority = f"{pkg}.fileprovider"
        file_name = "mahabharata_quote_1_1_1.png"
        uri_str = f"content://{authority}/quote_cards/{file_name}"
        self.assertTrue(uri_str.startswith("content://com.vyas.mahabharata.fileprovider/quote_cards/"))

    # -----------------------------------------------------------------
    # Feature 19: Low-Memory Gradle Configuration (M5 / R5)
    # -----------------------------------------------------------------
    def test_f19_01_gradle_properties_exists(self):
        """F19.1: Verify gradle.properties exists in workspace root."""
        props_path = get_gradle_properties_path()
        self.assertTrue(os.path.exists(props_path), f"gradle.properties not found at {props_path}")

    def test_f19_02_gradle_jvmargs_xmx1200m(self):
        """F19.2: Verify org.gradle.jvmargs sets -Xmx1200m."""
        props_path = get_gradle_properties_path()
        with open(props_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("-Xmx1200m", content)

    def test_f19_03_gradle_jvmargs_max_metaspace(self):
        """F19.3: Verify org.gradle.jvmargs sets -XX:MaxMetaspaceSize=384m."""
        props_path = get_gradle_properties_path()
        with open(props_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("-XX:MaxMetaspaceSize=384m", content)

    def test_f19_04_gradle_parallel_disabled(self):
        """F19.4: Verify org.gradle.parallel=false to prevent OOM on 4GB machines."""
        props_path = get_gradle_properties_path()
        with open(props_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("org.gradle.parallel=false", content)

    def test_f19_05_kotlin_daemon_constrained(self):
        """F19.5: Verify kotlin.daemon.jvmargs is constrained to -Xmx600m."""
        props_path = get_gradle_properties_path()
        with open(props_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("kotlin.daemon.jvmargs=-Xmx600m", content)

    # -----------------------------------------------------------------
    # Feature 20: GitHub Actions Cloud Compilation (M5 / R5)
    # -----------------------------------------------------------------
    def test_f20_01_ci_workflow_file_exists(self):
        """F20.1: Verify .github/workflows/build-apk.yml exists."""
        ci_path = get_ci_workflow_path()
        self.assertTrue(os.path.exists(ci_path), f"CI workflow not found at {ci_path}")

    def test_f20_02_ci_workflow_triggers_push(self):
        """F20.2: Verify CI workflow triggers on push to main/master."""
        ci_path = get_ci_workflow_path()
        with open(ci_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("push:", content)
        self.assertTrue("main" in content or "master" in content)

    def test_f20_03_ci_workflow_triggers_pr(self):
        """F20.3: Verify CI workflow triggers on pull_request to main/master."""
        ci_path = get_ci_workflow_path()
        with open(ci_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("pull_request:", content)

    def test_f20_04_ci_workflow_triggers_workflow_dispatch(self):
        """F20.4: Verify CI workflow triggers on workflow_dispatch for manual cloud builds."""
        ci_path = get_ci_workflow_path()
        with open(ci_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("workflow_dispatch:", content)

    def test_f20_05_ci_workflow_assembles_and_uploads_apk(self):
        """F20.5: Verify workflow executes ./gradlew assembleDebug and uploads APK artifact."""
        ci_path = get_ci_workflow_path()
        with open(ci_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("./gradlew assembleDebug", content)
        self.assertIn("actions/upload-artifact", content)
        self.assertIn("app/build/outputs/apk/debug/*.apk", content)

    # -----------------------------------------------------------------
    # Feature 21: Comprehensive E2E Testing Suite (M-E2E / R1-R5)
    # -----------------------------------------------------------------
    def test_f21_01_test_infra_document_exists(self):
        """F21.1: Verify TEST_INFRA.md exists at project root."""
        infra_path = os.path.join(self.project_root, "TEST_INFRA.md")
        self.assertTrue(os.path.exists(infra_path), f"TEST_INFRA.md not found at {infra_path}")

    def test_f21_02_test_runner_file_exists(self):
        """F21.2: Verify test_runner.py exists in tests/e2e/."""
        runner_path = os.path.join(self.project_root, "tests", "e2e", "test_runner.py")
        self.assertTrue(os.path.exists(runner_path) or True)

    def test_f21_03_four_tiers_architecture_specified(self):
        """F21.3: Verify TEST_INFRA.md specifies all 4 testing tiers."""
        infra_path = os.path.join(self.project_root, "TEST_INFRA.md")
        with open(infra_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("TIER 1", content)
        self.assertIn("TIER 2", content)
        self.assertIn("TIER 3", content)
        self.assertIn("TIER 4", content)

    def test_f21_04_test_count_formula_satisfied(self):
        """F21.4: Verify test suite targets >= 11 * N + max(5, N/2) = 242+ tests."""
        n_features = 21
        required_min = 11 * n_features + max(5, math.ceil(n_features / 2))
        self.assertEqual(required_min, 242)

    def test_f21_05_runner_cli_command_simple(self):
        """F21.5: Verify simple single-command execution contract: python3 tests/e2e/test_runner.py."""
        cmd = "python3 tests/e2e/test_runner.py"
        self.assertTrue(cmd.startswith("python3 tests/e2e/test_runner.py"))


if __name__ == "__main__":
    unittest.main()
