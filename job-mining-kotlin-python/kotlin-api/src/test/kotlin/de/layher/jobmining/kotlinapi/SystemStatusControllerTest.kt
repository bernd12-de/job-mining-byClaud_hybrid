package de.layher.jobmining.kotlinapi

import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Assertions.*
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.test.web.servlet.MockMvc
import org.springframework.test.web.servlet.get
import com.fasterxml.jackson.databind.ObjectMapper

@SpringBootTest
@AutoConfigureMockMvc
class SystemStatusControllerTest {

    @Autowired
    private lateinit var mockMvc: MockMvc
    
    @Autowired
    private lateinit var objectMapper: ObjectMapper
    
    @Test
    fun `test GET api_v1_system_status returns 200 with valid JSON`() {
        val result = mockMvc.get("/api/v1/system/status") {
        }.andExpect {
            status { isOk }
            content { contentType("application/json") }
        }.andReturn()

        val response = result.response.contentAsString
        println("✅ SystemStatus Response: $response")

        // Parse JSON
        val jsonNode = objectMapper.readTree(response)

        // Verify required fields exist
        assertTrue(jsonNode.has("status"), "Field 'status' is missing")
        assertTrue(jsonNode.has("service"), "Field 'service' is missing")
        assertTrue(jsonNode.has("timestamp"), "Field 'timestamp' is missing")
        assertTrue(jsonNode.has("version"), "Field 'version' is missing")
        assertTrue(jsonNode.has("database"), "Field 'database' is missing")
    }

    @Test
    fun `test system status returns correct service name`() {
        val result = mockMvc.get("/api/v1/system/status") {
        }.andExpect {
            status { isOk }
        }.andReturn()

        val response = result.response.contentAsString
        val jsonNode = objectMapper.readTree(response)

        val service = jsonNode.get("service").asText()
        assertEquals("kotlin-api", service, "Service name should be 'kotlin-api'")
    }

    @Test
    fun `test system status returns UP status`() {
        val result = mockMvc.get("/api/v1/system/status") {
        }.andExpect {
            status { isOk }
        }.andReturn()

        val response = result.response.contentAsString
        val jsonNode = objectMapper.readTree(response)

        val status = jsonNode.get("status").asText()
        assertEquals("UP", status, "Status should be 'UP'")
    }

    @Test
    fun `test system status includes valid version`() {
        val result = mockMvc.get("/api/v1/system/status") {
        }.andExpect {
            status { isOk }
        }.andReturn()

        val response = result.response.contentAsString
        val jsonNode = objectMapper.readTree(response)

        val version = jsonNode.get("version").asText()
        assertNotNull(version, "Version should not be null")
        assertFalse(version.isEmpty(), "Version should not be empty")
        println("✅ System Version: $version")
    }


    @Test
    fun `test system status includes timestamp`() {
        val result = mockMvc.get("/api/v1/system/status") {
        }.andExpect {
            status { isOk }
        }.andReturn()

        val response = result.response.contentAsString
        val jsonNode = objectMapper.readTree(response)

        val timestamp = jsonNode.get("timestamp").asText()
        assertNotNull(timestamp, "Timestamp should not be null")
        assertTrue(timestamp.contains("T"), "Timestamp should be ISO format (contain 'T')")
        println("✅ System Timestamp: $timestamp")
    }

    @Test
    fun `test system database field is populated`() {
        val result = mockMvc.get("/api/v1/system/status") {
        }.andExpect {
            status { isOk }
        }.andReturn()

        val response = result.response.contentAsString
        val jsonNode = objectMapper.readTree(response)

        val database = jsonNode.get("database").asText()
        assertNotNull(database, "Database field should not be null")
        assertFalse(database.isEmpty(), "Database field should not be empty")
        println("✅ Database Status: $database")
    }
}
}
