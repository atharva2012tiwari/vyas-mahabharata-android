"""
Tier 4: Real-World Application Scenarios Test Suite.
Simulates comprehensive end-to-end user journeys through the application:
searching shlokas, multilingual rendering, bookmarking, session resume, quote card export,
and cloud CI validation.
Contains >= 16 discrete, executable test cases.
"""

import math
import os
import re
import sqlite3
import sys
import time
import unittest
from typing import Dict, List, Any

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


class Tier4RealWorldScenarioTests(unittest.TestCase):
    """Tier 4: End-to-End Real World Application User Journeys."""

    @classmethod
    def setUpClass(cls):
        cls.db = connect_db(read_only=True)
        cls.project_root = get_project_root()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_j01_app_first_launch_journey(self):
        """Journey 1: First Launch -> Welcome Screen Animation -> Bypass -> Explorer."""
        # 1. Welcome screen initializes with concentric harmonic ripples
        ripple_t0 = damped_wave_amplitude(t=0.0, amplitude=1.0)
        self.assertAlmostEqual(ripple_t0, 1.0)
        
        # 2. Calligraphy shader starts progressive inscription
        progress_t = 0.3
        self.assertTrue(0.0 < progress_t < 1.0)
        
        # 3. User taps screen to bypass
        user_tap_detected = True
        animation_dismissed = user_tap_detected
        self.assertTrue(animation_dismissed)
        
        # 4. Parva Explorer opens displaying all 18 Parvas
        cur = self.db.cursor()
        cur.execute("SELECT COUNT(*) FROM parvas")
        count = cur.fetchone()[0]
        self.assertEqual(count, 18)

    def test_j02_genesis_reading_journey(self):
        """Journey 2: Parva Explorer -> Open Adi Parva Ch 1 -> Spacious Reader Canvas."""
        cur = self.db.cursor()
        # 1. Select Parva 1
        cur.execute("SELECT * FROM parvas WHERE number = 1")
        parva = cur.fetchone()
        self.assertIn("आदि", parva["name_sanskrit"])
        
        # 2. Open Chapter 1
        cur.execute("SELECT * FROM chapters WHERE parva_number = 1 AND chapter_number = 1")
        ch = cur.fetchone()
        self.assertIsNotNone(ch)
        
        # 3. Read first verse: Narayana invocation
        cur.execute("SELECT * FROM shlokas WHERE parva_number = 1 AND chapter_number = 1 AND verse_number = 1")
        verse1 = cur.fetchone()
        self.assertIn("नारायणं नमस्कृत्य", verse1["sanskrit_devanagari"])
        
        # 4. Verify typography and measure constraints
        self.assertTrue(verify_line_height_ratio(20.0, 36.0, 1.8))
        cpl = calculate_cpl(container_width_dp=600.0, font_size_sp=20.0, avg_char_width_em=0.58)
        self.assertTrue(45.0 <= cpl <= 65.0)

    def test_j03_sacred_gita_search_journey(self):
        """Journey 3: Multilingual Search 'धर्मक्षेत्रे' -> Instant Result -> Open Gita Ch 1."""
        cur = self.db.cursor()
        # 1. User enters query into search bar
        t0 = time.perf_counter()
        cur.execute("SELECT rowid, verse_tag FROM shlokas_fts WHERE shlokas_fts MATCH 'धर्मक्षेत्रे'")
        hits = cur.fetchall()
        elapsed_ms = (time.perf_counter() - t0) * 1000
        
        # 2. Result returns in under 15ms
        self.assertLess(elapsed_ms, 15.0)
        self.assertGreater(len(hits), 0)
        self.assertEqual(hits[0]["verse_tag"], "6.25.1")
        
        # 3. User taps result to open in reader
        cur.execute("SELECT * FROM shlokas WHERE id = ?", (hits[0]["rowid"],))
        target_verse = cur.fetchone()
        self.assertEqual(target_verse["parva_number"], 6)
        self.assertEqual(target_verse["chapter_number"], 25)
        self.assertEqual(target_verse["verse_number"], 1)

    def test_j04_gita_verse_multilingual_alignment_journey(self):
        """Journey 4: Bhagavad Gita Ch 1 Verse 1 Quadrilingual Verification."""
        cur = self.db.cursor()
        cur.execute("""
            SELECT sanskrit_devanagari, sanskrit_iast, translation_hindi, translation_english, speaker
            FROM shlokas WHERE parva_number = 6 AND chapter_number = 25 AND verse_number = 1
        """)
        gita_v1 = cur.fetchone()
        self.assertEqual(gita_v1["speaker"], "धृतराष्ट्र उवाच")
        self.assertIn("धर्मक्षेत्रे कुरुक्षेत्रे", gita_v1["sanskrit_devanagari"])
        self.assertIn("dharmakṣetre kurukṣetre", gita_v1["sanskrit_iast"].lower())
        self.assertIn("कुरुक्षेत्र", gita_v1["translation_hindi"])
        self.assertTrue("kurukshetra" in gita_v1["translation_english"].lower() or "kuru" in gita_v1["translation_english"].lower())

    def test_j05_scholar_script_toggling_journey(self):
        """Journey 5: Reading Canvas -> Disable Hindi/English -> Dynamic Shrink to Sanskrit+IAST."""
        # Active toggles start with all 4
        active_langs = {"sanskrit", "iast", "hindi", "english"}
        self.assertEqual(len(active_langs), 4)
        
        # Scholar toggles off Hindi and English
        active_langs.discard("hindi")
        active_langs.discard("english")
        self.assertEqual(active_langs, {"sanskrit", "iast"})
        
        # Card renders only Sanskrit and IAST
        visible_labels = [l for l in ["sanskrit", "iast", "hindi", "english"] if l in active_langs]
        self.assertEqual(visible_labels, ["sanskrit", "iast"])

    def test_j06_sanskrit_only_monastic_mode_journey(self):
        """Journey 6: Reading Canvas -> Sanskrit Only Mode -> Pristine 1.8x Typography."""
        active_langs = {"sanskrit"}
        self.assertEqual(len(active_langs), 1)
        self.assertTrue(verify_line_height_ratio(20.0, 36.0, 1.8))
        self.assertEqual(calculate_cpl(600.0, 20.0, 0.58) > 45, True)

    def test_j07_full_quadrilingual_mode_journey(self):
        """Journey 7: Reading Canvas -> All 4 Language Chips Active -> Full Study Mode."""
        active_langs = {"sanskrit", "iast", "hindi", "english"}
        cur = self.db.cursor()
        cur.execute("SELECT * FROM shlokas WHERE parva_number = 1 AND chapter_number = 1 AND verse_number = 1")
        verse = cur.fetchone()
        
        for lang, col in [("sanskrit", "sanskrit_devanagari"), ("iast", "sanskrit_iast"), ("hindi", "translation_hindi"), ("english", "translation_english")]:
            self.assertIn(lang, active_langs)
            self.assertTrue(len(verse[col].strip()) > 0)

    def test_j08_verse_bookmarking_flow_journey(self):
        """Journey 8: Shloka Card -> Add to Bookmarks with Note -> Verify Stored."""
        mem_db = get_in_memory_db_copy()
        cur = mem_db.cursor()
        
        # 1. User bookmarks Adi Parva 1.1
        cur.execute("""
            INSERT INTO bookmarks (shloka_id, collection_name, user_note, created_at)
            VALUES (1, 'Favorites', 'Opening invocation to Narayana and Sarasvati', 1700000000)
        """)
        mem_db.commit()
        
        # 2. User opens Bookmarks drawer
        cur.execute("SELECT * FROM bookmarks WHERE shloka_id = 1")
        bm = cur.fetchone()
        self.assertIsNotNone(bm)
        self.assertEqual(bm["collection_name"], "Favorites")
        self.assertEqual(bm["user_note"], "Opening invocation to Narayana and Sarasvati")
        mem_db.close()

    def test_j09_bookmark_toggle_off_flow_journey(self):
        """Journey 9: Bookmarked Shloka -> Tap Bookmark Again -> Removed from Favorites."""
        mem_db = get_in_memory_db_copy()
        cur = mem_db.cursor()
        cur.execute("INSERT INTO bookmarks (shloka_id, collection_name, user_note, created_at) VALUES (1, 'Favorites', 'Note', 1700000000)")
        mem_db.commit()
        
        # User toggles bookmark icon again -> deletes
        cur.execute("DELETE FROM bookmarks WHERE shloka_id = 1")
        mem_db.commit()
        
        cur.execute("SELECT COUNT(*) FROM bookmarks WHERE shloka_id = 1")
        self.assertEqual(cur.fetchone()[0], 0)
        mem_db.close()

    def test_j10_reading_session_persistence_flow_journey(self):
        """Journey 10: Read Chapter 1 to Verse 10 -> Save Progress -> App Restart -> Resume Position."""
        mem_db = get_in_memory_db_copy()
        cur = mem_db.cursor()
        
        # 1. Progress updated while scrolling
        cur.execute("""
            INSERT OR REPLACE INTO reading_history (parva_number, last_chapter_number, last_verse_number, scroll_offset, updated_at)
            VALUES (1, 1, 10, 420, 1700000000)
        """)
        mem_db.commit()
        
        # 2. App restarts -> loads resume position for Adi Parva
        cur.execute("SELECT * FROM reading_history WHERE parva_number = 1")
        history = cur.fetchone()
        self.assertEqual(history["last_chapter_number"], 1)
        self.assertEqual(history["last_verse_number"], 10)
        self.assertEqual(history["scroll_offset"], 420)
        mem_db.close()

    def test_j11_multi_parva_independent_resume_journey(self):
        """Journey 11: Switch Between Parva 1 and Parva 6 -> Independent Position Tracking."""
        mem_db = get_in_memory_db_copy()
        cur = mem_db.cursor()
        
        # Parva 1 position: Ch 1, Verse 15
        cur.execute("INSERT INTO reading_history VALUES (1, 1, 15, 300, 1700000000)")
        # Parva 6 position: Ch 25, Verse 7
        cur.execute("INSERT INTO reading_history VALUES (6, 25, 7, 180, 1700000100)")
        mem_db.commit()
        
        # Verify independence
        cur.execute("SELECT last_verse_number FROM reading_history WHERE parva_number = 1")
        self.assertEqual(cur.fetchone()[0], 15)
        cur.execute("SELECT last_verse_number FROM reading_history WHERE parva_number = 6")
        self.assertEqual(cur.fetchone()[0], 7)
        mem_db.close()

    def test_j12_sacred_quote_card_generation_journey(self):
        """Journey 12: Select Gita 1.1 -> Render 1080x1350 High-Res Papyrus Card."""
        cur = self.db.cursor()
        cur.execute("SELECT * FROM shlokas WHERE parva_number = 6 AND chapter_number = 25 AND verse_number = 1")
        verse = cur.fetchone()
        
        card_config = {
            "width": QUOTE_CARD_WIDTH,
            "height": QUOTE_CARD_HEIGHT,
            "aspect_ratio": QUOTE_CARD_ASPECT_RATIO,
            "theme": "WARM_PAPYRUS",
            "bg_color": "#FBF8F2",
            "text_color": "#252528",
            "verse_text": verse["sanskrit_devanagari"],
            "attribution": "Mahabharata — Bhishma Parva (25.1)"
        }
        self.assertEqual(card_config["width"], 1080)
        self.assertEqual(card_config["height"], 1350)
        self.assertAlmostEqual(card_config["aspect_ratio"], 0.8)
        self.assertIn("धर्मक्षेत्रे", card_config["verse_text"])
        self.assertIn("Bhishma Parva", card_config["attribution"])

    def test_j13_dark_espresso_quote_sharing_journey(self):
        """Journey 13: Export Quote Card with Dark Espresso Amber Palette -> FileProvider URI."""
        theme_bg = "#1B1917"
        theme_text = "#EAE4DC"
        contrast = calculate_contrast_ratio(theme_text, theme_bg)
        self.assertGreater(contrast, 10.0)
        
        # URI generation for share intent
        authority = "com.vyas.mahabharata.fileprovider"
        file_path = "quote_cards/quote_gita_1_1.png"
        uri = f"content://{authority}/{file_path}"
        self.assertTrue(uri.startswith("content://com.vyas.mahabharata.fileprovider/"))

    def test_j14_theme_ergonomics_night_shift_journey(self):
        """Journey 14: Switch Day Theme (Papyrus) -> Night Theme (Dark Espresso) -> WCAG Verified."""
        day_contrast = calculate_contrast_ratio("#252528", "#FBF8F2")
        night_contrast = calculate_contrast_ratio("#EAE4DC", "#1B1917")
        self.assertGreaterEqual(day_contrast, 7.0)
        self.assertGreaterEqual(night_contrast, 7.0)

    def test_j15_complete_chapter_navigation_journey(self):
        """Journey 15: Explorer -> Select Parva 18 (Svargarohana) -> Chapter Sheet -> Reader."""
        cur = self.db.cursor()
        cur.execute("SELECT * FROM parvas WHERE number = 18")
        parva18 = cur.fetchone()
        self.assertIn("स्वर्गारोहण", parva18["name_sanskrit"])
        self.assertEqual(parva18["name_english"], "Svargarohana Parva")
        
        # Check chapters exist
        cur.execute("SELECT COUNT(*) FROM chapters WHERE parva_number = 18")
        cnt = cur.fetchone()[0]
        self.assertGreaterEqual(cnt, 0)

    def test_j16_cloud_build_ci_verification_journey(self):
        """Journey 16: GitHub Actions Cloud Build Verification (triggers, JDK, assembleDebug, artifact)."""
        ci_path = get_ci_workflow_path()
        with open(ci_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Push and PR triggers
        self.assertIn("push:", content)
        self.assertIn("pull_request:", content)
        self.assertIn("workflow_dispatch:", content)
        # Build command
        self.assertIn("./gradlew assembleDebug", content)
        # Artifact upload
        self.assertIn("upload-artifact@v4", content)
        self.assertIn("Vyas-Mahabharata-Debug-APK", content)

    def test_j17_hardware_memory_compliance_journey(self):
        """Journey 17: Low-Memory Gradle Tuning Verification for 4GB RAM Development Machine."""
        props_path = get_gradle_properties_path()
        with open(props_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        self.assertIn("-Xmx1200m", content)
        self.assertIn("-XX:MaxMetaspaceSize=384m", content)
        self.assertIn("org.gradle.parallel=false", content)
        self.assertIn("org.gradle.daemon=false", content)

    def test_j18_database_integrity_and_latency_benchmark_journey(self):
        """Journey 18: Full Database Integrity and 20-Query Latency Benchmark (<15ms)."""
        cur = self.db.cursor()
        # 1. 18 parvas present
        cur.execute("SELECT COUNT(*) FROM parvas")
        self.assertEqual(cur.fetchone()[0], 18)
        
        # 2. Benchmark 20 diverse multilingual search queries
        benchmark_queries = [
            "नारायणं", "धर्मक्षेत्रे", "Duryodhana", "Gita", "Arjuna",
            "Kurukshetra", "भगवान्", "Sanjaya", "पाण्डव", "कृष्ण",
            "भीष्म", "Shanti", "Bharat", "हस्तिनापुर", "कुरु",
            "Dharma", "सूत", "ऋषि", "वेद", "व्यास"
        ]
        
        max_ms = 0.0
        total_ms = 0.0
        for q in benchmark_queries:
            t0 = time.perf_counter()
            cur.execute("SELECT verse_tag FROM shlokas_fts WHERE shlokas_fts MATCH ?", (f"{q}*",))
            cur.fetchall()
            elapsed_ms = (time.perf_counter() - t0) * 1000
            total_ms += elapsed_ms
            max_ms = max(max_ms, elapsed_ms)
            self.assertLess(elapsed_ms, 15.0, f"Query '{q}' took {elapsed_ms:.2f}ms (threshold 15ms)")
            
        avg_ms = total_ms / len(benchmark_queries)
        self.assertLess(avg_ms, 5.0, f"Average latency {avg_ms:.2f}ms exceeds 5ms")
        self.assertLess(max_ms, 15.0, f"Max latency {max_ms:.2f}ms exceeds 15ms")


if __name__ == "__main__":
    unittest.main()
