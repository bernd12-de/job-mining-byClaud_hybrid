package de.layher.jobmining.kotlinapi.domain
// core/domain/EscoModels.kt
data class EscoSkill(
    val uri: String,
    val preferredLabel: String,
    val altLabels: List<String>,
    val isDigital: Boolean = false,
    val isResearch: Boolean = false,
    val isTransversal: Boolean = false,
    val parentUris: List<String> = emptyList(),
    val skillGroup: String? = null
)

data class ExtractionResult(
    val term: String,
    val escoSkill: EscoSkill?,
    val timestamp: java.time.Instant = java.time.Instant.now()
)
