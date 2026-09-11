import math
from typing import Optional, List, Dict, Any
from sqlalchemy import text, select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.healthcare_facility import HealthcareFacility
from app.schemas.facility import (
    DBHealthcareFacilityResponse, DBNearbyFacilityResponse,
    DBFacilityPaginatedResponse, LocationHierarchyResponse
)

def build_formatted_address(d: dict) -> str:
    parts = []
    # Local address components
    if d.get("address"):
        parts.append(d["address"].strip())
    if d.get("street") and d["street"].strip() not in parts:
        parts.append(d["street"].strip())
    if d.get("landmark") and d["landmark"].strip() not in parts:
        parts.append(d["landmark"].strip())
    if d.get("locality") and d["locality"].strip() not in parts:
        parts.append(d["locality"].strip())

    # Fallback if no local address details exist
    if not parts:
        if d.get("facility_name"):
            parts.append(d["facility_name"].strip())
        local_area = d.get("taluka_name") or d.get("block_name")
        if local_area and local_area.strip() not in parts:
            parts.append(local_area.strip())

    # Administrative boundaries
    if d.get("district_name") and d["district_name"].strip() not in parts:
        parts.append(d["district_name"].strip())
    if d.get("state_name") and d["state_name"].strip() not in parts:
        parts.append(d["state_name"].strip())

    addr_str = ", ".join([p for p in parts if p])
    if d.get("pincode"):
        addr_str += f" - {d['pincode'].strip()}"
    return addr_str

def format_facility_response(d: dict) -> DBHealthcareFacilityResponse:
    d["formatted_address"] = build_formatted_address(d)
    return DBHealthcareFacilityResponse(**d)

