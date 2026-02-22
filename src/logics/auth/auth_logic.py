from uuid import UUID

from archipy.helpers.decorators.sqlalchemy_atomic import async_sqlite_sqlalchemy_atomic_decorator
from archipy.models.errors import NotFoundError, UnauthenticatedError

from src.models.dtos.auth.domain.v1.auth_domain_interface_dtos import (
    GetMeOutputDTOV1,
    LoginInputDTOV1,
    LoginOutputDTOV1,
    RefreshTokenInputDTOV1,
    RefreshTokenOutputDTOV1,
    RegisterUserInputDTOV1,
    RegisterUserOutputDTOV1,
)
from src.models.dtos.user.repository.user_repository_interface_dtos import (
    CreateUserCommandDTO,
    GetUserByEmailQueryDTO,
    GetUserFullByUUIDQueryDTO,
)
from src.repositories.user.user_repository import UserRepository
from src.utils.jwt_utils import JWTUtils
from src.utils.security_utils import SecurityUtils


class AuthLogic:
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    @async_sqlite_sqlalchemy_atomic_decorator
    async def register_user(self, input_dto: RegisterUserInputDTOV1) -> RegisterUserOutputDTOV1:
        hashed_password = SecurityUtils.get_password_hash(input_dto.password)

        command_dto = CreateUserCommandDTO(
            email=input_dto.email,
            username=input_dto.username,
            first_name=input_dto.first_name,
            last_name=input_dto.last_name,
            hashed_password=hashed_password,
            is_active=True,
        )

        repo_response = await self._user_repository.create_user(input_dto=command_dto)

        return RegisterUserOutputDTOV1.model_validate(obj=repo_response)

    @async_sqlite_sqlalchemy_atomic_decorator
    async def login(self, input_dto: LoginInputDTOV1) -> LoginOutputDTOV1:
        query = GetUserByEmailQueryDTO(email=input_dto.email)
        try:
            user = await self._user_repository.get_user_by_email(input_dto=query)
        except NotFoundError:
            raise UnauthenticatedError()
        if not SecurityUtils.verify_password(input_dto.password, user.hashed_password):
            raise UnauthenticatedError()
        if not user.is_active:
            raise UnauthenticatedError()
        access_token = JWTUtils.create_access_token(user.user_uuid)
        refresh_token = JWTUtils.create_refresh_token(user.user_uuid)
        return LoginOutputDTOV1(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

    @async_sqlite_sqlalchemy_atomic_decorator
    async def refresh_token(self, input_dto: RefreshTokenInputDTOV1) -> RefreshTokenOutputDTOV1:
        user_uuid = JWTUtils.get_user_uuid_from_token(input_dto.refresh_token, expected_type="refresh")
        query = GetUserFullByUUIDQueryDTO(user_uuid=user_uuid)
        try:
            user = await self._user_repository.get_user_full_by_uuid(input_dto=query)
        except NotFoundError:
            raise UnauthenticatedError()
        if not user.is_active:
            raise UnauthenticatedError()
        access_token = JWTUtils.create_access_token(user_uuid)
        return RefreshTokenOutputDTOV1(access_token=access_token, token_type="bearer")

    @async_sqlite_sqlalchemy_atomic_decorator
    async def get_me(self, user_uuid: UUID) -> GetMeOutputDTOV1:
        query = GetUserFullByUUIDQueryDTO(user_uuid=user_uuid)
        response = await self._user_repository.get_user_full_by_uuid(input_dto=query)
        return GetMeOutputDTOV1.model_validate(obj=response)
