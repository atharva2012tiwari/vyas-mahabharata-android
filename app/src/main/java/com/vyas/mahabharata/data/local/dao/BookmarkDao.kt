package com.vyas.mahabharata.data.local.dao

import androidx.room.Dao
import androidx.room.Delete
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.vyas.mahabharata.data.local.entity.BookmarkEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface BookmarkDao {

    @Query("SELECT * FROM bookmarks ORDER BY created_at DESC")
    fun getAllBookmarks(): Flow<List<BookmarkEntity>>

    @Query("SELECT * FROM bookmarks WHERE collection_name = :collectionName ORDER BY created_at DESC")
    fun getBookmarksByCollection(collectionName: String): Flow<List<BookmarkEntity>>

    @Query("SELECT * FROM bookmarks WHERE shloka_id = :shlokaId LIMIT 1")
    suspend fun getBookmarkByShlokaId(shlokaId: Long): BookmarkEntity?

    @Query("SELECT EXISTS(SELECT 1 FROM bookmarks WHERE shloka_id = :shlokaId)")
    fun isBookmarked(shlokaId: Long): Flow<Boolean>

    @Query("SELECT EXISTS(SELECT 1 FROM bookmarks WHERE shloka_id = :shlokaId)")
    suspend fun isBookmarkedSync(shlokaId: Long): Boolean

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertBookmark(bookmark: BookmarkEntity): Long

    @Delete
    suspend fun deleteBookmark(bookmark: BookmarkEntity)

    @Query("DELETE FROM bookmarks WHERE shloka_id = :shlokaId")
    suspend fun deleteBookmarkByShlokaId(shlokaId: Long): Int
}
