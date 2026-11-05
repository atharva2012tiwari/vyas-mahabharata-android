package com.vyas.mahabharata.data.local.dao

import androidx.room.Dao
import androidx.room.Query
import com.vyas.mahabharata.data.local.entity.ShlokaEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface ShlokaDao {

    @Query("""
        SELECT * FROM shlokas 
        WHERE parva_number = :parvaNumber AND chapter_number = :chapterNumber 
        ORDER BY verse_number ASC
    """)
    fun getShlokasForChapter(parvaNumber: Int, chapterNumber: Int): Flow<List<ShlokaEntity>>

    @Query("SELECT * FROM shlokas WHERE verse_tag = :verseTag LIMIT 1")
    suspend fun getShlokaByTag(verseTag: String): ShlokaEntity?

    @Query("SELECT * FROM shlokas WHERE id = :id LIMIT 1")
    suspend fun getShlokaById(id: Long): ShlokaEntity?

    @Query("""
        SELECT s.* FROM shlokas s
        JOIN shlokas_fts fts ON s.id = fts.rowid
        WHERE shlokas_fts MATCH :query
        ORDER BY s.parva_number ASC, s.chapter_number ASC, s.verse_number ASC
        LIMIT :limit OFFSET :offset
    """)
    suspend fun searchShlokas(query: String, limit: Int = 50, offset: Int = 0): List<ShlokaEntity>

    @Query("SELECT COUNT(*) FROM shlokas WHERE parva_number = :parvaNumber AND chapter_number = :chapterNumber")
    suspend fun getShlokaCountForChapter(parvaNumber: Int, chapterNumber: Int): Int

    @Query("SELECT COUNT(*) FROM shlokas")
    suspend fun getTotalShlokaCount(): Int
}
