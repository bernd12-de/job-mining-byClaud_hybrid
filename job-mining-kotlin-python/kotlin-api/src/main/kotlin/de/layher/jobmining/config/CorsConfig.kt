package de.layher.jobmining.config

import org.springframework.context.annotation.Configuration
import org.springframework.web.servlet.config.annotation.CorsRegistry
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer

/**
 * ✅ CORS Configuration für Swagger UI und Frontend
 * - Erlaubt Requests von localhost für Swagger UI
 * - Konfiguriert Headers für API-Zugriff
 */
@Configuration
class CorsConfig : WebMvcConfigurer {

    override fun addCorsMappings(registry: CorsRegistry) {
        registry.addMapping("/**")
            .allowedOriginPatterns("*")  // Erlaubt alle Origins für Swagger UI
            .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH")
            .allowedHeaders("*")
            .allowCredentials(true)
            .maxAge(3600)
    }
}
