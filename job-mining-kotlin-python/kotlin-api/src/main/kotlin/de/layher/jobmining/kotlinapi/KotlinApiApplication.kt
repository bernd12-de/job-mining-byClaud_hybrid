package de.layher.jobmining.kotlinapi

// KotlinApiApplication.kt

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.context.annotation.DependsOn // Import HINZUFÜGEN

@SpringBootApplication
@DependsOn("flywayInitializer") // 🚨 KRITISCHER FIX: Stellt sicher, dass Flyway zuerst läuft
class KotlinApiApplication

fun main(args: Array<String>) {
    runApplication<KotlinApiApplication>(*args)
}
