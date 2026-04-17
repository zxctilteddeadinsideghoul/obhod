package ru.scp.myapplication.data.repository

import com.google.gson.Gson
import kotlinx.coroutines.flow.Flow
import ru.scp.myapplication.data.local.dao.SyncQueueDao
import ru.scp.myapplication.data.remote.ToirApiService
import ru.scp.myapplication.data.remote.dto.SyncActionPayloadDto
import ru.scp.myapplication.data.remote.dto.SyncBatchRequestDto
import ru.scp.myapplication.data.sync.SyncScheduler
import ru.scp.myapplication.domain.repository.SyncRepository
import java.time.Instant

class SyncRepositoryImpl(
    private val syncQueueDao: SyncQueueDao,
    private val apiService: ToirApiService,
    private val syncScheduler: SyncScheduler,
    private val gson: Gson
) : SyncRepository {

    override fun observePendingCount(): Flow<Int> = syncQueueDao.observePendingCount()

    override suspend fun syncPending() {
        val pendingItems = syncQueueDao.getPendingQueue()
        if (pendingItems.isEmpty()) return

        val payloads = pendingItems.map { queue ->
            gson.fromJson(queue.payloadJson, SyncActionPayloadDto::class.java).copy(queueId = queue.id)
        }

        try {
            val response = apiService.syncChecklist(
                SyncBatchRequestDto(
                    deviceId = "MOB-0091",
                    actions = payloads
                )
            )
            if (response.acceptedIds.isNotEmpty()) {
                syncQueueDao.markSynced(response.acceptedIds, response.serverTimestamp)
            }
            val rejectedIds = pendingItems.map { it.id } - response.acceptedIds.toSet()
            rejectedIds.forEach { rejectedId ->
                syncQueueDao.markFailed(
                    id = rejectedId,
                    errorMessage = "Server did not acknowledge action",
                    updatedAt = response.serverTimestamp
                )
            }
        } catch (error: Exception) {
            val failedAt = Instant.now().toString()
            pendingItems.forEach { pending ->
                syncQueueDao.markFailed(
                    id = pending.id,
                    errorMessage = error.message ?: "Sync failed",
                    updatedAt = failedAt
                )
            }
            throw error
        }
    }

    override suspend fun enqueueSync() {
        syncScheduler.schedule()
    }
}
