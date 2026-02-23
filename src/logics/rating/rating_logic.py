from archipy.helpers.decorators.sqlalchemy_atomic import async_postgres_sqlalchemy_atomic_decorator
from archipy.models.errors import AlreadyExistsError

from src.models.dtos.rating.domain.v1.rating_domain_interface_dtos import (
    RateMovieInputDTOV1,
    RateMovieOutputDTOV1,
    UpdateRatingInputDTOV1,
)
from src.models.dtos.rating.repository.rating_repository_interface_dtos import (
    CheckRatingExistsQueryDTO,
    CreateRatingCommandDTO,
    UpdateRatingCommandDTO,
)
from src.repositories.rating.rating_repository import RatingRepository


class RatingLogic:
    def __init__(self, repository: RatingRepository) -> None:
        self._repository = repository

    @async_postgres_sqlalchemy_atomic_decorator
    async def rate_movie(self, input_dto: RateMovieInputDTOV1) -> RateMovieOutputDTOV1:
        exists_query = CheckRatingExistsQueryDTO(
            user_uuid=input_dto.user_uuid,
            movie_uuid=input_dto.movie_uuid,
        )
        already_rated = await self._repository.check_rating_exists(input_dto=exists_query)
        if already_rated:
            raise AlreadyExistsError(resource_type="UserRateMovieEntity")

        command = CreateRatingCommandDTO(
            user_uuid=input_dto.user_uuid,
            movie_uuid=input_dto.movie_uuid,
            score=input_dto.score,
        )
        response = await self._repository.create_rating(input_dto=command)
        return RateMovieOutputDTOV1.model_validate(obj=response)

    @async_postgres_sqlalchemy_atomic_decorator
    async def update_rating(self, input_dto: UpdateRatingInputDTOV1) -> None:
        command = UpdateRatingCommandDTO(
            rate_uuid=input_dto.rate_uuid,
            user_uuid=input_dto.user_uuid,
            score=input_dto.score,
        )
        await self._repository.update_rating(input_dto=command)
