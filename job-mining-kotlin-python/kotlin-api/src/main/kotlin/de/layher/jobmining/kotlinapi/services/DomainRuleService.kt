package de.layher.jobmining.kotlinapi.services

import de.layher.jobmining.kotlinapi.adapters.CompetenceDTO
import de.layher.jobmining.kotlinapi.domain.DomainRule
import de.layher.jobmining.kotlinapi.domain.EscoSkill
import de.layher.jobmining.kotlinapi.infrastructure.DomainRuleRepository
import de.layher.jobmining.kotlinapi.infrastructure.EscoDataRepository
import de.layher.jobmining.kotlinapi.infrastructure.JobPostingRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

@Service
class DomainRuleService(
    private val repository: DomainRuleRepository,
    private val escoDataRepository: EscoDataRepository,
    private val jobRepository: JobPostingRepository
) {
    // Statische Konstanten für die Regeltypen (SSoT für Typen)
    companion object {
        const val RULE_TYPE_BLACKLIST = "BLACKLIST"
        const val RULE_TYPE_INDUSTRY_MAPPING = "INDUSTRY_MAPPING"
        const val RULE_TYPE_ROLE_MAPPING = "ROLE_MAPPING"
    }

    /**
     * Gibt alle aktiven Blacklist-Einträge als Liste von Strings zurück.
     * Dies wird der Endpunkt, den das Python-Backend abfragen wird.
     */
    @Transactional(readOnly = true)
    fun getActiveBlacklistKeys(): List<String> {
        return repository.findAllByRuleTypeAndIsActiveTrue(RULE_TYPE_BLACKLIST)
            .map { it.ruleKey }
    }

    // In DomainRuleService.kt / DomainRuleController.kt
    fun getKnowledgeBaseStats(): Map<String, Any> {
        val jobs = jobRepository.findAll()
        val segmentedCount = jobs.count { it.isSegmented }
        val totalJobs = jobs.size
        val allSkills = escoDataRepository.findAllLoadedSkills()

        val successRate = if (totalJobs > 0) (segmentedCount.toDouble() / totalJobs * 100) else 100.0

        return mapOf(
            "total_skills" to allSkills.size,
            "analysis_quality" to mapOf(
                "total_analyzed_jobs" to totalJobs,
                "segmentation_success_rate" to successRate,
                "warning" to if (segmentedCount < totalJobs) "Achtung: Einige Analysen nutzen Rohtext-Fallback (Precision-Risiko)" else "Optimal"
            ),
            "ssot_skills_total" to allSkills.size
        )
    }

    /**
     * Gibt alle aktiven Branchen-Mappings als Map<Branche, Regex-Muster> zurück.
     * Dies ist der zukünftige SSoT für den Organization Service.
     */
    @Transactional(readOnly = true)
    fun getActiveIndustryMappings(): Map<String, String> {
        return repository.findAllByRuleTypeAndIsActiveTrue(RULE_TYPE_INDUSTRY_MAPPING)
            .filter { it.ruleValue != null }
            .associate { it.ruleKey to it.ruleValue!! }
    }



    // 🚨 FIX: Diese Methode wird vom HybridCompetenceService aufgerufen
    fun isBlacklisted(term: String): Boolean {
        // Sucht in der DB nach einem Eintrag vom Typ BLACKLIST mit diesem Key
        return repository.findByRuleTypeAndRuleKey(RULE_TYPE_BLACKLIST, term.lowercase()).isNotEmpty()
    }

    /**
     * Gibt alle aktiven Rollen-Mappings als Map<Rolle, Regex-Muster> zurück.
     */
    @Transactional(readOnly = true)
    fun getActiveRoleMappings(): Map<String, String> {
        return repository.findAllByRuleTypeAndIsActiveTrue(RULE_TYPE_ROLE_MAPPING)
            .filter { it.ruleValue != null }
            .associate { it.ruleKey to it.ruleValue!! } // ruleKey=Rolle, ruleValue=Regex
    }

    // In DomainRuleService.kt hinzufügen:

    /**
     * Holt alle geladenen ESCO-Kompetenzen für die API-Synchronisation mit Python.
     * Dies stellt sicher, dass Python die exakt gleichen 31.655 Begriffe nutzt.
     */
    @Transactional(readOnly = true)
    fun getAllCompetences(): List<CompetenceDTO> {
        // Wir nutzen die neue Methode aus deinem Repository
        return escoDataRepository.findAllLoadedSkills().map { escoSkill ->
            CompetenceDTO(
                escoLabel = escoSkill.preferredLabel,
                escoUri = escoSkill.uri,
                originalTerm = escoSkill.preferredLabel,
                confidenceScore = 1.0,
                escoGroupCode = escoSkill.skillGroup ?: "GENERIC" // Fallback falls null
            )
        }
    }
}
