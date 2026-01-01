package de.layher.jobmining.config

import org.slf4j.LoggerFactory
import org.springframework.boot.ApplicationRunner
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.core.io.ClassPathResource
import java.util.Properties

/**
 * ✅ Dependency Checker - Validiert Spring Boot + Springdoc Kompatibilität beim Start
 */
@Configuration
class DependencyCheckConfig {

    private val logger = LoggerFactory.getLogger(javaClass)

    @Bean
    fun dependencyChecker(): ApplicationRunner = ApplicationRunner {
        logger.info("🔍 Starte Dependency-Validierung...")
        
        try {
            // Prüfe Spring Boot Version
            val springBootVersion = getSpringBootVersion()
            logger.info("✅ Spring Boot Version: $springBootVersion")
            
            // Prüfe Springdoc Version
            val springdocVersion = getSpringdocVersion()
            logger.info("✅ Springdoc-OpenAPI Version: $springdocVersion")
            
            // Validiere Kompatibilität
            validateVersionCompatibility(springBootVersion, springdocVersion)
            
            // Prüfe kritische Beans
            validateCriticalBeans()
            
            logger.info("✅ Alle Dependency-Checks erfolgreich!")
            
        } catch (e: Exception) {
            logger.error("❌ Dependency-Check FEHLGESCHLAGEN: ${e.message}", e)
            logger.error("⚠️  Applikation kann fehlerhaft sein. Überprüfe build.gradle.kts")
        }
    }

    private fun getSpringBootVersion(): String {
        return try {
            val prop = Properties()
            val resource = ClassPathResource("META-INF/maven/org.springframework.boot/spring-boot/pom.properties")
            resource.inputStream.use { prop.load(it) }
            prop.getProperty("version", "UNKNOWN")
        } catch (e: Exception) {
            logger.warn("⚠️  Konnte Spring Boot Version nicht auslesen")
            "UNKNOWN"
        }
    }

    private fun getSpringdocVersion(): String {
        return try {
            val prop = Properties()
            val resource = ClassPathResource("META-INF/maven/org.springdoc/springdoc-openapi-starter-webmvc-ui/pom.properties")
            resource.inputStream.use { prop.load(it) }
            prop.getProperty("version", "UNKNOWN")
        } catch (e: Exception) {
            logger.warn("⚠️  Springdoc nicht in Classpath gefunden")
            "NOT_FOUND"
        }
    }

    private fun validateVersionCompatibility(springBootVersion: String, springdocVersion: String) {
        if (springBootVersion == "UNKNOWN" || springdocVersion == "NOT_FOUND") {
            logger.warn("⚠️  Konnte Versionen nicht validieren, fahre fort...")
            return
        }

        val springMajor = springBootVersion.split(".")[0].toIntOrNull() ?: 0
        val springdocMinor = springdocVersion.split(".").getOrNull(1)?.toIntOrNull() ?: 0

        when {
            springMajor >= 4 && springdocMinor < 7 -> {
                logger.error("❌ KOMPATIBILITÄTSFEHLER: Spring Boot $springBootVersion benötigt Springdoc >= 2.7.0, aber $springdocVersion gefunden!")
                throw IllegalStateException("Springdoc-Version zu alt für Spring Boot $springBootVersion")
            }
            springMajor == 3 && springdocMinor < 0 -> {
                logger.warn("⚠️  Springdoc-Version könnte zu alt sein für Spring Boot 3.x")
            }
            else -> {
                logger.info("✅ Kompatibilität validiert: Spring Boot $springBootVersion + Springdoc $springdocVersion")
            }
        }
    }

    private fun validateCriticalBeans() {
        try {
            // Versuche kritische Beans zu laden
            Class.forName("org.springframework.web.method.ControllerAdviceBean")
            logger.info("✅ ControllerAdviceBean erfolgreich geladen")
            
            Class.forName("org.springdoc.openapi.models.OpenAPI")
            logger.info("✅ Springdoc OpenAPI erfolgreich geladen")
            
            Class.forName("org.springframework.boot.autoconfigure.SpringBootApplication")
            logger.info("✅ Spring Boot Autoconfigure erfolgreich geladen")
            
        } catch (e: ClassNotFoundException) {
            logger.warn("⚠️  Kritische Klasse nicht gefunden: ${e.message}")
            throw IllegalStateException("Erforderliche Dependency nicht vorhanden: ${e.message}")
        }
    }
}
