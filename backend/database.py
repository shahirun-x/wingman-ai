from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# Get the URL
raw_url = os.getenv("DATABASE_URL")

if not raw_url:
    raise ValueError("❌ DATABASE_URL is missing! Check your .env file.")

# --- THE FIX: Force asyncpg and handle SSL correctly ---

# 1. Correct the driver prefix
if raw_url.startswith("postgres://"):
    DATABASE_URL = raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif raw_url.startswith("postgresql://"):
    DATABASE_URL = raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    DATABASE_URL = raw_url

# 2. Remove '?sslmode=require' from the string (asyncpg hates it there)
if "?" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.split("?")[0]

# 3. Create the engine with explicit SSL argument
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    # This tells asyncpg to connect securely to Neon
    connect_args={"ssl": "require"} 
)

# 4. Create the Session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 5. Base class for our tables
Base = declarative_base()

# Dependency to get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session