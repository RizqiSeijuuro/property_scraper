import logging
import sys

APP_LOGGER_NAME = "property_scraper"


class CustomFormatter(logging.Formatter):
    grey: str = "\x1b[38;20m"
    yellow: str = "\x1b[33;20m"
    red: str = "\x1b[31;20m"
    bold_red: str = "\x1b[31;1m"
    reset: str = "\x1b[0m"
    log_format: str = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s (line:%(lineno)d)"
    )

    FORMATS = {
        logging.DEBUG: grey + log_format + reset,
        logging.INFO: grey + log_format + reset,
        logging.WARNING: yellow + log_format + reset,
        logging.ERROR: red + log_format + reset,
        logging.CRITICAL: bold_red + log_format + reset,
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def setup_applevel_logger(
    logger_name: str = APP_LOGGER_NAME, is_debug: bool = True, file_name: str = None
) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG if is_debug else logging.INFO)
    formatter = CustomFormatter()

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    logger.handlers.clear()
    logger.addHandler(sh)

    if file_name:
        fh = logging.FileHandler(file_name)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


def get_logger(module_name: str) -> logging.Logger:
    return logging.getLogger(APP_LOGGER_NAME).getChild(module_name)


is_debug = True
# if os.environ.get("_PROJECT_ENV", "dev") == "prod":
#    is_debug = False
setup_applevel_logger(is_debug=is_debug)
