import asyncio
import os
import sys
import time
import pandas as pd
from pathlib import Path
from sqlalchemy import text

backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.session import engine, AsyncSessionLocal
from app.db.base import Base
from app.db.models.healthcare_facility import HealthcareFacility

CLEANED_DATASET_PATH = os.path.join(backend_dir, "datasets", "cleaned_nin_health_facilities.csv")

def clean_val(val):
    if pd.isna(val) or val is None:
        return None
    s = str(val).strip()
    return s if s else None

def clean_pin(val):
    if pd.isna(val) or val is None:
        return None
    v = str(val).strip()
    if v.endswith('.0'):
        v = v[:-2]
    if '.' in v:
        v = v.split('.')[0]
    return v if len(v) == 6 and v.isdigit() else None

def clean_float(val):
    if pd.isna(val) or val is None:
        return None
    try:
        return float(val)
    except Exception:
        return None

def clean_int(val):
    if pd.isna(val) or val is None:
        return None
    try:
        return int(float(val))
    except Exception:
        return None

async def seed_facilities():
    print(f"Loading cleaned dataset from {CLEANED_DATASET_PATH}...")
    df = pd.read_csv(CLEANED_DATASET_PATH, encoding='utf-8', low_memory=False, dtype={'pincode': str})
    total_rows = len(df)
    print(f"Total rows to seed: {total_rows}")

    # Create tables if not exists
    async with engine.begin() as conn:
        print("Ensuring database tables exist...")
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        print("Clearing existing healthcare_facilities records...")
        await session.execute(text("TRUNCATE TABLE healthcare_facilities RESTART IDENTITY CASCADE;"))
        await session.commit()

        start_time = time.time()
        batch_size = 5000
        records = []
        inserted_count = 0

        for idx, row in df.iterrows():
            facility = HealthcareFacility(
                sr_no=clean_int(row.get("SrNo")),
                facility_name=clean_val(row.get("Health Facility Name")) or "Unknown Health Facility",
                address=clean_val(row.get("Address")),
                street=clean_val(row.get("street")),
                landmark=clean_val(row.get("landmark")),
                locality=clean_val(row.get("locality")),
                pincode=clean_pin(row.get("pincode")),
                landline_number=clean_val(row.get("landline_number")),
                latitude=clean_float(row.get("latitude")),
                longitude=clean_float(row.get("longitude")),
                facility_type=clean_val(row.get("Facility Type")) or "Unknown",
                tier_level=clean_val(row.get("tier_level")) or "4_specialized",
                state_name=clean_val(row.get("State_Name")) or "Unknown",
                district_name=clean_val(row.get("District_Name")) or "Unknown",
                taluka_name=clean_val(row.get("Taluka_Name")),
                block_name=clean_val(row.get("Block_Name"))
            )
            records.append(facility)

            if len(records) >= batch_size:
                session.add_all(records)
                await session.commit()
                inserted_count += len(records)
                print(f"Inserted {inserted_count} / {total_rows} records ({inserted_count/total_rows*100:.1f}%)...")
                records = []

        if records:
            session.add_all(records)
            await session.commit()
            inserted_count += len(records)

        elapsed = time.time() - start_time
        print(f"Successfully seeded {inserted_count} healthcare facilities into PostgreSQL in {elapsed:.2f} seconds!")

if __name__ == "__main__":
    asyncio.run(seed_facilities())
