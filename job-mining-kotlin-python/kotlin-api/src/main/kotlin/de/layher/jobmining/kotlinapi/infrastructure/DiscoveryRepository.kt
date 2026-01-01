package de.layher.jobmining.kotlinapi.infrastructure

import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import com.fasterxml.jackson.module.kotlin.readValue
import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Repository
import java.io.File

@Repository
class DiscoveryRepository(
    @Value("\${app.data.base-path:/app/data}")
    private val basePath: String
) {
    private val objectMapper = jacksonObjectMapper()
    data class Candidate(
        val term: String,
        val role: String? = null,
        val context: String? = null,
        val count: Int = 1
    )

    private fun discoveryDir(): File {
        var dir = File("$basePath/discovery")
        if (!dir.exists()) {
            // Fallback für lokale Entwicklung außerhalb Docker
            dir = File("../python-backend/data/discovery")
        }
        if (!dir.exists()) {
            dir.mkdirs()
        }
        return dir
    }

    private fun candidatesFile(): File = File(discoveryDir(), "candidates.json")
    private fun approvedFile(): File = File(discoveryDir(), "approved_skills.json")
    private fun ignoreFile(): File = File(discoveryDir(), "ignore_skills.json")

    fun listCandidates(): List<Candidate> {
        val f = candidatesFile()
        if (!f.exists() || f.length() == 0L) return emptyList()
        val ignored: Set<String> = try {
            val ig = ignoreFile()
            if (ig.exists() && ig.length() > 0) {
                objectMapper.readValue<List<String>>(ig).map { it.lowercase().trim() }.toSet()
            } else emptySet()
        } catch (e: Exception) { emptySet() }
        return try {
            objectMapper.readValue<List<Candidate>>(f).filterNot { ignored.contains(it.term.lowercase().trim()) }
        } catch (e: Exception) {
            emptyList()
        }
    }

    fun listApproved(): Map<String, String> {
        val f = approvedFile()
        if (!f.exists() || f.length() == 0L) return emptyMap()
        return try {
            objectMapper.readValue(f)
        } catch (e: Exception) {
            emptyMap()
        }
    }

    fun approve(term: String, canonicalLabel: String) {
        val current = listApproved().toMutableMap()
        current[term] = canonicalLabel
        val f = approvedFile()
        objectMapper.writerWithDefaultPrettyPrinter().writeValue(f, current)
        // Kandidat entfernen
        try {
            val remaining = listCandidates().filterNot { it.term.equals(term, ignoreCase = true) }
            objectMapper.writerWithDefaultPrettyPrinter().writeValue(candidatesFile(), remaining)
        } catch (_: Exception) {
            // ignore
        }
    }

    fun listIgnore(): List<String> {
        val f = ignoreFile()
        if (!f.exists() || f.length() == 0L) return emptyList()
        return try {
            objectMapper.readValue(f)
        } catch (_: Exception) {
            emptyList()
        }
    }

    fun reject(term: String) {
        val ignored = listIgnore().toMutableSet()
        ignored.add(term)
        objectMapper.writerWithDefaultPrettyPrinter().writeValue(ignoreFile(), ignored.toList())
        // Kandidat entfernen
        try {
            val remaining = listCandidates().filterNot { it.term.equals(term, ignoreCase = true) }
            objectMapper.writerWithDefaultPrettyPrinter().writeValue(candidatesFile(), remaining)
        } catch (_: Exception) {
            // ignore
        }
    }
}
