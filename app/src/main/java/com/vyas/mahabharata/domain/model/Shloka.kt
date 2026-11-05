package com.vyas.mahabharata.domain.model

/**
 * Domain model representing a single Shloka (Verse) with 4-way language alignment:
 * 1. Sanskrit Devanagari (मूल श्लोक)
 * 2. Roman IAST Transliteration (with diacritics)
 * 3. Hindi Translation (Gita Press tradition)
 * 4. English Translation (K.M. Ganguli / M.N. Dutt)
 */
data class Shloka(
    val id: Long,
    val parvaNumber: Int,
    val chapterNumber: Int,
    val verseNumber: Int,
    val verseTag: String,
    val speaker: String?,
    val sanskritDevanagari: String,
    val sanskritIast: String,
    val translationHindi: String,
    val translationEnglish: String,
    val isBookmarked: Boolean = false
)
