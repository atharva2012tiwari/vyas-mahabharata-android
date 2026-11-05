package com.vyas.mahabharata.data.local.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey
import com.vyas.mahabharata.domain.model.Shloka

@Entity(
    tableName = "shlokas",
    foreignKeys = [
        ForeignKey(
            entity = ParvaEntity::class,
            parentColumns = ["number"],
            childColumns = ["parva_number"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [
        Index(value = ["parva_number", "chapter_number"], name = "idx_shloka_parva_chapter"),
        Index(value = ["verse_tag"], name = "idx_shloka_verse_tag")
    ]
)
data class ShlokaEntity(
    @PrimaryKey(autoGenerate = true)
    @ColumnInfo(name = "id")
    val id: Long = 0,

    @ColumnInfo(name = "parva_number")
    val parvaNumber: Int,

    @ColumnInfo(name = "chapter_number")
    val chapterNumber: Int,

    @ColumnInfo(name = "verse_number")
    val verseNumber: Int,

    @ColumnInfo(name = "verse_tag")
    val verseTag: String,

    @ColumnInfo(name = "speaker")
    val speaker: String?,

    @ColumnInfo(name = "sanskrit_devanagari")
    val sanskritDevanagari: String,

    @ColumnInfo(name = "sanskrit_iast")
    val sanskritIast: String,

    @ColumnInfo(name = "translation_hindi")
    val translationHindi: String,

    @ColumnInfo(name = "translation_english")
    val translationEnglish: String
) {
    fun toDomain(isBookmarked: Boolean = false): Shloka = Shloka(
        id = id,
        parvaNumber = parvaNumber,
        chapterNumber = chapterNumber,
        verseNumber = verseNumber,
        verseTag = verseTag,
        speaker = speaker,
        sanskritDevanagari = sanskritDevanagari,
        sanskritIast = sanskritIast,
        translationHindi = translationHindi,
        translationEnglish = translationEnglish,
        isBookmarked = isBookmarked
    )
}
