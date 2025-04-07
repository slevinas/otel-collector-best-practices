from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5435/postgres"
DATABASE_URL = "postgresql+asyncpg://xplg_user:xplg_pass@localhost:5435/xplg_db"


engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
