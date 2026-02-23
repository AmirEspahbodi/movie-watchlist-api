from archipy.adapters.base.sqlalchemy.adapters import SQLAlchemyFilterMixin
from archipy.adapters.base.sqlalchemy.ports import AsyncSQLAlchemyPort
from archipy.adapters.postgres.sqlalchemy.adapters import AsyncPostgresSQLAlchemyAdapter
from archipy.models.errors import AlreadyExistsError, NotFoundError
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from src.models.dtos.rating.repository.rating_repository_interface_dtos import (
    CheckRatingExistsQueryDTO,
    CreateRatingCommandDTO,
    CreateRatingResponseDTO,
    UpdateRatingCommandDTO,
)
from src.models.entities.user_rate_movie_entity import UserRateMovieEntity


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
