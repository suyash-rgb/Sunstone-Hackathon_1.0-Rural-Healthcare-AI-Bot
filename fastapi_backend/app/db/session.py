import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# --- Configuration for Local MySQL ---
# The driver is now 'mysql+asyncmy' (Make sure you installed 'asyncmy')
# Format: mysql+asyncmy://<user>:<password>@<host>:<port>/<dbname>
# Default port is 3306.
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "mysql+asyncmy://root:root@localhost:3306/rural_healthcare_ai_bot_db" 
)

# Create the asynchronous database engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Keep true for initial debugging, set to False later
    future=True 
)

# Create a factory for new AsyncSession objects
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    autoflush=False, 
    expire_on_commit=False, 
    class_=AsyncSession
)

# Dependency function to get a database session
async def get_session():
    """Provides a transactional database session using yield."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()