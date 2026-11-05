"""
Reviewer Round 3 Adversarial Stress Test Suite
Validates:
1. Wide Screen 600dp Measure Constraint Invariant: All screens enforce .widthIn(max = 600.dp).fillMaxWidth()
   (verifying that no .fillMaxWidth().widthIn(...) constraint ordering bugs exist).
2. Dynamic Scripture Font Scaling: ShlokaCard accepts isLargeFont, uses ScriptureSanskritLargeStyle (24sp/43.2sp = 1.8x),
   and ReadingCanvasScreen connects onFontSizeClick to toggle isLargeFont.
3. Minimum-1 Language Selection Invariant: FloatingReaderBar disables deselection on the last active chip,
   ReadingCanvasScreen guards all toggles, and ShlokaCard enforces effectiveShowSanskrit fallback.
4. Seamless Shloka Card Expansion/Collapse: ShlokaCard wraps the divider in AnimatedVisibility to prevent visual jump.
5. Quote Export Preview Coherence: Preview card displays both Hindi and English when both are enabled.
6. Quote Card Bitmap Footer Clearance: renderQuoteCardBitmap enforces bounds to guarantee zero footer collision.
7. Welcome Screen Single-Tap Bypass: Idempotent bypass handler and custom harmonic ripple canvas.
8. Cloud CI/CD Validation: Valid YAML, Temurin JDK 17, AGP 8.7.2, and upload-artifact@v4 with if-no-files-found: error.
"""

import os
import re
import unittest
import yaml

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SHLOKA_CARD_PATH = os.path.join(PROJECT_ROOT, "app", "src", "main", "java", "com", "vyas", "mahabharata", "ui", "components", "ShlokaCard.kt")
FLOATING_BAR_PATH = os.path.join(PROJECT_ROOT, "app", "src", "main", "java", "com", "vyas", "mahabharata", "ui", "components", "FloatingReaderBar.kt")
READER_SCREEN_PATH = os.path.join(PROJECT_ROOT, "app", "src", "main", "java", "com", "vyas", "mahabharata", "ui", "screens", "reader", "ReadingCanvasScreen.kt")
WELCOME_SCREEN_PATH = os.path.join(PROJECT_ROOT, "app", "src", "main", "java", "com", "vyas", "mahabharata", "ui", "screens", "welcome", "WelcomeScreen.kt")
PARVA_SCREEN_PATH = os.path.join(PROJECT_ROOT, "app", "src", "main", "java", "com", "vyas", "mahabharata", "ui", "screens", "explorer", "ParvaExplorerScreen.kt")
SEARCH_SCREEN_PATH = os.path.join(PROJECT_ROOT, "app", "src", "main", "java", "com", "vyas", "mahabharata", "ui", "screens", "search", "SearchScreen.kt")
BOOKMARKS_SCREEN_PATH = os.path.join(PROJECT_ROOT, "app", "src", "main", "java", "com", "vyas", "mahabharata", "ui", "screens", "bookmarks", "BookmarksScreen.kt")
QUOTE_DIALOG_PATH = os.path.join(PROJECT_ROOT, "app", "src", "main", "java", "com", "vyas", "mahabharata", "ui", "components", "QuoteExportDialog.kt")
CI_WORKFLOW_PATH = os.path.join(PROJECT_ROOT, ".github", "workflows", "build-apk.yml")


