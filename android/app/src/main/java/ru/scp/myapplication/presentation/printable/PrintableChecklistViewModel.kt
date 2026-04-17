package ru.scp.myapplication.presentation.printable

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

data class PrintableChecklistUiState(
    val isLoading: Boolean = true,
    val checklist: Checklist? = null,
    val errorMessage: String? = null
)

class PrintableChecklistViewModel(
    container: AppContainer,
    private val roundId: String
) : ViewModel() {

    private val observeChecklistUseCase = container.observeChecklistUseCase
    private val refreshChecklistUseCase = container.refreshChecklistUseCase
    private val isRefreshing = MutableStateFlow(true)
    private val errorMessage = MutableStateFlow<String?>(null)

    val uiState: StateFlow<PrintableChecklistUiState> = combine(
        observeChecklistUseCase(roundId),
        isRefreshing,
        errorMessage
    ) { checklist, loading, error ->
        PrintableChecklistUiState(
            isLoading = loading && checklist == null,
            checklist = checklist,
            errorMessage = error
        )
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = PrintableChecklistUiState()
    )

    init {
        refresh()
    }

    fun refresh() {
        viewModelScope.launch {
            isRefreshing.value = true
            errorMessage.value = null
            runCatching { refreshChecklistUseCase(roundId) }
                .onFailure { errorMessage.value = it.message ?: "Не удалось загрузить печатный вид" }
            isRefreshing.value = false
        }
    }
}

class PrintableChecklistViewModelFactory(
    private val container: AppContainer,
    private val roundId: String
) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        @Suppress("UNCHECKED_CAST")
        return PrintableChecklistViewModel(container, roundId) as T
    }
}
