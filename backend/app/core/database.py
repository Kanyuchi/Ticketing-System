from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Strip sslmode param if present in URL (handled by driver automatically)
db_url = settings.database_url.split("?")[0] if "sslmode" in settings.database_url else settings.database_url

# Use NullPool for external poolers (pgbouncer), standard pool for local
is_pooler = "pooler.supabase.com" in db_url or ":6543" in db_url
pool_kwargs = {"poolclass": NullPool} if is_pooler else {}

engine = create_async_engine(db_url, echo=False, **pool_kwargs)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
