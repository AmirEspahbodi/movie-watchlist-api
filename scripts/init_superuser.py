import logging
from uuid import UUID
import asyncio

from archipy.adapters.postgres.sqlalchemy.adapters import AsyncPostgresSQLAlchemyAdapter
from archipy.models.entities.sqlalchemy.base_entities import BaseEntity
from archipy.models.errors import DatabaseQueryError, DatabaseConnectionError
from sqlalchemy import Column, String
from src.configs.runtime_config import RuntimeConfig
from src.models.entities.user_entity import UserEntity
from src.utils.security_utils import SecurityUtils

configs = RuntimeConfig.global_config()
from src.models.dtos.auth.domain.v1.auth_domain_interface_dtos import RegisterUserInputDTOV1


# Configure logging
logger = logging.getLogger(__name__)

class SuperUserCreateDTO(RegisterUserInputDTOV1):
    is_super_user: bool = True

# Create adapter
async def init_super_user():
    adapter = AsyncPostgresSQLAlchemyAdapter()
    try:
        session = adapter.get_session()

        user_in = SuperUserCreateDTO(
            email=configs.FIRST_SUPERUSER_EMAIL,
            first_name=configs.FIRST_SUPERUSER_FIRSTNAME,
            last_name=configs.FIRST_SUPERUSER_LASTNAME,
            username=configs.FIRST_SUPERUSER_USERNAME,
            password=configs.FIRST_SUPERUSER_PASSWORD,
            is_super_user=True,
        )
        user_in_password = user_in.password
        del user_in.password
        db_obj = UserEntity(
            **{
                **user_in.model_dump(),
                "hashed_password": SecurityUtils.get_password_hash(user_in_password)
            }
        )
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)

    except (DatabaseQueryError, DatabaseConnectionError) as e:
        logger.error(f"Database operation failed: {e}")
        raise

asyncio.run(init_super_user())
