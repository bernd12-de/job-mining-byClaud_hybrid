package de.layher.jobmining.kotlinapi.adapters

import com.fasterxml.jackson.annotation.JsonProperty
import org.springframework.beans.factory.annotation.Value
import org.springframework.core.io.ByteArrayResource
import org.springframework.http.HttpEntity
import org.springframework.http.HttpHeaders
import org.springframework.http.MediaType
import org.springframework.stereotype.Component
import org.springframework.util.LinkedMultiValueMap
import org.springframework.web.client.RestTemplate
import org.springframework.core.ParameterizedTypeReference
import org.springframework.http.HttpMethod
import org.slf4j.LoggerFactory

// NEUE IMPORTS FÜR ROBUSTES FEHLERHANDLING
import org.springframework.web.client.HttpStatusCodeException
import org.springframework.web.client.ResourceAccessException

// Input-Modell für die URL (muss dem Python-Modell entsprechen)
data class URLInput(val url: String, @JsonProperty("render_js") val renderJs: Boolean = false)

@Component
class PythonAnalysisClient(
    @Value("\${python.api.base-url:http://localhost:8000}")
    private val pythonApiBaseUrl: String
) {

    private val restTemplate = RestTemplate()
    private val logger = LoggerFactory.getLogger(PythonAnalysisClient::class.java)

    /**
     * Führt den Datei-Upload und den Analyse-Aufruf an das Python-Backend (/analyse) durch.
     * FIX: Korrekte Verwendung von HttpHeaders und ByteArrayResource.
     */
    fun sendDocumentForAnalysis(bytes: ByteArray, filename: String): AnalysisResultDTO {

        try {
            val headers = HttpHeaders().apply {
                contentType = MediaType.MULTIPART_FORM_DATA // Wichtig: Multipart
            }

            // Definiere die Datei als Resource
            val fileResource = object : ByteArrayResource(bytes) {
                override fun getFilename(): String = filename
            }

            // Erstelle den Body mit dem Dateiteil
            val body = LinkedMultiValueMap<String, Any>().apply {
                add("file", fileResource) // Name muss 'file' sein (wie in FastAPI erwartet)
            }

            val requestEntity = HttpEntity(body, headers)
            val url = "$pythonApiBaseUrl/analyse/file"

            val response = restTemplate.postForEntity(url, requestEntity, AnalysisResultDTO::class.java)

            return response.body
                ?: throw IllegalStateException("Analyse-Ergebnis vom Python-Service war leer.")
        } catch (e: HttpStatusCodeException) {
            val pythonErrorDetail = e.responseBodyAsString.substringAfter("{\"detail\":\"").substringBeforeLast("\"}")
            throw RuntimeException("Fehler bei Dateianalyse im Python-Backend (${e.statusCode.value()}): $pythonErrorDetail")
        } catch (e: ResourceAccessException) {
            throw RuntimeException("Verbindungsfehler zum Python-Backend: Ist der Service gestartet? Fehler: ${e.message}")
        }
    }

    // In de.layher.jobmining.kotlinapi.infrastructure.bridge.PythonNlpBridge
    fun analyze(text: String): List<String> {
        // Hier kommt dein REST-Call an Python (Port 8000) rein
        return emptyList()
    }

    /**
     * Löst die Batch-Analyse aller lokalen Dateien im Python-Backend aus.
     */
    fun processLocalJobDirectory(): List<AnalysisResultDTO> {
        val url = "$pythonApiBaseUrl/batch-process"
        val responseType = object : ParameterizedTypeReference<List<AnalysisResultDTO>>() {}

        try {
            val response = restTemplate.exchange(
                url,
                HttpMethod.POST, // Es ist ein POST
                HttpEntity.EMPTY, // WICHTIG: Senden KEINEN Body, sondern ein leeres Entity
                responseType
            )
            return response.body
                ?: throw IllegalStateException("Batch-Analyse-Ergebnis vom Python-Service war leer.")
        } catch (e: HttpStatusCodeException) {
            val pythonErrorDetail = e.responseBodyAsString.substringAfter("{\"detail\":\"").substringBeforeLast("\"}")
            throw RuntimeException("Batch-Fehler im Python-Backend (${e.statusCode.value()}): $pythonErrorDetail")
        } catch (e: ResourceAccessException) {
            throw RuntimeException("Verbindungsfehler zum Python-Backend: Ist der Service gestartet? Fehler: ${e.message}")
        }
    }

    /**
     * Ruft den Scraper-Endpunkt im Python-Backend auf, um eine URL zu analysieren.
     * NEU: Fängt HTTP-Fehler ab, um die Jackson-Deserialisierungs-Warnung zu vermeiden.
     */
    fun scrapeAndAnalyzeUrl(url: String, renderJs: Boolean = false): AnalysisResultDTO {
        val requestUrl = "$pythonApiBaseUrl/analyse/scrape-url"
        // WICHTIG: renderJs wird durch @JsonProperty("render_js") im DTO korrekt gemappt
        val requestBody = URLInput(url, renderJs)


        try {
            // Führt den POST Request durch und mappt das Ergebnis
            val response = restTemplate.postForEntity(
                requestUrl,
                requestBody,
                AnalysisResultDTO::class.java
            )

            return response.body
                ?: throw IllegalStateException("Scraping-Analyse-Ergebnis vom Python-Service war leer.")

        } catch (e: HttpStatusCodeException) {
            // Graceful Error Handling: 4xx = Client-Fehler (z.B. zu wenig Text), 5xx = Server-Fehler
            val pythonErrorDetail = try {
                e.responseBodyAsString.substringAfter("{\"detail\":\"").substringBeforeLast("\"}")
            } catch (ex: Exception) {
                e.responseBodyAsString
            }
            
            val errorMsg = "Web-Scraping fehlgeschlagen (${e.statusCode.value()}): $pythonErrorDetail"
            logger.warn("⚠️ $errorMsg")
            
            // Werfe keine RuntimeException mehr, sondern IllegalStateException für bessere Spring-Behandlung
            throw IllegalStateException(errorMsg, e)

        } catch (e: ResourceAccessException) {
            val errorMsg = "Python-Backend nicht erreichbar: Ist der Service gestartet? (${e.message})"
            logger.error("❌ $errorMsg")
            throw IllegalStateException(errorMsg, e)
        } catch (e: Exception) {
            val errorMsg = "Unerwarteter Fehler beim Scraping: ${e.message}"
            logger.error("❌ $errorMsg", e)
            throw IllegalStateException(errorMsg, e)
        }
    }

    // In PythonAnalysisClient.kt
    /**
     * Python mitteilen, Kotlin ist aktiv
     */
    fun triggerKnowledgeRefresh(): String {
        val url = "$pythonApiBaseUrl/internal/admin/refresh-knowledge"
        println("📡 Sende Refresh-Signal an Python: $url")

        return try {
            // Wir senden einen leeren POST Request
            val response = restTemplate.postForEntity(url, null, Map::class.java)

            if (response.statusCode.is2xxSuccessful) {
                "✅ Python Refresh erfolgreich! Status: ${response.body?.get("status")}"
            } else {
                "⚠️ Python hat mit Fehler geantwortet: ${response.statusCode}"
            }
        } catch (e: Exception) {
            println("❌ Fehler beim Senden des Refresh-Signals: ${e.message}")
            "❌ Fehler: Konnte Python nicht erreichen. (${e.message})"
        }
    }

    /**
     * 5. CHECK HEALTH (Admin: Status prüfen)
     * FIX: Nutzt 'exchange' statt 'getForEntity', um den Map-Typ strikt festzulegen.
     */
    fun checkHealth(): Map<String, Any> {
        return try {
            val url = "$pythonApiBaseUrl/system/status"

            // Wir sagen Spring explizit: "Wir wollen eine Map<String, Any>"
            val responseType = object : ParameterizedTypeReference<Map<String, Any>>() {}

            val response = restTemplate.exchange(
                url,
                HttpMethod.GET,
                null,
                responseType
            )

            response.body ?: mapOf("status" to "UNKNOWN")
        } catch (e: Exception) {
            // Falls Python tot ist, geben wir das sauber zurück
            mapOf("status" to "OFFLINE", "error" to (e.message ?: "Unknown"))
        }
    }

    // ------------------------ DASHBOARD / REPORTING -------------------------

    fun getDashboardMetrics(topN: Int = 10): Map<String, Any> {
        val url = "$pythonApiBaseUrl/reports/dashboard-metrics?top_n=$topN"
        return try {
            val responseType = object : ParameterizedTypeReference<Map<String, Any>>() {}
            val response = restTemplate.exchange(url, HttpMethod.GET, null, responseType)
            response.body ?: emptyMap()
        } catch (e: Exception) {
            println("❌ Fehler beim Abrufen von Dashboard-Metriken: ${e.message}")
            mapOf("error" to (e.message ?: "Unknown error"))
        }
    }

    fun downloadCsvReport(): ByteArray? {
        val url = "$pythonApiBaseUrl/reports/export.csv"
        return try {
            restTemplate.getForObject(url, ByteArray::class.java)
        } catch (e: Exception) {
            println("❌ Fehler beim CSV-Download von Python: ${e.message}")
            null
        }
    }

    fun downloadPdfReport(): ByteArray? {
        val url = "$pythonApiBaseUrl/reports/export.pdf"
        return try {
            restTemplate.getForObject(url, ByteArray::class.java)
        } catch (e: Exception) {
            println("❌ Fehler beim PDF-Download von Python: ${e.message}")
            null
        }
    }
}
