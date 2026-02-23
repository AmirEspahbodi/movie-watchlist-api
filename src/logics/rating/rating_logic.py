from archipy.helpers.decorators.sqlalchemy_atomic import async_postgres_sqlalchemy_atomic_decorator
from archipy.models.errors import AlreadyExistsError

from src.models.dtos.rating.domain.v1.rating_domain_interface_dtos import (
    GetMovieRatersInputDTOV1,
    GetMovieRatersOutputDTOV1,
    GetMyRatingsInputDTOV1,
    GetMyRatingsOutputDTOV1,
    GetUserRatingsInputDTOV1,
    GetUserRatingsOutputDTOV1,
    RatedMovieItemDTOV1,
    RateMovieInputDTOV1,
    RateMovieOutputDTOV1,
    RaterUserItemDTOV1,
    UpdateRatingInputDTOV1,
)
from src.models.dtos.rating.repository.rating_repository_interface_dtos import (
    CheckRatingExistsQueryDTO,
    CreateRatingCommandDTO,
    GetMovieRatersQueryDTO,
    GetMyRatingsQueryDTO,
    GetUserRatingsQueryDTO,
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

    @async_postgres_sqlalchemy_atomic_decorator
    async def get_my_ratings(self, input_dto: GetMyRatingsInputDTOV1) -> GetMyRatingsOutputDTOV1:
        query = GetMyRatingsQueryDTO(
            user_uuid=input_dto.user_uuid,
            pagination=input_dto.pagination,
            sort_info=input_dto.sort_info,
        )
        response = await self._repository.get_my_ratings(input_dto=query)
        return GetMyRatingsOutputDTOV1(
            ratings=[
                RatedMovieItemDTOV1(
                    rate_uuid=r.rate_uuid,
                    movie_uuid=r.movie_uuid,
                    title=r.title,
                    description=r.description,
                    genre_uuid=r.genre_uuid,
                    score=r.score,
                    rated_at=r.rated_at,
                )
                for r in response.ratings
            ],
            total=response.total,
        )

    @async_postgres_sqlalchemy_atomic_decorator
    async def get_user_ratings(self, input_dto: GetUserRatingsInputDTOV1) -> GetUserRatingsOutputDTOV1:
        query = GetUserRatingsQueryDTO(
            user_uuid=input_dto.user_uuid,
            pagination=input_dto.pagination,
            sort_info=input_dto.sort_info,
        )
        response = await self._repository.get_user_ratings(input_dto=query)
        return GetUserRatingsOutputDTOV1(
            ratings=[
                RatedMovieItemDTOV1(
                    rate_uuid=r.rate_uuid,
                    movie_uuid=r.movie_uuid,
                    title=r.title,
                    description=r.description,
                    genre_uuid=r.genre_uuid,
                    score=r.score,
                    rated_at=r.rated_at,
                )
                for r in response.ratings
            ],
            total=response.total,
        )

    @async_postgres_sqlalchemy_atomic_decorator
    async def get_movie_raters(self, input_dto: GetMovieRatersInputDTOV1) -> GetMovieRatersOutputDTOV1:
        query = GetMovieRatersQueryDTO(
            movie_uuid=input_dto.movie_uuid,
            pagination=input_dto.pagination,
            sort_info=input_dto.sort_info,
        )
        response = await self._repository.get_movie_raters(input_dto=query)
        return GetMovieRatersOutputDTOV1(
            raters=[
                RaterUserItemDTOV1(
                    rate_uuid=u.rate_uuid,
                    user_uuid=u.user_uuid,
                    first_name=u.first_name,
                    last_name=u.last_name,
                    email=u.email,
                    score=u.score,
                    rated_at=u.rated_at,
                )
                for u in response.raters
            ],
            total=response.total,
        )
