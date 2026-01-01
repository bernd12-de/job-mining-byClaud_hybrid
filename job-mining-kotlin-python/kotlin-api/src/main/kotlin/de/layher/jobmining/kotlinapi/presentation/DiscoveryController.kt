package de.layher.jobmining.kotlinapi.presentation

import de.layher.jobmining.kotlinapi.infrastructure.DiscoveryRepository
import de.layher.jobmining.kotlinapi.services.DiscoveryService
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/discovery")
class DiscoveryController(
    private val discoveryService: DiscoveryService
) {
    data class ApproveRequest(
        val term: String,
        val canonicalLabel: String
    )

    @GetMapping("/candidates")
    fun listCandidates(): List<DiscoveryRepository.Candidate> = discoveryService.getCandidates()

    @GetMapping("/approved")
    fun listApproved(): Map<String, String> = discoveryService.getApprovedMappings()

    @GetMapping("/ignore")
    fun listIgnore(): List<String> = discoveryService.getIgnoreList()

    @PostMapping("/approve")
    fun approve(@RequestBody req: ApproveRequest): ResponseEntity<Void> {
        if (req.term.isBlank() || req.canonicalLabel.isBlank()) {
            return ResponseEntity.badRequest().build()
        }
        discoveryService.approve(req.term, req.canonicalLabel)
        return ResponseEntity.ok().build()
    }

    data class RejectRequest(val term: String)

    @PostMapping("/reject")
    fun reject(@RequestBody req: RejectRequest): ResponseEntity<Void> {
        if (req.term.isBlank()) {
            return ResponseEntity.badRequest().build()
        }
        discoveryService.reject(req.term)
        return ResponseEntity.ok().build()
    }
}
