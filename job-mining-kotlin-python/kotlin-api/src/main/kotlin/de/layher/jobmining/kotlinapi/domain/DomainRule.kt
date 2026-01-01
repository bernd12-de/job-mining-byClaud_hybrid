package de.layher.jobmining.kotlinapi.domain

import jakarta.persistence.*
import java.time.LocalDateTime

@Entity
@Table(name = "domain_rule", uniqueConstraints = [
    UniqueConstraint(columnNames = ["rule_type", "rule_key"])
])
data class DomainRule(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    // Typ der Regel: 'BLACKLIST', 'INDUSTRY_MAPPING', 'ROLE_PATTERN'
    @Column(name = "rule_type", nullable = false, length = 50)
    val ruleType: String,

    // Der Schlüsselbegriff (z.B. "kenntnisse" für Blacklist)
    @Column(name = "rule_key", nullable = false, unique = true, length = 512)
    val ruleKey: String,

    // Der Wert oder das Muster (z.B. "TRUE" für Blacklist-Einträge)
    @Column(name = "rule_value", columnDefinition = "TEXT")
    val ruleValue: String?,

    @Column(name = "is_active", nullable = false)
    val isActive: Boolean = true,

    @Column(name = "created_at", nullable = false)
    val createdAt: LocalDateTime = LocalDateTime.now()
)
