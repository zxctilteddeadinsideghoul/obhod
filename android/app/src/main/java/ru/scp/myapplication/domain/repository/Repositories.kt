package ru.scp.myapplication.domain.repository

import kotlinx.coroutines.flow.Flow
import ru.scp.myapplication.domain.model.Checklist
import ru.scp.myapplication.domain.model.RoundSheet
import ru.scp.myapplication.domain.model.RouteSheet

interface RoundRepository {
    fun observeCurrentRound(): Flow<RoundSheet?>
    suspend fun refreshCurrentRound()
}

interface RouteRepository {
    fun observeRoute(routeId: String): Flow<RouteSheet?>
    suspend fun refreshRoute(routeId: String)
}

interface ChecklistRepository {
    fun observeChecklist(roundId: String): Flow<Checklist?>
    suspend fun refreshChecklist(roundId: String)
    suspend fun updateChecklistItem(checklistId: String, seqNo: Int, checked: Boolean)
}

interface SyncRepository {
    fun observePendingCount(): Flow<Int>
    suspend fun syncPending()
    suspend fun enqueueSync()
}
