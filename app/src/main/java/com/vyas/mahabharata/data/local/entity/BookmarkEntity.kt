package com.vyas.mahabharata.data.local.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey
import com.vyas.mahabharata.domain.model.Bookmark
import com.vyas.mahabharata.domain.model.Shloka

@Entity(
    tableName = "bookmarks",
    foreignKeys = [
        ForeignKey(
            entity = ShlokaEntity::class,
            parentColumns = ["id"],
            childColumns = ["shloka_id"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [
        Index(value = ["shloka_id"], name = "idx_bookmark_shloka_id")
    ]
)
data class BookmarkEntity(
    @PrimaryKey(autoGenerate = true)
    @ColumnInfo(name = "id")
    val id: Long = 0,

    @ColumnInfo(name = "shloka_id")
    val shlokaId: Long,

    @ColumnInfo(name = "collection_name", defaultValue = "'Favorites'")
    val collectionName: String = "Favorites",

    @ColumnInfo(name = "user_note")
    val userNote: String? = null,

    @ColumnInfo(name = "created_at")
    val createdAt: Long = System.currentTimeMillis()
) {
    fun toDomain(shloka: Shloka? = null): Bookmark = Bookmark(
        id = id,
        shlokaId = shlokaId,
        collectionName = collectionName,
        userNote = userNote,
        createdAt = createdAt,
        shloka = shloka
    )
}
