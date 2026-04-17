package ru.scp.myapplication.data.remote

import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query
import ru.scp.myapplication.data.remote.dto.ChecklistDto
import ru.scp.myapplication.data.remote.dto.RouteSheetDto
import ru.scp.myapplication.data.remote.dto.RoundSheetDto
import ru.scp.myapplication.data.remote.dto.SyncBatchRequestDto
import ru.scp.myapplication.data.remote.dto.SyncBatchResponseDto

interface ToirApiService {
    @GET("round/current")
    suspend fun getCurrentRound(): RoundSheetDto

    @GET("routes/{id}")
    suspend fun getRoute(@Path("id") routeId: String): RouteSheetDto

    @GET("checklists/current")
    suspend fun getChecklist(@Query("entityId") entityId: String): ChecklistDto

    @POST("sync/checklists")
    suspend fun syncChecklist(@Body request: SyncBatchRequestDto): SyncBatchResponseDto
}
