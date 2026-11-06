# Keep Room SQLite schemas, DAOs, and entities
-keep class com.vyas.mahabharata.data.local.entity.** { *; }
-keep class com.vyas.mahabharata.data.local.dao.** { *; }
-keep class com.vyas.mahabharata.data.local.** { *; }
-keep class com.vyas.mahabharata.domain.model.** { *; }
-keep class androidx.room.** { *; }

# Preserve Compose Runtime and reflection
-keep class androidx.compose.runtime.** { *; }
-dontwarn androidx.room.**
