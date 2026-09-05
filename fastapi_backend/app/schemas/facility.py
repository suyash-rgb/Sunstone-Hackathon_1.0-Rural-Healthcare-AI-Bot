from pydantic import BaseModel
from typing import Optional, List

class MedicalFacility(BaseModel):
    place_id: str
    name: str
    address: str
    distance_meters: int
    distance_km: float
    lat: float
    lon: float
    is_government: bool
    facility_tier: str
    phone: Optional[str] = None
    open_now: Optional[bool] = None
    google_maps_url: str

class FacilityDiscoveryResponse(BaseModel):
    total_found: int
    user_location: dict
    facilities: List[MedicalFacility]
