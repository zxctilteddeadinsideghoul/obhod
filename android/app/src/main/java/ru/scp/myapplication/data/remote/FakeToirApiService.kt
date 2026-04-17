package ru.scp.myapplication.data.remote

import kotlinx.coroutines.delay
import ru.scp.myapplication.data.remote.dto.AuditDto
import ru.scp.myapplication.data.remote.dto.ChecklistDto
import ru.scp.myapplication.data.remote.dto.ChecklistItemDto
import ru.scp.myapplication.data.remote.dto.EntityRefDto
import ru.scp.myapplication.data.remote.dto.ParameterReadingDto
import ru.scp.myapplication.data.remote.dto.RouteSheetDto
import ru.scp.myapplication.data.remote.dto.RouteStepDto
import ru.scp.myapplication.data.remote.dto.RoundObjectDto
import ru.scp.myapplication.data.remote.dto.RoundSheetDto
import ru.scp.myapplication.data.remote.dto.SyncBatchRequestDto
import ru.scp.myapplication.data.remote.dto.SyncBatchResponseDto
import java.time.Instant

class FakeToirApiService : ToirApiService {

    override suspend fun getCurrentRound(): RoundSheetDto {
        delay(250)
        return RoundSheetDto(
            id = "ROUND-2026-04-17-000123",
            orgId = "ORG-01",
            routeId = "ROUTE-KC0103",
            plannedStart = "2026-04-17T06:00:00+03:00",
            plannedEnd = "2026-04-17T07:00:00+03:00",
            employeeId = "EMP-145",
            shiftId = "SHIFT-A-2026-04-17",
            qualificationId = "OPERATOR-TU",
            status = "in_progress",
            objects = listOf(
                RoundObjectDto(
                    seqNo = 1,
                    equipmentId = "EQ-KC0103",
                    checkpointId = "PI-2",
                    parameterReadings = listOf(
                        ParameterReadingDto(
                            parameterCode = "PRESSURE_OUT",
                            value = 1.48,
                            unit = "MPa",
                            withinLimits = true,
                            comment = "норма"
                        )
                    )
                ),
                RoundObjectDto(
                    seqNo = 2,
                    equipmentId = "EQ-BLOCK-REAGENT-01",
                    checkpointId = "TEMP-7",
                    parameterReadings = listOf(
                        ParameterReadingDto(
                            parameterCode = "TEMP_OUT",
                            value = 83.0,
                            unit = "C",
                            withinLimits = true,
                            comment = "стабильно"
                        )
                    )
                )
            ),
            attachments = emptyList(),
            signatures = emptyList(),
            audit = AuditDto(
                deviceId = "MOB-0091",
                schemaVersion = "1.0.0",
                snapshotTsUtc = "2026-04-17T03:18:44Z"
            )
        )
    }

    override suspend fun getRoute(routeId: String): RouteSheetDto {
        delay(200)
        return RouteSheetDto(
            id = routeId,
            name = "КС0103",
            orgId = "ORG-01",
            departmentId = "DEPT-UGP",
            qualificationId = "OPERATOR-TU",
            location = "АНГКМ / ЦПТГ / УКПГ",
            durationMin = 60,
            planningRule = "every_3_hours",
            steps = listOf(
                RouteStepDto(
                    seqNo = 1,
                    equipmentId = "EQ-KC0103",
                    checkpointId = "PI-2",
                    mandatoryVisit = true,
                    confirmBy = "nfc"
                ),
                RouteStepDto(
                    seqNo = 2,
                    equipmentId = "EQ-BLOCK-REAGENT-01",
                    checkpointId = "TEMP-7",
                    mandatoryVisit = true,
                    confirmBy = "manual"
                )
            ),
            version = "3"
        )
    }

    override suspend fun getChecklist(entityId: String): ChecklistDto {
        delay(225)
        return ChecklistDto(
            id = "CL-2026-04-17-555",
            templateId = "TPL-EVERYDAY-SAFTY-02",
            entityRef = EntityRefDto(
                entityType = "round",
                entityId = entityId
            ),
            startedAt = "2026-04-17T06:05:00+03:00",
            finishedAt = null,
            status = "running",
            items = listOf(
                ChecklistItemDto(
                    seqNo = 1,
                    question = "На оборудовании установлены защитные кожухи и блокировки",
                    answerType = "bool",
                    result = true,
                    comment = "",
                    dueDate = null
                ),
                ChecklistItemDto(
                    seqNo = 2,
                    question = "Освобождены проходы вокруг оборудования",
                    answerType = "bool",
                    result = false,
                    comment = "требуется контроль после уборки",
                    dueDate = null
                ),
                ChecklistItemDto(
                    seqNo = 3,
                    question = "Давление на выходе компрессора",
                    answerType = "number",
                    result = 1.48,
                    comment = "в пределах допуска",
                    dueDate = null
                )
            )
        )
    }

    override suspend fun syncChecklist(request: SyncBatchRequestDto): SyncBatchResponseDto {
        delay(350)
        return SyncBatchResponseDto(
            acceptedIds = request.actions.map { it.queueId },
            serverTimestamp = Instant.now().toString()
        )
    }
}
