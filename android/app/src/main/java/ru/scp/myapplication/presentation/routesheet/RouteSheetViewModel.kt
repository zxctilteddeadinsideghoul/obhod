package ru.scp.myapplication.presentation.routesheet

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
import ru.scp.myapplication.domain.model.RouteSheet

data class RouteSheetUiState(
    val isLoading: Boolean = true,
    val route: RouteSheet? = null,
    val errorMessage: String? = null
)

class RouteSheetViewModel(
    container: AppContainer,
    private val routeId: String
) : ViewModel() {

    private val observeRouteUseCase = container.observeRouteUseCase
    private val refreshRouteUseCase = container.refreshRouteUseCase
    private val isRefreshing = MutableStateFlow(true)
    private val errorMessage = MutableStateFlow<String?>(null)

    val uiState: StateFlow<RouteSheetUiState> = combine(
        observeRouteUseCase(routeId),
        isRefreshing,
        errorMessage
    ) { route, loading, error ->
        RouteSheetUiState(
            isLoading = loading && route == null,
            route = route,
            errorMessage = error
        )
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = RouteSheetUiState()
    )

    init {
        refresh()
    }

    fun refresh() {
        viewModelScope.launch {
            isRefreshing.value = true
            errorMessage.value = null
            runCatching { refreshRouteUseCase(routeId) }
                .onFailure { errorMessage.value = it.message ?: "Не удалось обновить маршрут" }
            isRefreshing.value = false
        }
    }
}

class RouteSheetViewModelFactory(
    private val container: AppContainer,
    private val routeId: String
) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        @Suppress("UNCHECKED_CAST")
        return RouteSheetViewModel(container, routeId) as T
    }
}
