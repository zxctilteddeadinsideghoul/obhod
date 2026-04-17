package ru.scp.myapplication.presentation.checklist

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
import ru.scp.myapplication.domain.model.ChecklistItemResultResponse
import ru.scp.myapplication.domain.model.ConfirmStepResponse
import ru.scp.myapplication.domain.model.EquipmentReadingResponse
import ru.scp.myapplication.domain.model.RouteStepDetails
import ru.scp.myapplication.domain.model.SubmittedChecklistValue
import ru.scp.myapplication.domain.model.TaskDetails
import java.io.IOException

data class ChecklistUiState(
    val isLoading: Boolean = true,
    val isSubmitting: Boolean = false,
    val details: TaskDetails? = null,
    val confirmedStep: ConfirmStepResponse? = null,
    val submittedItems: Map<String, SubmittedChecklistValue> = emptyMap(),
    val readingStatuses: Map<String, EquipmentReadingResponse> = emptyMap(),
    val errorMessage: String? = null,
    val infoMessage: String? = null
) {
    val checklistStatus: String
        get() = confirmedStep?.checklistInstance?.status ?: details?.checklistInstance?.status ?: "draft"

    val checklistCompletionPct: Int
        get() = confirmedStep?.checklistInstance?.completionPct ?: details?.checklistInstance?.completionPct ?: 0

    val visibleChecklistItems = confirmedStep?.checklistTemplate?.items.orEmpty()
}

