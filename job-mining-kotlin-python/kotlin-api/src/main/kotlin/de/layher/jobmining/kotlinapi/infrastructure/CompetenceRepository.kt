package de.layher.jobmining.kotlinapi.infrastructure

import de.layher.jobmining.kotlinapi.domain.Competence
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository

@Repository
interface CompetenceRepository : JpaRepository<Competence, Long> {
    // Hier kannst du später spezifische Abfragen für deine Statistik ergänzen,
    // z.B. alle Kompetenzen einer bestimmten Ebene (level) finden.
    fun findAllByLevel(level: Int): List<Competence>
}
