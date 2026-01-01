package de.layher.jobmining.kotlinapi.presentation

import de.layher.jobmining.kotlinapi.adapters.CompetenceDTO
import de.layher.jobmining.kotlinapi.services.DomainRuleService
import org.springframework.web.bind.annotation.*
import io.swagger.v3.oas.annotations.Operation
import io.swagger.v3.oas.annotations.tags.Tag
import org.springframework.http.ResponseEntity

@RestController
@RequestMapping("/api/v1/rules")
@Tag(name = "Regelverwaltung", description = "API für das Abrufen und Verwalten von Domänenregeln (Blacklist, Mappings).")
class DomainRuleController(
    private val domainRuleService: DomainRuleService
) {

    @Operation(
        summary = "Blacklist abrufen",
        description = "Gibt alle aktiven Blacklist-Schlüssel (generische Begriffe) als Liste zurück. Wird vom Python-Backend verwendet."
    )
    @GetMapping("/blacklist")
    fun getBlacklist(): ResponseEntity<List<String>> {
        val blacklist = domainRuleService.getActiveBlacklistKeys()
        return ResponseEntity.ok(blacklist)
    }

    @Operation(
        summary = "Rollen-Mappings abrufen",
        description = "Gibt aktive Mappings von Rolle (Key) zu Regex-Muster (Value) zurück."
    )
    @GetMapping("/role-mappings")
    fun getRoleMappings(): ResponseEntity<Map<String, String>> {
        val mappings = domainRuleService.getActiveRoleMappings()
        return ResponseEntity.ok(mappings)
    }

    @Operation(
        summary = "Branchen-Mappings abrufen",
        description = "Gibt aktive Mappings von Branche (Key) zu Regex-Muster (Value) zurück."
    )
    @GetMapping("/industry-mappings")
    fun getIndustryMappings(): ResponseEntity<Map<String, String>> {
        val mappings = domainRuleService.getActiveIndustryMappings()
        return ResponseEntity.ok(mappings)
    }

    @Operation(summary = "Vollständige ESCO-Wissensbasis abrufen")
    @GetMapping("/esco-full")
    fun getFullEscoKnowledgeBase(): ResponseEntity<List<CompetenceDTO>> {
        val allSkills = domainRuleService.getAllCompetences()
        return ResponseEntity.ok(allSkills)
    }

    // --- HIER WAR DER FEHLER (Doppelte Klasse entfernt) ---

    @Operation(summary = "SSoT-Statistik abrufen", description = "Liefert Mengen und Qualitäts-Metriken.")
    @GetMapping("/stats")
    fun getStats(): ResponseEntity<Map<String, Any>> {
        return ResponseEntity.ok(domainRuleService.getKnowledgeBaseStats())
    }


}
// Zukünftige Endpunkte (z.B. POST /rules/blacklist zum Hinzufügen über Admin-UI)
// ...
