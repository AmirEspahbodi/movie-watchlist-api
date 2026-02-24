from __future__ import annotations

import archipy.helpers.decorators.sqlalchemy_atomic as _atomic_module


def _async_noop_decorator(func):  # type: ignore[no-untyped-def]
    """Passthrough replacement for async_postgres_sqlalchemy_atomic_decorator."""
    return func


_atomic_module.async_postgres_sqlalchemy_atomic_decorator = _async_noop_decorator  # type: ignore[attr-defined]

# ── Standard library imports (after the patch) ───────────────────────────────
import asyncio


# ── Helper available to step files ───────────────────────────────────────────

def run(context, coro):  # type: ignore[no-untyped-def]
    """
    Run an async coroutine synchronously using the shared event loop stored on
    the behave context object.

    Step files import this helper:
        from features.environment import run
    """
    return context.loop.run_until_complete(coro)


# ── Behave lifecycle hooks ────────────────────────────────────────────────────

def before_all(context) -> None:  # type: ignore[no-untyped-def]
    """
    1. Create a new asyncio event loop and store it as context.loop.
    2. Set BaseConfig global to TestRuntimeConfig (SQLite config).
    3. Instantiate TestServiceContainer and store as context.container.
    4. Create the SQLite schema (all tables).
    5. Store frequently used Logic instances as convenience attributes.
    """
    # Step 1 – event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    context.loop = loop

    # Step 2 – runtime config
    # Environment variables are set inside tests/container.py at import time,
    # which happens below.  We import the config and set it as global AFTER
    # the env vars are exported.
    from src.configs.runtime_config import RuntimeConfig
    from archipy.configs.base_config import BaseConfig

    # RuntimeConfig() reads env-vars set by tests/container.py (imported next).
    # We delay this import so the env-var setup in container.py runs first.
    import tests.container as _tc_module  # noqa: F401 – triggers os.environ.setdefault calls

    test_config = RuntimeConfig()
    BaseConfig.set_global(test_config)

    # Step 3 – container
    from tests.container import TestServiceContainer, create_test_schema

    container = TestServiceContainer()
    context.container = container

    # Step 4 – schema
    loop.run_until_complete(create_test_schema(container.sqlite_adapter()))

    # Step 5 – convenience attributes
    context.auth_logic = container.auth_logic()
    context.user_logic = container.user_logic()
    context.genre_logic = container.genre_logic()
    context.movie_logic = container.movie_logic()
    context.watch_logic = container.watch_logic()
    context.rating_logic = container.rating_logic()


def after_all(context) -> None:  # type: ignore[no-untyped-def]
    """
    1. Drop the SQLite schema (if initialized).
    2. Close and clean up the event loop (if initialized).
    """
    if hasattr(context, "container") and hasattr(context, "loop"):
        from tests.container import drop_test_schema
        context.loop.run_until_complete(drop_test_schema(context.container.sqlite_adapter()))

    if hasattr(context, "loop") and context.loop is not None:
        context.loop.close()
        asyncio.set_event_loop(None)

def before_scenario(context, scenario) -> None:  # type: ignore[no-untyped-def]
    """
    1. Clear all table rows (fast truncation pattern for test isolation).
    2. Reset per-scenario context state.
    """
    from tests.container import clear_all_tables

    context.loop.run_until_complete(clear_all_tables(context.container.sqlite_adapter()))

    # Reset per-scenario state
    context.current_user_uuid = None
    context.current_access_token = None
    context.current_refresh_token = None
    context.last_error = None
    context.last_result = None

    # User tracking dicts
    context.users = {}            # email → user_uuid
    context.user_passwords = {}   # email → plaintext password (for re-login)

    # Domain entity tracking dicts
    context.genres = {}    # genre_name → genre_uuid
    context.movies = {}    # title → movie_uuid
    context.watches = {}   # (str(user_uuid), title) → watch_uuid
    context.ratings = {}   # (str(user_uuid), title) → rate_uuid

    # Convenience tracking
    context.last_genre_name = None


def after_scenario(context, scenario) -> None:  # type: ignore[no-untyped-def]
    """
    No-op.  Table cleanup is performed in before_scenario for simplicity.
    This hook exists for future extension (e.g. screenshots on failure).
    """
