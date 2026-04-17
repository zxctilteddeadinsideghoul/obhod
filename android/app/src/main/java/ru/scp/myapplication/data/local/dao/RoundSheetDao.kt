package ru.scp.myapplication.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import kotlinx.coroutines.flow.Flow
import ru.scp.myapplication.data.local.entity.RoundSheetEntity

@Dao
interface RoundSheetDao {
    @Query("SELECT * FROM round_sheet ORDER BY plannedStart DESC LIMIT 1")
    fun observeCurrentRound(): Flow<RoundSheetEntity?>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(roundSheet: RoundSheetEntity)
}
