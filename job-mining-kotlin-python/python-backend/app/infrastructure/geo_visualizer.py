"""
Geo-Visualisierung Service
==========================

Konvertiert Regions-Namen zu Geo-Koordinaten für interaktive Karten.

Features:
- Deutsche Städte Geocoding
- Koordinaten-Lookup
- Map Data Generation für Plotly/Folium
"""

from typing import Dict, List, Optional, Tuple
import re
import logging

logger = logging.getLogger(__name__)


# Deutsche Städte mit Koordinaten (Top 100)
GERMAN_CITIES_GEO = {
    # Großstädte
    "berlin": (52.5200, 13.4050),
    "hamburg": (53.5511, 9.9937),
    "münchen": (48.1351, 11.5820),
    "köln": (50.9375, 6.9603),
    "frankfurt": (50.1109, 8.6821),
    "stuttgart": (48.7758, 9.1829),
    "düsseldorf": (51.2277, 6.7735),
    "dortmund": (51.5136, 7.4653),
    "essen": (51.4556, 7.0116),
    "leipzig": (51.3397, 12.3731),
    "bremen": (53.0793, 8.8017),
    "dresden": (51.0504, 13.7373),
    "hannover": (52.3759, 9.7320),
    "nürnberg": (49.4521, 11.0767),
    "duisburg": (51.4344, 6.7623),
    "bochum": (51.4818, 7.2162),
    "wuppertal": (51.2562, 7.1508),
    "bonn": (50.7374, 7.0982),
    "bielefeld": (52.0302, 8.5325),
    "mannheim": (49.4875, 8.4660),

    # Mittelgroße Städte
    "karlsruhe": (49.0069, 8.4037),
    "münster": (51.9607, 7.6261),
    "wiesbaden": (50.0825, 8.2400),
    "augsburg": (48.3705, 10.8978),
    "aachen": (50.7753, 6.0839),
    "mönchengladbach": (51.1805, 6.4428),
    "gelsenkirchen": (51.5177, 7.0857),
    "braunschweig": (52.2689, 10.5268),
    "chemnitz": (50.8278, 12.9214),
    "kiel": (54.3233, 10.1228),
    "halle": (51.4825, 11.9697),
    "magdeburg": (52.1205, 11.6276),
    "freiburg": (47.9990, 7.8421),
    "krefeld": (51.3388, 6.5853),
    "lübeck": (53.8655, 10.6866),
    "oberhausen": (51.4697, 6.8516),
    "erfurt": (50.9848, 11.0299),
    "mainz": (49.9929, 8.2473),
    "rostock": (54.0924, 12.0991),
    "kassel": (51.3127, 9.4797),
    "hagen": (51.3671, 7.4632),
    "saarbrücken": (49.2401, 6.9969),
    "hamm": (51.6734, 7.8150),
    "mülheim": (51.4274, 6.8826),
    "potsdam": (52.3906, 13.0645),
    "ludwigshafen": (49.4774, 8.4452),
    "oldenburg": (53.1435, 8.2146),
    "leverkusen": (51.0459, 6.9891),
    "osnabrück": (52.2799, 8.0472),
    "solingen": (51.1652, 7.0670),
    "heidelberg": (49.3988, 8.6724),
    "herne": (51.5386, 7.2251),
    "neuss": (51.2045, 6.6883),
    "darmstadt": (49.8728, 8.6512),
    "paderborn": (51.7189, 8.7575),
    "regensburg": (49.0134, 12.1016),
    "ingolstadt": (48.7665, 11.4257),
    "würzburg": (49.7913, 9.9534),
    "fürth": (49.4778, 10.9889),
    "wolfsburg": (52.4227, 10.7865),
    "offenbach": (50.1006, 8.7664),
    "ulm": (48.3974, 9.9934),
    "heilbronn": (49.1427, 9.2109),
    "pforzheim": (48.8917, 8.6945),
    "göttingen": (51.5412, 9.9158),
    "bottrop": (51.5230, 6.9285),
    "trier": (49.7490, 6.6371),
    "recklinghausen": (51.6142, 7.1978),
    "reutlingen": (48.4914, 9.2044),
    "bremerhaven": (53.5396, 8.5809),
    "koblenz": (50.3569, 7.5890),
    "bergisch gladbach": (50.9916, 7.1343),
    "jena": (50.9275, 11.5865),
    "remscheid": (51.1790, 7.1896),
    "erlangen": (49.5897, 11.0089),
    "moers": (51.4508, 6.6268),
    "siegen": (50.8748, 8.0243),
    "hildesheim": (52.1520, 9.9517),
    "salzgitter": (52.1530, 10.3316),

    # Regionen
    "bayern": (48.7904, 11.4979),  # München als Zentrum
    "baden-württemberg": (48.6616, 9.3501),  # Stuttgart als Zentrum
    "nordrhein-westfalen": (51.4332, 7.6616),  # Dortmund als Zentrum
    "hessen": (50.6521, 9.1624),  # Zentrum
    "niedersachsen": (52.6367, 9.8451),  # Hannover als Zentrum
    "rheinland-pfalz": (50.1186, 7.3089),  # Koblenz als Zentrum
    "sachsen": (51.1045, 13.2017),  # Dresden als Zentrum
    "thüringen": (50.9848, 11.0299),  # Erfurt als Zentrum
    "brandenburg": (52.4125, 12.5316),  # Potsdam als Zentrum
    "sachsen-anhalt": (51.9503, 11.6924),  # Magdeburg als Zentrum
    "schleswig-holstein": (54.2194, 9.6961),  # Kiel als Zentrum
    "mecklenburg-vorpommern": (53.6127, 12.4296),  # Schwerin als Zentrum
    "saarland": (49.3964, 7.0229),  # Saarbrücken als Zentrum

    # Spezielle
    "remote": (51.1657, 10.4515),  # Deutschland Zentrum
    "deutschland": (51.1657, 10.4515),  # Deutschland Zentrum
    "österreich": (47.5162, 14.5501),  # Österreich Zentrum
    "schweiz": (46.8182, 8.2275),  # Schweiz Zentrum
}


