from logging import getLogger

from fastapi import FastAPI
from uvicorn import run

from employee_registry.config import DefaultSettings
from employee_registry.config.utils import get_settings
from employee_registry.endpoints import list_of_routes


logger = getLogger(__name__)


def bind_routes(application: FastAPI, setting: DefaultSettings) -> None:
    """
    Bind all routes to application.
    """
    for route in list_of_routes:
        application.include_router(route, prefix=setting.PATH_PREFIX)


def get_app() -> FastAPI:
    """
    Creates application and all dependable objects.
    """
    description = "Сервис, реализующий реестр сотрудников."

    tags_metadata = [
        {
            "name": "Employees",
            "description": "Управление сотрудниками",
        },
    ]

    application = FastAPI(
        title="Employee registry",
        description=description,
        docs_url="/swagger",
        openapi_url="/openapi",
        version="1.0.0",
        openapi_tags=tags_metadata,
    )

    settings = get_settings()
    bind_routes(application, settings)
    application.state.settings = settings
    return application


app = get_app()

if __name__ == "__main__":
    settings_for_application = get_settings()
    run(
        "employee_registry.main:app",
        host=settings_for_application.APP_HOST,
        port=settings_for_application.APP_PORT,
        reload=True,
        reload_dirs=["employee_registry", "tests"],
        log_level="debug",
    )
