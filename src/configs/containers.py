from archipy.adapters.postgres.sqlalchemy.adapters import AsyncPostgresSQLAlchemyAdapter
from dependency_injector import containers, providers

from src.configs.runtime_config import RuntimeConfig
from src.logics.auth.auth_logic import AuthLogic
from src.logics.genre.genre_logic import GenreLogic
from src.logics.movie.movie_logic import MovieLogic
from src.logics.rating.rating_logic import RatingLogic
from src.logics.user.user_logic import UserLogic
from src.logics.watch.watch_logic import WatchLogic
from src.repositories.genre.adapters.genre_postgres_adapter import GenrePostgresAdapter
from src.repositories.genre.genre_repository import GenreRepository
from src.repositories.movie.adapters.movie_postgres_adapter import MoviePostgresAdapter
from src.repositories.movie.movie_repository import MovieRepository
from src.repositories.rating.adapters.rating_postgres_adapter import RatingPostgresAdapter
from src.repositories.rating.rating_repository import RatingRepository
from src.repositories.user.adapters.user_postgres_adapter import UserPostgresAdapter
from src.repositories.user.user_repository import UserRepository
from src.repositories.watch.adapters.watch_postgres_adapter import WatchPostgresAdapter
from src.repositories.watch.watch_repository import WatchRepository


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

    _movie_postgres_adapter = providers.ThreadSafeSingleton(
        MoviePostgresAdapter,
        adapter=_postgres_adapter,
    )
    _movie_repository = providers.ThreadSafeSingleton(
        MovieRepository,
        postgres_adapter=_movie_postgres_adapter,
    )
    movie_logic = providers.ThreadSafeSingleton(
        MovieLogic,
        repository=_movie_repository,
    )

    _watch_postgres_adapter = providers.ThreadSafeSingleton(
        WatchPostgresAdapter,
        adapter=_postgres_adapter,
    )
    _watch_repository = providers.ThreadSafeSingleton(
        WatchRepository,
        postgres_adapter=_watch_postgres_adapter,
    )
    watch_logic = providers.ThreadSafeSingleton(
        WatchLogic,
        repository=_watch_repository,
    )

    _rating_postgres_adapter = providers.ThreadSafeSingleton(
        RatingPostgresAdapter,
        adapter=_postgres_adapter,
    )
    _rating_repository = providers.ThreadSafeSingleton(
        RatingRepository,
        postgres_adapter=_rating_postgres_adapter,
    )
    rating_logic = providers.ThreadSafeSingleton(
        RatingLogic,
        repository=_rating_repository,
    )
