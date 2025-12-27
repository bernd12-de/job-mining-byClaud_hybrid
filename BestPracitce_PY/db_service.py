# infrastructure/storage/db_service.py
from core.entities.job_posting import JobPosting
from core.entities.competence import Competence
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, declarative_base, Session
from typing import List, Dict
from sqlalchemy.orm import joinedload

# --- Konfiguration ---
# SQLite für den lokalen Mac-Start. Die Datei job_mining_local.db wird erstellt.
DATABASE_URL_SQLITE = "sqlite:///./job_mining_local.db"
Base = declarative_base()

# --- ORM Modelle (SQLAlchemy) ---

class DBJob(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    # WICHTIG: source_id muss UNIQUE sein für die Idempotenz (upsert-Logik)
    source_id = Column(String(255), unique=True, index=True)
    title = Column(String(255))
    company = Column(String(255))
    region = Column(String(100))
    year = Column(Integer)
    # cascade="all, delete-orphan" sorgt dafür, dass Kompetenzen mitgelöscht werden,
    # wenn der Job gelöscht wird (wichtig für Upsert).
    competences = relationship("DBCompetence", back_populates="job", cascade="all, delete-orphan")
    # NEU: Die Felder für den Raw Text und den Quellpfad fehlen im aktuellen Code!
    source_path = Column(String) # Hinzufügen des Pfades
    raw_text = Column(String)    # Hinzufügen des Rohtextes

class DBCompetence(Base):
    __tablename__ = "competences"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    original_skill = Column(String(255))
    esco_match = Column(String(255))
    score = Column(Float)
    category = Column(String(100))
    context_section = Column(String(255))
    job = relationship("DBJob", back_populates="competences")


def get_engine():
    """Gibt die konfigurierte Datenbank-Engine zurück."""
    return create_engine(DATABASE_URL_SQLITE, echo=False)

def setup_db(engine):
    """Erstellt alle Tabellen, falls sie noch nicht existieren."""
    Base.metadata.create_all(bind=engine)

def get_db_session() -> Session:
    """Gibt eine neue Session für die Dependency Injection zurück."""
    engine = get_engine()
    setup_db(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()
