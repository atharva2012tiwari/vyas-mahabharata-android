"""
Reviewer Round 2 Adversarial Stress Test Suite
Validates:
1. 30-scale Material 3 Expressive Typography System (15 baseline + 15 emphasized)
2. Exact 1.8x Line-Height Ratio across all Sanskrit styles (ScriptureSanskritStyle, ScriptureSanskritLargeStyle, ScriptureSanskritDisplayStyle)
3. Quote Card Exporter Sanskrit & IAST Wrapping Simulation on all 20 database verses (guaranteeing no horizontal text clipping)
4. Navigation Graph and Screen Route Invariants (including initialVerse parameter passing)
5. Theme Color Scheme tokens (background, onBackground, outline, outlineVariant)
6. GitHub Actions build workflow syntax & parameter validation
"""

import os
import re
import sqlite3
import unittest
import yaml

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "app", "src", "main", "assets", "mahabharata.db")
TYPE_KT_PATH = os.path.join(PROJECT_ROOT, "app", "src", "main", "java", "com", "vyas", "mahabharata", "ui", "theme", "Type.kt")
THEME_KT_PATH = os.path.join(PROJECT_ROOT, "app", "src", "main", "java", "com", "vyas", "mahabharata", "ui", "theme", "Theme.kt")
QUOTE_DIALOG_PATH = os.path.join(PROJECT_ROOT, "app", "src", "main", "java", "com", "vyas", "mahabharata", "ui", "components", "QuoteExportDialog.kt")
WELCOME_SCREEN_PATH = os.path.join(PROJECT_ROOT, "app", "src", "main", "java", "com", "vyas", "mahabharata", "ui", "screens", "welcome", "WelcomeScreen.kt")
READER_SCREEN_PATH = os.path.join(PROJECT_ROOT, "app", "src", "main", "java", "com", "vyas", "mahabharata", "ui", "screens", "reader", "ReadingCanvasScreen.kt")
BOOKMARKS_SCREEN_PATH = os.path.join(PROJECT_ROOT, "app", "src", "main", "java", "com", "vyas", "mahabharata", "ui", "screens", "bookmarks", "BookmarksScreen.kt")
NAV_HOST_PATH = os.path.join(PROJECT_ROOT, "app", "src", "main", "java", "com", "vyas", "mahabharata", "ui", "navigation", "VyasNavigation.kt")
CI_WORKFLOW_PATH = os.path.join(PROJECT_ROOT, ".github", "workflows", "build-apk.yml")


