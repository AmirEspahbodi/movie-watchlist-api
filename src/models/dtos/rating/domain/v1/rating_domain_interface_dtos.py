from datetime import datetime
from uuid import UUID

from archipy.models.dtos.base_dtos import BaseDTO
from archipy.models.dtos.pagination_dto import PaginationDTO
from archipy.models.dtos.sort_dto import SortDTO
from pydantic import BaseModel, ConfigDict, Field

from src.models.types.rating_sort_type import RatingSortColumnType


class RateMovieRestInputDTOV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    movie_uuid: UUID
    score: int = Field(..., ge=1, le=5)


class RateMovieInputDTOV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    movie_uuid: UUID
    user_uuid: UUID
    score: int


class RateMovieOutputDTOV1(BaseDTO):
    rate_uuid: UUID
    user_uuid: UUID
    movie_uuid: UUID
    score: int
    created_at: datetime
    updated_at: datetime


class UpdateRatingRestInputDTOV1(BaseDTO):
    score: int = Field(..., ge=1, le=10)


class UpdateRatingInputDTOV1(BaseDTO):
    rate_uuid: UUID
    user_uuid: UUID
    score: int


class RatedMovieItemDTOV1(BaseDTO):
    rate_uuid: UUID
    movie_uuid: UUID
    title: str
    description: str | None = None
    genre_uuid: UUID
    score: int
    rated_at: datetime


class GetMyRatingsInputDTOV1(BaseDTO):
    user_uuid: UUID
    pagination: PaginationDTO
    sort_info: SortDTO[RatingSortColumnType]

    @classmethod
    def create(
        cls,
        user_uuid: UUID,
        page: int = 1,
        page_size: int = 10,
        sort_column: RatingSortColumnType = RatingSortColumnType.CREATED_AT,
        sort_order: str = "desc",
    ) -> "GetMyRatingsInputDTOV1":
        return cls(
            user_uuid=user_uuid,
            pagination=PaginationDTO(page=page, page_size=page_size),
            sort_info=SortDTO[RatingSortColumnType](column=sort_column, order=sort_order),
        )


class GetMyRatingsOutputDTOV1(BaseDTO):
    ratings: list[RatedMovieItemDTOV1]
    total: int


class GetUserRatingsInputDTOV1(BaseDTO):
    user_uuid: UUID
    pagination: PaginationDTO
    sort_info: SortDTO[RatingSortColumnType]

    @classmethod
    def create(
        cls,
        user_uuid: UUID,
        page: int = 1,
        page_size: int = 10,
        sort_column: RatingSortColumnType = RatingSortColumnType.CREATED_AT,
        sort_order: str = "desc",
    ) -> "GetUserRatingsInputDTOV1":
        return cls(
            user_uuid=user_uuid,
            pagination=PaginationDTO(page=page, page_size=page_size),
            sort_info=SortDTO[RatingSortColumnType](column=sort_column, order=sort_order),
        )


class GetUserRatingsOutputDTOV1(BaseDTO):
    ratings: list[RatedMovieItemDTOV1]
    total: int


class RaterUserItemDTOV1(BaseDTO):
    rate_uuid: UUID
    user_uuid: UUID
    first_name: str
    last_name: str
    email: str
    score: int
    rated_at: datetime


class GetMovieRatersInputDTOV1(BaseDTO):
    movie_uuid: UUID
    pagination: PaginationDTO
    sort_info: SortDTO[RatingSortColumnType]

    @classmethod
    def create(
        cls,
        movie_uuid: UUID,
        page: int = 1,
        page_size: int = 10,
        sort_column: RatingSortColumnType = RatingSortColumnType.CREATED_AT,
        sort_order: str = "desc",
    ) -> "GetMovieRatersInputDTOV1":
        return cls(
            movie_uuid=movie_uuid,
            pagination=PaginationDTO(page=page, page_size=page_size),
            sort_info=SortDTO[RatingSortColumnType](column=sort_column, order=sort_order),
        )


class GetMovieRatersOutputDTOV1(BaseDTO):
    raters: list[RaterUserItemDTOV1]
    total: int
