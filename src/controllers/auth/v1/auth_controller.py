from uuid import UUID

from archipy.models.errors import AlreadyExistsError, UnauthenticatedError
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.configs.containers import ServiceContainer
from src.logics.auth.auth_logic import AuthLogic
from src.models.dtos.auth.domain.v1.auth_domain_interface_dtos import (
    GetMeOutputDTOV1,
    LoginInputDTOV1,
    LoginOutputDTOV1,
    LoginRestInputDTOV1,
    RefreshTokenInputDTOV1,
    RefreshTokenOutputDTOV1,
    RefreshTokenRestInputDTOV1,
    RegisterUserInputDTOV1,
    RegisterUserOutputDTOV1,
    RegisterUserRestInputDTOV1,
)
from src.utils.auth_dependencies import get_current_user_uuid
from src.utils.utils import Utils

routerV1 = APIRouter(tags=["Auth V1"])

# Reusable response schema for endpoints that require a valid token.
_AUTH_RESPONSES = Utils.get_fastapi_exception_responses([UnauthenticatedError])


@routerV1.post(
    "/register",
    status_code=201,
    response_model=RegisterUserOutputDTOV1,
    responses=Utils.get_fastapi_exception_responses([AlreadyExistsError]),
)
@inject
async def register(
    request: RegisterUserRestInputDTOV1,
    auth_logic: AuthLogic = Depends(Provide[ServiceContainer.auth_logic]),
) -> RegisterUserOutputDTOV1:
    logic_dto = RegisterUserInputDTOV1(
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name,
        username=request.username,
        password=request.password,
    )
    return await auth_logic.register_user(input_dto=logic_dto)


@routerV1.post(
    "/login",
    status_code=200,
    response_model=LoginOutputDTOV1,
    responses=Utils.get_fastapi_exception_responses([AlreadyExistsError]),
)
@inject
async def login(
    request: LoginRestInputDTOV1,
    auth_logic: AuthLogic = Depends(Provide[ServiceContainer.auth_logic]),
) -> LoginOutputDTOV1:
    logic_dto = LoginInputDTOV1(email=request.email, password=request.password)
    return await auth_logic.login(input_dto=logic_dto)


@routerV1.post(
    "/refresh",
    status_code=200,
    response_model=RefreshTokenOutputDTOV1,
    responses=_AUTH_RESPONSES,
)
@inject
async def refresh(
    request: RefreshTokenRestInputDTOV1,
    auth_logic: AuthLogic = Depends(Provide[ServiceContainer.auth_logic]),
) -> RefreshTokenOutputDTOV1:
    logic_dto = RefreshTokenInputDTOV1(refresh_token=request.refresh_token)
    return await auth_logic.refresh_token(input_dto=logic_dto)


@routerV1.get(
    "/me",
    status_code=200,
    response_model=GetMeOutputDTOV1,
    responses=_AUTH_RESPONSES,
)
@inject
async def get_me(
    current_user_uuid: UUID = Depends(get_current_user_uuid),
    auth_logic: AuthLogic = Depends(Provide[ServiceContainer.auth_logic]),
) -> GetMeOutputDTOV1:
    return await auth_logic.get_me(user_uuid=current_user_uuid)
