from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from app.schemas.facility import FacilityDiscoveryResponse
from app.services.olamaps_service import olamaps_service

router = APIRouter(prefix="/healthcare-facilities", tags=["Healthcare Facility Discovery"])

@router.get("/nearby", response_model=FacilityDiscoveryResponse)
async def get_nearby_facilities(
    lat: Optional[float] = Query(None, description="User Latitude"),
    lon: Optional[float] = Query(None, description="User Longitude"),
    latitude: Optional[float] = Query(None, description="User Latitude"),
    longitude: Optional[float] = Query(None, description="User Longitude"),
    radius: int = Query(5000, description="Search radius in meters"),
    facility_type: str = Query("all", description="Facility type filter: 'all' or 'government'"),
    exclude_specialty: bool = Query(True, description="Filter out non-general specialized clinics (dental, skin, etc.)")
):
    final_lat = lat if lat is not None else latitude
    final_lon = lon if lon is not None else longitude

    if final_lat is None or final_lon is None:
        raise HTTPException(status_code=400, detail="Latitude and longitude parameters are required.")

    try:
        facilities = await olamaps_service.get_nearby_facilities(
            lat=final_lat,
            lon=final_lon,
            radius=radius,
            facility_type=facility_type,
            exclude_specialty=exclude_specialty
        )
        return FacilityDiscoveryResponse(
            total_found=len(facilities),
            user_location={"lat": final_lat, "lon": final_lon},
            facilities=facilities
        )
    except Exception as e:
        return FacilityDiscoveryResponse(
            total_found=0,
            user_location={"lat": final_lat, "lon": final_lon},
            facilities=[]
        )
