package com.vyas.mahabharata.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.vyas.mahabharata.data.local.entity.ReadingHistoryEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface ReadingHistoryDao {

    @Query("SELECT * FROM reading_history WHERE parva_number = :parvaNumber LIMIT 1")
    fun getHistoryForParva(parvaNumber: Int): Flow<ReadingHistoryEntity?>

    @Query("SELECT * FROM reading_history WHERE parva_number = :parvaNumber LIMIT 1")
    suspend fun getHistoryForParvaSync(parvaNumber: Int): ReadingHistoryEntity?

    @Query("SELECT * FROM reading_history ORDER BY updated_at DESC")
    fun getAllHistory(): Flow<List<ReadingHistoryEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun saveProgress(history: ReadingHistoryEntity)

    @Query("DELETE FROM reading_history WHERE parva_number = :parvaNumber")
    suspend fun clearHistoryForParva(parvaNumber: Int)
}
