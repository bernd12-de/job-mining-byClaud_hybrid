package de.layher.jobmining.kotlinapi.presentation

import org.springframework.beans.factory.annotation.Value
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController
import io.swagger.v3.oas.annotations.Operation
import io.swagger.v3.oas.annotations.tags.Tag

@RestController
@RequestMapping("/api/links")
@Tag(name = "Service Links", description = "Zugriff auf alle verfügbaren UIs und Dashboards")
class ServiceLinksController(
    @Value("\${server.port:8080}") private val serverPort: String
) {
    
    data class ServiceLink(
        val name: String,
        val description: String,
        val url: String,
        val category: String
    )
    
    data class ServiceLinksResponse(
        val services: List<ServiceLink>,
        val info: String
    )

    @GetMapping
    @Operation(
        summary = "Alle verfügbaren Service-Links",
        description = """
            Liefert URLs zu allen verfügbaren UIs und Dashboards:
            - Swagger UI (diese API-Dokumentation)
            - Streamlit Dashboard (🔐 Passwort-geschützt: admin123, Visualisierung & Docker Management)
            - Python FastAPI Docs (Backend-API mit NLP-Engine)
            - Actuator Health (System-Status)
            
            ⚠️ WICHTIG - KERNFUNKTION:
            POST /api/v1/jobs/upload - Stellenanzeige hochladen (PDF/DOCX)
            
            Hinweis: Bei GitHub Codespaces URLs anpassen:
            localhost → https://CODESPACE_NAME-PORT.app.github.dev
        """
    )
    fun getServiceLinks(): ServiceLinksResponse {
        val baseUrl = if (serverPort == "8080") "http://localhost" else "http://localhost:$serverPort"
        
        return ServiceLinksResponse(
            services = listOf(
                ServiceLink(
                    name = "Swagger UI",
                    description = "API-Dokumentation & Discovery-Review (Kandidaten freigeben/ablehnen)",
                    url = "$baseUrl:8080/swagger-ui/index.html",
                    category = "API Documentation"
                ),
                ServiceLink(
                    name = "Streamlit Dashboard",
                    description = "🐳 Docker Management (Restart, Logs), Visualisierung & Reports | 🔐 Passwort: admin123",
                    url = "http://localhost:8501",
                    category = "Dashboard"
                ),
                ServiceLink(
                    name = "Python FastAPI Docs",
                    description = "Python Backend API-Tests & Workflow-Management",
                    url = "http://localhost:8000/docs",
                    category = "API Documentation"
                ),
                ServiceLink(
                    name = "Actuator Health",
                    description = "System-Status: DB, Disk, Liveness, Readiness",
                    url = "$baseUrl:8080/actuator/health",
                    category = "Monitoring"
                ),
                ServiceLink(
                    name = "Discovery Candidates",
                    description = "Unbekannte Begriffe aus Job-Analysen (JSON-API)",
                    url = "$baseUrl:8080/api/discovery/candidates",
                    category = "Discovery"
                ),
                ServiceLink(
                    name = "Discovery Approved",
                    description = "Freigegebene Skill-Mappings (JSON-API)",
                    url = "$baseUrl:8080/api/discovery/approved",
                    category = "Discovery"
                ),
                ServiceLink(
                    name = "Discovery Ignore",
                    description = "Abgelehnte Begriffe (JSON-API)",
                    url = "$baseUrl:8080/api/discovery/ignore",
                    category = "Discovery"
                )
            ),
            info = """
                ✅ Alle Services laufen im Docker-Stack. 
                
                🔧 KERN-ENDPOINTS:
                • POST /api/v1/jobs/upload - Datei hochladen (PDF/DOCX)
                • POST /api/v1/jobs/scrape - URL scrapen & analysieren
                • GET /api/v1/jobs - Alle Jobs abrufen
                
                📊 DASHBOARD-FEATURES:
                • Live-Logs von Python/Kotlin/DB
                • Container-Restart per Knopf
                • Analytics & Reports
                
                🔐 Dashboard-Passwort: admin123
            """.trimIndent()
        )
    }
}