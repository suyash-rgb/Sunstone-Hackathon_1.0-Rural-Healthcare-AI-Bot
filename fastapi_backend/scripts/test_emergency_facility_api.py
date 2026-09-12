import asyncio
import sys
import httpx
from app.main import app
from app.db.session import engine, AsyncSession
from app.services.emergency_service import emergency_service

async def test_direct_service():
    print("\n--- 1. Testing EmergencyService directly ---")
    async with AsyncSession(engine) as session:
        # Dhar, Madhya Pradesh coordinates
        lat, lon = 22.605883, 75.320098
        res = await emergency_service.get_nearby_emergency_facilities(
            session=session,
            lat=lat,
            lon=lon,
            radius_km=10.0
        )
        print(f"Total Combined Facilities Found: {res.total_found}")
        print(f"User Location: {res.user_location}")
        print(f"Search Radius: {res.search_radius_km} km\n")

        assert res.total_found > 0, "No facilities found!"

        govt_count = 0
        ext_count = 0

        for idx, fac in enumerate(res.facilities):
            govt_flag = " [GOVT]" if fac.is_government else ""
            print(f"[{idx+1:2d}] Source: {fac.source:15} | Dist: {fac.distance_km:5.2f}km ({fac.distance_meters:6.1f}m) | Name: {fac.facility_name[:35]:35} | Type: {fac.type}{govt_flag}")

            if fac.source == "government_db" or fac.is_government:
                govt_count += 1
            else:
                ext_count += 1

        print(f"\nStats: Government DB = {govt_count}, External (OlaMaps/OSM) = {ext_count}")
        assert govt_count > 0, "Expected government DB results!"
        
        # Verify Top 5 Government Facility Assertion
        top_5 = res.facilities[:5]
        top_5_has_govt = any(f.is_government for f in top_5)
        print(f"Top 5 contains government facility: {top_5_has_govt}")
        assert top_5_has_govt, "FAILED: Top 5 results must contain at least one government facility!"

        print("Direct EmergencyService test PASSED successfully!\n")

async def test_asgi_endpoint():
    print("--- 2. Testing FastAPI Router /api/v1/emergency/facilities/nearby via ASGITransport ---")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        params = {
            "lat": 22.605883,
            "lon": 75.320098,
            "radius_km": 10.0
        }
        resp = await client.get("/api/v1/emergency/facilities/nearby", params=params)
        print(f"HTTP Status: {resp.status_code}")
        assert resp.status_code == 200, f"Router failed: {resp.text}"
        data = resp.json()
        print(f"Endpoint returned {data.get('total_found')} facilities.")
        facilities = data.get("facilities", [])
        if facilities:
            print(f"Top result: {facilities[0]['facility_name']} ({facilities[0]['source']}) at {facilities[0]['distance_km']}km")
            top_5_govt = [f['facility_name'] for f in facilities[:5] if f.get('is_government')]
            print(f"Govt facilities in Top 5: {top_5_govt}")
            assert len(top_5_govt) > 0, "Top 5 must contain at least one government facility!"
        print("FastAPI ASGITransport Router test PASSED successfully!")

async def main():
    await test_direct_service()
    await test_asgi_endpoint()

if __name__ == '__main__':
    asyncio.run(main())
