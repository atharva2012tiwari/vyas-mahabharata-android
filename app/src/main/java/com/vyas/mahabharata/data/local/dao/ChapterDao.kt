package com.vyas.mahabharata.data.local.dao

import androidx.room.Dao
import androidx.room.Query
import com.vyas.mahabharata.data.local.entity.ChapterEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface ChapterDao {

    @Query("SELECT * FROM chapters WHERE parva_number = :parvaNumber ORDER BY chapter_number ASC")
    fun getChaptersForParva(parvaNumber: Int): Flow<List<ChapterEntity>>

    @Query("SELECT * FROM chapters WHERE parva_number = :parvaNumber AND chapter_number = :chapterNumber LIMIT 1")
    suspend fun getChapter(parvaNumber: Int, chapterNumber: Int): ChapterEntity?

    @Query("SELECT * FROM chapters WHERE id = :id LIMIT 1")
    suspend fun getChapterById(id: Long): ChapterEntity?
}
