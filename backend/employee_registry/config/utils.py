from os import environ

from employee_registry.config.default import DefaultSettings


def get_settings() -> DefaultSettings:
    env = environ.get("ENV", "local")
    if env == "local":
        return DefaultSettings()

    return DefaultSettings()
