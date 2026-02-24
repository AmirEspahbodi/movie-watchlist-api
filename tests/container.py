from __future__ import annotations

import os

# ── Provide required env-vars before any ArchiPy config is constructed ──────
os.environ.setdefault("FIRST_SUPERUSER_EMAIL", "superuser@test.com")
# ... (keep all your existing os.environ.setdefault lines here) ...
os.environ.setdefault("POSTGRES_SQLALCHEMY__PORT", "5432")

# ── FIX: Intercept SQLAlchemy engine creation to strip incompatible kwargs ──
# ── FIX: Intercept SQLAlchemy engine creation to strip incompatible kwargs ──
import sqlalchemy.ext.asyncio
from sqlalchemy.pool import StaticPool

_orig_create_async_engine = sqlalchemy.ext.asyncio.create_async_engine


def _safe_create_async_engine(*args, **kwargs):
    url = str(args[0]) if args else str(kwargs.get("url", ""))
    if "sqlite" in url:
        # 1. Strip incompatible PostgreSQL kwargs
        for key in ["pool_size", "pool_timeout", "pool_use_lifo", "max_overflow"]:
            kwargs.pop(key, None)

        # 2. Force StaticPool so the in-memory DB persists across all sessions!
        kwargs["poolclass"] = StaticPool

        # 3. Ensure check_same_thread is False for async compatibility
        connect_args = kwargs.get("connect_args", {})
        connect_args["check_same_thread"] = False
        kwargs["connect_args"] = connect_args

    return _orig_create_async_engine(*args, **kwargs)


sqlalchemy.ext.asyncio.create_async_engine = _safe_create_async_engine


# Apply patch before archipy imports it
sqlalchemy.ext.asyncio.create_async_engine = _safe_create_async_engine

# ── Provide required env-vars before any ArchiPy config is constructed ──────
os.environ.setdefault("FIRST_SUPERUSER_EMAIL", "superuser@test.com")
os.environ.setdefault("FIRST_SUPERUSER_FIRSTNAME", "Super")
os.environ.setdefault("FIRST_SUPERUSER_LASTNAME", "User")
os.environ.setdefault("FIRST_SUPERUSER_USERNAME", "superuser")
os.environ.setdefault("FIRST_SUPERUSER_PASSWORD", "SuperPass123!")
os.environ.setdefault("AUTH__SECRET_KEY", "test-secret-key-for-bdd-tests-only")
os.environ.setdefault("AUTH__HASH_ALGORITHM", "HS256")
os.environ.setdefault("FASTAPI__PROJECT_NAME", "movie_watchlist_api_test")
os.environ.setdefault("FASTAPI__OPENAPI_URL", "/openapi.json")
os.environ.setdefault("FASTAPI__DOCS_URL", "/docs")
# SQLite config – ArchiPy reads these when constructing AsyncSQLiteSQLAlchemyAdapter
os.environ.setdefault("SQLITE_SQLALCHEMY__DATABASE", ":memory:")
os.environ.setdefault("SQLITE_SQLALCHEMY__DRIVER_NAME", "sqlite+aiosqlite")
# Provide stub postgres vars to satisfy pydantic-settings validation on BaseConfig
os.environ.setdefault("POSTGRES_SQLALCHEMY__DATABASE", "test_db")
os.environ.setdefault("POSTGRES_SQLALCHEMY__PASSWORD", "test_password")
os.environ.setdefault("POSTGRES_SQLALCHEMY__USERNAME", "test_user")
os.environ.setdefault("POSTGRES_SQLALCHEMY__DRIVER_NAME", "postgresql+asyncpg")
os.environ.setdefault("POSTGRES_SQLALCHEMY__HOST", "localhost")
os.environ.setdefault("POSTGRES_SQLALCHEMY__PORT", "5432")

from archipy.adapters.sqlite.sqlalchemy.adapters import AsyncSQLiteSQLAlchemyAdapter  # noqa: E402
from archipy.models.entities.sqlalchemy.base_entities import BaseEntity  # noqa: E402
from sqlalchemy import text  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

# Import ALL entity models so they are registered on BaseEntity.metadata
import src.models.entities  # noqa: E402, F401  (side-effect import)
from src.logics.auth.auth_logic import AuthLogic  # noqa: E402
from src.logics.genre.genre_logic import GenreLogic  # noqa: E402
from src.logics.movie.movie_logic import MovieLogic  # noqa: E402
from src.logics.rating.rating_logic import RatingLogic  # noqa: E402
from src.logics.user.user_logic import UserLogic  # noqa: E402
from src.logics.watch.watch_logic import WatchLogic  # noqa: E402
from src.repositories.genre.adapters.genre_postgres_adapter import GenrePostgresAdapter  # noqa: E402
from src.repositories.genre.genre_repository import GenreRepository  # noqa: E402
from src.repositories.movie.adapters.movie_postgres_adapter import MoviePostgresAdapter  # noqa: E402
from src.repositories.movie.movie_repository import MovieRepository  # noqa: E402
from src.repositories.rating.adapters.rating_postgres_adapter import RatingPostgresAdapter  # noqa: E402
from src.repositories.rating.rating_repository import RatingRepository  # noqa: E402
from src.repositories.user.adapters.user_postgres_adapter import UserPostgresAdapter  # noqa: E402
from src.repositories.user.user_repository import UserRepository  # noqa: E402
from src.repositories.watch.adapters.watch_postgres_adapter import WatchPostgresAdapter  # noqa: E402
from src.repositories.watch.watch_repository import WatchRepository  # noqa: E402


