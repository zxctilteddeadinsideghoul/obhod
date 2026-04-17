package ru.scp.myapplication.domain.model

enum class RoundStatus(val rawValue: String) {
    PLANNED("planned"),
    SENT("sent"),
    IN_PROGRESS("in_progress"),
    PAUSED("paused"),
    DONE("done"),
    DONE_WITH_REMARKS("done_with_remarks"),
    CANCELLED("cancelled");

    companion object {
        fun fromRaw(value: String): RoundStatus =
            entries.firstOrNull { it.rawValue == value } ?: IN_PROGRESS
    }
}

enum class ChecklistStatus(val rawValue: String) {
    DRAFT("draft"),
    RUNNING("running"),
    PAUSED("paused"),
    COMPLETED("completed"),
    SIGNED("signed");

    companion object {
        fun fromRaw(value: String): ChecklistStatus =
            entries.firstOrNull { it.rawValue == value } ?: DRAFT
    }
}

enum class AnswerType(val rawValue: String) {
    BOOL("bool"),
    ENUM("enum"),
    NUMBER("number"),
    TEXT("text"),
    PHOTO("photo");

    companion object {
        fun fromRaw(value: String): AnswerType =
            entries.firstOrNull { it.rawValue == value } ?: TEXT
    }
}

enum class SyncState {
    SYNCED,
    PENDING,
    FAILED
}

data class ParameterReading(
    val parameterCode: String,
    val value: String,
    val unit: String,
    val withinLimits: Boolean,
    val comment: String?
)

data class RoundObject(
    val seqNo: Int,
    val equipmentId: String,
    val checkpointId: String,
    val parameterReadings: List<ParameterReading>
)

data class RoundSheet(
    val id: String,
    val orgId: String,
    val routeId: String,
    val plannedStart: String,
    val plannedEnd: String?,
    val employeeId: String,
    val shiftId: String,
    val qualificationId: String?,
    val status: RoundStatus,
    val objects: List<RoundObject>,
    val syncState: SyncState
)

data class RouteStep(
    val seqNo: Int,
    val equipmentId: String,
    val checkpointId: String?,
    val mandatoryVisit: Boolean,
    val confirmBy: String?
)

data class RouteSheet(
    val id: String,
    val name: String,
    val orgId: String,
    val departmentId: String?,
    val qualificationId: String?,
    val location: String?,
    val durationMin: Int,
    val planningRule: String,
    val steps: List<RouteStep>,
    val version: String
)

data class ChecklistItem(
    val id: String,
    val checklistId: String,
    val seqNo: Int,
    val question: String,
    val answerType: AnswerType,
    val resultBoolean: Boolean?,
    val resultNumber: Double?,
    val resultText: String?,
    val comment: String?,
    val dueDate: String?,
    val syncState: SyncState
)

data class Checklist(
    val id: String,
    val templateId: String,
    val entityType: String,
    val entityId: String,
    val startedAt: String,
    val finishedAt: String?,
    val status: ChecklistStatus,
    val items: List<ChecklistItem>,
    val syncState: SyncState
)
