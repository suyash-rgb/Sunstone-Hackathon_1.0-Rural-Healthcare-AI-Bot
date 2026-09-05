import math
import re
from typing import Tuple, Optional, List, Dict, Any

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

def is_relevant_healthcare_facility(name: str, address: str, tags: Optional[dict] = None) -> bool:
    """Determine if a facility is a relevant general healthcare facility (excluding dental, skin, optical, labs, vet)."""
    name_lower = name.lower()
    text_lower = f"{name} {address}".lower()

    # Check for veterinary / pet clinic
    if any(kw in text_lower for kw in ["veterinary", "pet clinic", "animal hospital", "vet clinic", "pashu"]):
        return False

    # Exempt major hospitals / public centers from single-specialty filtering
    is_major_center = any(kw in name_lower for kw in ["hospital", "phc", "chc", "medical college", "aiims", "civil hospital", "district hospital"])

    if not is_major_center:
        # Check for dental single-specialty
        if any(kw in text_lower for kw in ["dental", "dant", "dentist", "teeth", "orthodontic"]):
            return False

        # Check for skin / derma / aesthetic / cosmetic / hair
        if any(kw in text_lower for kw in ["skin", "derma", "dermatology", "cosmetic", "aesthetic", "hair transplant", "plastic surgery"]):
            return False

        # Check for eye / optical standalone
        if any(kw in text_lower for kw in ["eye clinic", "eye center", "eye centre", "optical", "optometry", "lasik", "drishti"]):
            return False

        # Check for standalone pathology lab / diagnostic center
        if any(kw in text_lower for kw in ["pathology", "path lab", "thyrocare", "lal path", "diagnostic", "blood bank", "scan center", "scan centre"]):
            return False

    return True

def classify_facility(name: str, address: str, tags: Optional[dict] = None) -> Tuple[bool, str, str]:
    """Classify a facility tier, government status, and UI badge based on keywords and OSM tags."""
    if tags is None:
        tags = {}
        
    name_lower = name.lower()
    text_lower = f"{name} {address}".lower()
    operator = str(tags.get("operator", "")).lower()
    operator_type = str(tags.get("operator:type", "")).lower()

    is_govt_operator = operator_type in ["government", "public"] or "govt" in operator or "government" in operator or tags.get("government") == "yes"

    if re.search(r"\bphc\b", text_lower) or "primary health" in text_lower or "prathamik swasthya" in text_lower:
        return True, "Govt. PHC (Primary Health Centre)", "GOVT. PHC"

    if re.search(r"\bchc\b", text_lower) or "community health" in text_lower or "samudayik swasthya" in text_lower:
        return True, "Govt. CHC (Community Health Centre)", "GOVT. CHC"

    if "district hospital" in text_lower or "civil hospital" in text_lower or "bhoj hospital" in text_lower or "zila hospital" in text_lower or ("district" in name_lower and "hospital" in text_lower):
        return True, "Govt. District / Civil Hospital", "CIVIL HOSPITAL"

    if "sub-centre" in text_lower or "sub centre" in text_lower or "up-swasthya" in text_lower or "hsc" in text_lower:
        return True, "Govt. Sub-Centre (HSC)", "GOVT. SUB-CENTRE"

    if "medical college" in text_lower or "aiims" in text_lower:
        return True, "Govt. Medical College & Hospital", "GOVT. MEDICAL COLLEGE"

    govt_keywords = [
        "govt", "government", "sub-district", "swasthya kendra",
        "arogya mandir", "sarkari", "jan aushadhi"
    ]
    if is_govt_operator or any(kw in name_lower for kw in govt_keywords):
        return True, "Govt. Healthcare Facility", "GOVT. FACILITY"

    if "hospital" in name_lower:
        return False, "Private Hospital", "PRIVATE HOSPITAL"
    else:
        return False, "Private Healthcare Clinic", "PRIVATE CLINIC"

def normalize_facility_name(name: str) -> str:
    """Normalize facility name by lowercasing, stripping punctuation, and removing common healthcare stop words."""
    name_clean = name.lower()
    name_clean = re.sub(r"[^a-z0-9\s]", " ", name_clean)
    stop_words = {
        "hospital", "hospitals", "clinic", "clinics", "center", "centre", "centers", "centres",
        "research", "nursing", "home", "pvt", "ltd", "private", "limited", "healthcare", "care",
        "multispecialty", "multi", "specialty", "speciality", "bhopal", "sehore", "aspataal",
        "and", "the", "of", "dr", "doctor"
    }
    tokens = [t for t in name_clean.split() if t not in stop_words and len(t) > 1]
    return " ".join(tokens)

def is_duplicate_facility(f1_name: str, f1_lat: float, f1_lon: float, f2_name: str, f2_lat: float, f2_lon: float) -> bool:
    """Determine if two facilities represent the same real-world location."""
    dist = haversine_distance(f1_lat, f1_lon, f2_lat, f2_lon)

    # 1. Close proximity (< 40m) -> likely same building/entrance marker
    if dist <= 40:
        return True

    norm1 = normalize_facility_name(f1_name)
    norm2 = normalize_facility_name(f2_name)

    if not norm1 or not norm2:
        return False

    # 2. Exact normalized core name match within 1500m
    if norm1 == norm2 and dist <= 1500:
        return True

    # 3. Substring match or high token overlap within 600m
    tokens1 = set(norm1.split())
    tokens2 = set(norm2.split())
    if tokens1 and tokens2:
        overlap = len(tokens1.intersection(tokens2)) / min(len(tokens1), len(tokens2))
        if overlap >= 0.75 and dist <= 600:
            return True

    return False

def deduplicate_facilities(facilities: List[Any]) -> List[Any]:
    """Deduplicate a list of MedicalFacility objects by spatial proximity and normalized name similarity."""
    unique: List[Any] = []

    for f in facilities:
        matched_idx = -1
        for idx, u in enumerate(unique):
            if is_duplicate_facility(f.name, f.lat, f.lon, u.name, u.lat, u.lon):
                matched_idx = idx
                break

        if matched_idx == -1:
            unique.append(f)
        else:
            existing = unique[matched_idx]
            # Preference logic: keep government, or entry with phone number, or more complete name
            prefer_f = False
            if f.is_government and not existing.is_government:
                prefer_f = True
            elif getattr(f, 'phone', None) and not getattr(existing, 'phone', None):
                prefer_f = True
            elif len(f.name) > len(existing.name) and not (existing.is_government and not f.is_government):
                prefer_f = True

            if prefer_f:
                unique[matched_idx] = f

    return unique
