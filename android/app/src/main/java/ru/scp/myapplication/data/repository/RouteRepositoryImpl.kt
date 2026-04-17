package ru.scp.myapplication.data.repository

import com.google.gson.Gson
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import ru.scp.myapplication.data.local.dao.RouteSheetDao
import ru.scp.myapplication.data.mapper.toDomain
import ru.scp.myapplication.data.mapper.toEntity
import ru.scp.myapplication.data.remote.ToirApiService
import ru.scp.myapplication.domain.model.RouteSheet
import ru.scp.myapplication.domain.repository.RouteRepository

class RouteRepositoryImpl(
    private val routeSheetDao: RouteSheetDao,
    private val apiService: ToirApiService,
    private val gson: Gson
) : RouteRepository {

    override fun observeRoute(routeId: String): Flow<RouteSheet?> =
        routeSheetDao.observeRoute(routeId).map { entity -> entity?.toDomain(gson) }

    override suspend fun refreshRoute(routeId: String) {
        routeSheetDao.upsert(apiService.getRoute(routeId).toEntity(gson))
    }
}
