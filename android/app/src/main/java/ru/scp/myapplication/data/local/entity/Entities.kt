package ru.scp.myapplication.data.local.entity

import androidx.room.Embedded
import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.Relation

@Entity(tableName = "round_sheet")
data class RoundSheetEntity(
    @PrimaryKey val id: String,
    val orgId: String,
    val routeId: String,
    val plannedStart: String,
    val plannedEnd: String?,
    val employeeId: String,
    val shiftId: String,
    val qualificationId: String?,
    val status: String,
    val objectsJson: String,
    val attachmentsJson: String,
    val signaturesJson: String,
    val auditJson: String?,
    val updatedAt: String,
    val syncState: String
)

@Entity(tableName = "route_sheet")
data class RouteSheetEntity(
    @PrimaryKey val id: String,
    val name: String,
    val orgId: String,
    val departmentId: String?,
    val qualificationId: String?,
    val location: String?,
    val durationMin: Int,
    val planningRule: String,
    val stepsJson: String,
    val version: String,
    val updatedAt: String
)

@Entity(tableName = "checklist")
data class ChecklistEntity(
    @PrimaryKey val id: String,
    val templateId: String,
    val entityType: String,
    val entityId: String,
    val startedAt: String,
    val finishedAt: String?,
    val status: String,
    val updatedAt: String,
    val syncState: String
)

@Entity(tableName = "checklist_item")
data class ChecklistItemEntity(
    @PrimaryKey val id: String,
    val checklistId: String,
    val seqNo: Int,
    val question: String,
    val answerType: String,
    val resultBoolean: Boolean?,
    val resultNumber: Double?,
    val resultText: String?,
    val comment: String?,
    val dueDate: String?,
    val updatedAt: String,
    val syncState: String
)

@Entity(tableName = "sync_queue")
data class SyncQueueEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val actionType: String,
    val entityId: String,
    val payloadJson: String,
    val status: String,
    val attempts: Int,
    val errorMessage: String?,
    val createdAt: String,
    val updatedAt: String
)

data class ChecklistWithItems(
    @Embedded val checklist: ChecklistEntity,
    @Relation(
        parentColumn = "id",
        entityColumn = "checklistId"
    )
    val items: List<ChecklistItemEntity>
)
