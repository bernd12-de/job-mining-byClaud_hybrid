package de.layher.jobmining.kotlinapi.adapters

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonCreator // NEUER IMPORT
import java.time.LocalDate

/**
 * DTO für eine einzelne extrahierte Kompetenz (Entspricht Python models.CompetenceDTO)
 */
data class CompetenceDTO @JsonCreator constructor(
    // Achtung: Wenn @JsonCreator genutzt wird, müssen alle Properties explizit im Konstruktor stehen.
    // Die @JsonProperty-Annotationen sind korrekt gesetzt.
    // 🚨 FIX 2: id muss String/Optional sein, da Python ESCO-ID (String) sendet
//    @JsonProperty("id")
//    val id: String?,

    @JsonProperty("original_term")
    val originalTerm: String,

    @JsonProperty("confidence_score")
    val confidenceScore: Double,

    @JsonProperty("esco_label")
    val escoLabel: String,

    @JsonProperty("esco_uri")
    val escoUri: String,

    // Optional, da Custom Skills keinen ESCO Group Code haben
    @JsonProperty("esco_group_code")
    val escoGroupCode: String? = null,


    // --- NEU: Flags von Python empfangen ---
    @JsonProperty("is_digital")
    val isDigital: Boolean = false,

    @JsonProperty("is_discovery")
    val isDiscovery: Boolean = false,
    // ---------------------------------------

    @JsonProperty("level") val level: Int = 2, // 2=ESCO, 4=Fachbuch, 5=Uni
    @JsonProperty("role_context") val roleContext: String? = null,
    @JsonProperty("source_domain") val sourceDomain: String? = null
)

/**
 * DTO für das gesamte Analyseergebnis (Entspricht Python models.AnalysisResultDTO)
 */
data class AnalysisResultDTO @JsonCreator constructor(
    // KORREKTUR: Alle Felder im Konstruktor müssen explizit mit @JsonProperty annotiert werden.
    @JsonProperty("title")
    val title: String,

    @JsonProperty("job_role")
    val jobRole: String,

    @JsonProperty("region")
    val region: String,

    @JsonProperty("industry")
    val industry: String,

    @JsonProperty("posting_date")
    val postingDate: String,

    @JsonProperty("raw_text_hash")
    val rawTextHash: String,

    @JsonProperty("raw_text")
    val rawText: String,

    @JsonProperty("is_segmented")
    val is_segmented: Boolean = false,

    @JsonProperty("source_url")
    val sourceUrl: String? = null,

    @JsonProperty("competences") // Das Feld war bereits korrekt annotiert
    val competences: List<CompetenceDTO>

)
