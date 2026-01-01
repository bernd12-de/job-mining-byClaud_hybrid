# Kotlin API - Detaillierte Dokumentation

**Package-Struktur:** `de.layher.jobmining.kotlinapi`
**Framework:** Spring Boot 3.x mit Kotlin
**ORM:** Exposed (nicht JPA)
**Gesamte Kotlin-Dateien:** 42

[← Zurück zu Architecture Index](./index.md)

---

## 📦 Package-Übersicht

```
de.layher.jobmining/
├── config/                          # Spring Boot Konfiguration
│   ├── CorsConfig.kt               # CORS-Einstellungen
│   ├── CorsFilter.kt               # CORS-Filter
│   ├── DependencyCheckConfig.kt    # Dependency Injection
│   └── GlobalExceptionHandler.kt   # Exception Handling
│
├── kotlinapi/
│   ├── KotlinApiApplication.kt     # Spring Boot Main
│   ├── AppConfig.kt                # App-Konfiguration
│   │
│   ├── presentation/               # HTTP Controllers (REST API)
│   │   ├── JobController.kt        # Job CRUD + Batch (Wichtig!)
│   │   ├── SystemStatusController.kt  # Health Check
│   │   ├── DiscoveryController.kt  # Skills Management
│   │   ├── DomainRuleController.kt # Custom Rules
│   │   ├── ConnectionTestController.kt
│   │   ├── ServiceLinksController.kt
│   │   ├── IndexController.kt
│   │   ├── CompetenceReportDTO.kt  # DTO
│   │   └── (andere DTOs)
│   │
│   ├── domain/                     # Business Objects (Entities)
│   │   ├── JobPosting.kt           # Job mit Competences
│   │   ├── Competence.kt           # Skill-Daten
│   │   ├── EscoSkill.kt            # ESCO-Mapping
│   │   ├── DomainRule.kt           # Parsing-Regeln
│   │   └── rules/SkillBlacklist.kt # Skill-Blacklist
│   │
│   ├── services/                   # Business-Logik
│   │   ├── JobMiningService.kt     # Zentrale Logik (Wichtig!)
│   │   ├── DiscoveryService.kt     # Skill-Discovery
│   │   ├── HybridCompetenceService.kt
│   │   ├── DomainRuleService.kt
│   │   └── TrendAnalysisService.kt
│   │
│   ├── core/services/
│   │   └── AnalyticsService.kt     # Analytics
│   │
│   ├── infrastructure/             # Datenzugriff & Integration
│   │   ├── *Repository.kt          # DB-Zugriff (Exposed)
│   │   ├── bridge/
│   │   │   ├── PythonBridge.kt     # HTTP zu Python-Backend
│   │   │   └── PythonNlpBridge.kt
│   │   ├── config/
│   │   │   ├── GlobalExceptionHandler.kt
│   │   │   └── StartupCheckRunner.kt
│   │   ├── database/
│   │   │   └── ExposedAuditLog.kt
│   │   └── io/
│   │       └── IOService.kt
│   │
│   └── adapters/                   # Externe Adapter
│       ├── AnalysisResultDTO.kt    # Python-Response DTO
│       └── PythonAnalysisClient.kt # HTTP-Client
```

---

## 🎯 Wichtigste Controller & Methoden

### 1. JobController (REST API)
**File:** `presentation/JobController.kt`
**Route Base:** `/api/v1/jobs`

#### Methoden:

##### POST `/api/v1/jobs/scrape`
```kotlin
fun scrapeUrlAndAnalyze(
    @RequestBody request: URLRequest,        // {url: String}
    @RequestParam renderJs: Boolean = false  // JS-Rendering?
): ResponseEntity<*>
```
- **Purpose:** Web-URL scrapen und analysieren
- **Parameters:**
  - `request.url` - Ziel-URL (z.B. StepStone, Softgarden)
  - `renderJs` - Mit Playwright JS-Rendering? (true/false)
- **Return:** JobDTO oder ErrorResponse
- **Intern:** Ruft `jobMiningService.processScrapedUrl()` auf

---

##### POST `/api/v1/jobs` (Upload)
```kotlin
fun uploadJobFile(
    @RequestParam("file") file: MultipartFile
): ResponseEntity<*>
```
- **Purpose:** PDF/DOCX hochladen und analysieren
- **Parameters:**
  - `file` - MultipartFile (PDF oder DOCX)
- **Return:** JobDTO mit extrahierten Competences
- **Intern:** Ruft `jobMiningService.processJobAd()` auf

---

##### POST `/api/v1/jobs/batch-process`
```kotlin
fun batchProcess(
    @RequestBody request: BatchRequest
): ResponseEntity<*>
```
- **Purpose:** Mehrere Jobs parallel verarbeiten
- **Parameters:**
  - `request.jobIds` - Liste von Job-IDs
  - `request.urls` - Liste von URLs
