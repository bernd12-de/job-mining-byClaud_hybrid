package de.layher.jobmining.kotlinapi.presentation

import java.time.LocalDate

/**
 * Leichtgewichtiges DTO für die Job-Liste (ohne rawText, nur Kompetenz-Anzahl)
 *
 * Verhindert "Broken Pipe" bei großen Responses.
 */
data class JobSummaryDTO(
    val id: Long,
    val title: String,
    val jobRole: String,
    val region: String,
    val industry: String,
    val postingDate: LocalDate,
    val sourceUrl: String?,
    val isSegmented: Boolean,
    val competenceCount: Int,  // Nur Anzahl, nicht alle Kompetenzen
    val topCompetences: List<String>  // Nur Top 5 Kompetenzen als Preview
)

/**
 * Detail-DTO für einzelnen Job (mit rawText und allen Kompetenzen)
 */
data class JobDetailDTO(
    val id: Long,
    val title: String,
    val jobRole: String,
    val region: String,
    val industry: String,
    val postingDate: LocalDate,
    val sourceUrl: String?,
    val isSegmented: Boolean,
    val rawText: String,  // Nur in Detail-View
    val competences: List<CompetenceSummaryDTO>  // Alle Kompetenzen
)

/**
 * Kompakte Kompetenz-Darstellung
 */
data class CompetenceSummaryDTO(
    val id: Long,
    val originalTerm: String,
    val escoLabel: String,
    val level: Int,
    val isDigital: Boolean
)

/**
 * Paginiertes Ergebnis für Job-Liste
 */
data class PagedJobResponse(
    val content: List<JobSummaryDTO>,
    val totalElements: Long,
    val totalPages: Int,
    val currentPage: Int,
    val pageSize: Int
)
