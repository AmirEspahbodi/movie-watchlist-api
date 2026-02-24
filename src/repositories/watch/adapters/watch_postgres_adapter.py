# src/repositories/watch/adapters/watch_postgres_adapter.py
from archipy.adapters.base.sqlalchemy.adapters import SQLAlchemyFilterMixin
from archipy.adapters.base.sqlalchemy.ports import AsyncSQLAlchemyPort
from archipy.adapters.postgres.sqlalchemy.adapters import AsyncPostgresSQLAlchemyAdapter
from archipy.models.errors import AlreadyExistsError, InvalidArgumentError, NotFoundError
from sqlalchemy import asc, delete, desc, func, select, update as sa_update
from sqlalchemy.exc import IntegrityError

from src.models.dtos.watch.repository.watch_repository_interface_dtos import (
    CheckWatchExistsQueryDTO,
    CreateWatchCommandDTO,
    CreateWatchResponseDTO,
    DeleteWatchCommandDTO,
    GetMovieWatchersQueryDTO,
    GetMovieWatchersResponseDTO,
    GetUserWatchHistoryQueryDTO,
    GetUserWatchHistoryResponseDTO,
    UpdateWatchStatusCommandDTO,
    WatchedMovieItemDTO,
    WatcherUserItemDTO,
)
from src.models.entities.movie_entity import MovieEntity
from src.models.entities.user_entity import UserEntity
from src.models.entities.user_watch_movie_entity import UserWatchMovieEntity
from src.models.types.watch_status_type import WatchStatusType


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
        # model_dump() yields the string value for WatchStatusType (it's a str-enum),
        # which matches the VARCHAR column directly.
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

        # Optional status filter
        if input_dto.status_filter is not None:
            base_query = base_query.where(UserWatchMovieEntity.status == input_dto.status_filter.value)

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
                status=row.UserWatchMovieEntity.status,
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

        # Optional status filter
        if input_dto.status_filter is not None:
            base_query = base_query.where(UserWatchMovieEntity.status == input_dto.status_filter.value)

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
                status=row.UserWatchMovieEntity.status,
                watched_at=row.UserWatchMovieEntity.created_at,
            )
            for row in rows
        ]

        return GetMovieWatchersResponseDTO(watchers=watchers, total=total)

    async def update_watch_status(self, input_dto: UpdateWatchStatusCommandDTO) -> None:
        # Fetch first to distinguish "not found" from an invalid transition.
        select_query = select(UserWatchMovieEntity).where(
            UserWatchMovieEntity.watch_uuid == input_dto.watch_uuid,
            UserWatchMovieEntity.user_uuid == input_dto.user_uuid,
        )
        fetch_result = await self._adapter.execute(statement=select_query)
        watch = fetch_result.scalar()

        if watch is None:
            raise NotFoundError(resource_type=UserWatchMovieEntity.__name__)

        # Guard: only the forward transition want_to_watch → watched is permitted.
        if watch.status != WatchStatusType.WANT_TO_WATCH.value:
            raise InvalidArgumentError()

        stmt = (
            sa_update(UserWatchMovieEntity)
            .where(UserWatchMovieEntity.watch_uuid == input_dto.watch_uuid)
            .where(UserWatchMovieEntity.user_uuid == input_dto.user_uuid)
            .values(status=input_dto.status.value)
        )
        await self._adapter.execute(statement=stmt)

    async def delete_watch(self, input_dto: DeleteWatchCommandDTO) -> None:
        # Fetch first to distinguish "not found" from "wrong status".
        select_query = select(UserWatchMovieEntity).where(
            UserWatchMovieEntity.user_uuid == input_dto.user_uuid,
            UserWatchMovieEntity.movie_uuid == input_dto.movie_uuid,
        )
        fetch_result = await self._adapter.execute(statement=select_query)
        watch = fetch_result.scalar()

        if watch is None:
            raise NotFoundError(resource_type=UserWatchMovieEntity.__name__)

        # Guard: deletion is only permitted while the entry is still "want_to_watch".
        if watch.status != WatchStatusType.WANT_TO_WATCH.value:
            raise InvalidArgumentError()

        delete_query = delete(UserWatchMovieEntity).where(
            UserWatchMovieEntity.user_uuid == input_dto.user_uuid,
            UserWatchMovieEntity.movie_uuid == input_dto.movie_uuid,
        )
        await self._adapter.execute(statement=delete_query)