- **Return:** BatchResult mit Progress

---

##### GET `/api/v1/jobs/{id}`
```kotlin
fun getJobById(
    @PathVariable id: Long
): ResponseEntity<JobPosting>
```
- **Purpose:** Job-Details mit allen Competences abrufen
- **Parameters:** `id` - Job-ID
- **Return:** Vollständige JobPosting Entity

---

##### GET `/batch-analyze` (Alias)
```kotlin
fun batchAnalyzeAlias(...)
```
- **Purpose:** Alias-Route für Batch-Verarbeitung
- **Routes:** `/batch-analyze`, `/batch-process`

---

### 2. SystemStatusController (Health Check)
**File:** `presentation/SystemStatusController.kt`
**Route Base:** `/api/v1/system`

#### Methode:

##### GET `/api/v1/system/status`
```kotlin
fun getStatus(): SystemStatus

data class SystemStatus(
    val status: String = "UP",
    val service: String = "kotlin-api",
    val timestamp: String,  // ISO 8601
    val version: String = "2.3.0",
    val database: String = "connected"
)
```
- **Purpose:** Systemstatus prüfen (Health Check)
- **Return:** JSON mit Status-Info
- **Verwendung:** Liveness Probe, Monitoring

---

### 3. DiscoveryController (Skill Management)
**File:** `presentation/DiscoveryController.kt`
**Route Base:** `/api/v1/discovery`

#### Methoden:

##### GET `/api/v1/discovery/candidates`
```kotlin
fun getCandidates(): List<SkillCandidate>
```
- **Purpose:** Neue/ungekannte Skills auflisten
- **Return:** Liste von Skill-Kandidaten

---

##### POST `/api/v1/discovery/approve`
```kotlin
fun approveSkill(
    @RequestBody request: ApproveRequest  // {skillId, escoUri}
): ResponseEntity<*>
```
- **Purpose:** Skill als gültig markieren
- **Parameters:**
  - `skillId` - Zu approving Skill-ID
  - `escoUri` - ESCO-URI oder null

---

##### DELETE `/api/v1/discovery/{skillId}`
```kotlin
fun ignoreSkill(
    @PathVariable skillId: Long
): ResponseEntity<*>
```
- **Purpose:** Skill ignorieren (Blacklist)

---

### 4. DomainRuleController (Custom Rules)
**File:** `presentation/DomainRuleController.kt`
**Route Base:** `/api/v1/domain-rules`

#### Methoden:

##### POST `/api/v1/domain-rules`
```kotlin
fun createRule(
    @RequestBody rule: DomainRule
): ResponseEntity<DomainRule>
```
- **Purpose:** Custom Parsing-Regel hinzufügen
- **Body:** DomainRule Entity

---

##### GET `/api/v1/domain-rules`
```kotlin
fun getAllRules(): List<DomainRule>
```
- **Purpose:** Alle Rules auflisten

---

---

## 🔧 Services (Business-Logik)

### JobMiningService (Zentral!)
**File:** `services/JobMiningService.kt`

#### Wichtigste Methoden:

##### `processJobAd(fileContent: ByteArray, filename: String): JobPosting`
```kotlin
@Transactional
fun processJobAd(fileContent: ByteArray, filename: String): JobPosting {
    // 1. Datei zum Python-Backend senden
    val resultDto = pythonClient.sendDocumentForAnalysis(fileContent, filename)
    
    // 2. Idempotenz-Check (Hash-basiert)
    val existingJob = repository.findByRawTextHash(resultDto.rawTextHash).firstOrNull()
    if (existingJob != null) return existingJob
    
    // 3. DTO → Entity Mapping
    val jobPosting = JobPosting(
        rawText = resultDto.rawText,
        rawTextHash = resultDto.rawTextHash,
        sourceUrl = resultDto.sourceUrl,
        // ... weitere Felder
    )
    
    // 4. Competences speichern
    resultDto.competences.forEach { competenceDTO ->
        val competence = mapDtoToEntity(competenceDTO, jobPosting)
        jobPosting.competences.add(competence)
    }
    
    // 5. In DB speichern
    return repository.save(jobPosting)
}
```

**Parameters:**
- `fileContent` - PDF/DOCX Bytes
- `filename` - Dateiname (für Logging)

**Return:** Gespeicherte JobPosting mit Competences

**Wirft:** Exception wenn Python-Backend offline ist

---

