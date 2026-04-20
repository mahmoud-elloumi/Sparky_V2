from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config import settings

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Create all tables if they don't exist yet (safe to call multiple times)."""
    # Import ORM models so Base.metadata is populated
    import orm_models  # noqa: F401
    from sqlalchemy import text

    async with engine.begin() as conn:
        # Ensure required PostgreSQL extensions exist
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "pg_trgm"'))

        # Create ENUM types (ignore if already exist)
        await conn.execute(text("""
            DO $$ BEGIN
                CREATE TYPE document_type AS ENUM
                    ('facture','bon_livraison','bon_commande','avoir','devis');
            EXCEPTION WHEN duplicate_object THEN NULL;
            END $$
        """))
        await conn.execute(text("""
            DO $$ BEGIN
                CREATE TYPE document_status AS ENUM
                    ('pending','classified','extracted','error');
            EXCEPTION WHEN duplicate_object THEN NULL;
            END $$
        """))
        await conn.execute(text("""
            DO $$ BEGIN
                CREATE TYPE mouvement_type AS ENUM
                    ('entree','sortie','correction');
            EXCEPTION WHEN duplicate_object THEN NULL;
            END $$
        """))

        # Create all ORM-mapped tables
        await conn.run_sync(Base.metadata.create_all)
