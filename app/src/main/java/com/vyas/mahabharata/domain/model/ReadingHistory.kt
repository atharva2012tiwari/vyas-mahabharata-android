package com.vyas.mahabharata.domain.model

/**
 * Domain model representing reading position and progress for a specific Parva.
 */
data class ReadingHistory(
    val parvaNumber: Int,
    val lastChapterNumber: Int,
    val lastVerseNumber: Int,
    val scrollOffset: Int = 0,
    val updatedAt: Long = System.currentTimeMillis()
)
