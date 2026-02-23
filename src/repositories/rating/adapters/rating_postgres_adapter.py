from archipy.adapters.base.sqlalchemy.adapters import SQLAlchemyFilterMixin
from archipy.adapters.base.sqlalchemy.ports import AsyncSQLAlchemyPort
from archipy.adapters.postgres.sqlalchemy.adapters import AsyncPostgresSQLAlchemyAdapter
from archipy.models.errors import AlreadyExistsError, NotFoundError
from sqlalchemy import asc, desc, func, select, update
from sqlalchemy.exc import IntegrityError

from src.models.dtos.rating.repository.rating_repository_interface_dtos import (
    CheckRatingExistsQueryDTO,
    CreateRatingCommandDTO,
    CreateRatingResponseDTO,
    GetMovieRatersQueryDTO,
    GetMovieRatersResponseDTO,
    GetMyRatingsQueryDTO,
    GetMyRatingsResponseDTO,
    GetUserRatingsQueryDTO,
    GetUserRatingsResponseDTO,
    RatedMovieItemDTO,
    RaterUserItemDTO,
    UpdateRatingCommandDTO,
)
from src.models.entities.movie_entity import MovieEntity
from src.models.entities.user_entity import UserEntity
from src.models.entities.user_rate_movie_entity import UserRateMovieEntity
from src.models.types.rating_sort_type import RatingSortColumnType


