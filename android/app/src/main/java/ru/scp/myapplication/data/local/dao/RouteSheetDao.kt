package ru.scp.myapplication.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import kotlinx.coroutines.flow.Flow
import ru.scp.myapplication.data.local.entity.RouteSheetEntity

@Dao
interface RouteSheetDao {
    @Query("SELECT * FROM route_sheet WHERE id = :routeId LIMIT 1")
    fun observeRoute(routeId: String): Flow<RouteSheetEntity?>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(routeSheet: RouteSheetEntity)
}
