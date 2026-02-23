from archipy.adapters.base.sqlalchemy.adapters import SQLAlchemyFilterMixin
from archipy.adapters.base.sqlalchemy.ports import AsyncSQLAlchemyPort
from archipy.adapters.postgres.sqlalchemy.adapters import AsyncPostgresSQLAlchemyAdapter
from archipy.models.errors import AlreadyExistsError
from sqlalchemy import asc, desc, func, select
from sqlalchemy.exc import IntegrityError

from src.models.dtos.watch.repository.watch_repository_interface_dtos import (
    CheckWatchExistsQueryDTO,
    CreateWatchCommandDTO,
    CreateWatchResponseDTO,
    GetMovieWatchersQueryDTO,
    GetMovieWatchersResponseDTO,
    GetUserWatchHistoryQueryDTO,
    GetUserWatchHistoryResponseDTO,
    WatchedMovieItemDTO,
    WatcherUserItemDTO,
)
from src.models.entities.movie_entity import MovieEntity
from src.models.entities.user_entity import UserEntity
from src.models.entities.user_watch_movie_entity import UserWatchMovieEntity


class WatchPostgresAdapter(SQLAlchemyFilterMixin):
    def __init__(self, adapter: AsyncPostgresSQLAlchemyAdapter) -> None:
        self._adapter: AsyncSQLAlchemyPort = adapter

    async def check_watch_exists(self, input_dto: CheckWatchExistsQueryDTO) -> bool:
        select_query = select(UserWatchMovieEntity).where(
            UserWatchMovieEntity.user_uuid == input_dto.user_uuid,
            UserWatchMovieEntity.movie_uuid == input_dto.movie_uuid,
        )
        result = await self._adapter.execute(statement=select_query)
        return result.scalar() is not None

    async def create_watch(self, input_dto: CreateWatchCommandDTO) -> CreateWatchResponseDTO:
        watch: UserWatchMovieEntity = UserWatchMovieEntity(**input_dto.model_dump())
        try:
            result = await self._adapter.create(entity=watch)
            return CreateWatchResponseDTO.model_validate(obj=result)
        except IntegrityError as exc:
            raise AlreadyExistsError(resource_type=UserWatchMovieEntity.__name__) from exc

    async def get_user_watch_history(
        self,
        input_dto: GetUserWatchHistoryQueryDTO,
    ) -> GetUserWatchHistoryResponseDTO:
        base_query = (
            select(UserWatchMovieEntity, MovieEntity)
            .join(MovieEntity, UserWatchMovieEntity.movie_uuid == MovieEntity.movie_uuid)
            .where(UserWatchMovieEntity.user_uuid == input_dto.user_uuid)
        )

        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self._adapter.execute(statement=count_query)
        total = count_result.scalar() or 0

        order_fn = desc if input_dto.sort_info.order.value.lower() == "desc" else asc
        page = input_dto.pagination.page
        page_size = input_dto.pagination.page_size
        offset = (page - 1) * page_size

        data_query = base_query.order_by(order_fn(UserWatchMovieEntity.created_at)).limit(page_size).offset(offset)
        data_result = await self._adapter.execute(statement=data_query)
        rows = data_result.all()

        watches = [
            WatchedMovieItemDTO(
                watch_uuid=row.UserWatchMovieEntity.watch_uuid,
                movie_uuid=row.MovieEntity.movie_uuid,
                title=row.MovieEntity.title,
                description=row.MovieEntity.description,
                genre_uuid=row.MovieEntity.genre_uuid,
                watched_at=row.UserWatchMovieEntity.created_at,
            )
            for row in rows
        ]

        return GetUserWatchHistoryResponseDTO(watches=watches, total=total)

    async def get_movie_watchers(
        self,
        input_dto: GetMovieWatchersQueryDTO,
    ) -> GetMovieWatchersResponseDTO:
        base_query = (
            select(UserWatchMovieEntity, UserEntity)
            .join(UserEntity, UserWatchMovieEntity.user_uuid == UserEntity.user_uuid)
            .where(UserWatchMovieEntity.movie_uuid == input_dto.movie_uuid)
        )

        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self._adapter.execute(statement=count_query)
        total = count_result.scalar() or 0

        order_fn = desc if input_dto.sort_info.order.value.lower() == "descending" else asc
        page = input_dto.pagination.page
        page_size = input_dto.pagination.page_size
        offset = (page - 1) * page_size

        data_query = base_query.order_by(order_fn(UserWatchMovieEntity.created_at)).limit(page_size).offset(offset)
        data_result = await self._adapter.execute(statement=data_query)
        rows = data_result.all()

        watchers = [
            WatcherUserItemDTO(
                watch_uuid=row.UserWatchMovieEntity.watch_uuid,
                user_uuid=row.UserEntity.user_uuid,
                first_name=row.UserEntity.first_name,
                last_name=row.UserEntity.last_name,
                email=row.UserEntity.email,
                watched_at=row.UserWatchMovieEntity.created_at,
            )
            for row in rows
        ]

        return GetMovieWatchersResponseDTO(watchers=watchers, total=total)