##### `processScrapedUrl(url: String, renderJs: Boolean): JobPosting`
```kotlin
fun processScrapedUrl(url: String, renderJs: Boolean): JobPosting {
    // 1. Python aufrufen (mit JS-Option)
    val resultDto = pythonClient.scrapeAndAnalyzeUrl(url, renderJs)
    
    // 2-5. Wie processJobAd()
}
```

---

##### `mapDtoToEntity(dto: CompetenceDTO, jobPosting: JobPosting): Competence`
```kotlin
private fun mapDtoToEntity(dto: CompetenceDTO, jobPosting: JobPosting): Competence {
    return Competence(
        originalTerm = dto.originalTerm,        // Original-Text aus Dokument
        escoLabel = dto.escoLabel,              // ESCO-Skill-Name
        escoUri = dto.escoUri,                  // ESCO-URI
        confidenceScore = dto.confidenceScore,  // 0.0-1.0
        escoGroupCode = dto.escoGroupCode,      // Ebene 3
        isDigital = dto.isDigital,              // Boolean (Ebene 3)
        isDiscovery = dto.isDiscovery,          // Neu entdeckt? (Ebene 1)
        level = dto.level,                      // 2, 4 oder 5 (ESCO Level)
        roleContext = dto.roleContext,          // Jobbezeichnung (Ebene 6)
        sourceDomain = dto.sourceDomain         // z.B. "Softgarden" (Ebene 4/5)
    ).apply { this.jobPosting = jobPosting }
}
```

---

### DiscoveryService
**File:** `services/DiscoveryService.kt`

#### Methoden:

##### `approveSkill(skillId: Long, escoUri: String?): void`
- **Purpose:** Skill als gültig markieren
- **Side Effects:** Entfernt aus `discovery_candidates`, speichert in `discovery_approved`

##### `rejectSkill(skillId: Long): void`
- **Purpose:** Skill in Blacklist setzen
- **Side Effects:** Speichert in `skill_blacklist`

---

### PythonBridge (HTTP-Integration)
**File:** `infrastructure/bridge/PythonBridge.kt`

#### Methoden:

##### `sendDocumentForAnalysis(fileContent: ByteArray, filename: String): AnalysisResultDTO`
```kotlin
fun sendDocumentForAnalysis(fileContent: ByteArray, filename: String): AnalysisResultDTO {
    // 1. Multipart POST zu Python-Backend
    val client = HttpClient()
    val response = client.post("http://python-backend:8000/analyze-document") {
        body = MultipartFormDataContent {
            append("file", filename, ContentType.Application.OctetStream) {
                writeFully(fileContent)
            }
        }
    }
    
    // 2. Response parsen als AnalysisResultDTO
    return objectMapper.readValue(response.body(), AnalysisResultDTO::class.java)
}
```

---

## 📊 Domain Models (Entities)

### JobPosting
**File:** `domain/JobPosting.kt`

```kotlin
data class JobPosting(
    val id: Long? = null,
    val sourceUrl: String?,           // URL (wenn Web scrape)
    val filename: String?,            // Dateiname (wenn PDF/DOCX)
    val rawText: String,              // Ursprünglicher Text
    val rawTextHash: String,          // MD5/SHA256 für Idempotenz
    val extractedText: String?,       // Bereinigter Text
    val jobTitle: String?,            // Berufsbezeichnung
    val jobRole: String?,             // "Sales", "IT", etc.
    val organization: String?,        // Arbeitgeber
    val competences: MutableSet<Competence> = mutableSetOf(),  // Extrahierte Skills
    val createdAt: LocalDateTime = LocalDateTime.now(),
    val updatedAt: LocalDateTime = LocalDateTime.now(),
    val isActive: Boolean = true
)
```

**Beziehungen:**
- **1:N** zu `Competence` (Ein Job hat viele Skills)

---

### Competence
**File:** `domain/Competence.kt`

```kotlin
data class Competence(
    val id: Long? = null,
    val originalTerm: String,         // Original-Text aus Job-Text
    val escoLabel: String?,           // ESCO-Skill-Name
    val escoUri: String?,             // https://data.europa.eu/esco/skill/XXX
    val confidenceScore: Double,      // 0.0-1.0 Confidence
    val escoGroupCode: String?,       // Ebene 3: Skill-Kategorie
    val isDigital: Boolean = false,   // Ebene 3: Digitale Kompetenz?
    val isDiscovery: Boolean = false, // Ebene 1: Neue Skill?
    val level: Int? = null,           // 2, 4 oder 5 (ESCO Level)
    val roleContext: String?,         // Ebene 6: Jobbezeichnung
    val sourceDomain: String?,        // Ebene 4/5: Wo entdeckt? ("Softgarden", etc.)
    val jobPosting: JobPosting? = null  // Foreign Key
)
```

---

### EscoSkill
**File:** `domain/EscoSkill.kt`

