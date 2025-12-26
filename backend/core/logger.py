import logging


def configure_logging(level: str | None = None):
    logger_level_str = (level or "INFO").upper()
    logger_level = getattr(logging, logger_level_str, logging.INFO)

    root_logger = logging.getLogger()

    root_logger.handlers.clear()

    root_handler = logging.StreamHandler()
    root_logger.setLevel(logger_level)
    root_handler.setLevel(logger_level)
    _fmt = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="%",
        validate=True,
    )
    root_handler.setFormatter(fmt=_fmt)
    root_logger.addHandler(root_handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
