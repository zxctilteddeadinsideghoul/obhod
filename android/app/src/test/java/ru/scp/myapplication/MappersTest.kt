package ru.scp.myapplication

import com.google.gson.Gson
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import ru.scp.myapplication.data.mapper.toDomain
import ru.scp.myapplication.data.mapper.toEntity
import ru.scp.myapplication.data.remote.dto.ChecklistItemDto
import ru.scp.myapplication.data.remote.dto.ParameterReadingDto
import ru.scp.myapplication.data.remote.dto.RoundObjectDto
import ru.scp.myapplication.data.remote.dto.RoundSheetDto

class MappersTest {

    private val gson = Gson()

    @Test
    fun checklistItemDto_bool_result_maps_to_boolean_field() {
        val entity = ChecklistItemDto(
            seqNo = 1,
            question = "Protective guards installed",
            answerType = "bool",
            result = true,
            comment = "",
            dueDate = null
        ).toEntity("CL-1")

        assertTrue(entity.resultBoolean == true)
        assertNull(entity.resultNumber)
        assertNull(entity.resultText)
    }

    @Test
    fun checklistItemDto_number_result_maps_to_numeric_field() {
        val entity = ChecklistItemDto(
            seqNo = 2,
            question = "Pressure",
            answerType = "number",
            result = 1.48,
            comment = "within range",
            dueDate = null
        ).toEntity("CL-1")

        assertEquals(1.48, entity.resultNumber ?: 0.0, 0.0)
        assertNull(entity.resultBoolean)
        assertNull(entity.resultText)
    }

    @Test
    fun roundSheet_roundtrip_preserves_route_and_parameter_data() {
        val dto = RoundSheetDto(
            id = "ROUND-1",
            orgId = "ORG-01",
            routeId = "ROUTE-KC0103",
            plannedStart = "2026-04-17T06:00:00+03:00",
            plannedEnd = "2026-04-17T07:00:00+03:00",
            employeeId = "EMP-145",
            shiftId = "SHIFT-A",
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
                )
            ),
            attachments = emptyList(),
            signatures = emptyList(),
            audit = null
        )

        val domain = dto.toEntity(gson).toDomain(gson)

        assertEquals("ROUTE-KC0103", domain.routeId)
        assertEquals("EQ-KC0103", domain.objects.first().equipmentId)
        assertEquals("PRESSURE_OUT", domain.objects.first().parameterReadings.first().parameterCode)
        assertEquals("1.48", domain.objects.first().parameterReadings.first().value)
    }
}
