import asyncio
import logging
import math
import re
import time
import uuid
from typing import Dict, List, Optional, Tuple

import httpx
from app.core.config import settings
from app.schemas.facility import MedicalFacility
from app.services.osm_service import osm_service

logger = logging.getLogger(__name__)

class TTLCache:
    def __init__(self, ttl_seconds: int = 600):
        self.ttl = ttl_seconds
        self.cache: Dict[Tuple[float, float], Tuple[float, List[MedicalFacility]]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: Tuple[float, float]) -> Optional[List[MedicalFacility]]:
        async with self._lock:
            if key in self.cache:
                timestamp, data = self.cache[key]
                if time.time() - timestamp < self.ttl:
                    return data
                del self.cache[key]
            return None

    async def set(self, key: Tuple[float, float], value: List[MedicalFacility]):
        async with self._lock:
            self.cache[key] = (time.time(), value)

facility_cache = TTLCache(ttl_seconds=600)

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return int(R * c)

class OlaMapsService:
    def __init__(self):
        self.base_url = settings.resolved_ola_maps_base_url.rstrip("/")
        self.api_key = settings.resolved_ola_maps_api_key

    def _classify_facility(self, name: str, address: str) -> Tuple[bool, str]:
        text = f"{name} {address}".lower()

        if re.search(r"\bphc\b", text) or "primary health" in text:
            return True, "Govt. PHC (Primary Health Centre)"

        if re.search(r"\bchc\b", text) or "community health" in text:
            return True, "Govt. CHC (Community Health Centre)"

        if "district" in text or "civil" in text or "bhoj hospital" in text:
            return True, "Govt. District / Civil Hospital"

        govt_keywords = [
            "govt", "government", "sub-district", "swasthya kendra",
            "arogya mandir", "sarkari"
        ]
        if any(kw in text for kw in govt_keywords):
            return True, "Govt. Healthcare Facility"

        return False, "Private Hospital / Clinic"

    async def _fetch_places_by_type(
        self,
        client: httpx.AsyncClient,
        lat: float,
        lon: float,
        radius: int,
        place_type: str
    ) -> List[dict]:
        endpoint = f"{self.base_url}/places/v1/nearbysearch/advanced"
        params = {
            "location": f"{lat},{lon}",
            "radius": str(radius),
            "types": place_type,
            "withCentroid": "true",
            "rankBy": "distance",
            "api_key": self.api_key
        }
        headers = {
            "X-Request-Id": f"aarogya-{uuid.uuid4()}"
        }

        try:
            response = await client.get(endpoint, params=params, headers=headers, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                predictions = data.get("predictions", []) or data.get("results", []) or []
                return predictions
            else:
                logger.warning(f"Ola Maps API returned HTTP {response.status_code} for type {place_type}: {response.text}")
                return []
        except Exception as e:
            logger.error(f"Ola Maps API request error for type {place_type}: {e}")
            return []

    async def get_nearby_facilities(
        self,
        lat: float,
        lon: float,
        radius: int = 5000
    ) -> List[MedicalFacility]:
        cache_key = (round(lat, 2), round(lon, 2))
        cached_results = await facility_cache.get(cache_key)
        if cached_results is not None:
            logger.info(f"Cache HIT for coordinates {cache_key}")
            return cached_results

        logger.info(f"Cache MISS for coordinates {cache_key}. Querying Ola Maps API...")

        facilities: List[MedicalFacility] = []
        try:
            async with httpx.AsyncClient() as client:
                raw_hospitals, raw_health = await asyncio.gather(
                    self._fetch_places_by_type(client, lat, lon, radius, "hospital"),
                    self._fetch_places_by_type(client, lat, lon, radius, "health")
                )

                all_raw = raw_hospitals + raw_health

                if len(all_raw) < 3 and radius < 10000:
                    logger.info(f"Fewer than 3 facilities found at radius={radius}. Expanding search to radius=10000...")
                    raw_hospitals_10k, raw_health_10k = await asyncio.gather(
                        self._fetch_places_by_type(client, lat, lon, 10000, "hospital"),
                        self._fetch_places_by_type(client, lat, lon, 10000, "health")
                    )
                    all_raw = raw_hospitals_10k + raw_health_10k

            seen_place_ids = set()

            for item in all_raw:
                place_id = item.get("place_id") or item.get("id") or str(uuid.uuid4())
                if place_id in seen_place_ids:
                    continue

                layer = item.get("layer", [])
                if isinstance(layer, str):
                    layer = [layer]
                if "locality" in layer or ("venue" not in layer and layer):
                    continue

                geometry = item.get("geometry", {})
                loc = geometry.get("location", {}) or geometry.get("centroid", {})
                fac_lat = loc.get("lat")
                fac_lon = loc.get("lng") or loc.get("lon")

                if fac_lat is None or fac_lon is None:
                    continue

                try:
                    fac_lat = float(fac_lat)
                    fac_lon = float(fac_lon)
                except (ValueError, TypeError):
                    continue

                seen_place_ids.add(place_id)

                name = item.get("name") or item.get("structured_formatting", {}).get("main_text") or "Healthcare Facility"
                address = item.get("formatted_address") or item.get("description") or item.get("structured_formatting", {}).get("secondary_text") or ""

                dist_m = item.get("distance_meters") or item.get("distance")
                if dist_m is None:
                    dist_m = haversine_distance(lat, lon, fac_lat, fac_lon)
                else:
                    dist_m = int(dist_m)

                dist_km = round(dist_m / 1000.0, 2)

                is_govt, tier = self._classify_facility(name, address)

                phone = item.get("formatted_phone_number") or item.get("international_phone_number") or item.get("phone")
                open_now = None
                opening_hours = item.get("opening_hours")
                if isinstance(opening_hours, dict):
                    open_now = opening_hours.get("open_now")

                google_maps_url = f"https://www.google.com/maps/dir/?api=1&destination={fac_lat},{fac_lon}"

                facility = MedicalFacility(
                    place_id=place_id,
                    name=name,
                    address=address,
                    distance_meters=dist_m,
                    distance_km=dist_km,
                    lat=fac_lat,
                    lon=fac_lon,
                    is_government=is_govt,
                    facility_tier=tier,
                    phone=phone,
                    open_now=open_now,
                    google_maps_url=google_maps_url
                )
                facilities.append(facility)
        except Exception as e:
            logger.error(f"Ola Maps API processing error: {e}")

        if len(facilities) == 0:
            logger.warning(f"[Hybrid Fallback Triggered] Ola Maps returned 0 results or failed. Falling back to OpenStreetMap Overpass API for lat={lat}, lon={lon}...")
            facilities = await osm_service.get_nearby_facilities(lat, lon, radius)

        facilities.sort(key=lambda x: (0 if x.is_government else 1, x.distance_meters))

        await facility_cache.set(cache_key, facilities)
        return facilities

olamaps_service = OlaMapsService()
