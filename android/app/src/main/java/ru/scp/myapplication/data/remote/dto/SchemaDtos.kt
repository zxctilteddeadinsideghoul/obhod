package ru.scp.myapplication.data.remote.dto

data class RoundSheetDto(
    val id: String,
    val orgId: String,
    val routeId: String,
    val plannedStart: String,
    val plannedEnd: String?,
    val employeeId: String,
    val shiftId: String,
    val qualificationId: String?,
    val status: String,
    val objects: List<RoundObjectDto>,
    val attachments: List<String>,
    val signatures: List<String>,
    val audit: AuditDto?
)

data class RoundObjectDto(
    val seqNo: Int,
    val equipmentId: String,
    val checkpointId: String,
    val parameterReadings: List<ParameterReadingDto>
)

data class ParameterReadingDto(
    val parameterCode: String,
    val value: Any?,
    val unit: String,
    val withinLimits: Boolean,
    val comment: String?
)

data class AuditDto(
    val deviceId: String?,
    val schemaVersion: String?,
    val snapshotTsUtc: String?
)

data class RouteSheetDto(
    val id: String,
    val name: String,
    val orgId: String,
    val departmentId: String?,
    val qualificationId: String?,
    val location: String?,
    val durationMin: Int,
    val planningRule: String,
    val steps: List<RouteStepDto>,
    val version: String
)

data class RouteStepDto(
    val seqNo: Int,
    val equipmentId: String,
    val checkpointId: String?,
    val mandatoryVisit: Boolean,
    val confirmBy: String?
)

data class ChecklistDto(
    val id: String,
    val templateId: String,
    val entityRef: EntityRefDto,
    val startedAt: String,
    val finishedAt: String?,
    val status: String,
    val items: List<ChecklistItemDto>
)

data class EntityRefDto(
    val entityType: String,
    val entityId: String
)

data class ChecklistItemDto(
    val seqNo: Int,
    val question: String,
    val answerType: String,
    val result: Any?,
    val comment: String?,
    val dueDate: String?
)

data class SyncActionPayloadDto(
    val queueId: Long,
    val checklistId: String,
    val seqNo: Int,
    val checked: Boolean,
    val updatedAt: String
)

data class SyncBatchRequestDto(
    val deviceId: String,
    val actions: List<SyncActionPayloadDto>
)

data class SyncBatchResponseDto(
    val acceptedIds: List<Long>,
    val serverTimestamp: String
)
