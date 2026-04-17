package ru.scp.myapplication.data.repository

import com.google.gson.Gson
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import ru.scp.myapplication.data.local.dao.ChecklistDao
import ru.scp.myapplication.data.local.dao.SyncQueueDao
import ru.scp.myapplication.data.local.entity.ChecklistItemEntity
import ru.scp.myapplication.data.local.entity.SyncQueueEntity
import ru.scp.myapplication.data.mapper.toDomain
import ru.scp.myapplication.data.mapper.toEntity
import ru.scp.myapplication.data.remote.ToirApiService
import ru.scp.myapplication.data.remote.dto.SyncActionPayloadDto
import ru.scp.myapplication.data.sync.SyncScheduler
import ru.scp.myapplication.domain.model.Checklist
import ru.scp.myapplication.domain.model.ChecklistStatus
import ru.scp.myapplication.domain.model.SyncState
import ru.scp.myapplication.domain.repository.ChecklistRepository
import java.time.Instant

class ChecklistRepositoryImpl(
    private val checklistDao: ChecklistDao,
    private val syncQueueDao: SyncQueueDao,
    private val apiService: ToirApiService,
    private val syncScheduler: SyncScheduler,
    private val gson: Gson
) : ChecklistRepository {

    override fun observeChecklist(roundId: String): Flow<Checklist?> =
        checklistDao.observeChecklist(roundId).map { relation -> relation?.toDomain() }

    override suspend fun refreshChecklist(roundId: String) {
        val remoteChecklist = apiService.getChecklist(roundId)
        checklistDao.replaceChecklist(
            checklist = remoteChecklist.toEntity(),
            items = remoteChecklist.items.map { it.toEntity(remoteChecklist.id) }
        )
    }

    override suspend fun updateChecklistItem(checklistId: String, seqNo: Int, checked: Boolean) {
        val item = checklistDao.getChecklistItem(checklistId, seqNo) ?: return
        if (item.answerType != "bool") return

        val now = Instant.now().toString()
        val updatedItem = item.copy(
            resultBoolean = checked,
            updatedAt = now,
            syncState = SyncState.PENDING.name
        )
        checklistDao.insertItems(listOf(updatedItem))

        val checklist = checklistDao.getChecklist(checklistId) ?: return
        val allItems = checklistDao.getChecklistItems(checklistId).replaceItem(updatedItem)
        val boolItems = allItems.filter { it.answerType == "bool" }
        val nextStatus = if (boolItems.isNotEmpty() && boolItems.all { it.resultBoolean == true }) {
            ChecklistStatus.COMPLETED
        } else {
            ChecklistStatus.RUNNING
        }

        checklistDao.upsertChecklist(
            checklist.copy(
                status = nextStatus.rawValue,
                updatedAt = now,
                syncState = SyncState.PENDING.name
            )
        )

        syncQueueDao.insert(
            SyncQueueEntity(
                actionType = "CHECKLIST_ITEM_UPDATED",
                entityId = checklistId,
                payloadJson = gson.toJson(
                    SyncActionPayloadDto(
                        queueId = 0,
                        checklistId = checklistId,
                        seqNo = seqNo,
                        checked = checked,
                        updatedAt = now
                    )
                ),
                status = "pending",
                attempts = 0,
                errorMessage = null,
                createdAt = now,
                updatedAt = now
            )
        )
        syncScheduler.schedule()
    }

    private fun List<ChecklistItemEntity>.replaceItem(updatedItem: ChecklistItemEntity): List<ChecklistItemEntity> =
        map { current ->
            if (current.id == updatedItem.id) updatedItem else current
        }
}
