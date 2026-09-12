from typing import Optional
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.facility import CombinedEmergencyFacilityResponse
from app.services.emergency_service import emergency_service

router = APIRouter(prefix="/emergency/facilities", tags=["Unified Emergency Facilities"])

@router.get("/nearby", response_model=CombinedEmergencyFacilityResponse, summary="Unified Emergency Nearby Healthcare Facilities")
async def get_nearby_emergency_facilities(
    lat: Optional[float] = Query(None, description="User Latitude"),
    lon: Optional[float] = Query(None, description="User Longitude"),
    latitude: Optional[float] = Query(None, description="User Latitude alias"),
    longitude: Optional[float] = Query(None, description="User Longitude alias"),
    radius_km: float = Query(10.0, ge=0.1, le=100.0, description="Search radius in kilometers (default 10km)"),
    radius: Optional[int] = Query(None, description="Alternative search radius in meters"),
    session: AsyncSession = Depends(get_session)
):
    """
    Unified Emergency Search API combining verified public healthcare facilities from PostgreSQL (192k+ records)
    with live commercial/crowdsourced POI APIs (OlaMaps & OpenStreetMap).
    Concurrently queries both data sources and returns a unified list strictly sorted by distance.
    """
    final_lat = lat if lat is not None else latitude
    final_lon = lon if lon is not None else longitude

    if final_lat is None or final_lon is None:
        raise HTTPException(status_code=400, detail="Latitude and longitude parameters are required.")

    if radius is not None and radius > 0:
        search_radius_km = round(radius / 1000.0, 2)
    else:
        search_radius_km = radius_km

    return await emergency_service.get_nearby_emergency_facilities(
        session=session,
        lat=final_lat,
        lon=final_lon,
        radius_km=search_radius_km
    )
