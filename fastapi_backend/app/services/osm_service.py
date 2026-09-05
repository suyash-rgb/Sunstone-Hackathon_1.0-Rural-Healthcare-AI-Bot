import asyncio
import logging
import math
import re
import uuid
from typing import List, Tuple, Optional

import httpx
from app.schemas.facility import MedicalFacility

logger = logging.getLogger(__name__)

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return int(R * c)

def classify_osm_facility(name: str, address: str, tags: dict) -> Tuple[bool, str]:
    text = f"{name} {address}".lower()
    operator = str(tags.get("operator", "")).lower()
    operator_type = str(tags.get("operator:type", "")).lower()

    is_govt_operator = operator_type in ["government", "public"] or "govt" in operator or "government" in operator

    if re.search(r"\bphc\b", text) or "primary health" in text:
        return True, "Govt. PHC (Primary Health Centre)"

    if re.search(r"\bchc\b", text) or "community health" in text:
        return True, "Govt. CHC (Community Health Centre)"

    if "district" in text or "civil" in text or "bhoj hospital" in text:
        return True, "Govt. District / Civil Hospital"

    govt_keywords = [
        "govt", "government", "sub-district", "swasthya kendra",
        "arogya mandir", "sarkari", "jan aushadhi"
    ]
    if is_govt_operator or any(kw in text for kw in govt_keywords):
        return True, "Govt. Healthcare Facility"

    return False, "Private Hospital / Clinic"

class OSMService:
    def __init__(self):
        self.endpoints = [
            "https://overpass-api.de/api/interpreter",
            "https://overpass.kumi.systems/api/interpreter",
            "https://overpass.nchc.org.tw/api/interpreter"
        ]
        self.headers = {
            "User-Agent": "AarogyaMitra-EmergencyApp/1.0 (Contact: healthcare@aarogyamitra.org)"
        }

    async def get_nearby_facilities(
        self,
        lat: float,
        lon: float,
        radius: int = 5000
    ) -> List[MedicalFacility]:
        logger.info(f"[OSM Hybrid Fallback] Querying Overpass API for lat={lat}, lon={lon}, radius={radius}m...")

        overpass_query = f"""[out:json][timeout:10];
(
  node["amenity"="hospital"](around:{radius},{lat},{lon});
  way["amenity"="hospital"](around:{radius},{lat},{lon});
  node["amenity"="clinic"](around:{radius},{lat},{lon});
  way["healthcare"="centre"](around:{radius},{lat},{lon});
  node["healthcare"="hospital"](around:{radius},{lat},{lon});
  way["healthcare"="hospital"](around:{radius},{lat},{lon});
);
out center;"""

        raw_elements = []
        async with httpx.AsyncClient() as client:
            for endpoint in self.endpoints:
                try:
                    # Try GET request first
                    response = await client.get(
                        endpoint,
                        params={"data": overpass_query},
                        headers=self.headers,
                        timeout=8.0
                    )
                    if response.status_code == 200:
                        data = response.json()
                        raw_elements = data.get("elements", [])
                        logger.info(f"[OSM Overpass] Successfully fetched {len(raw_elements)} elements from {endpoint}")
                        break
                    else:
                        # Try POST request fallback
                        response_post = await client.post(
                            endpoint,
                            data={"data": overpass_query},
                            headers=self.headers,
                            timeout=8.0
                        )
                        if response_post.status_code == 200:
                            data = response_post.json()
                            raw_elements = data.get("elements", [])
                            logger.info(f"[OSM Overpass] Successfully fetched {len(raw_elements)} elements via POST from {endpoint}")
                            break
                        else:
                            logger.warning(f"[OSM Overpass] Endpoint {endpoint} returned status GET:{response.status_code} POST:{response_post.status_code}")
                except Exception as e:
                    logger.error(f"[OSM Overpass] Request to {endpoint} failed: {e}")

        facilities: List[MedicalFacility] = []
        seen_ids = set()

        for item in raw_elements:
            osm_type = item.get("type", "node")
            osm_id = item.get("id")
            place_id = f"osm-{osm_type}-{osm_id}" if osm_id else str(uuid.uuid4())

            if place_id in seen_ids:
                continue

            if osm_type == "node":
                fac_lat = item.get("lat")
                fac_lon = item.get("lon")
            else:
                center = item.get("center", {})
                fac_lat = center.get("lat")
                fac_lon = center.get("lon")

            if fac_lat is None or fac_lon is None:
                continue

            try:
                fac_lat = float(fac_lat)
                fac_lon = float(fac_lon)
            except (ValueError, TypeError):
                continue

            tags = item.get("tags", {})
            name = (
                tags.get("name")
                or tags.get("name:en")
                or tags.get("name:hi")
                or tags.get("operator")
                or "Healthcare Centre (OSM)"
            )

            addr_parts = [
                tags.get("addr:full"),
                tags.get("addr:street"),
                tags.get("addr:village") or tags.get("addr:subdistrict"),
                tags.get("addr:district") or tags.get("addr:city"),
                tags.get("addr:postcode")
            ]
            address = ", ".join([p for p in addr_parts if p])
            if not address:
                address = "Rural Healthcare Center / OpenStreetMap"

            dist_m = haversine_distance(lat, lon, fac_lat, fac_lon)
            dist_km = round(dist_m / 1000.0, 2)

            is_govt, tier = classify_osm_facility(name, address, tags)

            phone = tags.get("phone") or tags.get("contact:phone") or tags.get("phone:mobile")
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
                open_now=None,
                google_maps_url=google_maps_url
            )
            facilities.append(facility)
            seen_ids.add(place_id)

        facilities.sort(key=lambda x: (0 if x.is_government else 1, x.distance_meters))
        return facilities

osm_service = OSMService()
