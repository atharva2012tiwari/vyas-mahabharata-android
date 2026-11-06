package com.vyas.mahabharata.data.repository

import com.vyas.mahabharata.data.local.VyasDatabase
import com.vyas.mahabharata.data.local.dao.BookmarkDao
import com.vyas.mahabharata.data.local.dao.ChapterDao
import com.vyas.mahabharata.data.local.dao.ParvaDao
import com.vyas.mahabharata.data.local.dao.ReadingHistoryDao
import com.vyas.mahabharata.data.local.dao.ShlokaDao
import com.vyas.mahabharata.data.local.entity.BookmarkEntity
import com.vyas.mahabharata.data.local.entity.ReadingHistoryEntity
import com.vyas.mahabharata.data.local.entity.ShlokaEntity
import com.vyas.mahabharata.domain.model.Bookmark
import com.vyas.mahabharata.domain.model.Chapter
import com.vyas.mahabharata.domain.model.Parva
import com.vyas.mahabharata.domain.model.ReadingHistory
import com.vyas.mahabharata.domain.model.Shloka
import com.vyas.mahabharata.domain.model.ShlokaSearchResult
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.flowOn
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.withContext

/**
 * Concrete implementation of [MahabharataRepository] using Room persistence.
 */
class MahabharataRepositoryImpl(
    private val parvaDao: ParvaDao,
    private val chapterDao: ChapterDao,
    private val shlokaDao: ShlokaDao,
    private val bookmarkDao: BookmarkDao,
    private val readingHistoryDao: ReadingHistoryDao,
    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO
) : MahabharataRepository {

    constructor(
        database: VyasDatabase,
        ioDispatcher: CoroutineDispatcher = Dispatchers.IO
    ) : this(
        parvaDao = database.parvaDao(),
        chapterDao = database.chapterDao(),
        shlokaDao = database.shlokaDao(),
        bookmarkDao = database.bookmarkDao(),
        readingHistoryDao = database.readingHistoryDao(),
        ioDispatcher = ioDispatcher
    )

    override fun getAllParvas(): Flow<List<Parva>> {
        return parvaDao.getAllParvas()
            .map { list -> list.map { it.toDomain() } }
            .flowOn(ioDispatcher)
    }

    override fun getParvaByNumber(number: Int): Flow<Parva?> {
        return parvaDao.observeParvaByNumber(number)
            .map { it?.toDomain() }
            .flowOn(ioDispatcher)
    }

    override fun getChaptersForParva(parvaNumber: Int): Flow<List<Chapter>> {
        return chapterDao.getChaptersForParva(parvaNumber)
            .map { list -> list.map { it.toDomain() } }
            .flowOn(ioDispatcher)
    }

    override fun getShlokasForChapter(parvaNumber: Int, chapterNumber: Int): Flow<List<Shloka>> {
        return combine(
            shlokaDao.getShlokasForChapter(parvaNumber, chapterNumber),
            bookmarkDao.getAllBookmarks()
        ) { shlokas, bookmarks ->
            val bookmarkedIds = bookmarks.map { it.shlokaId }.toSet()
            shlokas.map { entity ->
                entity.toDomain(isBookmarked = entity.id in bookmarkedIds)
            }
        }.flowOn(ioDispatcher)
    }

    override fun searchShlokas(query: String): Flow<List<ShlokaSearchResult>> = flow {
        val trimmed = query.trim()
        if (trimmed.isEmpty()) {
            emit(emptyList())
            return@flow
        }

        val entities = shlokaDao.searchShlokas(trimmed, limit = 100)
        val searchResults = entities.map { entity ->
            val isBookmarked = bookmarkDao.isBookmarkedSync(entity.id)
            ShlokaSearchResult(
                shloka = entity.toDomain(isBookmarked = isBookmarked),
                matchSnippet = extractSnippet(entity, trimmed),
                matchedField = detectMatchedField(entity, trimmed)
            )
        }
        emit(searchResults)
    }.flowOn(ioDispatcher)

    override fun getReadingHistory(parvaNumber: Int): Flow<ReadingHistory?> {
        return readingHistoryDao.getHistoryForParva(parvaNumber)
            .map { it?.toDomain() }
            .flowOn(ioDispatcher)
    }

    override fun getAllReadingHistory(): Flow<List<ReadingHistory>> {
        return readingHistoryDao.getAllHistory()
            .map { list -> list.map { it.toDomain() } }
            .flowOn(ioDispatcher)
    }

    override suspend fun saveReadingPosition(
        parvaNumber: Int,
        chapterNumber: Int,
        verseNumber: Int,
        scrollOffset: Int
    ) = withContext(ioDispatcher) {
        readingHistoryDao.saveProgress(
            ReadingHistoryEntity(
                parvaNumber = parvaNumber,
                lastChapterNumber = chapterNumber,
                lastVerseNumber = verseNumber,
                scrollOffset = scrollOffset,
                updatedAt = System.currentTimeMillis()
            )
        )
    }

    override fun getBookmarks(): Flow<List<Bookmark>> {
        return bookmarkDao.getAllBookmarks().map { bookmarkEntities ->
            bookmarkEntities.map { entity ->
                val shloka = shlokaDao.getShlokaById(entity.shlokaId)?.toDomain(isBookmarked = true)
                entity.toDomain(shloka = shloka)
            }
        }.flowOn(ioDispatcher)
    }

    override suspend fun toggleBookmark(
        shlokaId: Long,
        collectionName: String,
        note: String?
    ): Unit = withContext(ioDispatcher) {
        val existing = bookmarkDao.getBookmarkByShlokaId(shlokaId)
        if (existing != null) {
            bookmarkDao.deleteBookmark(existing)
        } else {
            bookmarkDao.insertBookmark(
                BookmarkEntity(
                    shlokaId = shlokaId,
                    collectionName = collectionName,
                    userNote = note,
                    createdAt = System.currentTimeMillis()
                )
            )
        }
        Unit
    }

    override suspend fun getShlokaByTag(verseTag: String): Shloka? = withContext(ioDispatcher) {
        val entity = shlokaDao.getShlokaByTag(verseTag) ?: return@withContext null
        val isBookmarked = bookmarkDao.isBookmarkedSync(entity.id)
        entity.toDomain(isBookmarked = isBookmarked)
    }

    override suspend fun isBookmarked(shlokaId: Long): Boolean = withContext(ioDispatcher) {
        bookmarkDao.isBookmarkedSync(shlokaId)
    }

    private fun sanitizeFts5Query(raw: String): String {
        // Preserve Unicode letters (\p{L}), combining marks/matras (\p{M}), numbers (\p{N}), and whitespace
        val cleaned = raw.replace(Regex("[^\\p{L}\\p{M}\\p{N}\\s]"), "").trim()
        if (cleaned.isEmpty()) return ""
        val rawTokens = cleaned.split("\\s+".toRegex()).filter { it.isNotBlank() }
        if (rawTokens.isEmpty()) return ""

        val processed = mutableListOf<String>()
        for (i in rawTokens.indices) {
            val token = rawTokens[i]
            val upper = token.uppercase()
            when {
                upper == "OR" -> {
                    if (i > 0 && i < rawTokens.size - 1 && processed.isNotEmpty() && processed.last() != "OR") {
                        processed.add("OR")
                    }
                }
                upper == "AND" || upper == "NOT" -> {
                    // Space in FTS5 acts as implicit AND; skip standalone operator to avoid syntax crash
                    continue
                }
                else -> {
                    processed.add("\"$token\"*")
                }
            }
        }
        while (processed.isNotEmpty() && processed.last() == "OR") {
            processed.removeAt(processed.size - 1)
        }
        while (processed.isNotEmpty() && processed.first() == "OR") {
            processed.removeAt(0)
        }
        return processed.joinToString(" ")
    }

    private fun extractSnippet(entity: ShlokaEntity, query: String): String {
        val lowerQuery = query.lowercase()
        val candidates = listOf(
            entity.sanskritDevanagari,
            entity.sanskritIast,
            entity.translationHindi,
            entity.translationEnglish
        )
        for (candidate in candidates) {
            val idx = candidate.lowercase().indexOf(lowerQuery)
            if (idx >= 0) {
                val start = maxOf(0, idx - 30)
                val end = minOf(candidate.length, idx + query.length + 50)
                val prefix = if (start > 0) "…" else ""
                val suffix = if (end < candidate.length) "…" else ""
                return "$prefix${candidate.substring(start, end).trim()}$suffix"
            }
        }
        return entity.translationEnglish.take(80) + "…"
    }

    private fun detectMatchedField(entity: ShlokaEntity, query: String): String {
        val q = query.lowercase()
        return when {
            entity.sanskritDevanagari.lowercase().contains(q) -> "Sanskrit (Devanagari)"
            entity.sanskritIast.lowercase().contains(q) -> "IAST Transliteration"
            entity.translationHindi.lowercase().contains(q) -> "Hindi Translation"
            entity.translationEnglish.lowercase().contains(q) -> "English Translation"
            else -> "Translation"
        }
    }
}
