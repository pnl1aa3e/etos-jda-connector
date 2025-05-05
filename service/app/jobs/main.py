import logging
import sys
from typing import Annotated

import typer
from typer import Typer

from app.glogger import setup_glogger
from app.jobs.job import Job
from app.jobs.job_get_stores import LoadStores
from app.settings import Settings

jobs = [LoadStores]

# Sub apps
ingoing = Typer()

# Main app
app = Typer()


@app.command()
def execute(job_name: Annotated[str, typer.Argument(help="Name of the job to execute")]) -> None:
    try:
        job: type[Job] = getattr(sys.modules[__name__], job_name)
    except AttributeError as e:
        msg = f"Invalid job name: {job_name}"
        raise ValueError(msg) from e

    with job() as job_instance:
        job_instance.run()


def main() -> None:
    global_settings = Settings()
    setup_glogger(
        app_name=global_settings.app_name,
        app_version=global_settings.application_version,
        environment=global_settings.environment,
        development=global_settings.disable_json_logs,
    )
    logger = logging.getLogger(__name__)

    try:
        logger.info("Starting application")
        app(standalone_mode=False)
    except Exception as e:
        logger.exception("Exception during runtime", exc_info=e)
        raise e
    finally:
        logger.info("Flushing logs")
        logging.shutdown()
        logger.info("Application finished")
