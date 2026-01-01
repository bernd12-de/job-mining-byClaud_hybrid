package de.layher.jobmining.kotlinapi.domain.rules

// core/domain/rules/SkillBlacklist.kt
object SkillBlacklist {
    // Minimale Blacklist - nur echte Noise-Wörter, keine Fachbegriffe!
    // WICHTIG: Keine technischen Begriffe wie "entwicklung", "management" etc. blockieren
    private val blacklist = setOf(
        "erfahrung", "kenntnisse", "bereich", "aufgaben",
        "verantwortung", "sowie"
    )

    fun isBlacklisted(label: String): Boolean = label.lowercase() in blacklist
}
