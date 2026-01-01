package de.layher.jobmining.kotlinapi.infrastructure

import de.layher.jobmining.kotlinapi.domain.JobPosting
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.stereotype.Repository

// Das Repository erbt von JpaRepository und ermöglicht Spring Data JPA
// das automatische Speichern, Finden und Aktualisieren der JobPosting-Entitäten.
@Repository
interface JobPostingRepository : JpaRepository<JobPosting, Long> {

    // KORREKTUR: Muss eine Liste zurückgeben (NonUniqueResultException Fix)
    fun findByRawTextHash(rawTextHash: String): List<JobPosting>
    /**
     * Aggregiert die Kompetenzen und zählt, wie oft jedes ESCO-Label vorkommt.
     * Gibt die Top-Ergebnisse zurück (z.B. die 5 häufigsten Skills).
     * Der Rückgabetyp ist ein Array von Objekten ([String, Long]).
     */
    @Query(
        """
        SELECT c.escoLabel, COUNT(c)
        FROM JobPosting jp
        JOIN jp.competences c
        GROUP BY c.escoLabel
        ORDER BY COUNT(c) DESC
        LIMIT :limit
    """
    )
    fun findTopCompetencesByCount(limit: Int): List<Array<Any>>

    // NEU: Methode zum schnellen Löschen aller Einträge
    //fun deleteAllInBatch()
}
