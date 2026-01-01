package de.layher.jobmining.kotlinapi.services

import de.layher.jobmining.kotlinapi.infrastructure.bridge.PythonNlpBridge
import de.layher.jobmining.kotlinapi.infrastructure.JobPostingRepository
import de.layher.jobmining.kotlinapi.infrastructure.EscoDataRepository
import de.layher.jobmining.kotlinapi.infrastructure.CompetenceRepository // 🚨 WICHTIG: Repository hinzufügen
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import de.layher.jobmining.kotlinapi.domain.Competence

@Service
class HybridCompetenceService(
    private val pythonBridge: PythonNlpBridge,
    private val escoRepo: EscoDataRepository,
    private val jobRepo: JobPostingRepository,
    private val competenceRepo: CompetenceRepository // 🚨 Hinzugefügt für das Speichern
) {

    @Transactional
    fun processAndSave(jobId: Long, text: String) {
        // 1. Hole das Job-Posting aus der DB
        val job = jobRepo.findById(jobId).orElseThrow {
            IllegalArgumentException("Job mit ID $jobId nicht gefunden")
        }

        // 2. Extraktion via Python (Ebenen 1-5 + 6 werden dort bestimmt)
        // Die Bridge muss ein AnalysisResultDTO zurückgeben
        val analysisResult = pythonBridge.analyzeFull(text.toByteArray(), "scan.txt")

        // 3. Transformation der DTOs in Domain-Entitäten
        val newCompetences = analysisResult.competences.map { dto ->
            // FIX: Wir müssen ALLE Pflichtfelder aus deinem DB-Schema befüllen!
            Competence(
                originalTerm = dto.originalTerm,
                escoLabel = dto.escoLabel,
                escoUri = dto.escoUri,
                confidenceScore = dto.confidenceScore,

                // Neue Felder aus deinem V2 Schema
                level = dto.level,
                sourceDomain = dto.sourceDomain ?: "Hybrid-Analysis",
                isDigital = dto.isDigital,
                isDiscovery = dto.isDiscovery,
                roleContext = analysisResult.jobRole, // Dynamisch aus der Analyse


            ).apply { this.jobPosting = job }
        }

        // 4. In die DB schreiben
        competenceRepo.saveAll(newCompetences)

        // 5. Metadaten am Job aktualisieren (Ebene 6)
        job.isSegmented = analysisResult.is_segmented
        job.jobRole = analysisResult.jobRole
        jobRepo.save(job)

        println("--- ✅ HYBRID-UPDATE: Job ${job.id} mit ${newCompetences.size} Skills nachqualifiziert.")
    }
}
