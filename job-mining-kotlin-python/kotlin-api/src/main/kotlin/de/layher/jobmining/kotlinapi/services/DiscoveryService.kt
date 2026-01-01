package de.layher.jobmining.kotlinapi.services

import de.layher.jobmining.kotlinapi.infrastructure.DiscoveryRepository
import org.springframework.stereotype.Service

@Service
class DiscoveryService(
    private val discoveryRepository: DiscoveryRepository
) {
    fun getCandidates(): List<DiscoveryRepository.Candidate> = discoveryRepository.listCandidates()

    fun getApprovedMappings(): Map<String, String> = discoveryRepository.listApproved()

    fun getIgnoreList(): List<String> = discoveryRepository.listIgnore()

    fun approve(term: String, canonicalLabel: String) {
        discoveryRepository.approve(term, canonicalLabel)
    }

    fun reject(term: String) {
        discoveryRepository.reject(term)
    }
}
