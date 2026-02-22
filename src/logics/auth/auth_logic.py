from archipy.helpers.decorators.sqlalchemy_atomic import async_sqlite_sqlalchemy_atomic_decorator

from src.models.dtos.auth.domain.v1.auth_domain_interface_dtos import (
    RegisterUserInputDTOV1,
    RegisterUserOutputDTOV1,
)
from src.models.dtos.user.repository.user_repository_interface_dtos import (
    CreateUserCommandDTO,
)
from src.repositories.user.user_repository import UserRepository
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
