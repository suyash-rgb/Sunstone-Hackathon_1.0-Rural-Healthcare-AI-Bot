from pydantic import BaseModel
from typing import Optional, List

# --- Legacy External Services Schemas ---
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
    tier: Optional[str] = None
    badge: Optional[str] = None
    phone: Optional[str] = None
    open_now: Optional[bool] = None
    google_maps_url: str

class FacilityDiscoveryResponse(BaseModel):
    total_found: int
    user_location: dict
    facilities: List[MedicalFacility]

# --- PostgreSQL DB Healthcare Facility Schemas ---
class DBHealthcareFacilityResponse(BaseModel):
    id: int
    sr_no: Optional[int] = None
    facility_name: str
    address: Optional[str] = None
    street: Optional[str] = None
    landmark: Optional[str] = None
    locality: Optional[str] = None
    pincode: Optional[str] = None
    landline_number: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    facility_type: str
    tier_level: str
    state_name: str
    district_name: str
    taluka_name: Optional[str] = None
    block_name: Optional[str] = None
    formatted_address: Optional[str] = None
    distance_meters: Optional[float] = None
    distance_km: Optional[float] = None

    class Config:
        from_attributes = True

class DBNearbyFacilityResponse(BaseModel):
    total_found: int
    user_location: dict
    radius_meters: int
    facilities: List[DBHealthcareFacilityResponse]

class DBFacilityPaginatedResponse(BaseModel):
    total_count: int
    page: int
    limit: int
    total_pages: int
    facilities: List[DBHealthcareFacilityResponse]

class LocationHierarchyResponse(BaseModel):
    states: Optional[List[str]] = None
    districts: Optional[List[str]] = None
    talukas: Optional[List[str]] = None
    blocks: Optional[List[str]] = None

# --- Unified Emergency Facility Schemas ---
class CombinedEmergencyFacility(BaseModel):
    id: str
    source: str  # "government_db", "olamaps", or "osm"
    facility_name: str
    formatted_address: str
    distance_meters: float
    distance_km: float
    latitude: float
    longitude: float
    type: str
    tier_level: Optional[str] = None
    contact_numbers: Optional[str] = None
    is_government: bool = False
    google_maps_url: Optional[str] = None

class CombinedEmergencyFacilityResponse(BaseModel):
    total_found: int
    search_radius_km: float
    user_location: dict
    facilities: List[CombinedEmergencyFacility]
