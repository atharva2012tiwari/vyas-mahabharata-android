package com.vyas.mahabharata.data.local.dao

import androidx.room.Dao
import androidx.room.Query
import com.vyas.mahabharata.data.local.entity.ParvaEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface ParvaDao {

    @Query("SELECT * FROM parvas ORDER BY number ASC")
    fun getAllParvas(): Flow<List<ParvaEntity>>

    @Query("SELECT * FROM parvas WHERE number = :number LIMIT 1")
    suspend fun getParvaByNumber(number: Int): ParvaEntity?

    @Query("SELECT * FROM parvas WHERE number = :number LIMIT 1")
    fun observeParvaByNumber(number: Int): Flow<ParvaEntity?>

    @Query("SELECT COUNT(*) FROM parvas")
    suspend fun getParvaCount(): Int
}
