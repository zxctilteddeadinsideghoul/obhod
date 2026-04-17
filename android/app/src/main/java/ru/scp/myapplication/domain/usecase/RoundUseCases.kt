package ru.scp.myapplication.domain.usecase

import kotlinx.coroutines.flow.Flow
import ru.scp.myapplication.domain.model.RoundSheet
import ru.scp.myapplication.domain.repository.RoundRepository

class ObserveCurrentRoundUseCase(
    private val repository: RoundRepository
) {
    operator fun invoke(): Flow<RoundSheet?> = repository.observeCurrentRound()
}

class RefreshCurrentRoundUseCase(
    private val repository: RoundRepository
) {
    suspend operator fun invoke() = repository.refreshCurrentRound()
}
