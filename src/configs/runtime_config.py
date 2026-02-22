from archipy.configs.base_config import BaseConfig
from pydantic import EmailStr


class RuntimeConfig(BaseConfig):
    FIRST_SUPERUSER_EMAIL: EmailStr
    FIRST_SUPERUSER_FIRSTNAME: str
    FIRST_SUPERUSER_LASTNAME: str
    FIRST_SUPERUSER_USERNAME: str
    FIRST_SUPERUSER_PASSWORD: str


BaseConfig.set_global(RuntimeConfig())
