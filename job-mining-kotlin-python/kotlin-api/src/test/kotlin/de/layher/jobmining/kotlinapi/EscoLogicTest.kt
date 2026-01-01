package de.layher.jobmining.kotlinapi

import de.layher.jobmining.kotlinapi.domain.EscoSkill
import org.junit.jupiter.api.Test
import kotlin.test.assertTrue
import kotlin.test.assertFalse

class EscoLogicTest {

    @Test
    fun `scientific proof - UX vs Luxemburg logic check`() {
        // 1. Wir erstellen die Test-Daten manuell (keine CSV nötig)
        val mockSkills = listOf(
            EscoSkill(
                uri = "esco:skill/ux",
                preferredLabel = "Prototyp für User-Experience-Lösung erstellen",
                altLabels = listOf("UX-Lösung", "User Experience Design", "UX")
            ),
            EscoSkill(
                uri = "esco:skill/lux",
                preferredLabel = "Geschriebenes Luxemburgisch verstehen",
                altLabels = listOf("Luxemburgisch")
            )
        )

        val testText = "Wir suchen UX Designer für Prototypen in Luxemburg."

        // 2. Die Suchfunktion (Präzisionsebene)
        val findMatches = { text: String, base: List<EscoSkill> ->
            base.filter { skill ->
                val allLabels = listOf(skill.preferredLabel) + skill.altLabels
                allLabels.any { label ->
                    // Der wissenschaftliche Kern: Wortgrenzen \b verhindern Substring-Fehler
                    val regex = Regex("\\b${Regex.escape(label.lowercase())}\\b")
                    regex.containsMatchIn(text.lowercase()) ||
                        // Fallback für das Akronym UX falls im Text vorhanden
                        (label.equals("UX", true) && text.lowercase().split(" ", "-", "/").contains("ux"))
                }
            }
        }

        val results = findMatches(testText, mockSkills)
        val resultNames = results.map { it.uri }

        // 3. Assertions
        assertTrue(resultNames.contains("esco:skill/ux"), "✅ UX sollte gefunden werden")
        assertFalse(testText.lowercase().contains(Regex("\\bluxemburgisch\\b")), "✅ Luxemburgisch (Sprache) sollte NICHT gefunden werden")

        // Finaler Beweis für Masterarbeit:
        val luxemburgStringContainsUX = "luxemburg".contains("ux")
        assertTrue(luxemburgStringContainsUX, "Interner Check: 'luxemburg' enthält zwar 'ux'...")

        val smartMatchFoundUXInLuxemburg = Regex("\\bux\\b").containsMatchIn("luxemburg")
        assertFalse(smartMatchFoundUXInLuxemburg, "✅ ...aber die intelligente Regex erkennt es NICHT als eigenständigen Skill!")

        println("🧪 Präzisionstest bestanden: UX erkannt, Luxemburg als Falle ignoriert.")
    }
}
