from datetime import datetime
from uuid import UUID

from archipy.models.errors import AlreadyExistsError, NotFoundError, PermissionDeniedError, UnauthenticatedError
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response

from src.configs.containers import ServiceContainer
from src.logics.user.user_logic import UserLogic
from src.models.dtos.user.domain.v1.user_domain_interface_dtos import (
    CreateUserInputDTOV1,
    CreateUserOutputDTOV1,
    DeleteUserInputDTOV1,
    GetUserInputDTOV1,
    GetUserOutputDTOV1,
    SearchUserInputDTOV1,
    SearchUserOutputDTOV1,
    UpdateUserInputDTOV1,
    UpdateUserRestInputDTOV1,
)
from src.models.types.api_router_type import ApiRouterType
from src.models.types.user_sort_type import UserSortColumnType
from src.utils.auth_dependencies import get_current_admin_user_uuid
from src.utils.utils import Utils

routerV1: APIRouter = APIRouter(tags=[ApiRouterType.USER])

# Response schemas shared by every admin-protected endpoint.
# UnauthenticatedError  → 401  (missing / invalid / expired token)
# PermissionDeniedError → 403  (valid token but caller is not a super-user)
_ADMIN_AUTH_RESPONSES = Utils.get_fastapi_exception_responses(
    [UnauthenticatedError, PermissionDeniedError],
)


@routerV1.post(
    path="/",
    response_model=CreateUserOutputDTOV1,
    status_code=status.HTTP_201_CREATED,
    responses=Utils.get_fastapi_exception_responses([AlreadyExistsError]) | _ADMIN_AUTH_RESPONSES,
)
@inject
async def create_user(
    input_dto: CreateUserInputDTOV1,
    # Admin guard — resolves before the handler body runs.
    # The UUID is accepted but intentionally unused here; its presence
    # is enough to prove the caller is an authenticated super-user.
    _admin_uuid: UUID = Depends(get_current_admin_user_uuid),
    logic: UserLogic = Depends(Provide[ServiceContainer.user_logic]),
) -> CreateUserOutputDTOV1:
    return await logic.create_user(input_dto=input_dto)


@routerV1.get(
    path="/{user_uuid}",
    response_model=GetUserOutputDTOV1,
    responses=Utils.get_fastapi_exception_responses([NotFoundError]) | _ADMIN_AUTH_RESPONSES,
)
@inject
async def get_user(
    user_uuid: UUID,
    _admin_uuid: UUID = Depends(get_current_admin_user_uuid),
    logic: UserLogic = Depends(Provide[ServiceContainer.user_logic]),
) -> GetUserOutputDTOV1:
    input_dto = GetUserInputDTOV1(user_uuid=user_uuid)
    return await logic.get_user(input_dto=input_dto)


@routerV1.get(
    path="/",
    response_model=SearchUserOutputDTOV1,
    responses=_ADMIN_AUTH_RESPONSES,
)
@inject
async def search_users(
    _admin_uuid: UUID = Depends(get_current_admin_user_uuid),
    first_name: str | None = None,
    last_name: str | None = None,
    birth_date_from: datetime | None = None,
    birth_date_to: datetime | None = None,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Number of items per page"),
    sort_column: UserSortColumnType = Query(default=UserSortColumnType.CREATED_AT),
    sort_order: str = Query(default="desc"),
    logic: UserLogic = Depends(Provide[ServiceContainer.user_logic]),
) -> SearchUserOutputDTOV1:
    input_dto = SearchUserInputDTOV1.create(
        first_name=first_name,
        last_name=last_name,
        birth_date_from=birth_date_from,
        birth_date_to=birth_date_to,
        page=page,
        page_size=page_size,
        sort_column=sort_column,
        sort_order=sort_order,
    )
    return await logic.search_users(input_dto=input_dto)


@routerV1.patch(
    path="/{user_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=Utils.get_fastapi_exception_responses([NotFoundError]) | _ADMIN_AUTH_RESPONSES,
)
@inject
async def update_user(
    user_uuid: UUID,
    input_dto: UpdateUserRestInputDTOV1,
    _admin_uuid: UUID = Depends(get_current_admin_user_uuid),
    logic: UserLogic = Depends(Provide[ServiceContainer.user_logic]),
) -> Response:
    update_dto = UpdateUserInputDTOV1(user_uuid=user_uuid, **input_dto.model_dump())
    await logic.update_user(input_dto=update_dto)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@routerV1.delete(
    path="/{user_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=Utils.get_fastapi_exception_responses([NotFoundError]) | _ADMIN_AUTH_RESPONSES,
)
@inject
async def delete_user(
    user_uuid: UUID,
    _admin_uuid: UUID = Depends(get_current_admin_user_uuid),
    logic: UserLogic = Depends(Provide[ServiceContainer.user_logic]),
) -> Response:
    input_dto = DeleteUserInputDTOV1(user_uuid=user_uuid)
    await logic.delete_user(input_dto=input_dto)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
