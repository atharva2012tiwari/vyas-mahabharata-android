package com.vyas.mahabharata.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.text.PlatformTextStyle
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.LineHeightStyle
import androidx.compose.ui.unit.sp

// ==========================================
// 1.8x LINE-HEIGHT SCRIPTURE TYPOGRAPHY
// Prevents Devanagari Shirorekha-matra clipping
// ==========================================

val DevanagariLineHeightStyle = LineHeightStyle(
    alignment = LineHeightStyle.Alignment.Center,
    trim = LineHeightStyle.Trim.None
)

val DevanagariPlatformTextStyle = PlatformTextStyle(
    includeFontPadding = false
)

val ScriptureSanskritStyle = TextStyle(
    fontFamily = FontFamily.Serif,
    fontWeight = FontWeight.Normal,
    fontSize = 20.sp,
    lineHeight = 36.sp, // 1.8x line-height ratio
    letterSpacing = 0.5.sp,
    platformStyle = DevanagariPlatformTextStyle,
    lineHeightStyle = DevanagariLineHeightStyle
)

val ScriptureSanskritLargeStyle = TextStyle(
    fontFamily = FontFamily.Serif,
    fontWeight = FontWeight.SemiBold,
    fontSize = 24.sp,
    lineHeight = 43.2.sp, // 1.8x line-height ratio
    letterSpacing = 0.5.sp,
    platformStyle = DevanagariPlatformTextStyle,
    lineHeightStyle = DevanagariLineHeightStyle
)

val ScriptureSanskritDisplayStyle = TextStyle(
    fontFamily = FontFamily.Serif,
    fontWeight = FontWeight.SemiBold,
    fontSize = 22.sp,
    lineHeight = 39.6.sp, // 1.8x line-height ratio (22 * 1.8 = 39.6)
    letterSpacing = 0.5.sp,
    platformStyle = DevanagariPlatformTextStyle,
    lineHeightStyle = DevanagariLineHeightStyle
)

val ScriptureIASTStyle = TextStyle(
    fontFamily = FontFamily.Serif,
    fontStyle = FontStyle.Italic,
    fontWeight = FontWeight.Normal,
    fontSize = 15.sp,
    lineHeight = 25.sp, // 1.66x ratio
    letterSpacing = 0.3.sp,
    platformStyle = DevanagariPlatformTextStyle,
    lineHeightStyle = DevanagariLineHeightStyle
)

val ScriptureHindiStyle = TextStyle(
    fontFamily = FontFamily.SansSerif,
    fontWeight = FontWeight.Normal,
    fontSize = 16.sp,
    lineHeight = 28.sp, // 1.75x ratio
    letterSpacing = 0.2.sp,
    platformStyle = DevanagariPlatformTextStyle,
    lineHeightStyle = DevanagariLineHeightStyle
)

val ScriptureEnglishStyle = TextStyle(
    fontFamily = FontFamily.Serif,
    fontWeight = FontWeight.Normal,
    fontSize = 16.sp,
    lineHeight = 26.sp, // 1.625x ratio
    letterSpacing = 0.2.sp,
    platformStyle = DevanagariPlatformTextStyle,
    lineHeightStyle = DevanagariLineHeightStyle
)

val SpeakerHeadingStyle = TextStyle(
    fontFamily = FontFamily.SansSerif,
    fontWeight = FontWeight.SemiBold,
    fontSize = 14.sp,
    lineHeight = 20.sp,
    letterSpacing = 0.8.sp,
    platformStyle = DevanagariPlatformTextStyle,
    lineHeightStyle = DevanagariLineHeightStyle
)

