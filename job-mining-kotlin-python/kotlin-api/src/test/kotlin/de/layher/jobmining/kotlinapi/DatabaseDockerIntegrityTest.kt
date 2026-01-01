package de.layher.jobmining.kotlinapi

import org.junit.jupiter.api.Test
import java.sql.DriverManager
import kotlin.test.assertTrue

class DatabaseDockerIntegrityTest {

    @Test
    fun `check if docker postgres is reachable`() {
        val url = "jdbc:postgresql://localhost:5432/jobmining_db"
        val user = "jobmining_user"
        val password = "secret_password"

        try {
            DriverManager.getConnection(url, user, password).use { conn ->
                val valid = conn.isValid(5)
                println("✅ Datenbank-Integrität bestätigt!")
                assertTrue(valid)
            }
        } catch (e: Exception) {
            println("❌ Integritäts-Check fehlgeschlagen: ${e.message}")
            throw e
        }
    }
}
