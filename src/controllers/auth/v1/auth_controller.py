from archipy.models.errors import AlreadyExistsError
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.configs.containers import ServiceContainer
from src.logics.auth.auth_logic import AuthLogic
from src.models.dtos.auth.domain.v1.auth_domain_interface_dtos import (
    RegisterUserInputDTOV1,
    RegisterUserOutputDTOV1,
    RegisterUserRestInputDTOV1,
)
from src.utils.utils import Utils

routerV1 = APIRouter(tags=["Auth V1"])


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
