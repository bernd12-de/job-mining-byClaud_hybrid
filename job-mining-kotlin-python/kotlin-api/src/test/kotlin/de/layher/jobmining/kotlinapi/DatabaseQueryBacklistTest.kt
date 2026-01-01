package de.layher.jobmining.kotlinapi

import de.layher.jobmining.kotlinapi.domain.DomainRule
import de.layher.jobmining.kotlinapi.infrastructure.DomainRuleRepository
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import com.fasterxml.jackson.module.kotlin.readValue
import java.io.File
import kotlin.test.assertNotNull
import kotlin.test.assertTrue
import kotlin.test.assertEquals

@SpringBootTest
class BlacklistIntegrityTest { // Name geändert gegen Redeclaration!

    @Autowired
    private lateinit var domainRuleRepository: DomainRuleRepository

    @Test
    fun `validate blacklist rules from flyway`() {
        val blacklist = domainRuleRepository.findAllByRuleTypeAndIsActiveTrue("BLACKLIST")
        println("📊 Blacklist-Check: ${blacklist.size} Einträge gefunden.")
        assertEquals(26, blacklist.size)
    }

    @Test
    fun `validate industry mappings from flyway`() {
        val mappings = domainRuleRepository.findAllByRuleTypeAndIsActiveTrue("INDUSTRY_MAPPING")
        println("🏢 Industry-Check: ${mappings.size} Branchen-Regeln gefunden.")
        assertEquals(6, mappings.size)
    }

    @Test
    fun `ensure academic reference data is present`() {
        val mapper = jacksonObjectMapper()
        val files = listOf("agile_methods.json", "product_management.json", "ux_design.json")
        val basePath = "../python-backend/data/job_domains/"

        files.forEach { fileName ->
            val file = File(basePath + fileName)
            if (file.exists()) {
                val content: Map<String, Any> = mapper.readValue(file)
                val skills = content["skills"] as? List<String> ?: emptyList()

                skills.forEach { skill ->
                    if (!domainRuleRepository.existsByRuleKey(skill)) {
                        domainRuleRepository.save(DomainRule(
                            ruleType = "ACADEMIC_REFERENCE",
                            ruleKey = skill,
                            ruleValue = "Imported from $fileName",
                            isActive = true
                        ))
                        println("🌱 Neu importiert: $skill")
                    } else {
                        println("⏩ Überspringe: $skill")
                    }
                }
            } else {
                println("⚠️ Datei fehlt: ${file.absolutePath}")
            }
        }

        val scrumSkill = domainRuleRepository.findByRuleKey("Scrum")
        assertNotNull(scrumSkill, "Integritätsfehler: 'Scrum' wurde nicht aus den JSONs importiert!")
        println("✅ Akademische Daten erfolgreich verifiziert.")
    }
}
