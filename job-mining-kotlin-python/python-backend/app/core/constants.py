# app/core/constants.py

import re,os

DEFAULT_KOTLIN_URL = os.environ.get("KOTLIN_API_URL", "http://localhost:8080")

# --- EBENE 1: FILTERUNG (RAUSCHEN) ---
GLOBAL_BLACKLIST = {
    "kenntnisse", "fähigkeiten", "kommunikation", "deutsch", "englisch",
    "r", "bau", "ski", "sport", "medien", "wissenschaft", "erfahrung",
    "agil", "strategie", "prozess", "management", "analyse", "projektleitung",
    "kunden", "lösung", "team", "technik", "bereich", "verantwortung übernehmen",
    "beratung", "dienstleistungen", "informatik", "digitalisierung",
    "prägen", "datenschutz", "ethik", "gesundheit", "kommunizieren", "agiles"
}

# --- STANDORT-MUSTER ---
LOCATION_PATTERNS = r"(berlin|hamburg|münchen|köln|frankfurt|stuttgart|düsseldorf|gummersbach|mainz|augsburg)"


# --- EBENE 6: SEGMENTIERUNG & KONTEXT ---
JOB_CATEGORY_PATTERNS = {
    "IT & Softwareentwicklung": r"(entwickler|developer|programmier|software|it|informatik|cloud)",
    "UX/UI & Design": r"(ux|ui|design|user experience|grafik|konzeption)",
    "Management & Strategie": r"(manager|leitung|führung|strategie|geschäftsführer|vorstand)",
    "Finanzen & Controlling": r"(finanz|accounting|controlling|bilanz|buchhaltung|steuer)",
    "Personal & HR": r"(hr|personal|recruiting|people|talent|human resources)", # NEU
    "Vertrieb & Sales": r"(sales|vertrieb|account manager|akquise|außendienst)", # NEU
    "Marketing & PR": r"(marketing|pr|social media|brand|kommunikation)",       # NEU
    "Recht & Compliance": r"(recht|legal|jurist|syndikus|compliance|anwalt)",     # NEU
    "Logistik & Supply Chain": r"(logistik|lager|supply chain|versand|transport)", # NEU
    "Assistenz & Office": r"(assistenz|sekretariat|büro|administration|sachbearbeiter)"
    # Alle weiteren Patterns hier zentral sammeln
}


# --- EBENE 6: SEKTIONS-ERKENNUNG (LOOKAHEADS) ---
TASK_SECTION_PATTERN = re.compile(
    r'(?:DEINE AUFGABEN|TÄTIGKEITEN|WAS DU BEI UNS MACHST|YOUR TASKS|RESPONSIBILITIES|TASKS|WHAT YOU WILL DO)[\s\r\n:.-]+(.*?)(?=(?:DEIN PROFIL|PROFIL|REQUIREMENTS|WIR BIETEN|WIR SUCHEN|BENEFITS|ABOUT US|$))',
    re.DOTALL | re.IGNORECASE)

REQUIREMENTS_SECTION_PATTERN = re.compile(
    r'(?:PROFIL|DEIN PROFIL|YOUR PROFILE|ANFORDERUNGEN|REQUIREMENTS|QUALIFICATIONS|VORAUSSETZUNGEN|SKILLSET)[\s\r\n:.-]+(.*?)(?=(?:DEINE AUFGABEN|TASKS|WIR BIETEN|WIR SUCHEN|BENEFITS|KONTAKT|$))',
    re.DOTALL | re.IGNORECASE)
