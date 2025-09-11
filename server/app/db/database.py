from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

load_dotenv()

# import .env variable of DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Create async engine of database
engine = create_async_engine(
    DATABASE_URL,
    echo = False, # Logging SQL
    poolclass = NullPool, #disable pool-connection to asyncpg
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    bind = engine,
    expire_on_commit = False,
    autoflush = False
)

Base = declarative_base()

async def get_db():
    # Session generator for FastAPI
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    # database initialization (create tables)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)