// Complete Material 3 Expressive Typography System (15 scales + scripture tokens)
val VyasTypography = Typography(
    displayLarge = TextStyle(
        fontFamily = FontFamily.Serif,
        fontWeight = FontWeight.Bold,
        fontSize = 40.sp,
        lineHeight = 52.sp,
        letterSpacing = (-0.5).sp,
        platformStyle = DevanagariPlatformTextStyle,
        lineHeightStyle = DevanagariLineHeightStyle
    ),
    displayMedium = TextStyle(
        fontFamily = FontFamily.Serif,
        fontWeight = FontWeight.SemiBold,
        fontSize = 32.sp,
        lineHeight = 44.sp,
        letterSpacing = (-0.25).sp,
        platformStyle = DevanagariPlatformTextStyle,
        lineHeightStyle = DevanagariLineHeightStyle
    ),
    displaySmall = TextStyle(
        fontFamily = FontFamily.Serif,
        fontWeight = FontWeight.Medium,
        fontSize = 28.sp,
        lineHeight = 38.sp,
        letterSpacing = 0.sp,
        platformStyle = DevanagariPlatformTextStyle,
        lineHeightStyle = DevanagariLineHeightStyle
    ),
    headlineLarge = TextStyle(
        fontFamily = FontFamily.Serif,
        fontWeight = FontWeight.SemiBold,
        fontSize = 28.sp,
        lineHeight = 38.sp,
        letterSpacing = 0.sp,
        platformStyle = DevanagariPlatformTextStyle,
        lineHeightStyle = DevanagariLineHeightStyle
    ),
    headlineMedium = TextStyle(
        fontFamily = FontFamily.Serif,
        fontWeight = FontWeight.Medium,
        fontSize = 24.sp,
        lineHeight = 34.sp,
        letterSpacing = 0.sp,
        platformStyle = DevanagariPlatformTextStyle,
        lineHeightStyle = DevanagariLineHeightStyle
    ),
    headlineSmall = TextStyle(
        fontFamily = FontFamily.Serif,
        fontWeight = FontWeight.Medium,
        fontSize = 20.sp,
        lineHeight = 28.sp,
        letterSpacing = 0.sp,
        platformStyle = DevanagariPlatformTextStyle,
        lineHeightStyle = DevanagariLineHeightStyle
    ),
    titleLarge = TextStyle(
        fontFamily = FontFamily.Serif,
        fontWeight = FontWeight.SemiBold,
        fontSize = 20.sp,
        lineHeight = 28.sp,
        letterSpacing = 0.sp,
        platformStyle = DevanagariPlatformTextStyle,
        lineHeightStyle = DevanagariLineHeightStyle
    ),
    titleMedium = TextStyle(
        fontFamily = FontFamily.SansSerif,
        fontWeight = FontWeight.Medium,
        fontSize = 16.sp,
        lineHeight = 24.sp,
        letterSpacing = 0.15.sp,
        platformStyle = DevanagariPlatformTextStyle,
        lineHeightStyle = DevanagariLineHeightStyle
    ),
    titleSmall = TextStyle(
        fontFamily = FontFamily.SansSerif,
        fontWeight = FontWeight.Medium,
        fontSize = 14.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.1.sp,
        platformStyle = DevanagariPlatformTextStyle,
        lineHeightStyle = DevanagariLineHeightStyle
    ),
    bodyLarge = ScriptureEnglishStyle,
    bodyMedium = ScriptureHindiStyle,
    bodySmall = TextStyle(
        fontFamily = FontFamily.SansSerif,
        fontWeight = FontWeight.Normal,
        fontSize = 12.sp,
        lineHeight = 16.sp,
        letterSpacing = 0.4.sp,
        platformStyle = DevanagariPlatformTextStyle,
        lineHeightStyle = DevanagariLineHeightStyle
    ),
    labelLarge = TextStyle(
        fontFamily = FontFamily.SansSerif,
        fontWeight = FontWeight.SemiBold,
        fontSize = 14.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.5.sp,
        platformStyle = DevanagariPlatformTextStyle,
        lineHeightStyle = DevanagariLineHeightStyle
    ),
    labelMedium = TextStyle(
        fontFamily = FontFamily.SansSerif,
        fontWeight = FontWeight.Medium,
        fontSize = 12.sp,
        lineHeight = 16.sp,
        letterSpacing = 0.5.sp,
        platformStyle = DevanagariPlatformTextStyle,
        lineHeightStyle = DevanagariLineHeightStyle
    ),
    labelSmall = TextStyle(
        fontFamily = FontFamily.SansSerif,
        fontWeight = FontWeight.Medium,
        fontSize = 11.sp,
        lineHeight = 16.sp,
        letterSpacing = 0.5.sp,
        platformStyle = DevanagariPlatformTextStyle,
        lineHeightStyle = DevanagariLineHeightStyle
    )
)

