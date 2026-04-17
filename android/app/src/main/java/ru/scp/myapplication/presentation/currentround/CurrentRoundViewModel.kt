package ru.scp.myapplication.presentation.currentround

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import retrofit2.HttpException
import ru.scp.myapplication.BuildConfig
import ru.scp.myapplication.core.di.AppContainer
import ru.scp.myapplication.domain.model.AssignedTask
import ru.scp.myapplication.domain.model.WorkerProfile
import java.io.IOException

data class CurrentRoundUiState(
    val isLoading: Boolean = true,
    val worker: WorkerProfile? = null,
    val tasks: List<AssignedTask> = emptyList(),
    val baseUrl: String = BuildConfig.API_BASE_URL,
    val errorMessage: String? = null
)

class CurrentRoundViewModel(
    container: AppContainer
) : ViewModel() {

    private val repository = container.mobileBackendRepository

    private val _uiState = MutableStateFlow(CurrentRoundUiState())
    val uiState: StateFlow<CurrentRoundUiState> = _uiState.asStateFlow()

    init {
        refresh()
    }

    fun refresh() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            runCatching {
                val worker = repository.getCurrentUser()
                val tasks = repository.getAssignedTasks()
                worker to tasks
            }.onSuccess { (worker, tasks) ->
                _uiState.value = CurrentRoundUiState(
                    isLoading = false,
                    worker = worker,
                    tasks = tasks.sortedBy { it.plannedStart },
                    baseUrl = BuildConfig.API_BASE_URL
                )
            }.onFailure { error ->
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        errorMessage = error.toUserMessage("Не удалось загрузить задания")
                    )
                }
            }
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

private fun Throwable.toUserMessage(fallback: String): String = when (this) {
    is HttpException -> when (code()) {
        401 -> "Backend отклонил токен dev-token"
        403 -> "Backend запретил доступ к данным работника"
        404 -> "Запрошенные данные не найдены на backend"
        else -> "$fallback: HTTP ${code()}"
    }
    is IOException -> "$fallback: нет соединения с сервером ${BuildConfig.API_BASE_URL}"
    else -> message ?: fallback
}
