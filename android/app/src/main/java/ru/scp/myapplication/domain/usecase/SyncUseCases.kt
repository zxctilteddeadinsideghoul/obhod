package ru.scp.myapplication.domain.usecase

import kotlinx.coroutines.flow.Flow
import ru.scp.myapplication.domain.repository.SyncRepository

class ObservePendingSyncCountUseCase(
    private val repository: SyncRepository
) {
    operator fun invoke(): Flow<Int> = repository.observePendingCount()
}

class SyncPendingUseCase(
    private val repository: SyncRepository
) {
    suspend operator fun invoke() = repository.syncPending()
}

class EnqueueSyncUseCase(
    private val repository: SyncRepository
) {
    suspend operator fun invoke() = repository.enqueueSync()
}
