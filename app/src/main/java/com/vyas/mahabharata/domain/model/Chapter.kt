package com.vyas.mahabharata.domain.model

/**
 * Domain model representing an Adhyaya (Chapter) within a Parva.
 */
data class Chapter(
    val id: Long,
    val parvaNumber: Int,
    val chapterNumber: Int,
    val titleSanskrit: String,
    val titleHindi: String,
    val titleEnglish: String,
    val shlokaCount: Int
)