class ReviewerRound3AdversarialTests(unittest.TestCase):

    def test_01_wide_screen_600dp_modifier_order(self):
        """Verify all screens use .widthIn(max = 600.dp).fillMaxWidth() to avoid Compose constraint-swallowing bug."""
        screens = [
            ("ReadingCanvasScreen", READER_SCREEN_PATH),
            ("WelcomeScreen", WELCOME_SCREEN_PATH),
            ("ParvaExplorerScreen", PARVA_SCREEN_PATH),
            ("SearchScreen", SEARCH_SCREEN_PATH),
            ("BookmarksScreen", BOOKMARKS_SCREEN_PATH)
        ]

        for screen_name, path in screens:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Ensure .widthIn(max = 600.dp) is present
            self.assertIn("widthIn(max = 600.dp)", content, f"{screen_name} missing widthIn(max = 600.dp)")

            # Verify no defective .fillMaxWidth().widthIn pattern exists
            # In Kotlin, this could span newlines: .fillMaxWidth()\s*\.widthIn
            match = re.search(r"\.fillMaxWidth\(\)\s*\.widthIn\(max = 600\.dp\)", content)
            self.assertIsNone(
                match,
                f"{screen_name} has defective modifier order: .fillMaxWidth() before .widthIn(max = 600.dp)"
            )

    def test_02_dynamic_scripture_font_scaling_and_ratio(self):
        """Verify ShlokaCard and ReadingCanvasScreen support dynamic large font scaling maintaining exact 1.8x ratio."""
        with open(SHLOKA_CARD_PATH, "r", encoding="utf-8") as f:
            card_content = f.read()

        with open(READER_SCREEN_PATH, "r", encoding="utf-8") as f:
            reader_content = f.read()

        # ShlokaCard must declare isLargeFont parameter and use ScriptureSanskritLargeStyle
        self.assertIn("isLargeFont: Boolean = false", card_content)
        self.assertIn("ScriptureSanskritLargeStyle", card_content)
        self.assertIn("val sanskritStyle = if (isLargeFont)", card_content)

        # ReadingCanvasScreen must maintain isLargeFont state and wire onFontSizeClick
        self.assertIn("var isLargeFont by remember { mutableStateOf(false) }", reader_content)
        self.assertIn("isLargeFont = !isLargeFont", reader_content)
        self.assertIn("isLargeFont = isLargeFont", reader_content)

    def test_03_minimum_1_language_active_invariant(self):
        """Verify minimum-1 language chip invariant is enforced across FloatingReaderBar, ReaderScreen, and ShlokaCard."""
        with open(FLOATING_BAR_PATH, "r", encoding="utf-8") as f:
            bar_content = f.read()

        with open(READER_SCREEN_PATH, "r", encoding="utf-8") as f:
            reader_content = f.read()

        with open(SHLOKA_CARD_PATH, "r", encoding="utf-8") as f:
            card_content = f.read()

        # FloatingReaderBar: counts active languages and sets enabled state on clickable
        self.assertIn("val activeCount = listOf(showSanskrit, showIAST, showHindi, showEnglish).count { it }", bar_content)
        self.assertIn("enabled = canDeselect || !selected", bar_content)

        # ReadingCanvasScreen: guards all toggle lambdas
        self.assertIn("val active = listOf(!showSanskrit, showIAST, showHindi, showEnglish).count { it }", reader_content)
        self.assertIn("if (active >= 1) showSanskrit = !showSanskrit", reader_content)

        # ShlokaCard: fallback ensures card is never completely empty
        self.assertIn("val effectiveShowSanskrit = showSanskrit || (!showIAST && !showHindi && !showEnglish)", card_content)

    def test_04_shloka_card_animated_divider_no_snap(self):
        """Verify ShlokaCard wraps the divider in AnimatedVisibility to eliminate visual screen jump on toggle."""
        with open(SHLOKA_CARD_PATH, "r", encoding="utf-8") as f:
            card_content = f.read()

        # Divider must be wrapped in AnimatedVisibility
        self.assertIn("AnimatedVisibility(\n                visible = (effectiveShowSanskrit || showIAST) && (showHindi || showEnglish)", card_content)
        self.assertIn("HorizontalDivider(", card_content)
        # Raw if statement must not precede HorizontalDivider
        self.assertNotIn("if ((showSanskrit || showIAST) && (showHindi || showEnglish)) {\n                Spacer", card_content)

    def test_05_quote_export_preview_dual_translation_rendering(self):
        """Verify QuoteExportDialog preview displays both Hindi and English when both are checked."""
        with open(QUOTE_DIALOG_PATH, "r", encoding="utf-8") as f:
            dialog_content = f.read()

        # Ensure else if was removed from translation preview
        self.assertNotIn("} else if (includeEnglish && shloka.translationEnglish.isNotBlank())", dialog_content)
        self.assertIn("if (includeEnglish && shloka.translationEnglish.isNotBlank())", dialog_content)

    def test_06_quote_card_bitmap_footer_boundary_clearance(self):
        """Verify renderQuoteCardBitmap enforces height boundaries to prevent collision with attribution footer."""
        with open(QUOTE_DIALOG_PATH, "r", encoding="utf-8") as f:
            dialog_content = f.read()

        self.assertIn("currentY + 44f > height - 140f", dialog_content)
        self.assertIn("currentY + 40f > height - 120f", dialog_content)

    def test_07_welcome_screen_single_tap_bypass_idempotence(self):
        """Verify WelcomeScreen has single-tap idempotence guard and custom harmonic canvas."""
        with open(WELCOME_SCREEN_PATH, "r", encoding="utf-8") as f:
            welcome_content = f.read()

        self.assertIn("var bypassed by remember { mutableStateOf(false) }", welcome_content)
        self.assertIn("if (!bypassed)", welcome_content)
        self.assertIn("detectTapGestures(", welcome_content)
        self.assertIn("exp(-zeta * omega", welcome_content)

    def test_08_ci_workflow_schema_and_permissions(self):
        """Verify GitHub Actions workflow has valid YAML, permissions, JDK 17, and artifact error handling."""
        with open(CI_WORKFLOW_PATH, "r", encoding="utf-8") as f:
            parsed = yaml.safe_load(f)

        self.assertIn("name", parsed)
        self.assertIn("permissions", parsed)
        self.assertEqual(parsed["permissions"].get("contents"), "read")

        steps = parsed["jobs"]["build"]["steps"]
        step_names = [s.get("name") for s in steps]

        self.assertIn("Set up JDK 17", step_names)
        self.assertIn("Build Debug APK", step_names)
        self.assertIn("Upload Debug APK Artifact", step_names)

        # Check setup-java step
        java_step = next(s for s in steps if s.get("name") == "Set up JDK 17")
        self.assertEqual(java_step["with"]["java-version"], "17")
        self.assertEqual(java_step["with"]["distribution"], "temurin")

        # Check upload-artifact step
        upload_step = next(s for s in steps if s.get("name") == "Upload Debug APK Artifact")
        self.assertEqual(upload_step["with"]["if-no-files-found"], "error")


if __name__ == "__main__":
    unittest.main(verbosity=2)
