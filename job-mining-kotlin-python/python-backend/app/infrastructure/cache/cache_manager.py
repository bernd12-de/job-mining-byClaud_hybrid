"""
Persistent Cache Manager für ESCO-Daten und SpaCy-Models
Reduziert Startup-Zeit von 15-20 Sek auf < 3 Sek
"""

import os
import pickle
import hashlib
import logging
from pathlib import Path
from typing import Any, Optional, Callable
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Verwaltet Pickle-basierte Caches für teure Operationen
    """

    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📦 CacheManager initialisiert: {self.cache_dir}")

    def get_cache_path(self, cache_key: str) -> Path:
        """Gibt Pfad für Cache-Datei zurück"""
        safe_key = hashlib.md5(cache_key.encode()).hexdigest()
        return self.cache_dir / f"{safe_key}.pkl"

    def is_cache_valid(
        self,
        cache_key: str,
        max_age_hours: Optional[int] = None
    ) -> bool:
        """
        Prüft ob Cache existiert und gültig ist

        Args:
            cache_key: Eindeutiger Schlüssel für den Cache
            max_age_hours: Maximales Alter in Stunden (None = unendlich)

        Returns:
            True wenn Cache existiert und gültig
        """
        cache_path = self.get_cache_path(cache_key)

        if not cache_path.exists():
            return False

        if max_age_hours is None:
            return True

        # Prüfe Alter
        cache_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        max_age = timedelta(hours=max_age_hours)

        is_valid = (datetime.now() - cache_time) < max_age

        if not is_valid:
            logger.info(f"⏰ Cache abgelaufen: {cache_key} (älter als {max_age_hours}h)")

        return is_valid

    def load_from_cache(self, cache_key: str) -> Optional[Any]:
        """
        Lädt Daten aus Cache

        Args:
            cache_key: Eindeutiger Schlüssel

        Returns:
            Gecachte Daten oder None
        """
        cache_path = self.get_cache_path(cache_key)

        try:
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)

            logger.info(f"✅ Cache geladen: {cache_key} ({cache_path.stat().st_size // 1024} KB)")
            return data

        except Exception as e:
            logger.warning(f"⚠️ Cache-Laden fehlgeschlagen: {cache_key} - {e}")
            return None

    def save_to_cache(self, cache_key: str, data: Any) -> bool:
        """
        Speichert Daten im Cache

        Args:
            cache_key: Eindeutiger Schlüssel
            data: Zu cachende Daten (muss pickle-bar sein)

        Returns:
            True bei Erfolg
        """
        cache_path = self.get_cache_path(cache_key)

        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

            size_kb = cache_path.stat().st_size // 1024
            logger.info(f"💾 Cache gespeichert: {cache_key} ({size_kb} KB)")
            return True

        except Exception as e:
            logger.error(f"❌ Cache-Speichern fehlgeschlagen: {cache_key} - {e}")
            return False

    def get_or_compute(
        self,
        cache_key: str,
        compute_func: Callable[[], Any],
        max_age_hours: Optional[int] = 24,
        force_refresh: bool = False
    ) -> Any:
        """
        Lädt aus Cache oder berechnet neu

        Args:
            cache_key: Eindeutiger Schlüssel
            compute_func: Funktion die Daten berechnet wenn Cache fehlt
            max_age_hours: Maximales Cache-Alter (None = unendlich)
            force_refresh: Erzwinge Neuberechnung

        Returns:
            Daten (aus Cache oder neu berechnet)
        """
        # Cache prüfen
        if not force_refresh and self.is_cache_valid(cache_key, max_age_hours):
            cached_data = self.load_from_cache(cache_key)
            if cached_data is not None:
                return cached_data

        # Neu berechnen
        logger.info(f"🔄 Berechne neu: {cache_key}")
        data = compute_func()

        # Speichern
        self.save_to_cache(cache_key, data)

        return data

    def invalidate(self, cache_key: str) -> bool:
        """
        Löscht einen Cache

        Args:
            cache_key: Zu löschender Cache

        Returns:
            True bei Erfolg
        """
        cache_path = self.get_cache_path(cache_key)

        try:
            if cache_path.exists():
                cache_path.unlink()
                logger.info(f"🗑️ Cache gelöscht: {cache_key}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Cache-Löschen fehlgeschlagen: {cache_key} - {e}")
            return False

    def clear_all(self) -> int:
        """
        Löscht alle Caches

        Returns:
            Anzahl gelöschter Dateien
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.pkl"):
            try:
                cache_file.unlink()
                count += 1
            except Exception as e:
                logger.error(f"❌ Fehler beim Löschen von {cache_file}: {e}")

        logger.info(f"🗑️ {count} Caches gelöscht")
        return count

    def get_cache_info(self) -> dict:
        """
        Gibt Informationen über alle Caches zurück

        Returns:
            Dict mit Cache-Statistiken
        """
        caches = []
        total_size = 0

        for cache_file in self.cache_dir.glob("*.pkl"):
            stat = cache_file.stat()
            size_kb = stat.st_size // 1024
            total_size += size_kb

            caches.append({
                'file': cache_file.name,
                'size_kb': size_kb,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'age_hours': (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).total_seconds() / 3600
            })

        return {
            'cache_dir': str(self.cache_dir),
            'total_caches': len(caches),
            'total_size_kb': total_size,
            'caches': sorted(caches, key=lambda x: x['size_kb'], reverse=True)
        }


# Globale Instanz für einfachen Zugriff
_cache_manager = None

def get_cache_manager() -> CacheManager:
    """Gibt globale CacheManager-Instanz zurück"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager
