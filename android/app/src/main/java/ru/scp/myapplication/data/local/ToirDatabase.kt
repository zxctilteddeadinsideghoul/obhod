package ru.scp.myapplication.data.local

import androidx.room.Database
import androidx.room.RoomDatabase
import ru.scp.myapplication.data.local.dao.ChecklistDao
import ru.scp.myapplication.data.local.dao.RoundSheetDao
import ru.scp.myapplication.data.local.dao.RouteSheetDao
import ru.scp.myapplication.data.local.dao.SyncQueueDao
import ru.scp.myapplication.data.local.entity.ChecklistEntity
import ru.scp.myapplication.data.local.entity.ChecklistItemEntity
import ru.scp.myapplication.data.local.entity.RoundSheetEntity
import ru.scp.myapplication.data.local.entity.RouteSheetEntity
import ru.scp.myapplication.data.local.entity.SyncQueueEntity

@Database(
    entities = [
        RoundSheetEntity::class,
        RouteSheetEntity::class,
        ChecklistEntity::class,
        ChecklistItemEntity::class,
        SyncQueueEntity::class
    ],
    version = 1,
    exportSchema = false
)
abstract class ToirDatabase : RoomDatabase() {
    abstract fun roundSheetDao(): RoundSheetDao
    abstract fun routeSheetDao(): RouteSheetDao
    abstract fun checklistDao(): ChecklistDao
    abstract fun syncQueueDao(): SyncQueueDao
}
