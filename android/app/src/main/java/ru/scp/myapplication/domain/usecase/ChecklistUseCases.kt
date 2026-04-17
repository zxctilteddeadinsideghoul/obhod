package ru.scp.myapplication.domain.usecase

import kotlinx.coroutines.flow.Flow
import ru.scp.myapplication.domain.model.Checklist
import ru.scp.myapplication.domain.repository.ChecklistRepository

class ObserveChecklistUseCase(
    private val repository: ChecklistRepository
) {
    operator fun invoke(roundId: String): Flow<Checklist?> = repository.observeChecklist(roundId)
}

class RefreshChecklistUseCase(
    private val repository: ChecklistRepository
) {
    suspend operator fun invoke(roundId: String) = repository.refreshChecklist(roundId)
}

class UpdateChecklistItemUseCase(
    private val repository: ChecklistRepository
) {
    suspend operator fun invoke(checklistId: String, seqNo: Int, checked: Boolean) {
        repository.updateChecklistItem(checklistId, seqNo, checked)
    }
}
