package com.vyas.mahabharata.data.local.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey
import com.vyas.mahabharata.domain.model.Chapter

@Entity(
    tableName = "chapters",
    foreignKeys = [
        ForeignKey(
            entity = ParvaEntity::class,
            parentColumns = ["number"],
            childColumns = ["parva_number"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [
        Index(value = ["parva_number"], name = "idx_chapter_parva_number")
    ]
)
data class ChapterEntity(
    @PrimaryKey(autoGenerate = true)
    @ColumnInfo(name = "id")
    val id: Long = 0,

    @ColumnInfo(name = "parva_number")
    val parvaNumber: Int,

    @ColumnInfo(name = "chapter_number")
    val chapterNumber: Int,

    @ColumnInfo(name = "title_sanskrit")
    val titleSanskrit: String,

    @ColumnInfo(name = "title_hindi")
    val titleHindi: String,

    @ColumnInfo(name = "title_english")
    val titleEnglish: String,

    @ColumnInfo(name = "shloka_count", defaultValue = "0")
    val shlokaCount: Int = 0
) {
    fun toDomain(): Chapter = Chapter(
        id = id,
        parvaNumber = parvaNumber,
        chapterNumber = chapterNumber,
        titleSanskrit = titleSanskrit,
        titleHindi = titleHindi,
        titleEnglish = titleEnglish,
        shlokaCount = shlokaCount
    )
}
