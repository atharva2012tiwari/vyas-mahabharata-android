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
        SELECT * FROM shlokas 
        WHERE sanskrit_devanagari LIKE '%' || :query || '%' 
           OR sanskrit_iast LIKE '%' || :query || '%' 
           OR translation_hindi LIKE '%' || :query || '%' 
           OR translation_english LIKE '%' || :query || '%'
        ORDER BY parva_number ASC, chapter_number ASC, verse_number ASC
        LIMIT :limit OFFSET :offset
    """)
    suspend fun searchShlokas(query: String, limit: Int = 50, offset: Int = 0): List<ShlokaEntity>

    @Query("SELECT COUNT(*) FROM shlokas WHERE parva_number = :parvaNumber AND chapter_number = :chapterNumber")
    suspend fun getShlokaCountForChapter(parvaNumber: Int, chapterNumber: Int): Int

    @Query("SELECT COUNT(*) FROM shlokas")
    suspend fun getTotalShlokaCount(): Int
}
