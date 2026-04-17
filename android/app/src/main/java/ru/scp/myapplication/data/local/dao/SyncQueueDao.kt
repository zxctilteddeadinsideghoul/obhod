package ru.scp.myapplication.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import kotlinx.coroutines.flow.Flow
import ru.scp.myapplication.data.local.entity.SyncQueueEntity

@Dao
interface SyncQueueDao {
    @Query("SELECT COUNT(*) FROM sync_queue WHERE status = 'pending'")
    fun observePendingCount(): Flow<Int>

    @Query("SELECT * FROM sync_queue WHERE status = 'pending' ORDER BY createdAt ASC")
    suspend fun getPendingQueue(): List<SyncQueueEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(queueItem: SyncQueueEntity): Long

    @Query("UPDATE sync_queue SET status = 'synced', errorMessage = NULL, updatedAt = :updatedAt WHERE id IN (:ids)")
    suspend fun markSynced(ids: List<Long>, updatedAt: String)

    @Query("UPDATE sync_queue SET status = 'failed', attempts = attempts + 1, errorMessage = :errorMessage, updatedAt = :updatedAt WHERE id = :id")
    suspend fun markFailed(id: Long, errorMessage: String, updatedAt: String)
}
