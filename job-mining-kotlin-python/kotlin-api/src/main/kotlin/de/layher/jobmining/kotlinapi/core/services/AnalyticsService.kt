package de.layher.jobmining.kotlinapi.core.services

import de.layher.jobmining.kotlinapi.domain.rules.SkillBlacklist
import de.layher.jobmining.kotlinapi.domain.EscoSkill // Falls benötigt
import de.layher.jobmining.kotlinapi.infrastructure.EscoDataRepository
// Und der Import für dein Repository (wahrscheinlich in infrastructure oder domain)
// core/services/AnalyticsService.kt
class AnalyticsService(private val repo: EscoDataRepository) {

    fun calculateDigitalShare(foundLabels: List<String>): Double {
        val validSkills = foundLabels
            .filterNot { SkillBlacklist.isBlacklisted(it) }
            .mapNotNull { repo.getSkillByLabel(it) }

        if (validSkills.isEmpty()) return 0.0

        val digitalCount = validSkills.count { it.isDigital }
        return (digitalCount.toDouble() / validSkills.size) * 100
    }
}
