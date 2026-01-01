package de.layher.jobmining.kotlinapi.infrastructure

import de.layher.jobmining.kotlinapi.domain.EscoSkill
import de.layher.jobmining.kotlinapi.infrastructure.io.IOService
import org.springframework.stereotype.Repository
import org.springframework.beans.factory.annotation.Value
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicBoolean
import jakarta.annotation.PostConstruct
import java.io.File
import kotlin.concurrent.thread
import org.slf4j.LoggerFactory

@Repository
class EscoDataRepository(
    private val ioService: IOService,
    @Value("\${app.esco.data-path:./python-backend/data/esco}") private val escoFolderPath: String
) {
    // 1. Primärspeicher: Alles läuft über die URI (eindeutig!)
    private val skillByUri = ConcurrentHashMap<String, EscoSkill>()
    private val occupationByUri = ConcurrentHashMap<String, EscoOccupation>()

    // 2. Lookup-Index: Welches Wort gehört zu welcher URI?
    private val skillKeyToUri = ConcurrentHashMap<String, String>()
    private val occupationKeyToUri = ConcurrentHashMap<String, String>()

    // 3. Relationen: Welcher Beruf hat welche Skills?
    private val skillsByOccupation = ConcurrentHashMap<String, MutableList<OccSkillRel>>()

    private val isReady = AtomicBoolean(false)

    private val logger = LoggerFactory.getLogger(EscoDataRepository::class.java)

    // Dein Speicher im RAM
    private val competenceCache = mutableListOf<EscoSkill>()

    @PostConstruct
    fun init() {
        println("🛠️ ESCO-Struktur-Loader startet...")
        var filetmp: String ="";

        thread(start = true, name = "EscoMasterLoader") {
            try {
                val folder = resolveEscoFolder(File(escoFolderPath))
                // 1. ANZEIGE: WELCHE DATEI WIRD GELADEN?
                println("📂 [ESCO-LOADER] Starte Laden der Datei: $folder")
                if (folder != null) {
                    filetmp = folder.toString();
                    loadAllFiles(folder)
                    isReady.set(true)
                    val totalKeys = skillKeyToUri.size + occupationKeyToUri.size
                    println("✅ SSoT BEREIT: $totalKeys Suchbegriffe, ${skillsByOccupation.size} Berufs-Skill-Relationen.")
                }
            } catch (e: Exception) { println("❌ [ESCO-LOADER] bei $filetmp Fehler: ${e.message}") }
        }
    }

    private fun loadAllFiles(folder: File) {
        val files = folder.listFiles { f -> f.extension == "csv" } ?: emptyArray()

        // 1. ANZEIGE: WELCHE DATEI WIRD GELADEN?
        println("📂 [ESCO-LOADER] Starte Laden der Datei: $files")

        // Phase 1: Skills und Occupations (Basis-Konzepte)
        files.forEach { file ->
            when {
                file.name.contains("skills", true) -> loadConcepts(file, isSkill = true)
                file.name.contains("occupations", true) -> loadConcepts(file, isSkill = false)
            }
        }

        // Phase 2: Relationen (Erst laden, wenn Konzepte da sind!)
        files.forEach { file ->
            if (file.name.contains("occupationSkillRelations", true)) loadRelations(file)
        }
    }

    private fun loadConcepts(file: File, isSkill: Boolean) {
        file.bufferedReader().use { reader ->
            val headerLine = reader.readLine()?.replace("\uFEFF", "") ?: return

            // DER FIX: Dynamische Delimiter-Erkennung auch hier!
            val delimiter = if (headerLine.count { it == ';' } > headerLine.count { it == ',' }) ';' else ','
            val header = splitCsv(headerLine, delimiter).map { it.trim('"', ' ') }

            val uriIdx = header.indexOf("conceptUri")
            val prefIdx = header.indexOf("preferredLabel")
            val altIdx = header.indexOfFirst { it.contains("altLabels", true) || it.contains("alternativeLabel", true) }

            if (uriIdx == -1 || prefIdx == -1) return

            reader.forEachLine { line ->
                if (line.isBlank()) return@forEachLine
                val cols = splitCsv(line, delimiter)
                if (cols.size > prefIdx) {
                    val uri = cols[uriIdx].trim('"', ' ')
                    val label = cols[prefIdx].trim('"', ' ')

                    // SYNONYM-ERZWINGUNG: Wir splitten am Pipe-Symbol |
                    val rawAlts = if (altIdx != -1 && cols.size > altIdx) cols[altIdx] else ""
                    val alts = rawAlts.split("|")
                        .map { it.trim('"', ' ', '\n', '\r') }
                        .filter { it.length > 1 }

                    if (isSkill) {
                        skillByUri[uri] = EscoSkill(uri, label, alts)
                        registerIndex(label, alts, uri, skillKeyToUri)
                    } else {
                        occupationByUri[uri] = EscoOccupation(uri, label, alts)
                        registerIndex(label, alts, uri, occupationKeyToUri)
                    }
                }
            }
        }
        println("  |-- Concept-Update: ${if(isSkill) "Skills" else "Occupations"} aus ${file.name}")
    }

    private fun loadRelations(file: File) {
        file.bufferedReader().use { reader ->
            val header = splitCsv(reader.readLine() ?: "", ',').map { it.trim('"', ' ') }
            val occIdx = header.indexOf("occupationUri")
            val skillIdx = header.indexOf("skillUri")
            val typeIdx = header.indexOf("relationType")

            if (occIdx == -1 || skillIdx == -1) return

            reader.forEachLine { line ->
                val cols = splitCsv(line, ',')
                if (cols.size > maxOf(occIdx, skillIdx)) {
                    val occUri = cols[occIdx].trim('"', ' ')
                    val skillUri = cols[skillIdx].trim('"', ' ')
                    val type = if (typeIdx != -1 && cols[typeIdx].contains("optional")) RelType.OPTIONAL else RelType.ESSENTIAL

                    skillsByOccupation.getOrPut(occUri) { mutableListOf() }.add(OccSkillRel(occUri, skillUri, type))
                }
            }
        }
        println("  |-- Relations-Update: Relationen aus ${file.name}")
    }

    private fun registerIndex(label: String, alts: List<String>, uri: String, map: ConcurrentHashMap<String, String>) {
        map[label.lowercase().trim()] = uri
        alts.forEach { map[it.lowercase().trim()] = uri }
    }

    private fun splitCsv(l: String, d: Char): List<String> {
        val r = mutableListOf<String>(); var s = StringBuilder(); var q = false
        for (c in l) { if (c == '\"') q = !q else if (c == d && !q) { r.add(s.toString()); s = StringBuilder() } else s.append(c) }
        r.add(s.toString()); return r
    }

    // --- ÖFFENTLICHE API FÜR DEINE SERVICES ---

    fun getSkillByLabel(label: String): EscoSkill? {
        val uri = skillKeyToUri[label.lowercase().trim()] ?: return null
        return skillByUri[uri]
    }

    fun getOccupationByLabel(label: String): EscoOccupation? {
        val uri = occupationKeyToUri[label.lowercase().trim()] ?: return null
        return occupationByUri[uri]
    }

    fun getSkillsForOccupation(occUri: String): List<OccSkillRel> = skillsByOccupation[occUri] ?: emptyList()

    fun isSystemReady() = isReady.get()
    fun findAllLoadedSkills() = skillByUri.values.toList()

    // Für die PDF-Suche in resolveEscoFolder (Pfad-Logik bleibt gleich)
    private fun resolveEscoFolder(start: File): File? {
        var curr: File? = start
        repeat(3) {
            if (curr?.exists() == true && curr!!.isDirectory && curr!!.listFiles()?.any { it.extension == "csv" } == true) return curr
            curr = curr?.parentFile?.let { File(it, start.path.removePrefix("./")) } ?: curr?.parentFile
        }
        return null
    }
}

// Hilfs-Modelle
data class EscoOccupation(val uri: String, val preferredLabel: String, val altLabels: List<String>)
enum class RelType { ESSENTIAL, OPTIONAL }
data class OccSkillRel(val occupationUri: String, val skillUri: String, val type: RelType)