def _build_sqlite_adapter() -> AsyncSQLiteSQLAlchemyAdapter:
    return AsyncSQLiteSQLAlchemyAdapter()


class TestServiceContainer:
    """
    Drop-in replacement for ServiceContainer that uses SQLite instead of
    PostgreSQL.  All repositories and logics are wired identically to
    ServiceContainer; only the underlying adapter is different.

    AC-1: Zero modifications to any file under src/.
    AC-4: Mirrors ServiceContainer structure exactly.
    AC-5: Uses sqlite+aiosqlite:///:memory: with StaticPool.
    """

    def __init__(self) -> None:
        # Single shared SQLite adapter – all adapters share the same connection.
        self._sqlite_adapter: AsyncSQLiteSQLAlchemyAdapter = _build_sqlite_adapter()

        # ── User layer ──────────────────────────────────────────────────────
        self._user_sqlite_adapter = UserPostgresAdapter(adapter=self._sqlite_adapter)  # type: ignore[arg-type]
        self._user_repository = UserRepository(postgres_adapter=self._user_sqlite_adapter)
        self._user_logic = UserLogic(repository=self._user_repository)
        self._auth_logic = AuthLogic(user_repository=self._user_repository)

        # ── Genre layer ─────────────────────────────────────────────────────
        self._genre_sqlite_adapter = GenrePostgresAdapter(adapter=self._sqlite_adapter)  # type: ignore[arg-type]
        self._genre_repository = GenreRepository(postgres_adapter=self._genre_sqlite_adapter)
        self._genre_logic = GenreLogic(repository=self._genre_repository)

        # ── Movie layer ─────────────────────────────────────────────────────
        self._movie_sqlite_adapter = MoviePostgresAdapter(adapter=self._sqlite_adapter)  # type: ignore[arg-type]
        self._movie_repository = MovieRepository(postgres_adapter=self._movie_sqlite_adapter)
        self._movie_logic = MovieLogic(repository=self._movie_repository)

        # ── Watch layer ─────────────────────────────────────────────────────
        self._watch_sqlite_adapter = WatchPostgresAdapter(adapter=self._sqlite_adapter)  # type: ignore[arg-type]
        self._watch_repository = WatchRepository(postgres_adapter=self._watch_sqlite_adapter)
        self._watch_logic = WatchLogic(repository=self._watch_repository)

        # ── Rating layer ────────────────────────────────────────────────────
        self._rating_sqlite_adapter = RatingPostgresAdapter(adapter=self._sqlite_adapter)  # type: ignore[arg-type]
        self._rating_repository = RatingRepository(postgres_adapter=self._rating_sqlite_adapter)
        self._rating_logic = RatingLogic(
            repository=self._rating_repository,
            watch_repository=self._watch_repository,
        )

    # ── Public accessors (mirrors ServiceContainer provider attribute names) ─

    def auth_logic(self) -> AuthLogic:
        return self._auth_logic

    def user_logic(self) -> UserLogic:
        return self._user_logic

    def genre_logic(self) -> GenreLogic:
        return self._genre_logic

    def movie_logic(self) -> MovieLogic:
        return self._movie_logic

    def watch_logic(self) -> WatchLogic:
        return self._watch_logic

    def rating_logic(self) -> RatingLogic:
        return self._rating_logic

    def sqlite_adapter(self) -> AsyncSQLiteSQLAlchemyAdapter:
        return self._sqlite_adapter


# ── Schema helpers ───────────────────────────────────────────────────────────


async def create_test_schema(adapter: AsyncSQLiteSQLAlchemyAdapter) -> None:
    """
    Create all tables in the in-memory SQLite database.
    Uses a standard session connection to avoid relying on private ArchiPy engine attributes.
    """
    import src.models.entities  # noqa: F401 – ensures all models are registered

    session = adapter.get_session()
    try:
        conn = await session.connection()
        await conn.run_sync(BaseEntity.metadata.create_all)
        await session.commit()
    finally:
        await session.close()


async def drop_test_schema(adapter: AsyncSQLiteSQLAlchemyAdapter) -> None:
    """Drop all tables from the in-memory SQLite database."""
    session = adapter.get_session()
    try:
        conn = await session.connection()
        await conn.run_sync(BaseEntity.metadata.drop_all)
        await session.commit()
    finally:
        await session.close()


async def clear_all_tables(adapter: AsyncSQLiteSQLAlchemyAdapter) -> None:
    """
    Delete all rows from every table in reverse FK-dependency order:
      user_rate_movie → user_watch_movie → movies → genres → users

    ED-1 NOTE: WatchStatusType is stored as VARCHAR(20); no ENUM migration
    issues exist with SQLite.
    """
    session = adapter.get_session()
    try:
        await session.execute(text("DELETE FROM user_rate_movie"))
        await session.execute(text("DELETE FROM user_watch_movie"))
        await session.execute(text("DELETE FROM movies"))
        await session.execute(text("DELETE FROM genres"))
        await session.execute(text("DELETE FROM users"))
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
