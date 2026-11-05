package com.vyas.mahabharata.domain.model

/**
 * Domain model representing a saved shloka bookmark.
 */
data class Bookmark(
    val id: Long,
    val shlokaId: Long,
    val collectionName: String = "Favorites",
    val userNote: String? = null,
    val createdAt: Long = System.currentTimeMillis(),
    val shloka: Shloka? = null
)
