from typing import Optional
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.facility import (
    DBNearbyFacilityResponse, DBFacilityPaginatedResponse,
    DBHealthcareFacilityResponse, LocationHierarchyResponse
)
from app.services.govt_healthcare_facility_service import govt_healthcare_facility_service

router = APIRouter(prefix="/govt-healthcare-facilities", tags=["Government Healthcare Facilities"])

@router.get("/nearby", response_model=DBNearbyFacilityResponse, summary="Spatial Nearby Government Healthcare Facilities")
async def get_nearby_govt_facilities(
    lat: Optional[float] = Query(None, description="User Latitude"),
    lon: Optional[float] = Query(None, description="User Longitude"),
    latitude: Optional[float] = Query(None, description="User Latitude alias"),
    longitude: Optional[float] = Query(None, description="User Longitude alias"),
    radius: int = Query(10000, ge=100, le=100000, description="Search radius in meters (default 10,000m / 10km)"),
    tier_level: str = Query("all", description="Filter by healthcare tier: 'all', '1_primary', '2_secondary', '3_tertiary', '4_specialized'"),
    facility_type: str = Query("all", description="Filter by facility type substring (e.g. 'SubCentre', 'District Hospital', 'PHC')"),
    limit: int = Query(20, ge=1, le=100, description="Max results to return"),
    session: AsyncSession = Depends(get_session)
):
    """
    High-speed spatial search querying 192,000+ verified government healthcare facilities from PostgreSQL.
    Uses bounding-box pre-filtering and exact Haversine distance calculation in SQL.
    """
    final_lat = lat if lat is not None else latitude
    final_lon = lon if lon is not None else longitude

    if final_lat is None or final_lon is None:
        raise HTTPException(status_code=400, detail="Latitude and longitude parameters are required.")

    return await govt_healthcare_facility_service.get_nearby_facilities(
        session=session,
        lat=final_lat,
        lon=final_lon,
        radius_meters=radius,
        tier_level=tier_level,
        facility_type=facility_type,
        limit=limit
    )

@router.get("/search", response_model=DBFacilityPaginatedResponse, summary="Filter & Search Facilities by Admin Boundaries")
async def search_govt_facilities(
    state_name: Optional[str] = Query(None, description="Filter by State (case-insensitive)"),
    district_name: Optional[str] = Query(None, description="Filter by District (case-insensitive)"),
    taluka_name: Optional[str] = Query(None, description="Filter by Taluka (case-insensitive)"),
    block_name: Optional[str] = Query(None, description="Filter by Block (case-insensitive)"),
    pincode: Optional[str] = Query(None, description="Filter by 6-digit Pincode"),
    tier_level: Optional[str] = Query(None, description="Filter by tier: '1_primary', '2_secondary', '3_tertiary', '4_specialized'"),
    facility_type: Optional[str] = Query(None, description="Filter by facility type"),
    query: Optional[str] = Query(None, description="Search keyword in facility name, locality, landmark, or street"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    session: AsyncSession = Depends(get_session)
):
    """
    Filter and list government healthcare facilities by administrative boundary (State, District, Taluka, Block, Pincode) 
    or text search query with pagination.
    """
    return await govt_healthcare_facility_service.search_facilities(
        session=session,
        state_name=state_name,
        district_name=district_name,
        taluka_name=taluka_name,
        block_name=block_name,
        pincode=pincode,
        tier_level=tier_level,
        facility_type=facility_type,
        query_str=query,
        page=page,
        limit=limit
    )

@router.get("/locations", response_model=LocationHierarchyResponse, summary="Cascading Location Hierarchy for Dropdowns")
async def get_govt_facility_locations(
    state_name: Optional[str] = Query(None, description="Provide state to list districts"),
    district_name: Optional[str] = Query(None, description="Provide district (along with state) to list talukas & blocks"),
    session: AsyncSession = Depends(get_session)
):
    """
    Returns available administrative locations for building cascading dropdown filters in UI:
    - If no parameters: returns all distinct States.
    - If state_name provided: returns distinct Districts in that State.
    - If state_name & district_name provided: returns distinct Talukas and Blocks in that District.
    """
    return await govt_healthcare_facility_service.get_location_hierarchy(
        session=session,
        state_name=state_name,
        district_name=district_name
    )

@router.get("/{facility_id}", response_model=DBHealthcareFacilityResponse, summary="Get Facility Details by ID")
async def get_govt_facility_by_id(
    facility_id: int,
    session: AsyncSession = Depends(get_session)
):
    facility = await govt_healthcare_facility_service.get_facility_by_id(session=session, facility_id=facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail=f"Government healthcare facility with ID {facility_id} not found.")
    return facility
