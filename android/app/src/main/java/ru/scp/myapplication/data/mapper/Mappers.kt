package ru.scp.myapplication.data.mapper

import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import ru.scp.myapplication.data.local.entity.ChecklistEntity
import ru.scp.myapplication.data.local.entity.ChecklistItemEntity
import ru.scp.myapplication.data.local.entity.ChecklistWithItems
import ru.scp.myapplication.data.local.entity.RoundSheetEntity
import ru.scp.myapplication.data.local.entity.RouteSheetEntity
import ru.scp.myapplication.data.remote.dto.ChecklistDto
import ru.scp.myapplication.data.remote.dto.ChecklistItemDto
import ru.scp.myapplication.data.remote.dto.ParameterReadingDto
import ru.scp.myapplication.data.remote.dto.RouteSheetDto
import ru.scp.myapplication.data.remote.dto.RouteStepDto
import ru.scp.myapplication.data.remote.dto.RoundObjectDto
import ru.scp.myapplication.data.remote.dto.RoundSheetDto
import ru.scp.myapplication.domain.model.AnswerType
import ru.scp.myapplication.domain.model.Checklist
import ru.scp.myapplication.domain.model.ChecklistItem
import ru.scp.myapplication.domain.model.ChecklistStatus
import ru.scp.myapplication.domain.model.ParameterReading
import ru.scp.myapplication.domain.model.RoundObject
import ru.scp.myapplication.domain.model.RoundSheet
import ru.scp.myapplication.domain.model.RoundStatus
import ru.scp.myapplication.domain.model.RouteSheet
import ru.scp.myapplication.domain.model.RouteStep
import ru.scp.myapplication.domain.model.SyncState
import java.time.Instant

fun RoundSheetDto.toEntity(gson: Gson): RoundSheetEntity = RoundSheetEntity(
    id = id,
    orgId = orgId,
    routeId = routeId,
    plannedStart = plannedStart,
    plannedEnd = plannedEnd,
    employeeId = employeeId,
    shiftId = shiftId,
    qualificationId = qualificationId,
    status = status,
    objectsJson = gson.toJson(objects),
    attachmentsJson = gson.toJson(attachments),
    signaturesJson = gson.toJson(signatures),
    auditJson = gson.toJson(audit),
    updatedAt = Instant.now().toString(),
    syncState = SyncState.SYNCED.name
)

fun RouteSheetDto.toEntity(gson: Gson): RouteSheetEntity = RouteSheetEntity(
    id = id,
    name = name,
    orgId = orgId,
    departmentId = departmentId,
    qualificationId = qualificationId,
    location = location,
    durationMin = durationMin,
    planningRule = planningRule,
    stepsJson = gson.toJson(steps),
    version = version,
    updatedAt = Instant.now().toString()
)

fun ChecklistDto.toEntity(): ChecklistEntity = ChecklistEntity(
    id = id,
    templateId = templateId,
    entityType = entityRef.entityType,
    entityId = entityRef.entityId,
    startedAt = startedAt,
    finishedAt = finishedAt,
    status = status,
    updatedAt = Instant.now().toString(),
    syncState = SyncState.SYNCED.name
)

fun ChecklistItemDto.toEntity(checklistId: String): ChecklistItemEntity {
    val booleanValue = result as? Boolean
    val numberValue = when (result) {
        is Number -> result.toDouble()
        else -> null
    }
    val textValue = when (result) {
        null -> null
        is String -> result
        is Number, is Boolean -> null
        else -> result.toString()
    }

    return ChecklistItemEntity(
        id = "$checklistId-$seqNo",
        checklistId = checklistId,
        seqNo = seqNo,
        question = question,
        answerType = answerType,
        resultBoolean = booleanValue,
        resultNumber = numberValue,
        resultText = textValue,
        comment = comment,
        dueDate = dueDate,
        updatedAt = Instant.now().toString(),
        syncState = SyncState.SYNCED.name
    )
}

fun RoundSheetEntity.toDomain(gson: Gson): RoundSheet {
    val objectsType = object : TypeToken<List<RoundObjectDto>>() {}.type
    val objects = gson.fromJson<List<RoundObjectDto>>(objectsJson, objectsType).map { it.toDomain() }

    return RoundSheet(
        id = id,
        orgId = orgId,
        routeId = routeId,
        plannedStart = plannedStart,
        plannedEnd = plannedEnd,
        employeeId = employeeId,
        shiftId = shiftId,
        qualificationId = qualificationId,
        status = RoundStatus.fromRaw(status),
        objects = objects,
        syncState = syncState.toSyncState()
    )
}

fun RouteSheetEntity.toDomain(gson: Gson): RouteSheet {
    val stepsType = object : TypeToken<List<RouteStepDto>>() {}.type
    val steps = gson.fromJson<List<RouteStepDto>>(stepsJson, stepsType).map { it.toDomain() }

    return RouteSheet(
        id = id,
        name = name,
        orgId = orgId,
        departmentId = departmentId,
        qualificationId = qualificationId,
        location = location,
        durationMin = durationMin,
        planningRule = planningRule,
        steps = steps,
        version = version
    )
}

fun ChecklistWithItems.toDomain(): Checklist {
    val itemSyncStates = items.map { it.syncState.toSyncState() }
    val overallSyncState = if (itemSyncStates.any { it == SyncState.PENDING }) {
        SyncState.PENDING
    } else {
        checklist.syncState.toSyncState()
    }

    return Checklist(
        id = checklist.id,
        templateId = checklist.templateId,
        entityType = checklist.entityType,
        entityId = checklist.entityId,
        startedAt = checklist.startedAt,
        finishedAt = checklist.finishedAt,
        status = ChecklistStatus.fromRaw(checklist.status),
        items = items.sortedBy { it.seqNo }.map { it.toDomain() },
        syncState = overallSyncState
    )
}

fun ChecklistItemEntity.toDomain(): ChecklistItem = ChecklistItem(
    id = id,
    checklistId = checklistId,
    seqNo = seqNo,
    question = question,
    answerType = AnswerType.fromRaw(answerType),
    resultBoolean = resultBoolean,
    resultNumber = resultNumber,
    resultText = resultText,
    comment = comment,
    dueDate = dueDate,
    syncState = syncState.toSyncState()
)

fun RoundObjectDto.toDomain(): RoundObject = RoundObject(
    seqNo = seqNo,
    equipmentId = equipmentId,
    checkpointId = checkpointId,
    parameterReadings = parameterReadings.map { it.toDomain() }
)

fun ParameterReadingDto.toDomain(): ParameterReading = ParameterReading(
    parameterCode = parameterCode,
    value = value?.toString().orEmpty(),
    unit = unit,
    withinLimits = withinLimits,
    comment = comment
)

fun RouteStepDto.toDomain(): RouteStep = RouteStep(
    seqNo = seqNo,
    equipmentId = equipmentId,
    checkpointId = checkpointId,
    mandatoryVisit = mandatoryVisit,
    confirmBy = confirmBy
)

fun String.toSyncState(): SyncState = when (this) {
    SyncState.PENDING.name -> SyncState.PENDING
    SyncState.FAILED.name -> SyncState.FAILED
    else -> SyncState.SYNCED
}
