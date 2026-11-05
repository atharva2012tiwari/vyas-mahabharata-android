package com.vyas.mahabharata.data.local.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey
import com.vyas.mahabharata.domain.model.Parva

@Entity(
    tableName = "parvas",
    indices = [
        Index(value = ["number"], unique = true)
    ]
)
data class ParvaEntity(
    @PrimaryKey
    @ColumnInfo(name = "id")
    val id: Long,

    @ColumnInfo(name = "number")
    val number: Int,

    @ColumnInfo(name = "name_sanskrit")
    val nameSanskrit: String,

    @ColumnInfo(name = "name_hindi")
    val nameHindi: String,

    @ColumnInfo(name = "name_english")
    val nameEnglish: String,

    @ColumnInfo(name = "sub_title")
    val subTitle: String?,

    @ColumnInfo(name = "summary_english")
    val summaryEnglish: String?,

    @ColumnInfo(name = "summary_hindi")
    val summaryHindi: String?,

    @ColumnInfo(name = "color_seed")
    val colorSeed: String?,

    @ColumnInfo(name = "chapter_count", defaultValue = "0")
    val chapterCount: Int = 0,

    @ColumnInfo(name = "shloka_count", defaultValue = "0")
    val shlokaCount: Int = 0
) {
    fun toDomain(): Parva = Parva(
        id = id,
        number = number,
        nameSanskrit = nameSanskrit,
        nameHindi = nameHindi,
        nameEnglish = nameEnglish,
        subTitle = subTitle,
        summaryEnglish = summaryEnglish,
        summaryHindi = summaryHindi,
        colorSeed = colorSeed,
        chapterCount = chapterCount,
        shlokaCount = shlokaCount
    )
}
