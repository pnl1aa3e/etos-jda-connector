import json
import logging
import sys
import traceback
from datetime import datetime


class HealthCheckFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return "healthcheck" not in record.getMessage()


class GLoggerHandler(logging.Handler):
    def __init__(
        self,
        app_name: str,
        environment: str,
        app_version: str,
        development: bool = False,
    ):
        self.app_name = app_name
        self.environment = environment
        self.app_version = app_version
        self.development = development
        super().__init__()

    def format(self, record):
        data = record.__dict__
        json_record = {}
        json_record["service"] = self.app_name
        json_record["env"] = self.environment
        json_record["app_version"] = self.app_version
        json_record["timestamp"] = datetime.now().isoformat()
        json_record["level"] = record.levelname
        json_record["msg"] = record.getMessage()

        if int(data["levelno"]) >= logging.ERROR:
            if record.exc_info:
                err_type, err_value, err_traceback = record.exc_info
                json_record["stacktrace"] = traceback.format_exception(
                    err_type, err_value, err_traceback
                )

        if "trace_id" in data:
            json_record["trace_id"] = data["trace_id"]
        if "data" in data:
            json_record["data"] = data["data"]

        if self.development:
            result = (
                f"{json_record.get('timestamp', 'timestamp')} | {json_record.get('level', 'level')}"
                + "\n"
            )
            result += json_record.get("msg", "msg") + "\n"
            if json_record.get("stacktrace"):
                result += "".join(json_record.get("stacktrace", [])) + "\n"

            return result

        return json.dumps(json_record)


def setup_glogger(
    app_name: str,
    environment: str,
    app_version: str = "local",
    level: str = "INFO",
    logger=logging.getLogger(),  # noqa: B008
    development=False,
):
    formatter = GLoggerHandler(app_name, environment, app_version, development)
    for logger_name in logging.root.manager.loggerDict.keys():
        override_logger = logging.getLogger(logger_name)
        override_logger.addFilter(HealthCheckFilter())
        for handler in override_logger.handlers:
            handler.setFormatter(formatter)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.handlers.append(handler)
    logger.setLevel(level)
    logger.addFilter(HealthCheckFilter())

    # Redirect exceptions to the logging module
    def excepthook(exc_type, exc_value, exc_traceback):
        logger.error(exc_value, exc_info=(exc_type, exc_value, exc_traceback))

    # Redirect print statements to the logging module
    class LoggerWriter:
        def __init__(self, level):
            self.level = level

        def write(self, message):
            if message != "\n":
                logger.log(self.level, message)

        def flush(self):
            pass

    # Redirect stdout and stderr
    sys.excepthook = excepthook
    sys.stdout = LoggerWriter(logging.DEBUG)
    sys.stderr = LoggerWriter(logging.ERROR)

    return logger
