package com.vyas.mahabharata.domain.model

/**
 * Domain model representing one of the 18 canonical Parvas (Books) of the Vyasa Mahabharata.
 */
data class Parva(
    val id: Long,
    val number: Int,
    val nameSanskrit: String,
    val nameHindi: String,
    val nameEnglish: String,
    val subTitle: String?,
    val summaryEnglish: String?,
    val summaryHindi: String?,
    val colorSeed: String?,
    val chapterCount: Int,
    val shlokaCount: Int
)
