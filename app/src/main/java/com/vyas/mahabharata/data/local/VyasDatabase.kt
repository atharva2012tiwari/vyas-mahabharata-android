package com.vyas.mahabharata.data.local

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import com.vyas.mahabharata.data.local.dao.BookmarkDao
import com.vyas.mahabharata.data.local.dao.ChapterDao
import com.vyas.mahabharata.data.local.dao.ParvaDao
import com.vyas.mahabharata.data.local.dao.ReadingHistoryDao
import com.vyas.mahabharata.data.local.dao.ShlokaDao
import com.vyas.mahabharata.data.local.entity.BookmarkEntity
import com.vyas.mahabharata.data.local.entity.ChapterEntity
import com.vyas.mahabharata.data.local.entity.ParvaEntity
import com.vyas.mahabharata.data.local.entity.ReadingHistoryEntity
import com.vyas.mahabharata.data.local.entity.ShlokaEntity

/**
 * Main Room database instance for the Vyasa Mahabharata application.
 * Pre-packaged from asset database 'mahabharata.db' with FTS5 search support.
 */
@Database(
    entities = [
        ParvaEntity::class,
        ChapterEntity::class,
        ShlokaEntity::class,
        BookmarkEntity::class,
        ReadingHistoryEntity::class
    ],
    version = 1,
    exportSchema = false
)
abstract class VyasDatabase : RoomDatabase() {

    abstract fun parvaDao(): ParvaDao
    abstract fun chapterDao(): ChapterDao
    abstract fun shlokaDao(): ShlokaDao
    abstract fun bookmarkDao(): BookmarkDao
    abstract fun readingHistoryDao(): ReadingHistoryDao

    companion object {
        const val DATABASE_NAME = "mahabharata.db"

        @Volatile
        private var INSTANCE: VyasDatabase? = null

        fun getInstance(context: Context): VyasDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    VyasDatabase::class.java,
                    DATABASE_NAME
                )
                    .createFromAsset("mahabharata.db")
                    .fallbackToDestructiveMigration()
                    .build()
                INSTANCE = instance
                instance
            }
        }
    }
}
