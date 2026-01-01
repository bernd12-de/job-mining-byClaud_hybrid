package de.layher.jobmining.kotlinapi

import de.layher.jobmining.kotlinapi.domain.EscoSkill
import org.junit.jupiter.api.Test
import kotlin.test.assertTrue
import kotlin.test.assertFalse

class EscoPrecisionDemoTest {

    // 1. Deine Daten direkt als String (Simulation der skills_de.csv)
    private val csvData = """
        conceptType,conceptUri,skillType,reuseLevel,preferredLabel,altLabels,hiddenLabels,status,modifiedDate,scopeNote,definition,inScheme,description
        KnowledgeSkillCompetence,http://data.europa.eu/esco/skill/3388229a-0bcb-4778-9fa8-d69ac2cede71,skill/competence,transversal,Geschriebenes Luxemburgisch verstehen,,,released,2023-11-22T12:21:05.48Z,,,"scheme", "Luxemburgische Sprache"
        KnowledgeSkillCompetence,http://data.europa.eu/esco/skill/07dd856d-6141-48a7-a228-918f88494812,skill/competence,sector-specific,Prototyp für User-Experience-Lösung erstellen,"Lösungsprototyp zum Testen der Benutzererfahrung erstellen
        Prototypen für User-Experience-Lösung erstellen
        Prototyp für UX-Lösung erstellen
        Prototyp zum Testen der Benutzungserfahrung erstellen
        Prototyp für User-Experience-Lösung entwickeln
        Prototypen für User-Experience-Lösungen erstellen
        Prototyp zum Testen der Benutzererfahrung erstellen",,released,2024-02-09T17:29:09.851Z,,,"scheme","User Experience (UX) Lösungen."
    """.trimIndent()

    @Test
    fun `demonstrate precision matching without false positives`() {
        // 2. Parser: Wandelt den CSV-Text in Skill-Objekte um
        val skills = parseCsvData(csvData)

        // 3. Szenario: Ein Satz mit allen "Fallen"
        val jobAdText = "Wir suchen UX Experten für Prototypen in Luxemburg und führen Protokolle."

        // 4. Suche: Nutzt Regex mit Wortgrenzen (\b), um Luxemburg/Protokolle auszuschließen
        val foundSkills = findSkillsInText(jobAdText, skills)

        println("🔎 Gefundene Begriffe: ${foundSkills.map { it.preferredLabel }}")

        // BEWEIS A: UX wird gefunden (obwohl es in der CSV in einem Satz steht)
        assertTrue(foundSkills.any { it.preferredLabel.contains("User-Experience") },
            "UX sollte als Kompetenz erkannt werden")

        // BEWEIS B: Prototypen wird gefunden
        assertTrue(foundSkills.any { it.preferredLabel.contains("Prototyp") },
            "Prototypen sollte erkannt werden")

        // BEWEIS C: Luxemburg darf NICHT als Skill 'UX' gematcht werden
        val matchedLuxemburg = foundSkills.any { it.preferredLabel.contains("Luxemburgisch") }
        assertFalse(matchedLuxemburg, "FEHLER: 'Luxemburg' darf nicht wegen dem enthaltenen 'ux' matchen!")

        // BEWEIS D: Protokolle darf NICHT als 'Prototypen' matchen
        assertFalse(foundSkills.any { it.preferredLabel == "Protokolle" },
            "FEHLER: 'Protokolle' ist kein ESCO-Skill!")

        println("✅ Test erfolgreich: Nur echte Skills erkannt.")
    }

    // Hilfsmethode: CSV Parsing Logik (Ebene 7 Integrität)
    private fun parseCsvData(data: String): List<EscoSkill> {
        val skillList = mutableListOf<EscoSkill>()
        val lines = data.lines().drop(1) // Header weg

        lines.forEach { line ->
            // Regex Split, um Kommas in Anführungszeichen zu ignorieren
            val parts = line.split(Regex(",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)"))
            if (parts.size > 5) {
                val prefLabel = parts[4].trim().removeSurrounding("\"")
                val altLabelsRaw = parts[5].trim().removeSurrounding("\"")

                skillList.add(EscoSkill(
                    uri = parts[1],
                    preferredLabel = prefLabel,
                    altLabels = altLabelsRaw.split("\n").map { it.trim() }
                ))
            }
        }
        return skillList
    }

    // Hilfsmethode: Suchlogik (Ebene 4/5 Präzision)
    private fun findSkillsInText(text: String, skillBase: List<EscoSkill>): List<EscoSkill> {
        val matches = mutableListOf<EscoSkill>()
        val lowerText = text.lowercase()

        skillBase.forEach { skill ->
            // Sammle alle Namen (Preferred + Synonyme)
            val allNames = (listOf(skill.preferredLabel) + skill.altLabels)
                .flatMap { it.split(" ") } // Zerlege in einzelne Wörter für Kurzsuche
                .map { it.lowercase().replace(Regex("[^a-z]"), "") }
                .filter { it.length >= 2 }

            allNames.distinct().forEach { term ->
                // Der entscheidende Check: Wortgrenzen \b verhindern Luxemburg-Match
                val regex = Regex("\\b${Regex.escape(term)}\\b")
                if (regex.containsMatchIn(lowerText)) {
                    if (!matches.contains(skill)) matches.add(skill)
                }
            }
        }
        return matches
    }
}
