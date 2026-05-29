import logging

import structlog


def configure_logging(log_level: str) -> None:
    logging.basicConfig(level=log_level)
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
    )


def get_logger() -> structlog.stdlib.BoundLogger:
    return structlog.get_logger()
