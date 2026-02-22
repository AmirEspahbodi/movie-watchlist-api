from archipy.configs.base_config import BaseConfig


class RuntimeConfig(BaseConfig):
    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str


BaseConfig.set_global(RuntimeConfig())
