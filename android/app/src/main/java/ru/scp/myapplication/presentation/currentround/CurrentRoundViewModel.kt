package ru.scp.myapplication.presentation.currentround

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
import ru.scp.myapplication.domain.model.RoundSheet

data class CurrentRoundUiState(
    val isLoading: Boolean = true,
    val round: RoundSheet? = null,
    val pendingSyncCount: Int = 0,
    val errorMessage: String? = null
)

class CurrentRoundViewModel(
    container: AppContainer
) : ViewModel() {

    private val observeCurrentRoundUseCase = container.observeCurrentRoundUseCase
    private val observePendingSyncCountUseCase = container.observePendingSyncCountUseCase
    private val refreshCurrentRoundUseCase = container.refreshCurrentRoundUseCase
    private val syncPendingUseCase = container.syncPendingUseCase

    private val isRefreshing = MutableStateFlow(true)
    private val errorMessage = MutableStateFlow<String?>(null)

    val uiState: StateFlow<CurrentRoundUiState> = combine(
        observeCurrentRoundUseCase(),
        observePendingSyncCountUseCase(),
        isRefreshing,
        errorMessage
    ) { round, pendingCount, loading, error ->
        CurrentRoundUiState(
            isLoading = loading && round == null,
            round = round,
            pendingSyncCount = pendingCount,
            errorMessage = error
        )
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = CurrentRoundUiState()
    )

    init {
        refresh()
    }

    fun refresh() {
        viewModelScope.launch {
            isRefreshing.value = true
            errorMessage.value = null
            runCatching { refreshCurrentRoundUseCase() }
                .onFailure { errorMessage.value = it.message ?: "Не удалось обновить обходной лист" }
            isRefreshing.value = false
        }
    }

    fun syncNow() {
        viewModelScope.launch {
            runCatching { syncPendingUseCase() }
                .onFailure { errorMessage.value = it.message ?: "Не удалось отправить очередь" }
        }
    }
}

class CurrentRoundViewModelFactory(
    private val container: AppContainer
) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        @Suppress("UNCHECKED_CAST")
        return CurrentRoundViewModel(container) as T
    }
}