// =====================================================================
// MATERIAL 3 EXPRESSIVE: 15 EMPHASIZED TYPE STYLES (COMPLETING 30 SCALES)
// =====================================================================

val DisplayLargeEmphasized = TextStyle(
    fontFamily = FontFamily.Serif,
    fontWeight = FontWeight.ExtraBold,
    fontSize = 40.sp,
    lineHeight = 52.sp,
    letterSpacing = (-0.5).sp,
    platformStyle = DevanagariPlatformTextStyle,
    lineHeightStyle = DevanagariLineHeightStyle
)

val DisplayMediumEmphasized = TextStyle(
    fontFamily = FontFamily.Serif,
    fontWeight = FontWeight.Bold,
    fontSize = 32.sp,
    lineHeight = 44.sp,
    letterSpacing = (-0.25).sp,
    platformStyle = DevanagariPlatformTextStyle,
    lineHeightStyle = DevanagariLineHeightStyle
)

val DisplaySmallEmphasized = TextStyle(
    fontFamily = FontFamily.Serif,
    fontWeight = FontWeight.Bold,
    fontSize = 28.sp,
    lineHeight = 38.sp,
    letterSpacing = 0.sp,
    platformStyle = DevanagariPlatformTextStyle,
    lineHeightStyle = DevanagariLineHeightStyle
)

val HeadlineLargeEmphasized = TextStyle(
    fontFamily = FontFamily.Serif,
    fontWeight = FontWeight.Bold,
    fontSize = 28.sp,
    lineHeight = 38.sp,
    letterSpacing = 0.sp,
    platformStyle = DevanagariPlatformTextStyle,
    lineHeightStyle = DevanagariLineHeightStyle
)

val HeadlineMediumEmphasized = TextStyle(
    fontFamily = FontFamily.Serif,
    fontWeight = FontWeight.SemiBold,
    fontSize = 24.sp,
    lineHeight = 34.sp,
    letterSpacing = 0.sp,
    platformStyle = DevanagariPlatformTextStyle,
    lineHeightStyle = DevanagariLineHeightStyle
)

val HeadlineSmallEmphasized = TextStyle(
    fontFamily = FontFamily.Serif,
    fontWeight = FontWeight.SemiBold,
    fontSize = 20.sp,
    lineHeight = 28.sp,
    letterSpacing = 0.sp,
    platformStyle = DevanagariPlatformTextStyle,
    lineHeightStyle = DevanagariLineHeightStyle
)

val TitleLargeEmphasized = TextStyle(
    fontFamily = FontFamily.Serif,
    fontWeight = FontWeight.Bold,
    fontSize = 20.sp,
    lineHeight = 28.sp,
    letterSpacing = 0.sp,
    platformStyle = DevanagariPlatformTextStyle,
    lineHeightStyle = DevanagariLineHeightStyle
)

val TitleMediumEmphasized = TextStyle(
    fontFamily = FontFamily.SansSerif,
    fontWeight = FontWeight.SemiBold,
    fontSize = 16.sp,
    lineHeight = 24.sp,
    letterSpacing = 0.15.sp,
    platformStyle = DevanagariPlatformTextStyle,
    lineHeightStyle = DevanagariLineHeightStyle
)

val TitleSmallEmphasized = TextStyle(
    fontFamily = FontFamily.SansSerif,
    fontWeight = FontWeight.SemiBold,
    fontSize = 14.sp,
    lineHeight = 20.sp,
    letterSpacing = 0.1.sp,
    platformStyle = DevanagariPlatformTextStyle,
    lineHeightStyle = DevanagariLineHeightStyle
)

