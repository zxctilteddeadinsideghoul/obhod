package ru.scp.myapplication.domain.usecase

import kotlinx.coroutines.flow.Flow
import ru.scp.myapplication.domain.model.RouteSheet
import ru.scp.myapplication.domain.repository.RouteRepository

class ObserveRouteUseCase(
    private val repository: RouteRepository
) {
    operator fun invoke(routeId: String): Flow<RouteSheet?> = repository.observeRoute(routeId)
}

class RefreshRouteUseCase(
    private val repository: RouteRepository
) {
    suspend operator fun invoke(routeId: String) = repository.refreshRoute(routeId)
}
