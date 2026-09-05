import math
import re
from typing import Tuple, Optional

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
    """Calculate the great circle distance in meters between two points on the earth."""
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return int(R * c)

def classify_facility(name: str, address: str, tags: Optional[dict] = None) -> Tuple[bool, str]:
    """Classify a facility tier and government status based on keywords and OSM tags."""
    if tags is None:
        tags = {}
        
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