class GeoVisualizer:
    """Geo-Visualisierung für Job-Daten"""

    def __init__(self):
        """Initialisiere Geo-Visualizer mit deutscher Städte-Datenbank"""
        self.cities_db = GERMAN_CITIES_GEO.copy()

        # Füge Aliase für Städte mit Umlauten hinzu (ü→ue, ö→oe, ä→ae, ß→ss)
        umlaut_aliases = {}
        for city, coords in list(self.cities_db.items()):
            # Erstelle ASCII-Version
            ascii_version = (city
                           .replace("ü", "ue")
                           .replace("ä", "ae")
                           .replace("ö", "oe")
                           .replace("ß", "ss"))
            if ascii_version != city:
                umlaut_aliases[ascii_version] = coords

        # Füge Aliase hinzu
        self.cities_db.update(umlaut_aliases)

        logger.info(f"✅ GeoVisualizer initialisiert mit {len(self.cities_db)} Städten ({len(umlaut_aliases)} Aliase)")

    def normalize_region_name(self, region: str) -> str:
        """Normalisiert Regions-Namen für Lookup"""
        if not region:
            return ""

        # Lowercase und trim
        normalized = region.lower().strip()

        # Entferne Klammern und Zusätze
        normalized = re.sub(r'\s*\([^)]*\)', '', normalized)

        # Entferne Bindestriche in zusammengesetzten Namen
        normalized = normalized.replace("-", " ")

        # Umlaute normalisieren (optional)
        normalized = (normalized
                     .replace("ü", "ue")
                     .replace("ä", "ae")
                     .replace("ö", "oe")
                     .replace("ß", "ss"))

        return normalized.strip()

    def geocode_region(self, region: str) -> Optional[Tuple[float, float]]:
        """
        Konvertiert Regions-Name zu Koordinaten (lat, lon)

        Returns:
            (lat, lon) oder None wenn nicht gefunden
        """
        if not region:
            return None

        # Normalisiere Region
        normalized = self.normalize_region_name(region)

        # Direkte Suche
        if normalized in self.cities_db:
            return self.cities_db[normalized]

        # Fuzzy Match (z.B. "Berlin (Remote)" -> "berlin")
        for city_key in self.cities_db:
            if city_key in normalized or normalized in city_key:
                return self.cities_db[city_key]

        logger.warning(f"⚠️ Region '{region}' konnte nicht geocodiert werden")
        return None

    def generate_map_data(self, regional_distribution: Dict[str, int]) -> List[Dict]:
        """
        Generiert Map-Daten für Plotly/Folium

        Args:
            regional_distribution: {region_name: job_count}

        Returns:
            List of dicts mit {region, lat, lon, count}
        """
        map_data = []

        for region, count in regional_distribution.items():
            coords = self.geocode_region(region)

            if coords:
                lat, lon = coords
                map_data.append({
                    "region": region,
                    "lat": lat,
                    "lon": lon,
                    "count": count,
                    "size": min(count * 5, 100)  # Bubble size (max 100)
                })
            else:
                logger.debug(f"🗺️ Region '{region}' übersprungen (keine Koordinaten)")

        return map_data

    def get_coverage_stats(self, regional_distribution: Dict[str, int]) -> Dict:
        """
        Berechnet Geocoding-Coverage

        Returns:
            {total_regions, geocoded_regions, coverage_percent, missing_regions}
        """
        total_regions = len(regional_distribution)
        geocoded = 0
        missing = []

        for region in regional_distribution.keys():
            if self.geocode_region(region):
                geocoded += 1
            else:
                missing.append(region)

        coverage_percent = (geocoded / total_regions * 100) if total_regions > 0 else 0

        return {
            "total_regions": total_regions,
            "geocoded_regions": geocoded,
            "coverage_percent": coverage_percent,
            "missing_regions": missing
        }

    def add_missing_city(self, city_name: str, lat: float, lon: float):
        """
        Fügt eine fehlende Stadt zur Datenbank hinzu

        Args:
            city_name: Name der Stadt
            lat: Breitengrad
            lon: Längengrad
        """
        normalized = self.normalize_region_name(city_name)
        self.cities_db[normalized] = (lat, lon)
        logger.info(f"✅ Stadt '{city_name}' hinzugefügt: ({lat}, {lon})")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_plotly_map_data(regional_dist: Dict[str, int]) -> Dict:
    """
    Erstellt Plotly-kompatible Map-Daten

    Returns:
        {
            'lat': [...],
            'lon': [...],
            'text': [...],
            'marker_size': [...],
            'regions': [...]
        }
    """
    visualizer = GeoVisualizer()
    map_data = visualizer.generate_map_data(regional_dist)

    return {
        'lat': [d['lat'] for d in map_data],
        'lon': [d['lon'] for d in map_data],
        'text': [f"{d['region']}: {d['count']} Jobs" for d in map_data],
        'marker_size': [d['size'] for d in map_data],
        'regions': [d['region'] for d in map_data],
        'counts': [d['count'] for d in map_data]
    }


if __name__ == "__main__":
    # Test
    viz = GeoVisualizer()

    test_regions = {
        "Berlin": 450,
        "München": 320,
        "Hamburg": 280,
        "Köln": 150,
        "Frankfurt": 200,
        "Remote": 100,
        "Stuttgart": 180
    }

    print("\n" + "="*60)
    print("GEO-VISUALISIERUNG TEST")
    print("="*60)

    # Geocoding
    print("\n1. Geocoding Test:")
    for region in test_regions.keys():
        coords = viz.geocode_region(region)
        print(f"   {region:15} → {coords}")

    # Map Data
    print("\n2. Map Data Generation:")
    map_data = viz.generate_map_data(test_regions)
    for entry in map_data:
        print(f"   {entry}")

    # Coverage
    print("\n3. Coverage Stats:")
    stats = viz.get_coverage_stats(test_regions)
    print(f"   Total: {stats['total_regions']}")
    print(f"   Geocoded: {stats['geocoded_regions']}")
    print(f"   Coverage: {stats['coverage_percent']:.1f}%")
    print(f"   Missing: {stats['missing_regions']}")

    print("\n" + "="*60)
    print("✅ Test abgeschlossen")
    print("="*60)
