package ru.scp.myapplication.data.repository

import ru.scp.myapplication.BuildConfig
import ru.scp.myapplication.data.remote.MobileBackendApiService
import ru.scp.myapplication.domain.model.AssignedTask
import ru.scp.myapplication.domain.model.ChecklistItemResultResponse
import ru.scp.myapplication.domain.model.ConfirmStepRequest
import ru.scp.myapplication.domain.model.ConfirmStepResponse
import ru.scp.myapplication.domain.model.DevicePayload
import ru.scp.myapplication.domain.model.EquipmentReadingResponse
import ru.scp.myapplication.domain.model.RoundLifecycleResponse
import ru.scp.myapplication.domain.model.RouteStepDetails
import ru.scp.myapplication.domain.model.ResultValuePayload
import ru.scp.myapplication.domain.model.SubmitChecklistItemResultRequest
import ru.scp.myapplication.domain.model.SubmitEquipmentReadingRequest
import ru.scp.myapplication.domain.model.TaskDetails
import ru.scp.myapplication.domain.model.WorkerProfile

interface MobileBackendRepository {
    suspend fun getCurrentUser(): WorkerProfile
    suspend fun getAssignedTasks(): List<AssignedTask>
    suspend fun getTaskDetails(roundId: String): TaskDetails
    suspend fun startRound(roundId: String): RoundLifecycleResponse
    suspend fun confirmStep(roundId: String, step: RouteStepDetails, scannedValue: String, confirmBy: String): ConfirmStepResponse
    suspend fun submitBooleanResult(
        checklistInstanceId: String,
        itemTemplateId: String,
        equipmentId: String,
        checked: Boolean,
        comment: String
    ): ChecklistItemResultResponse

    suspend fun submitNumericResult(
        checklistInstanceId: String,
        itemTemplateId: String,
        equipmentId: String,
        value: Double,
        unit: String?,
        comment: String
    ): ChecklistItemResultResponse

    suspend fun submitEquipmentReading(
        equipmentId: String,
        routeStepId: String,
        parameterDefId: String,
        value: Double,
        checklistItemResultId: String?
    ): EquipmentReadingResponse

    suspend fun finishRound(roundId: String): RoundLifecycleResponse
}

class MobileBackendRepositoryImpl(
    private val apiService: MobileBackendApiService
) : MobileBackendRepository {

    override suspend fun getCurrentUser(): WorkerProfile = apiService.getCurrentUser()

    override suspend fun getAssignedTasks(): List<AssignedTask> = apiService.getAssignedTasks()

    override suspend fun getTaskDetails(roundId: String): TaskDetails = apiService.getTaskDetails(roundId)

    override suspend fun startRound(roundId: String): RoundLifecycleResponse = apiService.startRound(roundId)

    override suspend fun confirmStep(
        roundId: String,
        step: RouteStepDetails,
        scannedValue: String,
        confirmBy: String
    ): ConfirmStepResponse = apiService.confirmStep(
        roundId = roundId,
        routeStepId = step.id,
        request = ConfirmStepRequest(
            confirmBy = confirmBy,
            scannedValue = scannedValue,
            payloadJson = DevicePayload(BuildConfig.DEVICE_ID)
        )
    )

    override suspend fun submitBooleanResult(
        checklistInstanceId: String,
        itemTemplateId: String,
        equipmentId: String,
        checked: Boolean,
        comment: String
    ): ChecklistItemResultResponse = apiService.submitChecklistItemResult(
        checklistInstanceId = checklistInstanceId,
        itemTemplateId = itemTemplateId,
        request = SubmitChecklistItemResultRequest(
            equipmentId = equipmentId,
            resultCode = "ok",
            resultValue = ResultValuePayload(value = checked),
            comment = comment.ifBlank { null }
        )
    )

    override suspend fun submitNumericResult(
        checklistInstanceId: String,
        itemTemplateId: String,
        equipmentId: String,
        value: Double,
        unit: String?,
        comment: String
    ): ChecklistItemResultResponse = apiService.submitChecklistItemResult(
        checklistInstanceId = checklistInstanceId,
        itemTemplateId = itemTemplateId,
        request = SubmitChecklistItemResultRequest(
            equipmentId = equipmentId,
            resultCode = "ok",
            resultValue = ResultValuePayload(value = value, unit = unit),
            comment = comment.ifBlank { null }
        )
    )

    override suspend fun submitEquipmentReading(
        equipmentId: String,
        routeStepId: String,
        parameterDefId: String,
        value: Double,
        checklistItemResultId: String?
    ): EquipmentReadingResponse = apiService.submitEquipmentReading(
        equipmentId = equipmentId,
        request = SubmitEquipmentReadingRequest(
            parameterDefId = parameterDefId,
            valueNum = value,
            source = "mobile",
            routeStepId = routeStepId,
            checklistItemResultId = checklistItemResultId,
            payloadJson = DevicePayload(BuildConfig.DEVICE_ID)
        )
    )

    override suspend fun finishRound(roundId: String): RoundLifecycleResponse = apiService.finishRound(roundId)
}
