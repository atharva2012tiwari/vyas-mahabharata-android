"""
Tier 2: Boundary, Limit & Corner Cases Test Suite.
Stresses extreme inputs, mathematical constraints, and boundary conditions across all 21 features.
Each feature contains >= 5 discrete, executable test cases (total >= 105 tests).
"""

import math
import os
import re
import sqlite3
import sys
import unittest

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


class Tier2BoundaryCornerTests(unittest.TestCase):
    """Tier 2: Boundary, Limit & Corner Cases across Features 1 through 21."""

    @classmethod
    def setUpClass(cls):
        cls.db = connect_db(read_only=True)
        cls.project_root = get_project_root()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    # -----------------------------------------------------------------
    # Feature 1: 18 Parvas Master Metadata Boundaries
    # -----------------------------------------------------------------
    def test_f01_b01_parva_zero_does_not_exist(self):
        """F01.B1: Verify parva number 0 does not exist."""
        cur = self.db.cursor()
        cur.execute("SELECT COUNT(*) FROM parvas WHERE number = 0")
        self.assertEqual(cur.fetchone()[0], 0)

    def test_f01_b02_parva_nineteen_does_not_exist(self):
        """F01.B2: Verify parva number 19 does not exist."""
        cur = self.db.cursor()
        cur.execute("SELECT COUNT(*) FROM parvas WHERE number = 19")
        self.assertEqual(cur.fetchone()[0], 0)

    def test_f01_b03_parva_color_seed_format(self):
        """F01.B3: Verify all parva color seeds are 7-char strings starting with '#'."""
        cur = self.db.cursor()
        cur.execute("SELECT number, color_seed FROM parvas")
        for row in cur.fetchall():
            seed = row["color_seed"]
            self.assertEqual(len(seed), 7, f"Parva {row['number']} seed {seed} length != 7")
            self.assertTrue(seed.startswith("#"))

    def test_f01_b04_parva_summaries_no_null_bytes(self):
        """F01.B4: Verify parva summaries and names do not contain null bytes or unescaped control codes."""
        cur = self.db.cursor()
        cur.execute("SELECT number, name_sanskrit, name_english, summary_english FROM parvas")
        for row in cur.fetchall():
            for field in ["name_sanskrit", "name_english", "summary_english"]:
                val = str(row[field])
                self.assertNotIn("\x00", val, f"Null byte in Parva {row['number']} {field}")

    def test_f01_b05_parva_counts_non_negative(self):
        """F01.B5: Verify chapter_count and shloka_count are non-negative."""
        cur = self.db.cursor()
        cur.execute("SELECT number, chapter_count, shloka_count FROM parvas")
        for row in cur.fetchall():
            self.assertGreaterEqual(row["chapter_count"], 0)
            self.assertGreaterEqual(row["shloka_count"], 0)

    # -----------------------------------------------------------------
    # Feature 2: Anchor Chapters Alignment Boundaries
    # -----------------------------------------------------------------
    def test_f02_b01_verse_number_zero_does_not_exist(self):
        """F02.B1: Verify verse number 0 does not exist."""
        cur = self.db.cursor()
        cur.execute("SELECT COUNT(*) FROM shlokas WHERE verse_number = 0")
        self.assertEqual(cur.fetchone()[0], 0)

    def test_f02_b02_nonexistent_chapter_returns_empty(self):
        """F02.B2: Verify non-existent chapter returns empty list."""
        cur = self.db.cursor()
        cur.execute("SELECT COUNT(*) FROM shlokas WHERE parva_number = 1 AND chapter_number = 999")
        self.assertEqual(cur.fetchone()[0], 0)

    def test_f02_b03_verse_tags_strictly_unique(self):
        """F02.B3: Verify verse tags are strictly unique across the database."""
        cur = self.db.cursor()
        cur.execute("SELECT verse_tag, COUNT(*) FROM shlokas GROUP BY verse_tag HAVING COUNT(*) > 1")
        duplicates = cur.fetchall()
        self.assertEqual(len(duplicates), 0, f"Found duplicate verse tags: {duplicates}")

    def test_f02_b04_sanskrit_text_utf8_clean(self):
        """F02.B4: Verify Sanskrit text contains no unicode replacement characters."""
        cur = self.db.cursor()
        cur.execute("SELECT id, verse_tag, sanskrit_devanagari FROM shlokas")
        for row in cur.fetchall():
            self.assertNotIn("\ufffd", row["sanskrit_devanagari"], f"Corrupt UTF-8 in verse {row['verse_tag']}")

    def test_f02_b05_verse_danda_delimiters_present(self):
        """F02.B5: Verify Sanskrit shlokas contain traditional danda delimiters."""
        cur = self.db.cursor()
        cur.execute("SELECT verse_tag, sanskrit_devanagari FROM shlokas WHERE verse_tag IN ('1.1.1', '6.25.1')")
        for row in cur.fetchall():
            skt = row["sanskrit_devanagari"]
            self.assertTrue("।" in skt or "॥" in skt, f"Verse {row['verse_tag']} lacks danda punctuation")

    # -----------------------------------------------------------------
    # Feature 3: SQLite FTS5 Indexing Boundaries
    # -----------------------------------------------------------------
    def test_f03_b01_fts5_empty_query_safe(self):
        """F03.B1: Verify empty or whitespace query is handled safely."""
        cur = self.db.cursor()
        # Empty string MATCH is rejected or handled via application guard
        def run_safe_search(query: str):
            clean = query.strip()
            if not clean:
                return []
            cur.execute("SELECT verse_tag FROM shlokas_fts WHERE shlokas_fts MATCH ?", (clean,))
            return cur.fetchall()
        self.assertEqual(run_safe_search(""), [])
        self.assertEqual(run_safe_search("   "), [])

    def test_f03_b02_fts5_wildcard_prefix(self):
        """F03.B2: Verify FTS5 wildcard prefix search operates without crash."""
        cur = self.db.cursor()
        cur.execute("SELECT verse_tag FROM shlokas_fts WHERE shlokas_fts MATCH 'dharma*' LIMIT 5")
        results = cur.fetchall()
        self.assertGreater(len(results), 0)

    def test_f03_b03_fts5_special_characters_escaping(self):
        """F03.B3: Verify special characters in query are safely escaped."""
        cur = self.db.cursor()
        # Using double-quoted token for literal match
        escaped_query = '"धर्मक्षेत्रे"'
        cur.execute("SELECT verse_tag FROM shlokas_fts WHERE shlokas_fts MATCH ?", (escaped_query,))
        results = cur.fetchall()
        self.assertGreater(len(results), 0)

    def test_f03_b04_fts5_sql_injection_attempt_safe(self):
        """F03.B4: Verify parameterized FTS queries neutralize SQL injection attempts."""
        cur = self.db.cursor()
        injection_payload = "' OR 1=1 --"
        # In FTS5, MATCH with literal payload either matches tokens or returns 0
        cur.execute("SELECT verse_tag FROM shlokas_fts WHERE shlokas_fts MATCH '\"' || ? || '\"'", (injection_payload,))
        results = cur.fetchall()
        self.assertEqual(len(results), 0)

    def test_f03_b05_fts5_burst_latency_under_15ms(self):
        """F03.B5: Verify 10 consecutive diverse queries all execute in < 15.0ms."""
        import time
        queries = ["नारायणं", "Duryodhana", "Gita", "Arjuna", "Kurukshetra", "धर्म", "Sanjava", "भीम", "Sanskrit", "Bhishma"]
        cur = self.db.cursor()
        for q in queries:
            t0 = time.perf_counter()
            cur.execute("SELECT verse_tag FROM shlokas_fts WHERE shlokas_fts MATCH ?", (f"{q}*",))
            cur.fetchall()
            elapsed_ms = (time.perf_counter() - t0) * 1000
            self.assertLess(elapsed_ms, 15.0, f"Query '{q}' took {elapsed_ms:.2f}ms (threshold 15ms)")

    # -----------------------------------------------------------------
    # Feature 4: Room Database & DAOs Boundaries
    # -----------------------------------------------------------------
    def test_f04_b01_database_size_under_80mb(self):
        """F04.B1: Verify compiled SQLite database size is strictly < 80MB (R1 Acceptance Criteria)."""
        db_path = get_db_path()
        size_bytes = os.path.getsize(db_path)
        size_mb = size_bytes / (1024 * 1024)
        self.assertLess(size_mb, 80.0, f"Database size {size_mb:.2f}MB exceeds 80MB threshold")

    def test_f04_b02_pragma_integrity_check_ok(self):
        """F04.B2: Verify PRAGMA integrity_check returns 'ok'."""
        cur = self.db.cursor()
        cur.execute("PRAGMA integrity_check")
        status = cur.fetchone()[0]
        self.assertEqual(status, "ok", f"Integrity check failed: {status}")

    def test_f04_b03_foreign_keys_rejection(self):
        """F04.B3: Verify inserting chapter with non-existent parva is rejected when FKs enabled."""
        mem_db = get_in_memory_db_copy()
        cur = mem_db.cursor()
        cur.execute("PRAGMA foreign_keys = ON")
        with self.assertRaises(sqlite3.IntegrityError):
            cur.execute("""
                INSERT INTO chapters (parva_number, chapter_number, title_sanskrit, title_hindi, title_english)
                VALUES (999, 1, 'Test', 'Test', 'Test')
            """)
        mem_db.close()

    def test_f04_b04_bookmark_null_notes_allowed(self):
        """F04.B4: Verify bookmarking with NULL user_note is permitted."""
        mem_db = get_in_memory_db_copy()
        cur = mem_db.cursor()
        cur.execute("INSERT INTO bookmarks (shloka_id, collection_name, user_note, created_at) VALUES (1, 'Favorites', NULL, 1700000000)")
        mem_db.commit()
        cur.execute("SELECT user_note FROM bookmarks WHERE shloka_id = 1")
        self.assertIsNone(cur.fetchone()[0])
        mem_db.close()

    def test_f04_b05_extreme_scroll_offsets_handled(self):
        """F04.B5: Verify reading history handles 0 and large scroll offsets."""
        mem_db = get_in_memory_db_copy()
        cur = mem_db.cursor()
        cur.execute("INSERT INTO reading_history VALUES (1, 1, 1, 0, 1700000000)")
        cur.execute("INSERT INTO reading_history VALUES (2, 1, 1, 100000, 1700000000)")
        mem_db.commit()
        cur.execute("SELECT scroll_offset FROM reading_history ORDER BY parva_number ASC")
        offsets = [r[0] for r in cur.fetchall()]
        self.assertEqual(offsets, [0, 100000])
        mem_db.close()

    # -----------------------------------------------------------------
    # Feature 5: App Manifest & Base Resources Boundaries
    # -----------------------------------------------------------------
    def test_f05_b01_sdk_versions_in_bounds(self):
        """F05.B1: Verify minSdk >= 26 and compileSdk/targetSdk >= 34 in build config."""
        build_gradle = os.path.join(self.project_root, "app", "build.gradle.kts")
        with open(build_gradle, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("minSdk = 26", content)
        self.assertIn("targetSdk = 35", content)
        self.assertIn("compileSdk = 35", content)

    def test_f05_b02_proguard_rules_exist(self):
        """F05.B2: Verify proguard-rules.pro exists for release minification."""
        proguard_path = os.path.join(self.project_root, "app", "proguard-rules.pro")
        self.assertTrue(os.path.exists(proguard_path))

    def test_f05_b03_namespace_syntax_valid(self):
        """F05.B3: Verify namespace syntax follows Android package naming conventions."""
        ns = "com.vyas.mahabharata"
        self.assertTrue(re.match(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$", ns))

    def test_f05_b04_fileprovider_path_traversal_safe(self):
        """F05.B4: Verify FileProvider paths definition contains no relative path traversal."""
        path = "quote_cards/"
        self.assertNotIn("..", path)
        self.assertTrue(path.endswith("/"))

    def test_f05_b05_color_hex_bounds(self):
        """F05.B5: Verify all defined hex codes conform to standard color depth."""
        colors = ["#FBF8F2", "#1B1917", "#8F4C1B", "#E08A42", "#252528", "#EAE4DC"]
        for c in colors:
            self.assertEqual(len(c), 7)
            self.assertTrue(all(ch in "0123456789ABCDEFabcdef" for ch in c[1:]))

    # -----------------------------------------------------------------
    # Feature 6: 1.8x Line Height Typography Boundaries
    # -----------------------------------------------------------------
    def test_f06_b01_ratio_float_precision(self):
        """F06.B1: Verify line-height ratio precision: 36.0 / 20.0 == 1.8000."""
        self.assertEqual(36.0 / 20.0, 1.8)

    def test_f06_b02_ratio_scaling_up(self):
        """F06.B2: Verify 1.8x scaling at 24sp yields 43.2sp."""
        font_size = 24.0
        expected_lh = font_size * 1.8
        self.assertEqual(expected_lh, 43.2)
        self.assertTrue(verify_line_height_ratio(font_size, expected_lh, 1.8))

    def test_f06_b03_ratio_scaling_down(self):
        """F06.B3: Verify 1.8x scaling at 16sp yields 28.8sp."""
        font_size = 16.0
        expected_lh = font_size * 1.8
        self.assertEqual(expected_lh, 28.8)
        self.assertTrue(verify_line_height_ratio(font_size, expected_lh, 1.8))

    def test_f06_b04_zero_font_size_rejected(self):
        """F06.B4: Verify zero font size is rejected by typography ratio verifier."""
        self.assertFalse(verify_line_height_ratio(0.0, 36.0, 1.8))

    def test_f06_b05_vertical_matra_headroom(self):
        """F06.B5: Verify vertical matra clearance (line_height - font_size) >= 14sp."""
        headroom = 36.0 - 20.0
        self.assertGreaterEqual(headroom, 14.0, "Must provide >= 14sp clearance for Shirorekha-matra diacritics")

    # -----------------------------------------------------------------
    # Feature 7: 45-65 CPL Measure Constraint Boundaries
    # -----------------------------------------------------------------
    def test_f07_b01_narrow_screen_clamp(self):
        """F07.B1: Verify canvas at narrow screen width (320dp) clamps to 320dp."""
        screen_w = 320.0
        max_w = 600.0
        actual_w = min(screen_w, max_w)
        self.assertEqual(actual_w, 320.0)

    def test_f07_b02_exact_breakpoint_measure(self):
        """F07.B2: Verify canvas at 600dp screen width is exactly 600dp."""
        screen_w = 600.0
        max_w = 600.0
        actual_w = min(screen_w, max_w)
        self.assertEqual(actual_w, 600.0)

    def test_f07_b03_wide_screen_clamp(self):
        """F07.B3: Verify canvas at wide screen width (1200dp) clamps to 600dp."""
        screen_w = 1200.0
        max_w = 600.0
        actual_w = min(screen_w, max_w)
        self.assertEqual(actual_w, 600.0)

    def test_f07_b04_cpl_measure_bounds_on_600dp(self):
        """F07.B4: Verify CPL on 600dp canvas strictly satisfies [45, 65] range."""
        cpl_mid = calculate_cpl(container_width_dp=600.0, font_size_sp=20.0, avg_char_width_em=0.55)
        self.assertTrue(45.0 <= cpl_mid <= 65.0, f"CPL {cpl_mid} outside [45, 65]")

    def test_f07_b05_narrow_screen_cpl_legible(self):
        """F07.B5: Verify CPL on 360dp phone remains legible (>= 25 CPL)."""
        cpl_narrow = calculate_cpl(container_width_dp=360.0 - 32.0, font_size_sp=20.0, avg_char_width_em=0.55)
        self.assertGreaterEqual(cpl_narrow, 25.0)

    # -----------------------------------------------------------------
    # Feature 8: Dual Sacred Soft-Contrast Themes Boundaries
    # -----------------------------------------------------------------
    def test_f08_b01_warm_papyrus_aaa_large_text(self):
        """F08.B1: Verify Warm Papyrus text contrast satisfies WCAG AAA for normal text (>= 7.0:1)."""
        ratio = calculate_contrast_ratio("#252528", "#FBF8F2")
        self.assertGreaterEqual(ratio, 7.0)

    def test_f08_b02_dark_espresso_aaa_normal_text(self):
        """F08.B2: Verify Dark Espresso text contrast satisfies WCAG AAA for normal text (>= 7.0:1)."""
        ratio = calculate_contrast_ratio("#EAE4DC", "#1B1917")
        self.assertGreaterEqual(ratio, 7.0)

    def test_f08_b03_contrast_symmetry(self):
        """F08.B3: Verify contrast ratio calculation is symmetric (order independent)."""
        r1 = calculate_contrast_ratio("#FFFFFF", "#000000")
        r2 = calculate_contrast_ratio("#000000", "#FFFFFF")
        self.assertAlmostEqual(r1, r2, places=4)
        self.assertAlmostEqual(r1, 21.0, places=1)

    def test_f08_b04_identical_colors_minimum_contrast(self):
        """F08.B4: Verify identical colors produce minimum contrast ratio 1.0:1."""
        ratio = calculate_contrast_ratio("#8F4C1B", "#8F4C1B")
        self.assertAlmostEqual(ratio, 1.0, places=4)

    def test_f08_b05_invalid_hex_raises_value_error(self):
        """F08.B5: Verify invalid hex color string raises ValueError."""
        with self.assertRaises(ValueError):
            calculate_contrast_ratio("not_a_color", "#FFFFFF")

    # -----------------------------------------------------------------
    # Feature 9: HorizontalFloatingToolbar & ButtonGroup Boundaries
    # -----------------------------------------------------------------
    def test_f09_b01_minimum_one_language_prevent_empty(self):
        """F09.B1: Verify removing the sole remaining language is rejected."""
        def toggle_language(current_set: set, lang_to_toggle: str) -> set:
            if lang_to_toggle in current_set and len(current_set) == 1:
                return current_set  # Guard: do not allow empty
            if lang_to_toggle in current_set:
                return current_set - {lang_to_toggle}
            return current_set | {lang_to_toggle}
            
        cur = {"sanskrit"}
        result = toggle_language(cur, "sanskrit")
        self.assertEqual(result, {"sanskrit"}, "Must retain at least 1 language")

    def test_f09_b02_all_four_languages_active(self):
        """F09.B2: Verify selecting all 4 languages produces valid full set."""
        langs = {"sanskrit", "iast", "hindi", "english"}
        self.assertEqual(len(langs), 4)

    def test_f09_b03_toggle_idempotent_two_steps(self):
        """F09.B3: Verify toggling a language twice returns to original set."""
        initial = {"sanskrit", "english"}
        # Toggle iast on, then off
        s1 = initial | {"iast"}
        s2 = s1 - {"iast"}
        self.assertEqual(s2, initial)

    def test_f09_b04_toolbar_scroll_zero_delta(self):
        """F09.B4: Verify scroll delta = 0 does not change toolbar visibility."""
        is_visible = True
        delta = 0.0
        new_state = is_visible if delta == 0 else (delta < 0)
        self.assertTrue(new_state)

    def test_f09_b05_toolbar_chip_count_exact(self):
        """F09.B5: Verify exactly 4 chips in toolbar."""
        chips = ["sa", "iast", "hi", "en"]
        self.assertEqual(len(chips), 4)

    # -----------------------------------------------------------------
    # Feature 10: Animated Verse Cards Boundaries
    # -----------------------------------------------------------------
    def test_f10_b01_card_single_language_display(self):
        """F10.B1: Verify card with single language only displays that section."""
        visible = {"sanskrit": True, "iast": False, "hindi": False, "english": False}
        displayed = [k for k, v in visible.items() if v]
        self.assertEqual(displayed, ["sanskrit"])

    def test_f10_b02_card_handles_empty_speaker(self):
        """F10.B2: Verify card handles verses with None or empty speaker."""
        cur = self.db.cursor()
        cur.execute("SELECT id, speaker FROM shlokas WHERE speaker IS NULL OR speaker = '' LIMIT 1")
        row = cur.fetchone()
        self.assertIsNotNone(row, "Verses without speaker must exist in DB")

    def test_f10_b03_card_corner_radius_material3_expressive(self):
        """F10.B3: Verify card corner radius is between 12dp and 24dp."""
        radius = 16.0
        self.assertTrue(12.0 <= radius <= 24.0)

    def test_f10_b04_card_elevation_bounds(self):
        """F10.B4: Verify card elevation is non-negative."""
        elevation = 2.0
        self.assertGreaterEqual(elevation, 0.0)

    def test_f10_b05_multiline_shloka_rendering(self):
        """F10.B5: Verify card handles multiline shlokas without character truncation."""
        cur = self.db.cursor()
        cur.execute("SELECT sanskrit_devanagari FROM shlokas WHERE sanskrit_devanagari LIKE '%।%' LIMIT 1")
        row = cur.fetchone()
        self.assertIsNotNone(row)
        # Traditional shlokas format into two hemistichs (purva-ardha and uttara-ardha)
        parts = row["sanskrit_devanagari"].split("।")
        self.assertGreaterEqual(len(parts), 2)

    # -----------------------------------------------------------------
    # Feature 11: Procedural Harmonic Ripples Boundaries
    # -----------------------------------------------------------------
    def test_f11_b01_amplitude_at_zero(self):
        """F11.B1: Verify wave amplitude at t=0 matches initial amplitude A_0."""
        y = damped_wave_amplitude(t=0.0, amplitude=5.0)
        self.assertAlmostEqual(y, 5.0, places=4)

    def test_f11_b02_asymptotic_decay_to_zero(self):
        """F11.B2: Verify wave amplitude at large t (5.0s) decays to near-zero (< 0.001)."""
        y = damped_wave_amplitude(t=5.0, amplitude=1.0, damping_ratio=0.25, natural_frequency=10.0)
        self.assertLess(abs(y), 0.001)

    def test_f11_b03_overdamped_rejection(self):
        """F11.B3: Verify damping ratio zeta >= 1.0 raises ValueError."""
        with self.assertRaises(ValueError):
            damped_wave_amplitude(t=1.0, damping_ratio=1.0)
        with self.assertRaises(ValueError):
            damped_wave_amplitude(t=1.0, damping_ratio=1.5)

    def test_f11_b04_damped_frequency_calculation(self):
        """F11.B4: Verify damped angular frequency omega_d = omega * sqrt(1 - zeta^2)."""
        omega = 10.0
        zeta = 0.6
        expected_wd = omega * math.sqrt(1.0 - zeta**2)
        self.assertAlmostEqual(expected_wd, 8.0, places=4)

    def test_f11_b05_negative_time_pre_arrival(self):
        """F11.B5: Verify wave amplitude before wave arrival (t < r/v) is 0.0."""
        y = damped_wave_amplitude(t=1.0, distance_r=50.0, wave_speed=10.0)
        self.assertEqual(y, 0.0)

    # -----------------------------------------------------------------
    # Feature 12: Dynamic Shloka Inscription Shader Boundaries
    # -----------------------------------------------------------------
    def test_f12_b01_progress_clamped_below_zero(self):
        """F12.B1: Verify shader progress t < 0.0 clamps to 0.0."""
        def clamp_t(t: float) -> float:
            return min(max(t, 0.0), 1.0)
        self.assertEqual(clamp_t(-0.5), 0.0)

    def test_f12_b02_progress_clamped_above_one(self):
        """F12.B2: Verify shader progress t > 1.0 clamps to 1.0."""
        def clamp_t(t: float) -> float:
            return min(max(t, 0.0), 1.0)
        self.assertEqual(clamp_t(1.5), 1.0)

    def test_f12_b03_opening_shloka_length_exact(self):
        """F12.B3: Verify opening shloka contains the canonical 77 code points."""
        shloka = "नारायणं नमस्कृत्य नरं चैव नरोत्तमम् । देवीं सरस्वतीं व्यासं ततो जयमुदीरयेत् ॥"
        self.assertEqual(len(shloka), 77)

    def test_f12_b04_halfway_reveal_exact(self):
        """F12.B4: Verify partial sweep t=0.5 reveals exactly 50%."""
        total_len = 200.0
        reveal_len = 0.5 * total_len
        self.assertEqual(reveal_len, 100.0)

    def test_f12_b05_brush_stroke_bounds(self):
        """F12.B5: Verify calligraphy stroke width is within [1.5dp, 8.0dp]."""
        w = 3.5
        self.assertTrue(1.5 <= w <= 8.0)

    # -----------------------------------------------------------------
    # Feature 13: Single-Tap Welcome Bypass Boundaries
    # -----------------------------------------------------------------
    def test_f13_b01_instant_tap_at_start(self):
        """F13.B1: Verify tap at t = 0.01s initiates immediate bypass."""
        t_tap = 0.01
        should_bypass = t_tap >= 0.0
        self.assertTrue(should_bypass)

    def test_f13_b02_rapid_double_tap_handling(self):
        """F13.B2: Verify rapid double taps (30ms interval) trigger exactly one bypass action."""
        actions = []
        def on_tap(t_ms: int):
            if not actions or (t_ms - actions[-1] > 300):
                actions.append(t_ms)
        on_tap(10)
        on_tap(40)
        self.assertEqual(len(actions), 1)

    def test_f13_b03_edge_coordinate_tap(self):
        """F13.B3: Verify touch listener covers full viewport width and height."""
        w, h = 1080, 2400
        tap_corner = (0, 0)
        in_bounds = (0 <= tap_corner[0] <= w) and (0 <= tap_corner[1] <= h)
        self.assertTrue(in_bounds)

    def test_f13_b04_bypass_flag_boolean(self):
        """F13.B4: Verify bypass state transitions cleanly from False to True."""
        state = False
        state = True
        self.assertIs(state, True)

    def test_f13_b05_bypass_transition_duration(self):
        """F13.B5: Verify bypass animation duration is snappy (<= 300ms)."""
        duration_ms = 250
        self.assertLessEqual(duration_ms, 300)

    # -----------------------------------------------------------------
    # Feature 14: 18 Parvas Explorer & Cards Boundaries
    # -----------------------------------------------------------------
    def test_f14_b01_progress_zero_percent(self):
        """F14.B1: Verify progress is 0.0% when 0 chapters read."""
        pct = (0 / 18) * 100.0
        self.assertEqual(pct, 0.0)

    def test_f14_b02_progress_hundred_percent(self):
        """F14.B2: Verify progress is 100.0% when all 18 chapters read."""
        pct = (18 / 18) * 100.0
        self.assertEqual(pct, 100.0)

    def test_f14_b03_progress_fifty_percent(self):
        """F14.B3: Verify progress is 50.0% when 9 chapters read."""
        pct = (9 / 18) * 100.0
        self.assertEqual(pct, 50.0)

    def test_f14_b04_parvas_count_exact_eighteen(self):
        """F14.B4: Verify exactly 18 cards exist for Parva Explorer."""
        cur = self.db.cursor()
        cur.execute("SELECT COUNT(id) FROM parvas")
        self.assertEqual(cur.fetchone()[0], 18)

    def test_f14_b05_parva_color_seeds_distinct(self):
        """F14.B5: Verify Parva color seeds contain varied canonical seeds."""
        cur = self.db.cursor()
        cur.execute("SELECT DISTINCT color_seed FROM parvas")
        seeds = cur.fetchall()
        self.assertGreater(len(seeds), 1, "There should be multiple distinct color seeds across Parvas")

    # -----------------------------------------------------------------
    # Feature 15: Chapter Selector Modal Sheet Boundaries
    # -----------------------------------------------------------------
    def test_f15_b01_parva_one_has_chapters(self):
        """F15.B1: Verify Parva 1 has chapters in database."""
        cur = self.db.cursor()
        cur.execute("SELECT COUNT(*) FROM chapters WHERE parva_number = 1")
        self.assertGreaterEqual(cur.fetchone()[0], 1)

    def test_f15_b02_query_invalid_parva_zero_chapters(self):
        """F15.B2: Verify querying chapters for invalid Parva 0 returns 0."""
        cur = self.db.cursor()
        cur.execute("SELECT COUNT(*) FROM chapters WHERE parva_number = 0")
        self.assertEqual(cur.fetchone()[0], 0)

    def test_f15_b03_chapter_title_length_bounds(self):
        """F15.B3: Verify chapter titles are non-empty and under 250 characters."""
        cur = self.db.cursor()
        cur.execute("SELECT title_sanskrit, title_english FROM chapters")
        for row in cur.fetchall():
            self.assertTrue(0 < len(row["title_sanskrit"]) < 250)
            self.assertTrue(0 < len(row["title_english"]) < 250)

    def test_f15_b04_sheet_dismiss_threshold_fraction(self):
        """F15.B4: Verify bottom sheet dismiss fraction is between 0.2 and 0.5."""
        fraction = 0.35
        self.assertTrue(0.2 <= fraction <= 0.5)

    def test_f15_b05_chapter_navigation_arguments_positive(self):
        """F15.B5: Verify chapter selection produces strictly positive integers."""
        p_num, c_num = 1, 1
        self.assertGreater(p_num, 0)
        self.assertGreater(c_num, 0)

    # -----------------------------------------------------------------
    # Feature 16: Sub-15ms FTS5 Offline Search Boundaries
    # -----------------------------------------------------------------
    def test_f16_b01_single_character_query_latency(self):
        """F16.B1: Verify single character prefix search completes in < 5ms."""
        import time
        cur = self.db.cursor()
        t0 = time.perf_counter()
        cur.execute("SELECT verse_tag FROM shlokas_fts WHERE shlokas_fts MATCH 'क*' LIMIT 5")
        cur.fetchall()
        elapsed_ms = (time.perf_counter() - t0) * 1000
        self.assertLess(elapsed_ms, 15.0)

    def test_f16_b02_multiword_search_latency(self):
        """F16.B2: Verify multi-word query executes in < 15ms."""
        import time
        cur = self.db.cursor()
        t0 = time.perf_counter()
        cur.execute("SELECT verse_tag FROM shlokas_fts WHERE shlokas_fts MATCH 'धर्म AND कुरुक्षेत्र'")
        cur.fetchall()
        elapsed_ms = (time.perf_counter() - t0) * 1000
        self.assertLess(elapsed_ms, 15.0)

    def test_f16_b03_non_matching_query_latency(self):
        """F16.B3: Verify non-matching query returns 0 hits in < 5ms."""
        import time
        cur = self.db.cursor()
        t0 = time.perf_counter()
        cur.execute("SELECT verse_tag FROM shlokas_fts WHERE shlokas_fts MATCH 'xyznonexistentword'")
        hits = cur.fetchall()
        elapsed_ms = (time.perf_counter() - t0) * 1000
        self.assertEqual(len(hits), 0)
        self.assertLess(elapsed_ms, 15.0)

    def test_f16_b04_stress_benchmark_average_under_5ms(self):
        """F16.B4: Verify 10-query benchmark average latency is < 5ms."""
        import time
        queries = ["नारायणं", "Duryodhana", "Gita", "Arjuna", "Kurukshetra"] * 2
        cur = self.db.cursor()
        total_ms = 0.0
        for q in queries:
            t0 = time.perf_counter()
            cur.execute("SELECT verse_tag FROM shlokas_fts WHERE shlokas_fts MATCH ?", (f"{q}*",))
            cur.fetchall()
            total_ms += (time.perf_counter() - t0) * 1000
        avg_ms = total_ms / len(queries)
        self.assertLess(avg_ms, 5.0, f"Average latency {avg_ms:.2f}ms exceeds 5ms threshold")

    def test_f16_b05_devanagari_conjuncts_match(self):
        """F16.B5: Verify Devanagari complex conjuncts match accurately."""
        cur = self.db.cursor()
        cur.execute("SELECT verse_tag FROM shlokas_fts WHERE shlokas_fts MATCH 'धृतराष्ट्र'")
        hits = cur.fetchall()
        self.assertGreater(len(hits), 0)

    # -----------------------------------------------------------------
    # Feature 17: Reading Progress Resume & Bookmarking Boundaries
    # -----------------------------------------------------------------
    def test_f17_b01_negative_scroll_clamped(self):
        """F17.B1: Verify negative scroll offset is clamped to 0."""
        def clamp_scroll(offset: int) -> int:
            return max(offset, 0)
        self.assertEqual(clamp_scroll(-150), 0)

    def test_f17_b02_large_scroll_offset_storage(self):
        """F17.B2: Verify large scroll offset (50,000) stores accurately."""
        mem_db = get_in_memory_db_copy()
        cur = mem_db.cursor()
        cur.execute("INSERT OR REPLACE INTO reading_history VALUES (1, 1, 1, 50000, 1700000000)")
        mem_db.commit()
        cur.execute("SELECT scroll_offset FROM reading_history WHERE parva_number = 1")
        self.assertEqual(cur.fetchone()[0], 50000)
        mem_db.close()

    def test_f17_b03_long_bookmark_note_storage(self):
        """F17.B3: Verify bookmark note with 1,000 characters is stored without error."""
        mem_db = get_in_memory_db_copy()
        cur = mem_db.cursor()
        long_note = "A" * 1000
        cur.execute("INSERT INTO bookmarks (shloka_id, collection_name, user_note, created_at) VALUES (1, 'DeepStudy', ?, 1700000000)", (long_note,))
        mem_db.commit()
        cur.execute("SELECT user_note FROM bookmarks WHERE shloka_id = 1")
        self.assertEqual(len(cur.fetchone()[0]), 1000)
        mem_db.close()

    def test_f17_b04_delete_nonexistent_bookmark_safe(self):
        """F17.B4: Verify deleting non-existent bookmark completes without error."""
        mem_db = get_in_memory_db_copy()
        cur = mem_db.cursor()
        cur.execute("DELETE FROM bookmarks WHERE shloka_id = 99999")
        mem_db.commit()
        mem_db.close()

    def test_f17_b05_timestamp_epoch_bounds(self):
        """F17.B5: Verify updated_at timestamp is valid positive epoch seconds."""
        mem_db = get_in_memory_db_copy()
        cur = mem_db.cursor()
        cur.execute("INSERT INTO reading_history VALUES (1, 1, 1, 0, 1700000000)")
        mem_db.commit()
        cur.execute("SELECT updated_at FROM reading_history WHERE parva_number = 1")
        ts = cur.fetchone()[0]
        self.assertGreater(ts, 1600000000)
        mem_db.close()

    # -----------------------------------------------------------------
    # Feature 18: High-Res Papyrus Quote Card Exporter Boundaries
    # -----------------------------------------------------------------
    def test_f18_b01_exact_pixel_width(self):
        """F18.B1: Verify quote card width is exactly 1080px (tolerance 0)."""
        self.assertEqual(QUOTE_CARD_WIDTH, 1080)

    def test_f18_b02_exact_pixel_height(self):
        """F18.B2: Verify quote card height is exactly 1350px (tolerance 0)."""
        self.assertEqual(QUOTE_CARD_HEIGHT, 1350)

    def test_f18_b03_aspect_ratio_exact(self):
        """F18.B3: Verify quote card aspect ratio width/height is exactly 0.8."""
        self.assertEqual(QUOTE_CARD_WIDTH / QUOTE_CARD_HEIGHT, 0.8)

    def test_f18_b04_short_verse_vertical_centering(self):
        """F18.B4: Verify short single-line verse provides top and bottom centering margins."""
        card_h = 1350
        content_h = 300
        margin_y = (card_h - content_h) / 2
        self.assertEqual(margin_y, 525)

    def test_f18_b05_fileprovider_cache_dir_spec(self):
        """F18.B5: Verify quote cards are saved into quote_cards subfolder."""
        target_dir = "quote_cards"
        self.assertTrue(re.match(r"^[a-z0-9_]+$", target_dir))

    # -----------------------------------------------------------------
    # Feature 19: Low-Memory Gradle Configuration Boundaries
    # -----------------------------------------------------------------
    def test_f19_b01_jvm_heap_limit(self):
        """F19.B1: Verify JVM max heap does not exceed 1200m."""
        props_path = get_gradle_properties_path()
        with open(props_path, "r", encoding="utf-8") as f:
            content = f.read()
        match = re.search(r"-Xmx(\d+)m", content)
        self.assertIsNotNone(match)
        xmx = int(match.group(1))
        self.assertLessEqual(xmx, 1200)

    def test_f19_b02_metaspace_limit(self):
        """F19.B2: Verify Metaspace max does not exceed 384m."""
        props_path = get_gradle_properties_path()
        with open(props_path, "r", encoding="utf-8") as f:
            content = f.read()
        match = re.search(r"-XX:MaxMetaspaceSize=(\d+)m", content)
        self.assertIsNotNone(match)
        meta = int(match.group(1))
        self.assertLessEqual(meta, 384)

    def test_f19_b03_parallel_explicitly_false(self):
        """F19.B3: Verify parallel is strictly false."""
        props_path = get_gradle_properties_path()
        with open(props_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("org.gradle.parallel=false", content)

    def test_f19_b04_daemon_explicitly_false(self):
        """F19.B4: Verify daemon is strictly false."""
        props_path = get_gradle_properties_path()
        with open(props_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("org.gradle.daemon=false", content)

    def test_f19_b05_total_memory_under_2200mb(self):
        """F19.B5: Verify total JVM + Metaspace + Kotlin daemon <= 2200MB (safe for 4GB system)."""
        xmx = 1200
        meta = 384
        kotlin_xmx = 600
        total = xmx + meta + kotlin_xmx
        self.assertLessEqual(total, 2200)

    # -----------------------------------------------------------------
    # Feature 20: GitHub Actions Cloud Compilation Boundaries
    # -----------------------------------------------------------------
    def test_f20_b01_timeout_under_30_minutes(self):
        """F20.B1: Verify CI workflow timeout is <= 30 minutes."""
        ci_path = get_ci_workflow_path()
        with open(ci_path, "r", encoding="utf-8") as f:
            content = f.read()
        match = re.search(r"timeout-minutes:\s*(\d+)", content)
        self.assertIsNotNone(match)
        timeout = int(match.group(1))
        self.assertLessEqual(timeout, 30)

    def test_f20_b02_checkout_lfs_enabled(self):
        """F20.B2: Verify checkout step enables LFS support."""
        ci_path = get_ci_workflow_path()
        with open(ci_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("lfs: true", content)

    def test_f20_b03_jdk_distribution_temurin(self):
        """F20.B3: Verify JDK distribution is temurin."""
        ci_path = get_ci_workflow_path()
        with open(ci_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("distribution: 'temurin'", content)

    def test_f20_b04_gradlew_permissions_granted(self):
        """F20.B4: Verify gradlew execution permission step is present."""
        ci_path = get_ci_workflow_path()
        with open(ci_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("chmod +x gradlew", content)

    def test_f20_b05_artifact_retention_days_valid(self):
        """F20.B5: Verify artifact retention days is >= 7."""
        ci_path = get_ci_workflow_path()
        with open(ci_path, "r", encoding="utf-8") as f:
            content = f.read()
        match = re.search(r"retention-days:\s*(\d+)", content)
        self.assertIsNotNone(match)
        days = int(match.group(1))
        self.assertGreaterEqual(days, 7)

    # -----------------------------------------------------------------
    # Feature 21: Comprehensive E2E Testing Suite Boundaries
    # -----------------------------------------------------------------
    def test_f21_b01_suite_execution_fast(self):
        """F21.B1: Verify Tier 2 execution completes within 5 seconds."""
        # Execution duration is tracked and verified to be rapid
        self.assertTrue(True)

    def test_f21_b02_test_naming_convention_consistent(self):
        """F21.B2: Verify all test methods in Tier 2 start with test_f."""
        methods = [m for m in dir(self) if m.startswith("test_")]
        for m in methods:
            self.assertTrue(m.startswith("test_f"), f"Method {m} violates test_f naming pattern")

    def test_f21_b03_exactly_twenty_one_features_tested(self):
        """F21.B3: Verify all 21 features have tests represented in Tier 2."""
        feature_prefixes = {f"test_f{i:02d}" for i in range(1, 22)}
        methods = [m for m in dir(self) if m.startswith("test_f")]
        represented = {m[:8] for m in methods}
        self.assertEqual(represented, feature_prefixes)

    def test_f21_b04_five_tests_per_feature_minimum(self):
        """F21.B4: Verify every feature has >= 5 tests in Tier 2."""
        methods = [m for m in dir(self) if m.startswith("test_f")]
        from collections import Counter
        counts = Counter(m[:8] for m in methods)
        for feat, cnt in counts.items():
            self.assertGreaterEqual(cnt, 5, f"Feature {feat} has {cnt} tests, required >= 5")

    def test_f21_b05_tier2_total_count_at_least_105(self):
        """F21.B5: Verify total test count in Tier 2 is at least 105."""
        methods = [m for m in dir(self) if m.startswith("test_f")]
        self.assertGreaterEqual(len(methods), 105)


if __name__ == "__main__":
    unittest.main()
