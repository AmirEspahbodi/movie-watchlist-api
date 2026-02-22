import logging

from pydantic import BaseModel
from src.models.dtos.auth.domain.v1.auth_domain_interface_dtos import RegisterUserInputDTOV1
from src.utils.security_utils import SecurityUtils
from src.models.entities.user_entity import UserEntity
from sqlalchemy import select


class SuperUserCreateDTO(RegisterUserInputDTOV1):
    is_superuser: bool = True


def init_db(session) -> None:
    # load these values from .env
    # first_super_user_email
    # first_super_user_first_name
    # first_super_user_last_name
    # first_super_user_username
    # first_super_user_password
    (
        first_super_user_email,
        first_super_user_first_name,
        first_super_user_last_name,
        first_super_user_username,
        first_super_user_password,
    ) = (None, None, None, None, None)
    user = session.exec(select(UserEntity).where(UserEntity.email == first_super_user_email)).first()
    if not user:
        user_in = SuperUserCreateDTO(
            email=first_super_user_email,
            first_name=first_super_user_first_name,
            last_name=first_super_user_last_name,
            username=first_super_user_username,
            password=first_super_user_password,
            is_superuser=True,
        )
        db_obj = UserEntity(
            **user_in.model_dump(), update={"hashed_password": SecurityUtils.get_password_hash(user_in.password)}
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    with Session(engine) as session:
        init_db(session)


def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
