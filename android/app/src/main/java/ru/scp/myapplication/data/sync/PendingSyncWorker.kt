package ru.scp.myapplication.data.sync

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import ru.scp.myapplication.ToirApplication

class PendingSyncWorker(
    appContext: Context,
    workerParameters: WorkerParameters
) : CoroutineWorker(appContext, workerParameters) {

    override suspend fun doWork(): Result = try {
        val application = applicationContext as ToirApplication
        application.appContainer.syncRepository.syncPending()
        Result.success()
    } catch (_: Exception) {
        Result.retry()
    }

    companion object {
        const val WORK_NAME = "pending_sync_work"
    }
}
