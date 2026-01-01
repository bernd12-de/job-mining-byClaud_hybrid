package de.layher.jobmining.kotlinapi.infrastructure.io

import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Service
import java.io.File
import java.io.InputStream
import java.io.FileNotFoundException

@Service
class IOService(
    @Value("\${app.data.base-path:/app/data}")
    private val basePath: String
) {
    /**
     * Liefert einen Stream für ESCO-Dateien (z.B. skills_de.csv).
     */
    fun getEscoStream(fileName: String): InputStream {
        val file = File("$basePath/esco/$fileName")
        if (!file.exists()) {
            throw FileNotFoundException("ESCO-Basisdatei nicht gefunden: ${file.absolutePath}")
        }
        return file.inputStream()
    }

    /**
     * Liefert alle Dateien aus dem Job-Ordner für die Batch-Verarbeitung.
     */
    fun listJobFiles(): List<File> {
        val directory = File("$basePath/jobs")
        return directory.listFiles()?.filter { it.isFile } ?: emptyList()
    }

    /**
     * Liefert alle CSV-Dateien aus dem ESCO-Ordner.
     * Beachtet den Test-Fallback, falls der Pfad lokal nicht existiert.
     */
    fun listEscoFiles(): List<File> {
        val path = "$basePath/esco"
        var directory = File(path)

        // Pfad-Check: Wenn der Standardpfad (Docker) nicht existiert,
        // weichen wir für den IntelliJ-Test auf den relativen Pfad aus.
        if (!directory.exists()) {
            directory = File("../python-backend/data/esco")
        }

        return directory.listFiles { f -> f.extension == "csv" }?.toList() ?: emptyList()
    }
}
