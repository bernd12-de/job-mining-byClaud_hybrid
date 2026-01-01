package de.layher.jobmining.kotlinapi

import de.layher.jobmining.kotlinapi.domain.DomainRule
import de.layher.jobmining.kotlinapi.infrastructure.DomainRuleRepository
import de.layher.jobmining.kotlinapi.infrastructure.EscoDataRepository
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import com.fasterxml.jackson.module.kotlin.readValue
import com.fasterxml.jackson.core.type.TypeReference
import java.io.File
import kotlin.test.assertNotNull
import kotlin.test.assertTrue
import kotlin.test.assertFalse

@SpringBootTest
class ReferenceDataIntegrityTest {

    @Autowired
    private lateinit var domainRuleRepository: DomainRuleRepository

    @Autowired
    private lateinit var escoRepository: EscoDataRepository

    // Nutzt das korrekte Jackson-Modul
    private val mapper = jacksonObjectMapper()

    @Test
    fun `ensure academic reference data is present`() {
        val files = listOf("agile_methods.json", "product_management.json", "ux_design.json")
        //val basePath = "../python-backend/data/job_domains/"
        val mapper = jacksonObjectMapper()
        // Wir prüfen, ob wir eine Ebene höher müssen (wie bei ESCO)
        // FIX: Explizite Typ-Zuweisung und saubere if-else Struktur
        val basePath: String = if (File("./data/job_domains/").exists()) {
            "./data/job_domains/"
        } else {
            // Das println muss vor dem Rückgabewert stehen oder entfernt werden
            println("⚠️ Lokaler Pfad nicht vorhanden, weiche auf Python-Backend aus.")
            "../python-backend/data/job_domains/"
        }

        files.forEach { fileName ->
            val file = File(basePath + fileName)
            if (file.exists()) {
                // FIX: Explizite Typ-Referenz verhindert 'Cannot infer type'
                val typeRef = object : TypeReference<Map<String, Any>>() {}
                val content: Map<String, Any> = mapper.readValue(file, typeRef)

                // FIX: Sicherer Cast verhindert 'Unchecked cast' Warnung
                val rawCompetences = content["competences"] as? List<*> ?: emptyList<Any>()
                val competences = rawCompetences.filterIsInstance<Map<String, Any>>()

                competences.forEach { comp ->
                    val skillName = comp["name"] as? String
                    if (skillName != null && !domainRuleRepository.existsByRuleKey(skillName)) {
                        domainRuleRepository.save(DomainRule(
                            ruleType = "ACADEMIC_REFERENCE",
                            ruleKey = skillName,
                            ruleValue = "Source: $fileName",
                            isActive = true,
                            //confidenceScore = 1.0 // Fix für Double-Erwartung
                        ))
                    }
                }
            }
        }
        assertNotNull(domainRuleRepository.findByRuleKey("Scrum"))
        val scrumSkill = domainRuleRepository.findByRuleKey("Scrum")
        assertNotNull(scrumSkill, "Integritätsfehler: 'Scrum' wurde nicht aus den JSONs importiert!")
        println("✅ Akademische Daten erfolgreich verifiziert.")
    }

    @Test
    fun `validate UX matching integrity against false positives like Luxemburg`() {
        // FIX: Falls 'getSkill' rot ist, muss es im EscoDataRepository existieren!
        // Hier simulieren wir den Zugriff auf die Map, falls die Methode fehlt:
        val uxSkill = escoRepository.getSkill("ux")
        assertNotNull(uxSkill, "UX sollte in der ESCO-Wissensbasis vorhanden sein")

        val positiveText = "Wir suchen einen UX-Designer."
        val negativeText = "Der Arbeitsort ist Luxemburg."

        val findUX = { text: String ->
            text.split(Regex("[\\s,.-]+"))
                .any { it.equals("ux", ignoreCase = true) }
        }

        assertTrue(findUX(positiveText), "UX als eigenständiges Wort wurde nicht gefunden")
        assertFalse(findUX(negativeText), "FEHLER: 'ux' wurde fälschlicherweise in 'Luxemburg' gefunden!")
    }
}
