package de.layher.jobmining.config

import org.slf4j.LoggerFactory
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.ExceptionHandler
import org.springframework.web.bind.annotation.RestControllerAdvice
import org.springframework.web.context.request.WebRequest
import java.time.LocalDateTime

/**
 * ✅ Global Exception Handler mit Dependency-Resilience
 * - Fängt alle unerwarteten Fehler ab
 * - Loggt Fehler strukturiert
 * - Gibt saubere Error-Responses
 */
@RestControllerAdvice
class GlobalExceptionHandler {

    private val logger = LoggerFactory.getLogger(javaClass)

    data class ErrorResponse(
        val timestamp: LocalDateTime = LocalDateTime.now(),
        val status: Int,
        val error: String,
        val message: String,
        val path: String? = null,
        val cause: String? = null
    )

    /**
     * Fängt NoSuchMethodError (Dependency-Versionsprobleme)
     */
    @ExceptionHandler(NoSuchMethodError::class)
    fun handleNoSuchMethodError(
        ex: NoSuchMethodError,
        request: WebRequest
    ): ResponseEntity<ErrorResponse> {
        logger.error("⚠️ DEPENDENCY ERROR: NoSuchMethodError - Wahrscheinlich Versionsinkompatibilität", ex)
        
        val response = ErrorResponse(
            status = HttpStatus.INTERNAL_SERVER_ERROR.value(),
            error = "DependencyError",
            message = "Spring Boot / Springdoc Versionskonflikt erkannt. Prüfe build.gradle.kts",
            path = request.getDescription(false).replace("uri=", ""),
            cause = ex.message
        )
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response)
    }

    /**
     * Fängt ClassNotFoundException (fehlende Dependencies)
     */
    @ExceptionHandler(ClassNotFoundException::class)
    fun handleClassNotFound(
        ex: ClassNotFoundException,
        request: WebRequest
    ): ResponseEntity<ErrorResponse> {
        logger.error("⚠️ MISSING DEPENDENCY: Klasse nicht gefunden - ${ex.message}", ex)
        
        val response = ErrorResponse(
            status = HttpStatus.INTERNAL_SERVER_ERROR.value(),
            error = "MissingDependency",
            message = "Erforderliche Dependency nicht vorhanden",
            path = request.getDescription(false).replace("uri=", ""),
            cause = ex.message
        )
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response)
    }

    /**
     * Fängt IllegalStateException (Spring-Initialisierungsfehler)
     */
    @ExceptionHandler(IllegalStateException::class)
    fun handleIllegalState(
        ex: IllegalStateException,
        request: WebRequest
    ): ResponseEntity<ErrorResponse> {
        logger.error("⚠️ STATE ERROR: Illegaler Zustand in Spring - ${ex.message}", ex)
        
        val response = ErrorResponse(
            status = HttpStatus.SERVICE_UNAVAILABLE.value(),
            error = "StateError",
            message = "Spring Boot Initialisierungsfehler. Starte Applikation neu.",
            path = request.getDescription(false).replace("uri=", ""),
            cause = ex.message
        )
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(response)
    }

    /**
     * Globaler Fallback für alle anderen Exceptions
     */
    @ExceptionHandler(Exception::class)
    fun handleGlobalException(
        ex: Exception,
        request: WebRequest
    ): ResponseEntity<ErrorResponse> {
        logger.error("❌ UNERWARTETER FEHLER: ${ex.javaClass.simpleName}", ex)
        
        val response = ErrorResponse(
            status = HttpStatus.INTERNAL_SERVER_ERROR.value(),
            error = ex.javaClass.simpleName,
            message = ex.message ?: "Ein unerwarteter Fehler ist aufgetreten",
            path = request.getDescription(false).replace("uri=", ""),
            cause = ex.cause?.toString()
        )
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response)
    }
}
