package com.vyas.mahabharata.data.local.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.PrimaryKey
import com.vyas.mahabharata.domain.model.ReadingHistory

@Entity(tableName = "reading_history")
data class ReadingHistoryEntity(
    @PrimaryKey
    @ColumnInfo(name = "parva_number")
    val parvaNumber: Int,

    @ColumnInfo(name = "last_chapter_number")
    val lastChapterNumber: Int,

    @ColumnInfo(name = "last_verse_number")
    val lastVerseNumber: Int,

    @ColumnInfo(name = "scroll_offset", defaultValue = "0")
    val scrollOffset: Int = 0,

    @ColumnInfo(name = "updated_at")
    val updatedAt: Long = System.currentTimeMillis()
) {
    fun toDomain(): ReadingHistory = ReadingHistory(
        parvaNumber = parvaNumber,
        lastChapterNumber = lastChapterNumber,
        lastVerseNumber = lastVerseNumber,
        scrollOffset = scrollOffset,
        updatedAt = updatedAt
    )
}
