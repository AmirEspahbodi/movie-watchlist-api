from archipy.adapters.postgres.sqlalchemy.adapters import AsyncPostgresSQLAlchemyAdapter
from dependency_injector import containers, providers

from src.configs.runtime_config import RuntimeConfig
from src.logics.auth.auth_logic import AuthLogic
from src.logics.genre.genre_logic import GenreLogic
from src.logics.user.user_logic import UserLogic
from src.repositories.genre.adapters.genre_postgres_adapter import GenrePostgresAdapter
from src.repositories.genre.genre_repository import GenreRepository
from src.repositories.user.adapters.user_postgres_adapter import UserPostgresAdapter
from src.repositories.user.user_repository import UserRepository


class ServiceContainer(containers.DeclarativeContainer):
    _config: RuntimeConfig = RuntimeConfig.global_config()
    _postgres_adapter: AsyncPostgresSQLAlchemyAdapter = providers.ThreadSafeSingleton(AsyncPostgresSQLAlchemyAdapter)

    _user_postgres_adapter = providers.ThreadSafeSingleton(
        UserPostgresAdapter,
        adapter=_postgres_adapter,
    )
    _user_repository = providers.ThreadSafeSingleton(
        UserRepository,
        postgres_adapter=_user_postgres_adapter,
    )
    user_logic = providers.ThreadSafeSingleton(
        UserLogic,
        repository=_user_repository,
    )
    auth_logic = providers.ThreadSafeSingleton(
        AuthLogic,
        user_repository=_user_repository,
    )

    _genre_postgres_adapter = providers.ThreadSafeSingleton(
        GenrePostgresAdapter,
        adapter=_postgres_adapter,
    )
    _genre_repository = providers.ThreadSafeSingleton(
        GenreRepository,
        postgres_adapter=_genre_postgres_adapter,
    )
    genre_logic = providers.ThreadSafeSingleton(
        GenreLogic,
        repository=_genre_repository,
    )
