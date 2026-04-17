package ru.scp.myapplication.data.remote

import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path
import ru.scp.myapplication.domain.model.AssignedTask
import ru.scp.myapplication.domain.model.ChecklistItemResultResponse
import ru.scp.myapplication.domain.model.ConfirmStepRequest
import ru.scp.myapplication.domain.model.ConfirmStepResponse
import ru.scp.myapplication.domain.model.EquipmentReadingResponse
import ru.scp.myapplication.domain.model.RoundLifecycleResponse
import ru.scp.myapplication.domain.model.SubmitChecklistItemResultRequest
import ru.scp.myapplication.domain.model.SubmitEquipmentReadingRequest
import ru.scp.myapplication.domain.model.TaskDetails
import ru.scp.myapplication.domain.model.WorkerProfile

interface MobileBackendApiService {
    @GET("api/auth/me")
    suspend fun getCurrentUser(): WorkerProfile

    @GET("api/field/tasks/my")
    suspend fun getAssignedTasks(): List<AssignedTask>

    @GET("api/field/tasks/{roundId}")
    suspend fun getTaskDetails(@Path("roundId") roundId: String): TaskDetails

    @POST("api/field/tasks/{roundId}/start")
    suspend fun startRound(@Path("roundId") roundId: String): RoundLifecycleResponse

    @POST("api/field/tasks/{roundId}/steps/{routeStepId}/confirm")
    suspend fun confirmStep(
        @Path("roundId") roundId: String,
        @Path("routeStepId") routeStepId: String,
        @Body request: ConfirmStepRequest
    ): ConfirmStepResponse

    @POST("api/field/checklists/{checklistInstanceId}/items/{itemTemplateId}/result")
    suspend fun submitChecklistItemResult(
        @Path("checklistInstanceId") checklistInstanceId: String,
        @Path("itemTemplateId") itemTemplateId: String,
        @Body request: SubmitChecklistItemResultRequest
    ): ChecklistItemResultResponse

    @POST("api/field/equipment/{equipmentId}/readings")
    suspend fun submitEquipmentReading(
        @Path("equipmentId") equipmentId: String,
        @Body request: SubmitEquipmentReadingRequest
    ): EquipmentReadingResponse

    @POST("api/field/tasks/{roundId}/finish")
    suspend fun finishRound(@Path("roundId") roundId: String): RoundLifecycleResponse
}