val BodyLargeEmphasized = TextStyle(
    fontFamily = FontFamily.Serif,
    fontWeight = FontWeight.SemiBold,
    fontSize = 16.sp,
    lineHeight = 26.sp,
    letterSpacing = 0.2.sp,
    platformStyle = DevanagariPlatformTextStyle,
    lineHeightStyle = DevanagariLineHeightStyle
)

val BodyMediumEmphasized = TextStyle(
    fontFamily = FontFamily.SansSerif,
    fontWeight = FontWeight.Medium,
    fontSize = 16.sp,
    lineHeight = 28.sp,
    letterSpacing = 0.2.sp,
    platformStyle = DevanagariPlatformTextStyle,
    lineHeightStyle = DevanagariLineHeightStyle
)

val BodySmallEmphasized = TextStyle(
    fontFamily = FontFamily.SansSerif,
    fontWeight = FontWeight.Medium,
    fontSize = 12.sp,
    lineHeight = 16.sp,
    letterSpacing = 0.4.sp,
    platformStyle = DevanagariPlatformTextStyle,
    lineHeightStyle = DevanagariLineHeightStyle
)

val LabelLargeEmphasized = TextStyle(
    fontFamily = FontFamily.SansSerif,
    fontWeight = FontWeight.Bold,
    fontSize = 14.sp,
    lineHeight = 20.sp,
    letterSpacing = 0.5.sp,
    platformStyle = DevanagariPlatformTextStyle,
    lineHeightStyle = DevanagariLineHeightStyle
)

val LabelMediumEmphasized = TextStyle(
    fontFamily = FontFamily.SansSerif,
    fontWeight = FontWeight.SemiBold,
    fontSize = 12.sp,
    lineHeight = 16.sp,
    letterSpacing = 0.5.sp,
    platformStyle = DevanagariPlatformTextStyle,
    lineHeightStyle = DevanagariLineHeightStyle
)

val LabelSmallEmphasized = TextStyle(
    fontFamily = FontFamily.SansSerif,
    fontWeight = FontWeight.SemiBold,
    fontSize = 11.sp,
    lineHeight = 16.sp,
    letterSpacing = 0.5.sp,
    platformStyle = DevanagariPlatformTextStyle,
    lineHeightStyle = DevanagariLineHeightStyle
)

/**
 * 30-Scale Material 3 Expressive Typography Hierarchy:
 * 15 Baseline styles (via standard [Typography]) + 15 Emphasized styles.
 */
data class VyasExpressiveTypography(
    val baseline: Typography = VyasTypography,
    val displayLargeEmphasized: TextStyle = DisplayLargeEmphasized,
    val displayMediumEmphasized: TextStyle = DisplayMediumEmphasized,
    val displaySmallEmphasized: TextStyle = DisplaySmallEmphasized,
    val headlineLargeEmphasized: TextStyle = HeadlineLargeEmphasized,
    val headlineMediumEmphasized: TextStyle = HeadlineMediumEmphasized,
    val headlineSmallEmphasized: TextStyle = HeadlineSmallEmphasized,
    val titleLargeEmphasized: TextStyle = TitleLargeEmphasized,
    val titleMediumEmphasized: TextStyle = TitleMediumEmphasized,
    val titleSmallEmphasized: TextStyle = TitleSmallEmphasized,
    val bodyLargeEmphasized: TextStyle = BodyLargeEmphasized,
    val bodyMediumEmphasized: TextStyle = BodyMediumEmphasized,
    val bodySmallEmphasized: TextStyle = BodySmallEmphasized,
    val labelLargeEmphasized: TextStyle = LabelLargeEmphasized,
    val labelMediumEmphasized: TextStyle = LabelMediumEmphasized,
    val labelSmallEmphasized: TextStyle = LabelSmallEmphasized
)

val ExpressiveTypography = VyasExpressiveTypography()

val LocalExpressiveTypography = staticCompositionLocalOf { ExpressiveTypography }