class RatingPostgresAdapter(SQLAlchemyFilterMixin):
    def __init__(self, adapter: AsyncPostgresSQLAlchemyAdapter) -> None:
        self._adapter: AsyncSQLAlchemyPort = adapter

    async def check_rating_exists(self, input_dto: CheckRatingExistsQueryDTO) -> bool:
        select_query = select(UserRateMovieEntity).where(
            UserRateMovieEntity.user_uuid == input_dto.user_uuid,
            UserRateMovieEntity.movie_uuid == input_dto.movie_uuid,
        )
        result = await self._adapter.execute(statement=select_query)
        return result.scalar() is not None

    async def create_rating(self, input_dto: CreateRatingCommandDTO) -> CreateRatingResponseDTO:
        rating: UserRateMovieEntity = UserRateMovieEntity(**input_dto.model_dump())
        try:
            result = await self._adapter.create(entity=rating)
            return CreateRatingResponseDTO.model_validate(obj=result)
        except IntegrityError as exc:
            raise AlreadyExistsError(resource_type=UserRateMovieEntity.__name__) from exc

    async def update_rating(self, input_dto: UpdateRatingCommandDTO) -> None:
        update_query = (
            update(UserRateMovieEntity)
            .where(UserRateMovieEntity.rate_uuid == input_dto.rate_uuid)
            .where(UserRateMovieEntity.user_uuid == input_dto.user_uuid)
            .values(score=input_dto.score)
        )
        result = await self._adapter.execute(statement=update_query)
        if result.rowcount == 0:
            raise NotFoundError(resource_type=UserRateMovieEntity.__name__)

    async def get_my_ratings(self, input_dto: GetMyRatingsQueryDTO) -> GetMyRatingsResponseDTO:
        base_query = (
            select(UserRateMovieEntity, MovieEntity)
            .join(MovieEntity, UserRateMovieEntity.movie_uuid == MovieEntity.movie_uuid)
            .where(UserRateMovieEntity.user_uuid == input_dto.user_uuid)
        )

        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self._adapter.execute(statement=count_query)
        total = count_result.scalar() or 0

        order_fn = desc if input_dto.sort_info.order.value.lower() == "desc" else asc
        sort_column = input_dto.sort_info.column
        sort_field = (
            UserRateMovieEntity.score if sort_column == RatingSortColumnType.SCORE else UserRateMovieEntity.created_at
        )

        page = input_dto.pagination.page
        page_size = input_dto.pagination.page_size
        offset = (page - 1) * page_size

        data_query = base_query.order_by(order_fn(sort_field)).limit(page_size).offset(offset)
        data_result = await self._adapter.execute(statement=data_query)
        rows = data_result.all()

        ratings = [
            RatedMovieItemDTO(
                rate_uuid=row.UserRateMovieEntity.rate_uuid,
                movie_uuid=row.MovieEntity.movie_uuid,
                title=row.MovieEntity.title,
                description=row.MovieEntity.description,
                genre_uuid=row.MovieEntity.genre_uuid,
                score=row.UserRateMovieEntity.score,
                rated_at=row.UserRateMovieEntity.created_at,
            )
            for row in rows
        ]

        return GetMyRatingsResponseDTO(ratings=ratings, total=total)

    async def get_user_ratings(self, input_dto: GetUserRatingsQueryDTO) -> GetUserRatingsResponseDTO:
        base_query = (
            select(UserRateMovieEntity, MovieEntity)
            .join(MovieEntity, UserRateMovieEntity.movie_uuid == MovieEntity.movie_uuid)
            .where(UserRateMovieEntity.user_uuid == input_dto.user_uuid)
        )

        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self._adapter.execute(statement=count_query)
        total = count_result.scalar() or 0

        order_fn = desc if input_dto.sort_info.order.value.lower() == "desc" else asc
        sort_column = input_dto.sort_info.column
        sort_field = (
            UserRateMovieEntity.score if sort_column == RatingSortColumnType.SCORE else UserRateMovieEntity.created_at
        )

        page = input_dto.pagination.page
        page_size = input_dto.pagination.page_size
        offset = (page - 1) * page_size

        data_query = base_query.order_by(order_fn(sort_field)).limit(page_size).offset(offset)
        data_result = await self._adapter.execute(statement=data_query)
        rows = data_result.all()

        ratings = [
            RatedMovieItemDTO(
                rate_uuid=row.UserRateMovieEntity.rate_uuid,
                movie_uuid=row.MovieEntity.movie_uuid,
                title=row.MovieEntity.title,
                description=row.MovieEntity.description,
                genre_uuid=row.MovieEntity.genre_uuid,
                score=row.UserRateMovieEntity.score,
                rated_at=row.UserRateMovieEntity.created_at,
            )
            for row in rows
        ]

        return GetUserRatingsResponseDTO(ratings=ratings, total=total)

    async def get_movie_raters(self, input_dto: GetMovieRatersQueryDTO) -> GetMovieRatersResponseDTO:
        base_query = (
            select(UserRateMovieEntity, UserEntity)
            .join(UserEntity, UserRateMovieEntity.user_uuid == UserEntity.user_uuid)
            .where(UserRateMovieEntity.movie_uuid == input_dto.movie_uuid)
        )

        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self._adapter.execute(statement=count_query)
        total = count_result.scalar() or 0

        order_fn = desc if input_dto.sort_info.order.value.lower() == "desc" else asc
        sort_column = input_dto.sort_info.column
        sort_field = (
            UserRateMovieEntity.score if sort_column == RatingSortColumnType.SCORE else UserRateMovieEntity.created_at
        )

        page = input_dto.pagination.page
        page_size = input_dto.pagination.page_size
        offset = (page - 1) * page_size

        data_query = base_query.order_by(order_fn(sort_field)).limit(page_size).offset(offset)
        data_result = await self._adapter.execute(statement=data_query)
        rows = data_result.all()

        raters = [
            RaterUserItemDTO(
                rate_uuid=row.UserRateMovieEntity.rate_uuid,
                user_uuid=row.UserEntity.user_uuid,
                first_name=row.UserEntity.first_name,
                last_name=row.UserEntity.last_name,
                email=row.UserEntity.email,
                score=row.UserRateMovieEntity.score,
                rated_at=row.UserRateMovieEntity.created_at,
            )
            for row in rows
        ]

        return GetMovieRatersResponseDTO(raters=raters, total=total)
