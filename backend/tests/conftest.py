import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models.admin_user import AdminUser
from app.models.ticket_type import TicketCategory, TicketType

TEST_DB_URL = "sqlite+aiosqlite://"  # in-memory


@pytest_asyncio.fixture
async def engine():
    eng = create_async_engine(TEST_DB_URL, echo=False)

    # SQLite UUID compat: store as hex strings
    @event.listens_for(eng.sync_engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, _):
        dbapi_conn.execute("PRAGMA journal_mode=WAL")

    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(engine):
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def seed_data(db_session: AsyncSession):
    """Seed ticket types and admin user for tests."""
    general = TicketType(
        id=uuid.uuid4(),
        name="General Pass",
        category=TicketCategory.GENERAL,
        price_eur=119900,
        sort_order=1,
    )
    speaker = TicketType(
        id=uuid.uuid4(),
        name="Speaker Pass",
        category=TicketCategory.SPEAKER,
        price_eur=0,
        is_complimentary=True,
        sort_order=2,
    )
    admin = AdminUser(
        id=uuid.uuid4(),
        email="test@admin.com",
        hashed_password=hash_password("testpass"),
        name="Test Admin",
    )
    db_session.add_all([general, speaker, admin])
    await db_session.commit()
    return {"general": general, "speaker": speaker, "admin": admin}
