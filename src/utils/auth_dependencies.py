from uuid import UUID

from archipy.models.errors import PermissionDeniedError, UnauthenticatedError
from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.configs.containers import ServiceContainer
from src.logics.auth.auth_logic import AuthLogic
from src.utils.jwt_utils import JWTUtils

_http_bearer = HTTPBearer(auto_error=False)


async def get_current_user_uuid(
    credentials: HTTPAuthorizationCredentials | None = Depends(_http_bearer),
) -> UUID:
    if credentials is None:
        raise UnauthenticatedError()
    return JWTUtils.get_user_uuid_from_token(credentials.credentials, expected_type="access")


@inject
async def get_current_admin_user_uuid(
    current_user_uuid: UUID = Depends(get_current_user_uuid),
    auth_logic: AuthLogic = Depends(Provide[ServiceContainer.auth_logic]),
) -> UUID:
    user = await auth_logic.get_me(user_uuid=current_user_uuid)
    if not user.is_super_user:
        raise PermissionDeniedError()
    return current_user_uuid
