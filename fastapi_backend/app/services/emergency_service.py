import asyncio
import logging
import re
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.facility import (
    CombinedEmergencyFacility,
    CombinedEmergencyFacilityResponse,
    DBNearbyFacilityResponse,
    MedicalFacility
)
from app.services.govt_healthcare_facility_service import govt_healthcare_facility_service
from app.services.olamaps_service import olamaps_service
from app.core.utils import haversine_distance

logger = logging.getLogger(__name__)

class EmergencyService:
    @staticmethod
    async def get_nearby_emergency_facilities(
        session: AsyncSession,
        lat: float,
        lon: float,
        radius_km: float = 10.0
    ) -> CombinedEmergencyFacilityResponse:
        radius_meters = int(radius_km * 1000)

        # Run concurrent queries for Govt DB and OlaMaps/OSM with graceful exception handling
        results = await asyncio.gather(
            govt_healthcare_facility_service.get_nearby_facilities(
                session=session,
                lat=lat,
                lon=lon,
                radius_meters=radius_meters,
                limit=100
            ),
            olamaps_service.get_nearby_facilities(
                lat=lat,
                lon=lon,
                radius=radius_meters,
                facility_type="all",
                exclude_specialty=True
            ),
            return_exceptions=True
        )

        govt_res = results[0]
        ola_res = results[1]

        govt_facilities_raw = []
        if isinstance(govt_res, DBNearbyFacilityResponse):
            govt_facilities_raw = govt_res.facilities
        elif isinstance(govt_res, Exception):
            logger.error(f"[EmergencyService] Government DB query failed: {govt_res}")

        ola_facilities_raw: List[MedicalFacility] = []
        if isinstance(ola_res, list):
            ola_facilities_raw = ola_res
        elif isinstance(ola_res, Exception):
            logger.error(f"[EmergencyService] OlaMaps/OSM query failed: {ola_res}")

        combined: List[CombinedEmergencyFacility] = []
        govt_coords: List[Tuple[float, float, str]] = []

        # 1. Process Government DB Results
        for g_fac in govt_facilities_raw:
            f_lat = g_fac.latitude if g_fac.latitude is not None else lat
            f_lon = g_fac.longitude if g_fac.longitude is not None else lon
            dist_m = float(g_fac.distance_meters) if g_fac.distance_meters is not None else 0.0
            dist_k = float(g_fac.distance_km) if g_fac.distance_km is not None else round(dist_m / 1000.0, 2)

            maps_url = f"https://www.google.com/maps/dir/?api=1&destination={f_lat},{f_lon}"

            combined_item = CombinedEmergencyFacility(
                id=str(g_fac.id),
                source="government_db",
                facility_name=g_fac.facility_name,
                formatted_address=g_fac.formatted_address or g_fac.address or "Government Healthcare Facility",
                distance_meters=dist_m,
                distance_km=dist_k,
                latitude=f_lat,
                longitude=f_lon,
                type=g_fac.facility_type,
                tier_level=g_fac.tier_level,
                contact_numbers=g_fac.landline_number,
                is_government=True,
                google_maps_url=maps_url
            )
            combined.append(combined_item)
            govt_coords.append((f_lat, f_lon, g_fac.facility_name.lower()))

        # 2. Process OlaMaps / OSM Results with Deduplication
        for o_fac in ola_facilities_raw:
            source_tag = "osm" if o_fac.place_id and o_fac.place_id.startswith("osm-") else "olamaps"

            # Check spatial deduplication against Govt DB items (within 150 meters)
            is_duplicate = False
            for g_lat, g_lon, g_name in govt_coords:
                spatial_dist = haversine_distance(o_fac.lat, o_fac.lon, g_lat, g_lon)
                if spatial_dist < 150:
                    # Near identical location; prioritize government DB entry
                    is_duplicate = True
                    break

            if is_duplicate:
                logger.info(f"[EmergencyService] Deduplicated external facility '{o_fac.name}' as Govt DB record takes priority.")
                continue

            combined_item = CombinedEmergencyFacility(
                id=str(o_fac.place_id),
                source=source_tag,
                facility_name=o_fac.name,
                formatted_address=o_fac.address or "Healthcare Facility",
                distance_meters=float(o_fac.distance_meters),
                distance_km=float(o_fac.distance_km),
                latitude=float(o_fac.lat),
                longitude=float(o_fac.lon),
                type=o_fac.facility_tier or o_fac.tier or "Private/General Clinic",
                tier_level=o_fac.tier,
                contact_numbers=o_fac.phone,
                is_government=o_fac.is_government,
                google_maps_url=o_fac.google_maps_url
            )
            combined.append(combined_item)

        # 3. Sort strictly by distance ascending
        combined.sort(key=lambda x: x.distance_meters)

        # 4. Guarantee at least one government facility in top 5 results
        top_k = 5
        if len(combined) > top_k:
            has_govt_in_top_k = any(item.is_government for item in combined[:top_k])
            if not has_govt_in_top_k:
                govt_idx = next(
                    (idx for idx, item in enumerate(combined[top_k:], start=top_k) if item.is_government),
                    None
                )
                if govt_idx is not None:
                    govt_item = combined.pop(govt_idx)
                    combined.insert(top_k - 1, govt_item)
                    logger.info(f"[EmergencyService] Promoted nearest Govt facility '{govt_item.facility_name}' to position {top_k} to guarantee Govt availability.")

        return CombinedEmergencyFacilityResponse(
            total_found=len(combined),
            search_radius_km=radius_km,
            user_location={"lat": lat, "lon": lon},
            facilities=combined
        )

emergency_service = EmergencyService()
