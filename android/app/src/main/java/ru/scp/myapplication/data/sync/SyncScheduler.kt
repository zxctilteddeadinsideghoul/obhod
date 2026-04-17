package ru.scp.myapplication.data.sync

import android.content.Context
import androidx.work.Constraints
import androidx.work.ExistingWorkPolicy
import androidx.work.NetworkType
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager

class SyncScheduler(
    context: Context
) {
    private val workManager = WorkManager.getInstance(context)

    fun schedule() {
        val request = OneTimeWorkRequestBuilder<PendingSyncWorker>()
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED)
                    .build()
            )
            .build()

        workManager.enqueueUniqueWork(
            PendingSyncWorker.WORK_NAME,
            ExistingWorkPolicy.KEEP,
            request
        )
    }
}
