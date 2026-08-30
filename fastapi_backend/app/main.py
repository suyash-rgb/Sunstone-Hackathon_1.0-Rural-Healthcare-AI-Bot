import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select

# Import database components - THESE IMPORTS ARE NOW RESOLVED
from app.db.base import Base, User  
from app.db.session import engine, get_session 
from app.api.vision import router as vision_router 

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FastAPI Lifespan Function (Startup/Shutdown Handler) ---

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Handles startup (DB connection check, table creation) and shutdown events."""
    
#     logger.info("Application startup: Starting database initialization...")

#     try:
#         # **STARTUP LOGIC: Check connection and create tables**
#         async with engine.begin() as conn:
#             # Creates tables based on models defined in app.db.base (if they don't exist)
#             await conn.run_sync(Base.metadata.create_all) 
            
#         # Simple connection test query
#         async with engine.connect() as conn:
#              result = await conn.execute(text("SELECT 'connection alive'"))
#              logger.info(f"DB check result: {result.scalar_one()}")
            
#         logger.info("Database connection verified and tables created successfully!")
        
#     except Exception as e:
#         logger.error(f"FATAL ERROR: Database connection or table creation failed: {e}")
#         # Stop the server if the database is unreachable
#         raise RuntimeError("Failed to initialize database on startup.") from e

#     yield # The application is ready to serve requests

#     # **SHUTDOWN LOGIC (runs when Uvicorn stops)**
#     logger.info("Application shutdown complete.")

# --- FastAPI App Initialization ---

app = FastAPI(
    # lifespan=lifespan,
    title="FastAPI & SQLAlchemy Async Backend"
)

# Register routers
app.include_router(vision_router, prefix="/api/v1")

# Define the session type alias for clearer type hints
SessionDep = Annotated[AsyncSession, Depends(get_session)]

# --- Test Endpoints ---
@app.get("/" , tags=["Health Check"])
async def root():
    return {
        "message": "Welcome to the ArogyaMitra Servers"
    }

@app.get("/db-status", tags=["Health Check"])
async def check_db_connection(session: SessionDep):
    """Tests the dependency injection and runs a simple query."""
    try:
        # Run a query to confirm the session is usable
        user_count = await session.scalar(select(User).count_rows())
        
        return {
            "status": "Success", 
            "message": "Database connection and session are functional.",
            "user_count": user_count
        }
    
    except Exception as e:
        logger.error(f"Endpoint DB check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database operational check failed: {e}")