package ru.scp.myapplication.presentation.checklist

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import ru.scp.myapplication.core.di.AppContainer
import ru.scp.myapplication.domain.model.Checklist

data class ChecklistUiState(
    val isLoading: Boolean = true,
    val checklist: Checklist? = null,
    val pendingSyncCount: Int = 0,
    val errorMessage: String? = null
)

class ChecklistViewModel(
    container: AppContainer,
    private val roundId: String
) : ViewModel() {

    private val observeChecklistUseCase = container.observeChecklistUseCase
    private val observePendingSyncCountUseCase = container.observePendingSyncCountUseCase
    private val refreshChecklistUseCase = container.refreshChecklistUseCase
    private val updateChecklistItemUseCase = container.updateChecklistItemUseCase
    private val syncPendingUseCase = container.syncPendingUseCase
    private val isRefreshing = MutableStateFlow(true)
    private val errorMessage = MutableStateFlow<String?>(null)

    val uiState: StateFlow<ChecklistUiState> = combine(
        observeChecklistUseCase(roundId),
        observePendingSyncCountUseCase(),
        isRefreshing,
        errorMessage
    ) { checklist, pendingCount, loading, error ->
        ChecklistUiState(
            isLoading = loading && checklist == null,
            checklist = checklist,
            pendingSyncCount = pendingCount,
            errorMessage = error
        )
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = ChecklistUiState()
    )

    init {
        refresh()
    }

    fun refresh() {
        viewModelScope.launch {
            isRefreshing.value = true
            errorMessage.value = null
            runCatching { refreshChecklistUseCase(roundId) }
                .onFailure { errorMessage.value = it.message ?: "Не удалось обновить чек-лист" }
            isRefreshing.value = false
        }
    }

    fun toggleItem(checklistId: String, seqNo: Int, checked: Boolean) {
        viewModelScope.launch {
            runCatching { updateChecklistItemUseCase(checklistId, seqNo, checked) }
                .onFailure { errorMessage.value = it.message ?: "Не удалось сохранить отметку" }
        }
    }

    fun syncNow() {
        viewModelScope.launch {
            runCatching { syncPendingUseCase() }
                .onFailure { errorMessage.value = it.message ?: "Не удалось отправить очередь" }
        }
    }
}

class ChecklistViewModelFactory(
    private val container: AppContainer,
    private val roundId: String
) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        @Suppress("UNCHECKED_CAST")
        return ChecklistViewModel(container, roundId) as T
    }
}
