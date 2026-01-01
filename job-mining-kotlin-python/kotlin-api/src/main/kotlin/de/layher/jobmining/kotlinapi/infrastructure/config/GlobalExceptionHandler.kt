package de.layher.jobmining.kotlinapi.infrastructure.config

import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.ControllerAdvice
import org.springframework.web.bind.annotation.ExceptionHandler
import org.springframework.web.multipart.MaxUploadSizeExceededException
import org.slf4j.LoggerFactory

/**
 * Globaler Exception Handler für die Kotlin API
 * Verhindert Abstürze durch unbehandelte Exceptions
 */
@ControllerAdvice
class GlobalExceptionHandler {

    private val logger = LoggerFactory.getLogger(GlobalExceptionHandler::class.java)

    @ExceptionHandler(IllegalArgumentException::class)
    fun handleIllegalArgument(ex: IllegalArgumentException): ResponseEntity<Map<String, Any>> {
        logger.warn("⚠️ Validierungsfehler: ${ex.message}")
        return ResponseEntity.badRequest().body(mapOf(
            "error" to "Validierungsfehler",
            "message" to (ex.message ?: "Ungültige Eingabe"),
            "status" to HttpStatus.BAD_REQUEST.value()
        ))
    }

    @ExceptionHandler(IllegalStateException::class)
    fun handleIllegalState(ex: IllegalStateException): ResponseEntity<Map<String, Any>> {
        logger.error("❌ Statusfehler: ${ex.message}", ex)
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(mapOf(
            "error" to "Interner Serverfehler",
            "message" to (ex.message ?: "Ein interner Fehler ist aufgetreten"),
            "status" to HttpStatus.INTERNAL_SERVER_ERROR.value()
        ))
    }

    @ExceptionHandler(MaxUploadSizeExceededException::class)
    fun handleMaxUploadSizeExceeded(ex: MaxUploadSizeExceededException): ResponseEntity<Map<String, Any>> {
        logger.warn("⚠️ Datei zu groß: ${ex.message}")
        return ResponseEntity.status(HttpStatus.PAYLOAD_TOO_LARGE).body(mapOf(
            "error" to "Datei zu groß",
            "message" to "Die hochgeladene Datei überschreitet die maximale Größe",
            "status" to HttpStatus.PAYLOAD_TOO_LARGE.value()
        ))
    }

    @ExceptionHandler(RuntimeException::class)
    fun handleRuntimeException(ex: RuntimeException): ResponseEntity<Map<String, Any>> {
        logger.error("❌ Runtime-Fehler: ${ex.message}", ex)
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(mapOf(
            "error" to "Serverfehler",
            "message" to (ex.message ?: "Ein unerwarteter Fehler ist aufgetreten"),
            "status" to HttpStatus.INTERNAL_SERVER_ERROR.value()
        ))
    }

    @ExceptionHandler(Exception::class)
    fun handleGenericException(ex: Exception): ResponseEntity<Map<String, Any>> {
        logger.error("❌ Unerwarteter Fehler: ${ex.message}", ex)
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(mapOf(
            "error" to "Unerwarteter Fehler",
            "message" to "Ein unerwarteter Fehler ist aufgetreten. Bitte kontaktieren Sie den Administrator.",
            "status" to HttpStatus.INTERNAL_SERVER_ERROR.value(),
            "technicalDetails" to (ex.message ?: "Keine Details verfügbar")
        ))
    }

    @ExceptionHandler(NoSuchElementException::class)
    fun handleNotFound(ex: NoSuchElementException): ResponseEntity<Map<String, Any>> {
        logger.warn("⚠️ Ressource nicht gefunden: ${ex.message}")
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(mapOf(
            "error" to "Nicht gefunden",
            "message" to (ex.message ?: "Die angeforderte Ressource wurde nicht gefunden"),
            "status" to HttpStatus.NOT_FOUND.value()
        ))
    }
}
