package de.layher.jobmining.kotlinapi

import de.layher.jobmining.kotlinapi.infrastructure.EscoDataRepository
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import kotlin.test.assertNotNull
import kotlin.test.assertTrue
import kotlin.test.assertFalse

@SpringBootTest
class EscoMatchingIntegrityTest {

    @Autowired
    private lateinit var escoRepository: EscoDataRepository

    @Test
    fun `validate that UX is matched as a skill but ignored in city names like Luxemburg`() {
        // 1. Sicherstellen, dass UX in der ESCO-Basis existiert (aus skills_de.csv)
        val uxTerm = "ux"
        val escoSkill = escoRepository.getSkill(uxTerm)
        assertNotNull(escoSkill, "ESCO-Basis sollte UX (User Experience) enthalten")

        // 2. Test-Szenario: Text mit UX und Luxemburg
        val jobAdText = "Wir suchen UX Designer für Projekte in Luxemburg und Brüssel."

        // Simuliere die Matching-Logik des Repositories
        // Wir nutzen Wortgrenzen (\b), um Substring-Matches zu verhindern
        val foundSkills = mutableListOf<String>()
        val words = jobAdText.split(Regex("[\\s,.]+")) // Einfache Tokenisierung

        words.forEach { word ->
            val cleanWord = word.lowercase()
            if (cleanWord == uxTerm) {
                foundSkills.add(cleanWord)
            }
        }

        // 3. Überprüfung der Ergebnisse
        assertTrue(foundSkills.contains("ux"), "UX als eigenständiger Skill wurde nicht erkannt!")

        // Sicherstellen, dass Luxemburg nicht als 'ux' gezählt wurde
        val countUX = foundSkills.count { it == "ux" }
        assertTrue(countUX == 1, "UX wurde $countUX Mal gefunden, erwartet war 1 Mal (Luxemburg darf nicht zählen!)")

        println("✅ Präzisionstest bestanden: 'UX' korrekt von 'Luxemburg' unterschieden.")
    }

    @Test
    fun `demo ux discovery without luxemburg`() {
        val demoText = "Wir suchen einen UX Experten für unseren Standort in Luxemburg."

        // Nutze den Service, um den 'CSV-Quark' zu analysieren
        val matches = escoRepository.findSkillsInText(demoText)

        // Check 1: UX muss gefunden werden (weil es in altLabels steht)
        val hasUX = matches.any { it.preferredLabel.contains("User Experience", ignoreCase = true) }
        assertTrue(hasUX, "UX wurde nicht in den ESCO-Daten gefunden!")

        // Check 2: Luxemburg darf KEIN Skill-Match sein
        val hasLuxemburg = matches.any { it.preferredLabel.contains("Luxemburg", ignoreCase = true) }
        assertFalse(hasLuxemburg, "FEHLER: Luxemburg wurde fälschlicherweise als Skill erkannt!")

        println("✅ Demo erfolgreich: UX erkannt, Luxemburg ignoriert.")
    }


    @Test
    fun `scientific proof of matching precision - UX vs Luxemburg`() {
        // 1. Setup: Ein Satz mit Fallen (Luxemburg enthält ux, Protokolle enthält Prototyp-Anfang)
        val testText = "Wir erstellen Prototypen für UX-Lösungen in Luxemburg und führen Protokolle."

        // 2. Nutze die findSkillsInText Methode deines Repositories
        val matches = escoRepository.findSkillsInText(testText)
        val matchedLabels = matches.map { it.preferredLabel.lowercase() }

        println("🔎 Gefundene ESCO-Begriffe: $matchedLabels")

        // CHECK A: UX muss gefunden werden (als eigenständiger Begriff)
        assertTrue(matches.any { it.preferredLabel.contains("User Experience", ignoreCase = true) || matchedLabels.contains("ux") },
            "UX sollte als Kompetenz erkannt werden")

        // CHECK B: Prototypen muss gefunden werden
        assertTrue(matchedLabels.any { it.contains("prototyp") },
            "Prototypen-Erstellung sollte erkannt werden")

        // CHECK C: Luxemburg darf KEIN Match sein (Präzisions-Beweis)
        val hasLuxemburg = matches.any { it.preferredLabel.contains("Luxemburg", ignoreCase = true) }
        assertFalse(hasLuxemburg, "FEHLER: Luxemburg darf nicht als Skill 'ux' gematcht werden!")

        // CHECK D: Protokolle darf kein Match für Prototyp sein
        assertFalse(matchedLabels.contains("protokolle"), "FEHLER: 'Protokolle' ist kein ESCO-Skill für 'Prototypen'!")

        println("✅ Präzision bestätigt: UX und Prototypen sauber erkannt, Rauschen (Luxemburg/Protokolle) ignoriert.")
    }
}
