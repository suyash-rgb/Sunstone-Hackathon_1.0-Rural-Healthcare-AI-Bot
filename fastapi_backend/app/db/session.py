import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Format: postgresql+asyncpg://<user>:<password>@<host>:<port>/<dbname>
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql+asyncpg://postgres:root@localhost:5432/arogyamitra_db" 
)

# Create the asynchronous database engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
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