class ChecklistViewModel(
    container: AppContainer,
    private val roundId: String
) : ViewModel() {

    private val repository = container.mobileBackendRepository

    private val _uiState = MutableStateFlow(ChecklistUiState())
    val uiState: StateFlow<ChecklistUiState> = _uiState.asStateFlow()

    init {
        refresh()
    }

    fun refresh() {
        viewModelScope.launch {
            _uiState.update {
                it.copy(isLoading = true, errorMessage = null, infoMessage = null)
            }
            runCatching { repository.getTaskDetails(roundId) }
                .onSuccess { details ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            details = details,
                            errorMessage = null
                        )
                    }
                }
                .onFailure { error ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            errorMessage = error.toUserMessage("Не удалось загрузить обход")
                        )
                    }
                }
        }
    }

    fun startRound() {
        submitAction("Не удалось запустить обход") {
            repository.startRound(roundId)
            refreshTaskDetails()
            _uiState.update { it.copy(infoMessage = "Обход переведён в работу") }
        }
    }

    fun confirmStep(step: RouteStepDetails, confirmBy: String, scannedValue: String) {
        submitAction("Не удалось подтвердить точку") {
            val response = repository.confirmStep(
                roundId = roundId,
                step = step,
                scannedValue = scannedValue,
                confirmBy = confirmBy
            )
            _uiState.update {
                it.copy(
                    confirmedStep = response,
                    errorMessage = null,
                    infoMessage = "Точка ${step.seqNo} подтверждена"
                )
            }
            refreshTaskDetails()
        }
    }

    fun submitBooleanResult(itemId: String, equipmentId: String, checked: Boolean, comment: String) {
        val checklistInstanceId = _uiState.value.confirmedStep?.checklistInstance?.id ?: return
        submitAction("Не удалось отправить ответ по чек-листу") {
            val response = repository.submitBooleanResult(
                checklistInstanceId = checklistInstanceId,
                itemTemplateId = itemId,
                equipmentId = equipmentId,
                checked = checked,
                comment = comment
            )
            storeChecklistResult(itemId, response, if (checked) "Да" else "Нет")
        }
    }

    fun submitNumericResult(
        itemId: String,
        equipmentId: String,
        value: Double,
        unit: String?,
        comment: String
    ) {
        val checklistInstanceId = _uiState.value.confirmedStep?.checklistInstance?.id ?: return
        submitAction("Не удалось отправить числовой результат") {
            val response = repository.submitNumericResult(
                checklistInstanceId = checklistInstanceId,
                itemTemplateId = itemId,
                equipmentId = equipmentId,
                value = value,
                unit = unit,
                comment = comment
            )
            storeChecklistResult(itemId, response, buildString {
                append(value)
                if (!unit.isNullOrBlank()) append(" ").append(unit)
            })
        }
    }

    fun submitReading(
        step: RouteStepDetails,
        equipmentId: String,
        itemId: String,
        normRef: String?,
        value: Double
    ) {
        val parameterDefId = pressureParameterDefIdFor(normRef = normRef, itemId = itemId) ?: return
        val checklistResultId = _uiState.value.submittedItems[itemId]?.resultId
        submitAction("Не удалось отправить показание оборудования") {
            val response = repository.submitEquipmentReading(
                equipmentId = equipmentId,
                routeStepId = step.id,
                parameterDefId = parameterDefId,
                value = value,
                checklistItemResultId = checklistResultId
            )
            _uiState.update {
                it.copy(
                    readingStatuses = it.readingStatuses + (itemId to response),
                    errorMessage = null,
                    infoMessage = "Показание отправлено"
                )
            }
        }
    }

    fun finishRound() {
        submitAction("Не удалось завершить обход") {
            repository.finishRound(roundId)
            refreshTaskDetails()
            _uiState.update { it.copy(infoMessage = "Обход завершён") }
        }
    }

    private suspend fun refreshTaskDetails() {
        val details = repository.getTaskDetails(roundId)
        _uiState.update { it.copy(details = details) }
    }

    private fun storeChecklistResult(
        itemId: String,
        response: ChecklistItemResultResponse,
        displayValue: String
    ) {
        _uiState.update {
            val currentConfirmed = it.confirmedStep ?: return@update it
            it.copy(
                confirmedStep = currentConfirmed.copy(checklistInstance = response.checklistInstance),
                submittedItems = it.submittedItems + (
                    itemId to SubmittedChecklistValue(
                        resultId = response.result.id,
                        displayValue = displayValue,
                        comment = response.result.comment,
                        status = response.result.status
                    )
                ),
                errorMessage = null,
                infoMessage = "Ответ по пункту сохранён"
            )
        }
    }

    private fun submitAction(fallbackMessage: String, action: suspend () -> Unit) {
        viewModelScope.launch {
            _uiState.update { it.copy(isSubmitting = true, errorMessage = null, infoMessage = null) }
            runCatching { action() }
                .onFailure { error ->
                    _uiState.update {
                        it.copy(
                            isSubmitting = false,
                            errorMessage = error.toUserMessage(fallbackMessage)
                        )
                    }
                }
                .onSuccess {
                    _uiState.update { it.copy(isSubmitting = false) }
                }
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

fun defaultUnitFor(normRef: String?): String? = when (normRef) {
    "PRESSURE_OUT" -> "MPa"
    else -> null
}

fun pressureParameterDefIdFor(normRef: String?, itemId: String): String? =
    when {
        normRef == "PRESSURE_OUT" -> BuildConfig.PRESSURE_PARAMETER_DEF_ID
        itemId == "TPL-EVERYDAY-SAFETY-02-ITEM-2" -> BuildConfig.PRESSURE_PARAMETER_DEF_ID
        else -> null
    }

private fun Throwable.toUserMessage(fallback: String): String = when (this) {
    is HttpException -> when (code()) {
        401 -> "Backend отклонил запрос: проверь токен Bearer dev-token"
        403 -> "Backend запретил это действие для текущего работника"
        404 -> "Backend не нашёл обход или точку маршрута"
        409 -> "Backend вернул конфликт: QR/NFC не совпадает или обязательные пункты не заполнены"
        else -> "$fallback: HTTP ${code()}"
    }
    is IOException -> "$fallback: сервер ${BuildConfig.API_BASE_URL} недоступен"
    else -> message ?: fallback
}
