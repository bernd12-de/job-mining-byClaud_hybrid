package de.layher.jobmining.kotlinapi.presentation


/**
 * DTO für die Darstellung aggregierter Kompetenz-Daten im Report.
 * Wird vom Controller an den Client gesendet.
 */
data class CompetenceReportDTO(
    // Der Name der Kompetenz (z.B. "Design Thinking")
    val competenceLabel: String,

    // Die Häufigkeit, mit der die Kompetenz in der Datenbank gefunden wurde (z.B. 15)
    val count: Long
)
