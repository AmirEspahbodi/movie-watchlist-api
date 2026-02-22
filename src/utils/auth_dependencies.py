from uuid import UUID

from archipy.models.errors import UnauthenticatedError
from fastapi import Header

from src.utils.jwt_utils import JWTUtils


async def get_current_user_uuid(authorization: str = Header(...)) -> UUID:
    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthenticatedError()
    token = parts[1]
    return JWTUtils.get_user_uuid_from_token(token, expected_type="access")
