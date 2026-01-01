package de.layher.jobmining.kotlinapi.presentation

import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RestController
import org.springframework.web.client.RestTemplate
import org.slf4j.LoggerFactory

@RestController
class ConnectionTestController(
    private val restTemplate: RestTemplate,
    @org.springframework.beans.factory.annotation.Value("\${python.api.base-url:http://localhost:8000}")
    private val pythonApiBaseUrl: String
) {

    private val logger = LoggerFactory.getLogger(ConnectionTestController::class.java)

    @GetMapping(value = ["/test-python", "/api/v1/test-python"]) 
    fun testPython(): String {
        var target = "unknown"
        return try {
            // Baue die URL einfach, aber robust
            val base = if (pythonApiBaseUrl != null && pythonApiBaseUrl.startsWith("http")) pythonApiBaseUrl else "http://localhost:8000"
            target = base.trimEnd('/') + "/system/status"

            logger.info("🔗 [ConnectionTest] Testing Python URL: {}", target)
            val entity = restTemplate.getForEntity(target, String::class.java)
            logger.info("🔗 [ConnectionTest] Response status={} body={}", entity.statusCode.value(), entity.body)
            "Python erreichbar: ${entity.statusCode.value()} ${entity.body}"
        } catch (e: Exception) {
            logger.error("❌ [ConnectionTest] Fehler beim Aufruf von $target", e)
            "Python NICHT erreichbar: ${e.message}"
        }
    }
}
