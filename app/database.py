from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./recipe.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,  # Логирование SQL-запросов
    future=True,
    poolclass=NullPool,
    connect_args={"check_same_thread": False}
)

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

