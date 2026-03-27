import ssl as _ssl

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# For remote databases (Supabase, etc.), enable SSL
connect_args = {}
if "localhost" not in settings.database_url and "127.0.0.1" not in settings.database_url:
    ssl_ctx = _ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = _ssl.CERT_NONE
    connect_args["ssl"] = ssl_ctx

# Strip sslmode param if present (asyncpg doesn't support it in URL)
db_url = settings.database_url.split("?")[0] if "sslmode" in settings.database_url else settings.database_url

# Supabase pooler (pgbouncer) doesn't support prepared statements
if "pooler.supabase.com" in db_url or ":6543" in db_url:
    connect_args["statement_cache_size"] = 0
    connect_args["prepared_statement_cache_size"] = 0

engine = create_async_engine(db_url, echo=False, connect_args=connect_args)
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