class GovtHealthcareFacilityService:
    @staticmethod
    async def get_nearby_facilities(
        session: AsyncSession,
        lat: float,
        lon: float,
        radius_meters: int = 10000,
        tier_level: str = "all",
        facility_type: str = "all",
        limit: int = 20
    ) -> DBNearbyFacilityResponse:
        """
        High-performance spatial search using bounding-box SQL pre-filtering 
        followed by exact Haversine distance calculation in PostgreSQL.
        """
        delta_lat = radius_meters / 111000.0
        cos_lat = math.cos(math.radians(lat))
        delta_lon = radius_meters / (111000.0 * cos_lat) if cos_lat != 0 else delta_lat

        min_lat = lat - delta_lat
        max_lat = lat + delta_lat
        min_lon = lon - delta_lon
        max_lon = lon + delta_lon

        where_clauses = [
            "latitude BETWEEN :min_lat AND :max_lat",
            "longitude BETWEEN :min_lon AND :max_lon"
        ]

        params: Dict[str, Any] = {
            "lat": lat,
            "lon": lon,
            "min_lat": min_lat,
            "max_lat": max_lat,
            "min_lon": min_lon,
            "max_lon": max_lon,
            "radius_meters": radius_meters,
            "limit": limit
        }

        if tier_level and tier_level.lower() != "all":
            where_clauses.append("tier_level = :tier_level")
            params["tier_level"] = tier_level.strip()

        if facility_type and facility_type.lower() != "all":
            where_clauses.append("facility_type ILIKE :facility_type")
            params["facility_type"] = f"%{facility_type.strip()}%"

        where_sql = " AND ".join(where_clauses)

        query_str = f"""
            SELECT * FROM (
                SELECT id, sr_no, facility_name, address, street, landmark, locality, pincode,
                       landline_number, latitude, longitude, facility_type, tier_level,
                       state_name, district_name, taluka_name, block_name,
                       (6371000 * acos(LEAST(1.0, GREATEST(-1.0, 
                           sin(radians(:lat)) * sin(radians(latitude)) + 
                           cos(radians(:lat)) * cos(radians(latitude)) * cos(radians(longitude) - radians(:lon))
                       )))) AS distance_meters
                FROM healthcare_facilities
                WHERE {where_sql}
            ) sub
            WHERE distance_meters <= :radius_meters
            ORDER BY distance_meters ASC
            LIMIT :limit;
        """

        res = await session.execute(text(query_str), params)
        rows = res.mappings().all()

        facilities = []
        for r in rows:
            dist_m = float(r["distance_meters"]) if r["distance_meters"] is not None else 0.0
            facility_dict = dict(r)
            facility_dict["distance_meters"] = round(dist_m, 1)
            facility_dict["distance_km"] = round(dist_m / 1000.0, 2)
            facilities.append(format_facility_response(facility_dict))

        return DBNearbyFacilityResponse(
            total_found=len(facilities),
            user_location={"lat": lat, "lon": lon},
            radius_meters=radius_meters,
            facilities=facilities
        )

    @staticmethod
    async def search_facilities(
        session: AsyncSession,
        state_name: Optional[str] = None,
        district_name: Optional[str] = None,
        taluka_name: Optional[str] = None,
        block_name: Optional[str] = None,
        pincode: Optional[str] = None,
        tier_level: Optional[str] = None,
        facility_type: Optional[str] = None,
        query_str: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> DBFacilityPaginatedResponse:
        """
        Filtered search across administrative levels (State, District, Taluka, Block, Pincode)
        with text search support and pagination.
        """
        stmt = select(HealthcareFacility)
        filters = []

        if state_name:
            filters.append(func.lower(HealthcareFacility.state_name) == state_name.strip().lower())
        if district_name:
            filters.append(func.lower(HealthcareFacility.district_name) == district_name.strip().lower())
        if taluka_name:
            filters.append(func.lower(HealthcareFacility.taluka_name) == taluka_name.strip().lower())
        if block_name:
            filters.append(func.lower(HealthcareFacility.block_name) == block_name.strip().lower())
        if pincode:
            filters.append(HealthcareFacility.pincode == pincode.strip())
        if tier_level and tier_level.lower() != "all":
            filters.append(HealthcareFacility.tier_level == tier_level.strip())
        if facility_type and facility_type.lower() != "all":
            filters.append(func.lower(HealthcareFacility.facility_type).contains(facility_type.strip().lower()))

        if query_str and query_str.strip():
            q = f"%{query_str.strip().lower()}%"
            filters.append(
                or_(
                    func.lower(HealthcareFacility.facility_name).like(q),
                    func.lower(HealthcareFacility.locality).like(q),
                    func.lower(HealthcareFacility.street).like(q),
                    func.lower(HealthcareFacility.landmark).like(q),
                    func.lower(HealthcareFacility.address).like(q)
                )
            )

        if filters:
            stmt = stmt.where(and_(*filters))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_res = await session.execute(count_stmt)
        total_count = total_res.scalar() or 0

        offset = (page - 1) * limit
        stmt = stmt.order_by(HealthcareFacility.facility_name.asc()).offset(offset).limit(limit)

        result = await session.execute(stmt)
        facilities_models = result.scalars().all()

        facilities = []
        for model in facilities_models:
            d = {c.name: getattr(model, c.name) for c in model.__table__.columns}
            facilities.append(format_facility_response(d))

        total_pages = math.ceil(total_count / limit) if limit > 0 else 1

        return DBFacilityPaginatedResponse(
            total_count=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages,
            facilities=facilities
        )

    @staticmethod
    async def get_facility_by_id(session: AsyncSession, facility_id: int) -> Optional[DBHealthcareFacilityResponse]:
        stmt = select(HealthcareFacility).where(HealthcareFacility.id == facility_id)
        res = await session.execute(stmt)
        facility = res.scalar_one_or_none()
        if facility:
            d = {c.name: getattr(facility, c.name) for c in facility.__table__.columns}
            return format_facility_response(d)
        return None

    @staticmethod
    async def get_location_hierarchy(
        session: AsyncSession,
        state_name: Optional[str] = None,
        district_name: Optional[str] = None
    ) -> LocationHierarchyResponse:
        if not state_name:
            stmt = select(HealthcareFacility.state_name).distinct().order_by(HealthcareFacility.state_name.asc())
            res = await session.execute(stmt)
            states = [r for r in res.scalars().all() if r]
            return LocationHierarchyResponse(states=states)

        state_clean = state_name.strip().lower()
        if not district_name:
            stmt = select(HealthcareFacility.district_name).where(
                func.lower(HealthcareFacility.state_name) == state_clean
            ).distinct().order_by(HealthcareFacility.district_name.asc())
            res = await session.execute(stmt)
            districts = [r for r in res.scalars().all() if r]
            return LocationHierarchyResponse(districts=districts)

        district_clean = district_name.strip().lower()
        stmt_t = select(HealthcareFacility.taluka_name).where(
            and_(
                func.lower(HealthcareFacility.state_name) == state_clean,
                func.lower(HealthcareFacility.district_name) == district_clean,
                HealthcareFacility.taluka_name.isnot(None)
            )
        ).distinct().order_by(HealthcareFacility.taluka_name.asc())
        
        stmt_b = select(HealthcareFacility.block_name).where(
            and_(
                func.lower(HealthcareFacility.state_name) == state_clean,
                func.lower(HealthcareFacility.district_name) == district_clean,
                HealthcareFacility.block_name.isnot(None)
            )
        ).distinct().order_by(HealthcareFacility.block_name.asc())

        res_t = await session.execute(stmt_t)
        res_b = await session.execute(stmt_b)

        talukas = [r for r in res_t.scalars().all() if r]
        blocks = [r for r in res_b.scalars().all() if r]

        return LocationHierarchyResponse(talukas=talukas, blocks=blocks)

govt_healthcare_facility_service = GovtHealthcareFacilityService()
