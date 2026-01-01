package de.layher.jobmining.kotlinapi.infrastructure.database

// infrastructure/database/ExposedAuditLog.kt
import org.jetbrains.exposed.sql.*
import org.jetbrains.exposed.sql.javatime.CurrentDateTime
import org.jetbrains.exposed.sql.transactions.transaction
import org.jetbrains.exposed.sql.javatime.datetime

object EscoAuditTable : Table("esco_audit_log") {
    val id = integer("id").autoIncrement()
    val timestamp = datetime("timestamp").defaultExpression(CurrentDateTime)
    val loadedCount = integer("loaded_skills_count")
    val status = varchar("status", 20)
    override val primaryKey = PrimaryKey(id)
}

fun logEscoStatus(count: Int) {
    transaction {
        EscoAuditTable.insert {
            it[loadedCount] = count
            it[status] = if (count >= 10000) "COMPLETE" else "INCOMPLETE"
        }
    }
}
