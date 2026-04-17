package ru.scp.myapplication

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test
import ru.scp.myapplication.presentation.checklist.defaultUnitFor
import ru.scp.myapplication.presentation.checklist.pressureParameterDefIdFor

class MobileIntegrationSupportTest {

    @Test
    fun pressureNormUsesDemoDefaults() {
        assertEquals("MPa", defaultUnitFor("PRESSURE_OUT"))
        assertEquals(
            "PARAM-COMPRESSOR-PRESSURE-OUT",
            pressureParameterDefIdFor("PRESSURE_OUT", "TPL-EVERYDAY-SAFETY-02-ITEM-2")
        )
    }

    @Test
    fun unknownNormDoesNotExposeReadingConfig() {
        assertNull(defaultUnitFor("TEMPERATURE"))
        assertNull(pressureParameterDefIdFor("TEMPERATURE", "UNKNOWN-ITEM"))
    }
}
