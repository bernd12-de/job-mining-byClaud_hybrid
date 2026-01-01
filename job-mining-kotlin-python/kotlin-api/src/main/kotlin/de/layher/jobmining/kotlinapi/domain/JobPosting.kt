package de.layher.jobmining.kotlinapi.domain

import jakarta.persistence.*
import java.time.LocalDate

// 🚨 FIX 1: Wechsel von data class zu class
@Entity
@Table(name = "job_posting")
class JobPosting(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @Column(nullable = false,length = 1024)
    val title: String,
    @Column(name = "job_role", nullable = false,length = 512)
    var jobRole: String,

    @Column(name = "raw_text_hash",nullable = false,columnDefinition = "TEXT",unique = true)
    val rawTextHash: String, // <- Wichtig für Idempotenz und Hashcode

    @Column(name = "raw_text", nullable = false, columnDefinition = "TEXT")
    val rawText: String,

    @Column(name = "posting_date", nullable = false)
    val postingDate: LocalDate,

    // In JobPosting.kt hinzufügen
    @Column(name = "is_segmented", nullable = false)
    var isSegmented: Boolean = false,

    @Column(name = "source_url", length = 2048)
    val sourceUrl: String? = null,

    @Column(nullable = false, length = 255)
    val region: String,
    @Column(nullable = false, length = 512)
    val industry: String,
) {
    // 🚨 FIX 2: Die bidirektionale Beziehung (ToMany) bleibt im Body.
    @OneToMany(mappedBy = "jobPosting", cascade = [CascadeType.ALL], orphanRemoval = true, fetch = FetchType.LAZY)
    @com.fasterxml.jackson.annotation.JsonManagedReference // 👈 Das ist die "Hauptseite"
    var competences: MutableSet<Competence> = mutableSetOf()

    // 🚨 FIX 3: Manuelle Implementierung von equals und hashCode (ohne competences!)
    // Wir verwenden rawTextHash als Business-Key, da es UNIQUE ist (Idempotenz).
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is JobPosting) return false

        // Wir nutzen den Hash des Textes zur Identifizierung, falls die ID noch null ist
        return rawTextHash == other.rawTextHash
    }

    override fun hashCode(): Int {
        // Wir nutzen den Hash des Textes zur Identifizierung
        return rawTextHash.hashCode()
    }
}
