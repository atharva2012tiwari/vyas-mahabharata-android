package com.vyas.mahabharata.data.repository

import com.vyas.mahabharata.domain.model.Bookmark
import com.vyas.mahabharata.domain.model.Chapter
import com.vyas.mahabharata.domain.model.Parva
import com.vyas.mahabharata.domain.model.ReadingHistory
import com.vyas.mahabharata.domain.model.Shloka
import com.vyas.mahabharata.domain.model.ShlokaSearchResult
import kotlinx.coroutines.flow.Flow

/**
 * Primary repository coordinating access to offline Mahabharata data:
 * - Parvas metadata and navigation
 * - Chapters within Parvas
 * - 4-language aligned Shlokas
 * - FTS5 full-text search across Sanskrit, IAST, Hindi, and English
 * - Reading history & progress tracking
 * - Bookmarks management
 */
interface MahabharataRepository {

    /**
     * Observes all 18 Parvas sorted by canonical order.
     */
    fun getAllParvas(): Flow<List<Parva>>

    /**
     * Observes a specific Parva by its 1-based number (1 to 18).
     */
    fun getParvaByNumber(number: Int): Flow<Parva?>

    /**
     * Observes all chapters belonging to a given Parva.
     */
    fun getChaptersForParva(parvaNumber: Int): Flow<List<Chapter>>

    /**
     * Observes all shlokas in a given chapter with active bookmark state.
     */
    fun getShlokasForChapter(parvaNumber: Int, chapterNumber: Int): Flow<List<Shloka>>

    /**
     * Executes FTS5 search across all 4 languages/scripts (Sanskrit, IAST, Hindi, English).
     */
    fun searchShlokas(query: String): Flow<List<ShlokaSearchResult>>

    /**
     * Observes reading progress for a given Parva.
     */
    fun getReadingHistory(parvaNumber: Int): Flow<ReadingHistory?>

    /**
     * Observes all reading history records across all Parvas.
     */
    fun getAllReadingHistory(): Flow<List<ReadingHistory>>

    /**
     * Saves or updates the last-read position for a Parva.
     */
    suspend fun saveReadingPosition(
        parvaNumber: Int,
        chapterNumber: Int,
        verseNumber: Int,
        scrollOffset: Int = 0
    )

    /**
     * Observes all user bookmarks with associated verse details.
     */
    fun getBookmarks(): Flow<List<Bookmark>>

    /**
     * Toggles bookmark state for a given shloka ID.
     */
    suspend fun toggleBookmark(
        shlokaId: Long,
        collectionName: String = "Favorites",
        note: String? = null
    )

    /**
     * Fetches a shloka by its canonical tag (e.g. "1.1.1" or "6.25.1").
     */
    suspend fun getShlokaByTag(verseTag: String): Shloka?

    /**
     * Checks if a shloka is currently bookmarked.
     */
    suspend fun isBookmarked(shlokaId: Long): Boolean
}
