package ru.scp.myapplication.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Transaction
import kotlinx.coroutines.flow.Flow
import ru.scp.myapplication.data.local.entity.ChecklistEntity
import ru.scp.myapplication.data.local.entity.ChecklistItemEntity
import ru.scp.myapplication.data.local.entity.ChecklistWithItems

@Dao
interface ChecklistDao {
    @Transaction
    @Query("SELECT * FROM checklist WHERE entityId = :roundId LIMIT 1")
    fun observeChecklist(roundId: String): Flow<ChecklistWithItems?>

    @Query("SELECT * FROM checklist WHERE id = :checklistId LIMIT 1")
    suspend fun getChecklist(checklistId: String): ChecklistEntity?

    @Query("SELECT * FROM checklist_item WHERE checklistId = :checklistId AND seqNo = :seqNo LIMIT 1")
    suspend fun getChecklistItem(checklistId: String, seqNo: Int): ChecklistItemEntity?

    @Query("SELECT * FROM checklist_item WHERE checklistId = :checklistId ORDER BY seqNo")
    suspend fun getChecklistItems(checklistId: String): List<ChecklistItemEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertChecklist(checklist: ChecklistEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertItems(items: List<ChecklistItemEntity>)

    @Query("DELETE FROM checklist_item WHERE checklistId = :checklistId")
    suspend fun deleteItems(checklistId: String)

    @Transaction
    suspend fun replaceChecklist(checklist: ChecklistEntity, items: List<ChecklistItemEntity>) {
        upsertChecklist(checklist)
        deleteItems(checklist.id)
        insertItems(items)
    }
}