```kotlin
data class EscoSkill(
    val id: Long? = null,
    val escoUri: String,              // Unique Identifier
    val preferredLabel: String,       // Skill-Name
    val description: String?,
    val skillType: String?,           // "knowledge" oder "competence"
    val reuseLevel: String?,
    val relatedOccupations: List<String> = emptyList()  // [Berufe]
)
```

**Verwendung:** Mapping von Python ESCO-Daten

---

## 🗄️ Repositories (DB-Zugriff mit Exposed)

### JobPostingRepository
**File:** `infrastructure/JobPostingRepository.kt`

```kotlin
interface JobPostingRepository : CrudRepository<JobPosting, Long> {
    fun findByRawTextHash(hash: String): List<JobPosting>
    fun findBySourceUrl(url: String): JobPosting?
    fun findByJobRole(role: String): List<JobPosting>
    fun findByOrganization(org: String): List<JobPosting>
    
    @Query("SELECT j FROM JobPosting j WHERE j.createdAt > :since")
    fun findRecent(since: LocalDateTime): List<JobPosting>
}
```

**Beispiel-Query:**
```kotlin
val recentJobs = repository.findRecent(LocalDateTime.now().minusDays(7))
```

---

### CompetenceRepository
**File:** `infrastructure/CompetenceRepository.kt`

```kotlin
interface CompetenceRepository : CrudRepository<Competence, Long> {
    fun findByJobPostingId(jobId: Long): List<Competence>
    fun findByEscoUri(uri: String): List<Competence>
    fun findByIsDiscoveryTrue(): List<Competence>  // Neue Skills
}
```

---

## ⚙️ Konfiguration

### AppConfig.kt
```kotlin
@Configuration
class AppConfig {
    
    @Bean
    fun objectMapper(): ObjectMapper {
        return ObjectMapper()
            .registerModule(JavaTimeModule())
            .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS)
    }
    
    @Bean
    fun restTemplate(): RestTemplate {
        return RestTemplate()
    }
}
```

---

### StartupCheckRunner.kt
```kotlin
@Component
class StartupCheckRunner(
    private val pythonBridge: PythonBridge
) : ApplicationRunner {
    
    override fun run(args: ApplicationArguments?) {
        try {
            val status = pythonBridge.checkPythonHealth()
            logger.info("✅ Python Backend is UP: $status")
        } catch (e: Exception) {
            logger.warn("⚠️ Python Backend is DOWN: ${e.message}")
        }
    }
}
```

**Zweck:** Beim Startup Python-Backend Verfügbarkeit prüfen

---

## 🔐 DTOs (Data Transfer Objects)

### AnalysisResultDTO (von Python)
```kotlin
data class AnalysisResultDTO(
    val rawText: String,
    val rawTextHash: String,
    val extractedText: String?,
    val sourceUrl: String?,
    val jobTitle: String?,
    val competences: List<CompetenceDTO>,
    val processingTime: Long  // ms
)
```

### CompetenceDTO (von Python)
```kotlin
data class CompetenceDTO(
    val originalTerm: String,
    val escoLabel: String?,
    val escoUri: String?,
    val confidenceScore: Double,
    val escoGroupCode: String?,
    val isDigital: Boolean,
    val isDiscovery: Boolean,
    val level: Int?,
    val roleContext: String?,
    val sourceDomain: String?
)
```

---

## 📋 Wichtige Konstanten

```kotlin
// In AppConfig oder Constants
const val PYTHON_BACKEND_URL = "http://python-backend:8000"
const val API_VERSION = "v1"
const val DEFAULT_PAGE_SIZE = 20
const val MAX_BATCH_SIZE = 100
const val TIMEOUT_SECONDS = 30
```

---

## 🔗 Dependency Injection

```kotlin
@Service
class JobMiningService(
    private val repository: JobPostingRepository,      // Auto-injected
    private val pythonClient: PythonAnalysisClient,   // Auto-injected
    private val discoveryService: DiscoveryService    // Auto-injected
) {
    // ...
}
```

Spring Boot kümmert sich automatisch um Dependency Injection durch `@Autowired` oder Constructor-Injection.

---

## 🧪 Testing Hinweise

**Test-Dateien:**
- `KotlinApiApplicationTests.kt` - Application Context Loading
- `JobMiningIntegrationTest.kt` - Integration Test mit Python-Backend
- `SystemStatusControllerTest.kt` - Controller Test (Neu erstellt!)

**Testfokus:**
- Controller Response Codes (200, 400, 500)
- Service Business-Logik
- Idempotenz (gleiche Input = gleiche Output)
- Fehlerbehandlung

---

[← Zurück zu Architecture Index](./index.md)
**Letzte Aktualisierung:** 2025-12-28
