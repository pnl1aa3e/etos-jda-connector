from app.glogger import setup_glogger
from app.settings import settings

if __name__ == "__main__":
    setup_glogger(
        app_name=settings.app_name,
        environment=settings.environment,
        app_version=settings.application_version,
        level=settings.log_level,
    )
