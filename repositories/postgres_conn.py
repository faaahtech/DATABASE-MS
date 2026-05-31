from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import URL
from config.setting import Settings 


url_object = URL.create(
    Settings.DATABASE_DRIVER_NAME,
    username=Settings.POSTGRES_ADMIN_USER,
    password=Settings.POSTGRES_ADMIN_PASSWORD,
    host=Settings.POSTGRES_HOST,
    database=Settings.POSTGRES_DATABASE
)

engine = create_async_engine(
    url= url_object,
    echo=False,
    pool_size=5, 
    max_overflow=5, # number of extra connections when all pools are locked
    pool_timeout=10, # connection be close after ten seconds when all pools are locked
    pool_recycle=1800, 
    pool_pre_ping=True,

)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise

session = get_session()
