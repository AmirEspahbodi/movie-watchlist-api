from datetime import UTC, datetime, timedelta
from uuid import UUID

from archipy.models.errors import UnauthenticatedError
from jose import JWTError, jwt

from src.configs.runtime_config import RuntimeConfig


class JWTUtils:
    @staticmethod
    def create_access_token(user_uuid: UUID) -> str:
        config = RuntimeConfig.global_config()
        iat = datetime.now(UTC)
        payload = {
            "sub": str(user_uuid),
            "type": "access",
            "iat": iat,
            "exp": iat + timedelta(minutes=15),
        }
        return jwt.encode(payload, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)

    @staticmethod
    def create_refresh_token(user_uuid: UUID) -> str:
        config = RuntimeConfig.global_config()
        iat = datetime.now(UTC)
        payload = {
            "sub": str(user_uuid),
            "type": "refresh",
            "iat": iat,
            "exp": iat + timedelta(days=7),
        }
        return jwt.encode(payload, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> dict:
        config = RuntimeConfig.global_config()
        try:
            return jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        except JWTError as exc:
            raise UnauthenticatedError() from exc

    @staticmethod
    def get_user_uuid_from_token(token: str, expected_type: str) -> UUID:
        payload = JWTUtils.decode_token(token)
        if payload.get("type") != expected_type:
            raise UnauthenticatedError()
        sub = payload.get("sub")
        if not sub:
            raise UnauthenticatedError()
        return UUID(sub)