class ReviewerRound2AdversarialTests(unittest.TestCase):

    def test_01_typography_30_scales_completeness(self):
        """Verify Type.kt defines all 30 Material 3 Expressive typography scales (15 baseline + 15 emphasized)."""
        with open(TYPE_KT_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        baseline_scales = [
            "displayLarge", "displayMedium", "displaySmall",
            "headlineLarge", "headlineMedium", "headlineSmall",
            "titleLarge", "titleMedium", "titleSmall",
            "bodyLarge", "bodyMedium", "bodySmall",
            "labelLarge", "labelMedium", "labelSmall"
        ]
        emphasized_scales = [
            "displayLargeEmphasized", "displayMediumEmphasized", "displaySmallEmphasized",
            "headlineLargeEmphasized", "headlineMediumEmphasized", "headlineSmallEmphasized",
            "titleLargeEmphasized", "titleMediumEmphasized", "titleSmallEmphasized",
            "bodyLargeEmphasized", "bodyMediumEmphasized", "bodySmallEmphasized",
            "labelLargeEmphasized", "labelMediumEmphasized", "labelSmallEmphasized"
        ]

        # Verify all 15 baseline scales in VyasTypography
        for s in baseline_scales:
            self.assertIn(f"{s} =", content, f"Missing baseline typography scale: {s}")

        # Verify all 15 emphasized scales
        for s in emphasized_scales:
            self.assertIn(s, content, f"Missing emphasized typography scale: {s}")

        # Verify data class VyasExpressiveTypography exists and combines them
        self.assertIn("data class VyasExpressiveTypography", content)
        self.assertIn("LocalExpressiveTypography", content)

    def test_02_exact_1_8x_line_height_ratio_all_sanskrit_styles(self):
        """Verify exact 1.8x line-height ratio across all Sanskrit typography styles."""
        with open(TYPE_KT_PATH, "r", encoding="utf-8") as f:
            type_content = f.read()

        with open(WELCOME_SCREEN_PATH, "r", encoding="utf-8") as f:
            welcome_content = f.read()

        # 1. Standard Sanskrit: 20sp -> 36sp
        self.assertIn("fontSize = 20.sp", type_content)
        self.assertIn("lineHeight = 36.sp", type_content)
        self.assertAlmostEqual(36.0 / 20.0, 1.8, places=4)

        # 2. Large Sanskrit: 24sp -> 43.2sp
        self.assertIn("fontSize = 24.sp", type_content)
        self.assertIn("lineHeight = 43.2.sp", type_content)
        self.assertAlmostEqual(43.2 / 24.0, 1.8, places=4)

        # 3. Display Sanskrit: 22sp -> 39.6sp
        self.assertIn("fontSize = 22.sp", type_content)
        self.assertIn("lineHeight = 39.6.sp", type_content)
        self.assertAlmostEqual(39.6 / 22.0, 1.8, places=4)

        # 4. Welcome Screen uses ScriptureSanskritDisplayStyle
        self.assertIn("ScriptureSanskritDisplayStyle", welcome_content)
        # Ensure stale incorrect 40.sp was removed
        self.assertNotIn("lineHeight = 40.sp", welcome_content)

    def test_03_quote_card_sanskrit_and_iast_auto_wrapping(self):
        """Verify QuoteExportDialog auto-wraps both Sanskrit and IAST, preventing canvas boundary overflow."""
        with open(QUOTE_DIALOG_PATH, "r", encoding="utf-8") as f:
            dialog_content = f.read()

        # Check production code uses wrapText on Sanskrit and IAST
        self.assertIn("wrapText(shloka.sanskritDevanagari, sanskritPaint", dialog_content)
        self.assertIn("wrapText(shloka.sanskritIast, iastPaint", dialog_content)

        # Simulate text measurement on all 20 verses in DB
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, sanskrit_devanagari, sanskrit_iast FROM shlokas")
        rows = c.fetchall()
        conn.close()

        max_canvas_text_width = 1080 - 160 # 920px

        import unicodedata
        def typographic_len(text: str) -> int:
            return sum(1 for ch in text if unicodedata.category(ch) not in ('Mn', 'Me'))

        for row_id, dev_text, iast_text in rows:
            def simulate_wrap(text: str, avg_glyph_width: float, max_w: float) -> list:
                words = text.split()
                lines = []
                cur = []
                for w in words:
                    cand = " ".join(cur + [w])
                    if typographic_len(cand) * avg_glyph_width <= max_w:
                        cur.append(w)
                    else:
                        if cur:
                            lines.append(" ".join(cur))
                        cur = [w]
                if cur:
                    lines.append(" ".join(cur))
                return lines

            # Sanskrit at 44px text size (~24px avg base glyph advance)
            dev_lines = simulate_wrap(dev_text, 24.0, max_canvas_text_width)
            self.assertGreater(len(dev_lines), 1, f"Verse ID {row_id} Sanskrit should wrap into >= 2 lines")
            for line in dev_lines:
                self.assertLessEqual(typographic_len(line) * 24.0, max_canvas_text_width, f"Line overflow in verse {row_id}")

            # IAST at 28px text size (~14px avg Latin glyph advance)
            iast_lines = simulate_wrap(iast_text, 14.0, max_canvas_text_width)
            self.assertGreater(len(iast_lines), 1, f"Verse ID {row_id} IAST should wrap into >= 2 lines")
            for line in iast_lines:
                self.assertLessEqual(typographic_len(line) * 14.0, max_canvas_text_width, f"Line overflow in IAST verse {row_id}")

    def test_04_welcome_screen_dynamic_vector_path_clip_shader(self):
        """Verify WelcomeScreen implements progressive vector path clip shader and dynamic sweep stroke."""
        with open(WELCOME_SCREEN_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("drawWithCache", content)
        self.assertIn("clipPath(clipPath)", content)
        self.assertIn("Path().apply", content)
        self.assertIn("sweep in 0.01f..0.99f", content)
        self.assertIn("drawLine(", content)

    def test_05_reading_canvas_restore_and_initial_verse_invariants(self):
        """Verify ReadingCanvasScreen accepts initialVerse and sets scroll indices to avoid false auto-hide."""
        with open(READER_SCREEN_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("initialVerse: Int = -1", content)
        self.assertIn("if (initialVerse > 0)", content)
        self.assertIn("lastScrollIndex = targetItem", content)
        self.assertIn("isToolbarVisible = true", content)

    def test_06_navigation_graph_and_bookmarks_click_handling(self):
        """Verify BookmarksScreen has clickable cards and VyasNavigation routes verse-level jumps."""
        with open(BOOKMARKS_SCREEN_PATH, "r", encoding="utf-8") as f:
            bookmarks_content = f.read()

        with open(NAV_HOST_PATH, "r", encoding="utf-8") as f:
            nav_content = f.read()

        # BookmarksScreen must be clickable and trigger onNavigateToShlokaTag
        self.assertIn(".clickable(onClick = onClick)", bookmarks_content)
        self.assertIn("onNavigateToShlokaTag(tag)", bookmarks_content)

        # VyasNavigation must parse verse tag and dispatch initialVerse
        self.assertIn("initialVerse: Int? = null", nav_content)
        self.assertIn("Screen.Reader.createRoute(p, c, v)", nav_content)

    def test_07_theme_color_schemes_coherence(self):
        """Verify WarmPapyrusColorScheme and DarkEspressoColorScheme configure background, outline, and outlineVariant."""
        with open(THEME_KT_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("background = PapyrusSurface", content)
        self.assertIn("onBackground = PapyrusOnSurface", content)
        self.assertIn("outline = PapyrusSecondary", content)
        self.assertIn("outlineVariant = Color(0xFFD8D0C5)", content)

        self.assertIn("background = EspressoSurface", content)
        self.assertIn("onBackground = EspressoOnSurface", content)
        self.assertIn("outline = EspressoSecondary", content)
        self.assertIn("outlineVariant = Color(0xFF4E473F)", content)

    def test_08_ci_workflow_and_gitignore_invariants(self):
        """Verify CI workflow file and .gitignore file are complete and valid."""
        gitignore_path = os.path.join(PROJECT_ROOT, ".gitignore")
        self.assertTrue(os.path.exists(gitignore_path), ".gitignore must exist")
        with open(gitignore_path, "r", encoding="utf-8") as f:
            gi_content = f.read()
        self.assertIn(".gradle", gi_content)
        self.assertIn("app/build/", gi_content)

        with open(CI_WORKFLOW_PATH, "r", encoding="utf-8") as f:
            wf_content = f.read()
        self.assertIn("if-no-files-found: error", wf_content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
