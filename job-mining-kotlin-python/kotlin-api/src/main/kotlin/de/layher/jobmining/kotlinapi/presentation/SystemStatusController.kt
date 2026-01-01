package de.layher.jobmining.kotlinapi.presentation

import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController
import io.swagger.v3.oas.annotations.Operation
import io.swagger.v3.oas.annotations.tags.Tag
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

@RestController
@RequestMapping("/api/v1/system")
@Tag(name = "System", description = "System-Status und Health-Checks")
class SystemStatusController {
    
    data class SystemStatus(
        val status: String = "UP",
        val service: String = "kotlin-api",
        val timestamp: String = LocalDateTime.now().format(DateTimeFormatter.ISO_DATE_TIME),
        val version: String = "2.3.0",
        val database: String = "connected"
    )

    @GetMapping("/status")
    @Operation(
        summary = "System Status",
        description = "Liefert den Systemstatus der Kotlin API"
    )
    fun getStatus(): SystemStatus {
        return SystemStatus()
    }
}
