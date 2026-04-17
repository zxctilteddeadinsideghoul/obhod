package ru.scp.myapplication.core.di

import android.content.Context
import androidx.room.Room
import com.google.gson.Gson
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import ru.scp.myapplication.data.local.ToirDatabase
import ru.scp.myapplication.data.remote.FakeToirApiService
import ru.scp.myapplication.data.remote.ToirApiService
import ru.scp.myapplication.data.repository.ChecklistRepositoryImpl
import ru.scp.myapplication.data.repository.RoundRepositoryImpl
import ru.scp.myapplication.data.repository.RouteRepositoryImpl
import ru.scp.myapplication.data.repository.SyncRepositoryImpl
import ru.scp.myapplication.data.sync.SyncScheduler
import ru.scp.myapplication.domain.repository.ChecklistRepository
import ru.scp.myapplication.domain.repository.RoundRepository
import ru.scp.myapplication.domain.repository.RouteRepository
import ru.scp.myapplication.domain.repository.SyncRepository
import ru.scp.myapplication.domain.usecase.ObserveChecklistUseCase
import ru.scp.myapplication.domain.usecase.ObserveCurrentRoundUseCase
import ru.scp.myapplication.domain.usecase.ObservePendingSyncCountUseCase
import ru.scp.myapplication.domain.usecase.ObserveRouteUseCase
import ru.scp.myapplication.domain.usecase.RefreshChecklistUseCase
import ru.scp.myapplication.domain.usecase.RefreshCurrentRoundUseCase
import ru.scp.myapplication.domain.usecase.RefreshRouteUseCase
import ru.scp.myapplication.domain.usecase.SyncPendingUseCase
import ru.scp.myapplication.domain.usecase.UpdateChecklistItemUseCase

class AppContainer(appContext: Context) {

    private val gson = Gson()

    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BASIC
    }

    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .build()

    val retrofit: Retrofit = Retrofit.Builder()
        .baseUrl("https://placeholder.toir.local/api/")
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create(gson))
        .build()

    val realApi: ToirApiService = retrofit.create(ToirApiService::class.java)
    private val fakeApi: ToirApiService = FakeToirApiService()
    private val apiService: ToirApiService = fakeApi

    private val database = Room.databaseBuilder(
        appContext,
        ToirDatabase::class.java,
        "toir.db"
    ).fallbackToDestructiveMigration().build()

    private val syncScheduler = SyncScheduler(appContext)

    private val roundSheetDao = database.roundSheetDao()
    private val routeSheetDao = database.routeSheetDao()
    private val checklistDao = database.checklistDao()
    private val syncQueueDao = database.syncQueueDao()

    val roundRepository: RoundRepository = RoundRepositoryImpl(
        roundSheetDao = roundSheetDao,
        apiService = apiService,
        gson = gson
    )

    val routeRepository: RouteRepository = RouteRepositoryImpl(
        routeSheetDao = routeSheetDao,
        apiService = apiService,
        gson = gson
    )

    val checklistRepository: ChecklistRepository = ChecklistRepositoryImpl(
        checklistDao = checklistDao,
        syncQueueDao = syncQueueDao,
        apiService = apiService,
        syncScheduler = syncScheduler,
        gson = gson
    )

    val syncRepository: SyncRepository = SyncRepositoryImpl(
        syncQueueDao = syncQueueDao,
        apiService = apiService,
        syncScheduler = syncScheduler,
        gson = gson
    )

    val observeCurrentRoundUseCase = ObserveCurrentRoundUseCase(roundRepository)
    val refreshCurrentRoundUseCase = RefreshCurrentRoundUseCase(roundRepository)
    val observeRouteUseCase = ObserveRouteUseCase(routeRepository)
    val refreshRouteUseCase = RefreshRouteUseCase(routeRepository)
    val observeChecklistUseCase = ObserveChecklistUseCase(checklistRepository)
    val refreshChecklistUseCase = RefreshChecklistUseCase(checklistRepository)
    val updateChecklistItemUseCase = UpdateChecklistItemUseCase(checklistRepository)
    val observePendingSyncCountUseCase = ObservePendingSyncCountUseCase(syncRepository)
    val syncPendingUseCase = SyncPendingUseCase(syncRepository)
}
