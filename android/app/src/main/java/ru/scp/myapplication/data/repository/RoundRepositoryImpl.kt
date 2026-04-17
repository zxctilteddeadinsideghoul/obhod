package ru.scp.myapplication.data.repository

import com.google.gson.Gson
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import ru.scp.myapplication.data.local.dao.RoundSheetDao
import ru.scp.myapplication.data.mapper.toDomain
import ru.scp.myapplication.data.mapper.toEntity
import ru.scp.myapplication.data.remote.ToirApiService
import ru.scp.myapplication.domain.model.RoundSheet
import ru.scp.myapplication.domain.repository.RoundRepository

class RoundRepositoryImpl(
    private val roundSheetDao: RoundSheetDao,
    private val apiService: ToirApiService,
    private val gson: Gson
) : RoundRepository {

    override fun observeCurrentRound(): Flow<RoundSheet?> =
        roundSheetDao.observeCurrentRound().map { entity -> entity?.toDomain(gson) }

    override suspend fun refreshCurrentRound() {
        roundSheetDao.upsert(apiService.getCurrentRound().toEntity(gson))
    }
}
