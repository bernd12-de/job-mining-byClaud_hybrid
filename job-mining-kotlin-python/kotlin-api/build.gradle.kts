plugins {
    kotlin("jvm") version "2.2.21"
    kotlin("plugin.spring") version "2.2.21"
    id("org.springframework.boot") version "4.0.0"
    id("io.spring.dependency-management") version "1.1.7"
    kotlin("plugin.jpa") version "2.2.21"
}

group = "de.layher.jobmining"
version = "0.0.1-SNAPSHOT"
description = "kotlin-api"

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(17)
    }
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    implementation("org.springframework.boot:spring-boot-starter-webmvc")
    implementation("org.jetbrains.kotlin:kotlin-reflect")
    implementation("com.fasterxml.jackson.module:jackson-module-kotlin")
    // FIXED: Springdoc 2.6.0 ist mit Spring Boot 4.0.0 inkompatibel
    // Nutze 2.7.0+ für Spring Boot 4.0+ Kompatibilität
    implementation("org.springdoc:springdoc-openapi-starter-webmvc-ui:2.7.0")
    // NEU: Health & Monitoring
    implementation("org.springframework.boot:spring-boot-starter-actuator")
    // Grundlegende Exposed-Funktionen
    implementation("org.jetbrains.exposed:exposed-core:0.56.0")
    implementation("org.jetbrains.exposed:exposed-dao:0.56.0")
    implementation("org.jetbrains.exposed:exposed-jdbc:0.56.0")

    // In build.gradle.kts -> dependencies { ... }
    implementation("org.springframework.boot:spring-boot-starter-validation")


    // WICHTIG: Für den Fehler bei 'datetime' benötigst du dieses Modul:
    implementation("org.jetbrains.exposed:exposed-java-time:0.56.0")
    // NEU: FLYWAY-ABHÄNGIGKEIT (Der Fix für die Resilienz)
    // 🚨 KRITISCHER FIX: Ersetze flyway-core durch den Spring Boot Starter
    implementation("org.springframework.boot:spring-boot-starter-flyway") // <--- DIES IST DER SCHLÜSSEL
    // 🚨 KRITISCHER FIX 1: Flyway-Modul für PostgreSQL hinzufügen (behebt 'Unsupported Database')
    // Dies muss hinzugefügt werden, da Flyway es nicht mehr automatisch erkennt.
    runtimeOnly("org.flywaydb:flyway-database-postgresql")
    runtimeOnly("org.postgresql:postgresql")
    testImplementation("org.springframework.boot:spring-boot-starter-data-jpa-test")
    testImplementation("org.springframework.boot:spring-boot-starter-webmvc-test")
    testImplementation("org.jetbrains.kotlin:kotlin-test-junit5")
    // Tests verwenden die gleiche Jackson-Koordinate wie die App:
    testImplementation("com.fasterxml.jackson.module:jackson-module-kotlin")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

kotlin {
    compilerOptions {
        freeCompilerArgs.addAll("-Xjsr305=strict", "-Xannotation-default-target=param-property")
    }
}

allOpen {
    annotation("jakarta.persistence.Entity")
    annotation("jakarta.persistence.MappedSuperclass")
    annotation("jakarta.persistence.Embeddable")
}

tasks.withType<Test> {
    useJUnitPlatform()
}


