package de.layher.jobmining.kotlinapi.presentation

import de.layher.jobmining.kotlinapi.services.JobMiningService
import de.layher.jobmining.kotlinapi.domain.JobPosting
import org.springframework.http.MediaType
import org.springframework.web.bind.annotation.*
import org.springframework.web.multipart.MultipartFile

// Swagger / OpenAPI
import io.swagger.v3.oas.annotations.Operation
import io.swagger.v3.oas.annotations.Parameter
import io.swagger.v3.oas.annotations.media.Schema
// Importieren Sie das neue DTO
import de.layher.jobmining.kotlinapi.presentation.CompetenceReportDTO
import org.springframework.http.ResponseEntity
import de.layher.jobmining.kotlinapi.adapters.PythonAnalysisClient

// Modell für den URL-Input vom Frontend
data class URLRequest(val url: String)

@RestController
@RequestMapping("/api/v1/jobs")
class JobController(
    private val jobMiningService: JobMiningService,
    // 👇 HIER kommt der "Client" her. Das ist einfach deine Klasse aus 'adapters/'
    private val pythonClient: PythonAnalysisClient
) {

    @Operation(
        summary = "Web-Scraping und Analyse",
        description = "Nimmt eine Web-URL (z.B. von StepStone) entgegen, scrapt den Inhalt und speichert die Analyse. Kann JavaScript-Rendering verwenden (renderJs=true)."
    )
    @PostMapping("/scrape")
    fun scrapeUrlAndAnalyze(
        @RequestBody request: URLRequest,
        @RequestParam(required = false, defaultValue = "false") renderJs: Boolean
    ): ResponseEntity<*> {
        return try {
            if (request.url.isBlank()) {
                return ResponseEntity.badRequest().body(mapOf(
                    "error" to "Die URL darf nicht leer sein."
                ))
            }

            val result = jobMiningService.processScrapedUrl(request.url, renderJs)
            ResponseEntity.ok(result)
        } catch (e: IllegalArgumentException) {
            ResponseEntity.badRequest().body(mapOf(
                "error" to e.message
            ))
        } catch (e: Exception) {
            ResponseEntity.status(500).body(mapOf(
                "error" to "Interner Fehler: ${e.message}"
            ))
        }
    }


    @Operation(
        summary = "Batch-Analyse lokaler Dateien",
        description = "Verarbeitet alle Stellenanzeigen-Dateien aus dem Python 'data/jobs' Ordner und speichert die Ergebnisse in der Datenbank."
    )
    @PostMapping("/batch-analyze", "/batch-process", "/batch")
    fun analyzeLocalDirectory(): ResponseEntity<*> {
        return try {
            val results = jobMiningService.processJobDirectoryBatch()
            ResponseEntity.ok(mapOf(
                "status" to "success",
                "processed" to results.size,
                "jobs" to results
            ))
        } catch (e: Exception) {
            ResponseEntity.status(500).body(mapOf(
                "error" to "Batch-Verarbeitung fehlgeschlagen: ${e.message}"
            ))
        }
    }

    @Operation(
        summary = "ADMIN: Datenbank bereinigen",
        description = "Löscht ALLE gespeicherten Stellenanzeigen und zugehörigen Kompetenzen."
    )
    @DeleteMapping("/admin/clear-all-data")
    fun clearAllData(): Map<String, Any> {
        val count = jobMiningService.deleteAllPostings()
        return mapOf("status" to "OK", "message" to "Datenbank erfolgreich bereinigt.", "deleted_count" to count)
    }

    @Operation(
        summary = "Upload einer Stellenanzeige",
        description = "Nimmt eine PDF oder DOCX-Datei entgegen und startet den Analyse-Workflow."
    )
    @PostMapping(
        "/upload",
        consumes = [MediaType.MULTIPART_FORM_DATA_VALUE]
    )
    fun uploadAndAnalyzeJobAd(
        @Parameter(
            description = "PDF- oder DOCX-Stellenanzeige",
            required = true,
            schema = Schema(type = "string", format = "binary")
        )
        @RequestPart("file")
        file: MultipartFile
    ): ResponseEntity<*> {
        return try {
            if (file.isEmpty) {
                return ResponseEntity.badRequest().body(mapOf(
                    "error" to "Die Datei darf nicht leer sein."
                ))
            }

            val result = jobMiningService.processJobAd(
                file.bytes,
                file.originalFilename ?: "unbekannt"
            )
            ResponseEntity.ok(result)
        } catch (e: IllegalArgumentException) {
            ResponseEntity.badRequest().body(mapOf(
                "error" to e.message
            ))
        } catch (e: Exception) {
            ResponseEntity.status(500).body(mapOf(
                "error" to "Fehler bei der Dateiverarbeitung: ${e.message}"
            ))
        }
    }

    @GetMapping("/reports/competence-trends")
    fun getCompetenceTrends(
        @RequestParam(defaultValue = "5") limit: Int
    ): List<CompetenceReportDTO> {
        return jobMiningService.getTopCompetenceTrends(limit)
    }

    @GetMapping("/reports/dashboard-metrics")
    fun getDashboardMetrics(@RequestParam(defaultValue = "10") top_n: Int): ResponseEntity<*> {
        return try {
            val metrics = pythonClient.getDashboardMetrics(top_n)
            ResponseEntity.ok(metrics)
        } catch (e: Exception) {
            ResponseEntity.status(502).body(mapOf(
                "error" to "Dashboard-Metriken konnten nicht geladen werden: ${e.message}"
            ))
        }
    }

    @GetMapping("/reports/export.csv")
    fun proxyCsvReport(): ResponseEntity<*> {
        return try {
            val bytes = pythonClient.downloadCsvReport()
                ?: return ResponseEntity.status(502).body(mapOf(
                    "error" to "CSV-Report konnte nicht vom Python-Backend geladen werden"
                ))

            ResponseEntity.ok()
                .header("Content-Disposition", "attachment; filename=job_mining_data_report.csv")
                .contentType(MediaType.TEXT_PLAIN)
                .body(bytes)
        } catch (e: Exception) {
            ResponseEntity.status(502).body(mapOf(
                "error" to "Fehler beim Laden des CSV-Reports: ${e.message}"
            ))
        }
    }

    @GetMapping("/reports/export.pdf")
    fun proxyPdfReport(): ResponseEntity<*> {
        return try {
            val bytes = pythonClient.downloadPdfReport()
                ?: return ResponseEntity.status(502).body(mapOf(
                    "error" to "PDF-Report konnte nicht vom Python-Backend geladen werden"
                ))

            ResponseEntity.ok()
                .header("Content-Disposition", "attachment; filename=job_mining_report.pdf")
                .contentType(MediaType.APPLICATION_PDF)
                .body(bytes)
        } catch (e: Exception) {
            ResponseEntity.status(502).body(mapOf(
                "error" to "Fehler beim Laden des PDF-Reports: ${e.message}"
            ))
        }
    }

    @Operation(
        summary = "Alle analysierten Stellenanzeigen abrufen (paginiert, ohne rawText)",
        description = "Gibt eine paginierte Liste aller Jobs zurück. OHNE rawText für bessere Performance. Nutze GET /api/v1/jobs/{id} für Details."
    )
    @GetMapping
    fun getAllJobs(
        @RequestParam(defaultValue = "0") page: Int,
        @RequestParam(defaultValue = "20") size: Int
    ): ResponseEntity<PagedJobResponse> {
        val jobs = jobMiningService.getAllStoredJobs()

        // Paginierung
        val totalElements = jobs.size.toLong()
        val totalPages = ((totalElements + size - 1) / size).toInt()
        val start = (page * size).coerceAtMost(jobs.size)
        val end = ((page + 1) * size).coerceAtMost(jobs.size)
        val pagedJobs = jobs.subList(start, end)

        // Konvertiere zu JobSummaryDTO (OHNE rawText)
        val summaries = pagedJobs.map { job ->
            JobSummaryDTO(
                id = job.id!!,
                title = job.title,
                jobRole = job.jobRole,
                region = job.region,
                industry = job.industry,
                postingDate = job.postingDate,
                sourceUrl = job.sourceUrl,
                isSegmented = job.isSegmented,
                competenceCount = job.competences.size,
                topCompetences = job.competences
                    .sortedByDescending { it.confidenceScore }
                    .take(5)
                    .mapNotNull { it.escoLabel }
            )
        }

        val response = PagedJobResponse(
            content = summaries,
            totalElements = totalElements,
            totalPages = totalPages,
            currentPage = page,
            pageSize = size
        )

        return ResponseEntity.ok(response)
    }

    @Operation(
        summary = "Einzelnen Job mit allen Details abrufen",
        description = "Gibt einen Job mit rawText und ALLEN Kompetenzen zurück. Nutze dies nur für Detail-Ansicht!"
    )
    @GetMapping("/{id}")
    fun getJobById(@PathVariable id: Long): ResponseEntity<JobDetailDTO> {
        val job = jobMiningService.getJobById(id)
            ?: return ResponseEntity.notFound().build()

        val detail = JobDetailDTO(
            id = job.id!!,
            title = job.title,
            jobRole = job.jobRole,
            region = job.region,
            industry = job.industry,
            postingDate = job.postingDate,
            sourceUrl = job.sourceUrl,
            isSegmented = job.isSegmented,
            rawText = job.rawText,
            competences = job.competences
                .filter { it.escoLabel != null }  // Nur Kompetenzen mit ESCO-Label
                .map { comp ->
                    CompetenceSummaryDTO(
                        id = comp.id!!,
                        originalTerm = comp.originalTerm,
                        escoLabel = comp.escoLabel!!,  // Safe: durch filter garantiert non-null
                        level = comp.level,
                        isDigital = comp.isDigital
                    )
                }
        )

        return ResponseEntity.ok(detail)
    }

    @PostMapping("/admin/sync-python-knowledge")
    fun syncPythonKnowledge(): ResponseEntity<*> {
        return try {
            val result = pythonClient.triggerKnowledgeRefresh()
            ResponseEntity.ok(mapOf(
                "status" to "success",
                "message" to result
            ))
        } catch (e: Exception) {
            ResponseEntity.status(502).body(mapOf(
                "error" to "Knowledge-Refresh fehlgeschlagen: ${e.message}"
            ))
        }
    }

    @Operation(summary = "ADMIN: System-Status prüfen")
    @GetMapping("/admin/system-health")
    fun checkSystemHealth(): ResponseEntity<*> {
        return try {
            val pythonStatus = pythonClient.checkHealth()

            val fullStatus = mapOf(
                "kotlin_backend" to "ONLINE",
                "database" to "CONNECTED",
                "python_worker" to pythonStatus
            )
            ResponseEntity.ok(fullStatus)
        } catch (e: Exception) {
            ResponseEntity.status(500).body(mapOf(
                "error" to "System-Health-Check fehlgeschlagen: ${e.message}",
                "kotlin_backend" to "ONLINE",
                "python_worker" to mapOf("status" to "ERROR", "message" to e.message)
            ))
        }
    }



}
