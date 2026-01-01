package de.layher.jobmining.kotlinapi.services

import de.layher.jobmining.kotlinapi.infrastructure.EscoDataRepository
import de.layher.jobmining.kotlinapi.infrastructure.JobPostingRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

@Service
class TrendAnalysisService(
    private val escoRepo: EscoDataRepository,
    private val jobRepo: JobPostingRepository // 🛠️ Dies ersetzt die 'db' Referenz
) {
    @Transactional
    fun analyzeJob(jobId: Long, foundLabels: List<String>) {
        // 1. Anreicherung der Skills
        val enrichedSkills = foundLabels.mapNotNull { escoRepo.getSkillByLabel(it) }

        if (enrichedSkills.isEmpty()) return

        // 2. Berechnung der Digitalisierungs-Rate
        val digitalRate = enrichedSkills.count { it.isTransversal }.toDouble() / enrichedSkills.size

        // 3. Speichern im JobPosting (Beispiel-Logik)
        jobRepo.findById(jobId).ifPresent { job ->
            // Hier speicherst du das Ergebnis in der DB über das Repository
            jobRepo.save(job)
        }
    }
}
