from datetime import UTC, datetime, timedelta
from uuid import UUID

from archipy.models.errors import InvalidTokenError, UnauthenticatedError
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
        return jwt.encode(payload, config.AUTH.SECRET_KEY.get_secret_value(), algorithm=config.AUTH.HASH_ALGORITHM)

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
        return jwt.encode(payload, config.AUTH.SECRET_KEY.get_secret_value(), algorithm=config.AUTH.HASH_ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> dict:
        config = RuntimeConfig.global_config()
        try:
            return jwt.decode(token, config.AUTH.SECRET_KEY.get_secret_value(), algorithms=[config.AUTH.HASH_ALGORITHM])
        except JWTError as exc:
            raise InvalidTokenError() from exc

    @staticmethod
    def get_user_uuid_from_token(token: str, expected_type: str) -> UUID:
        payload = JWTUtils.decode_token(token)
        print("asdafsdkjfnaskfdn")
        if payload.get("type") != expected_type:
            raise InvalidTokenError()
        sub = payload.get("sub")
        if not sub:
            raise InvalidTokenError()
        return UUID(sub)
