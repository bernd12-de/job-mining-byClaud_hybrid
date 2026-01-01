package de.layher.jobmining.kotlinapi.infrastructure.bridge

import de.layher.jobmining.kotlinapi.adapters.AnalysisResultDTO
import org.springframework.stereotype.Component
import org.springframework.web.client.RestTemplate
import org.springframework.beans.factory.annotation.Value

@Component
class PythonNlpBridge(
    private val restTemplate: RestTemplate,
    @Value("\${python.api.base-url:http://python-backend:8000}")
    private val baseUrl: String
) {
    /**
     * Sendet den Text an die Python-Engine und empfängt die Roh-Labels.
     * Dies löst die Typ-Inferenz-Probleme im HybridCompetenceService.
     */
//    fun analyze(text: String): List<String> {
//        return try {
//            val response = restTemplate.postForObject(
//                "$baseUrl/analyse",
//                mapOf("text" to text),
//                Array<String>::class.java
//            )
//            response?.toList() ?: emptyList()
//        } catch (e: Exception) {
//            println("❌ Fehler bei Kommunikation mit Python: ${e.message}")
//            emptyList()
//        }
//    }

    // FIX: Gibt jetzt das volle Objekt zurück
    fun analyzeFull(fileContent: ByteArray, filename: String): AnalysisResultDTO {
        // Hinweis: Hier müsstest du eigentlich Multipart-Upload nutzen (siehe PythonAnalysisClient).
        // Wenn du den PythonAnalysisClient schon hast (Adapter), ist diese Klasse ggf. redundant.
        // Falls du sie nutzt, muss sie so aussehen:
        throw UnsupportedOperationException("Nutze bitte PythonAnalysisClient für Datei-Uploads!")
    }
}
