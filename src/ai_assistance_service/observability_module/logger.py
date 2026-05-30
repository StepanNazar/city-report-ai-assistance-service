import logging

import structlog


def _resolve_log_level(log_level: str | int) -> int:
    if isinstance(log_level, int):
        return log_level

    normalized = log_level.strip().upper()
    if normalized.isdigit():
        return int(normalized)

    resolved = logging.getLevelName(normalized)
    if isinstance(resolved, int):
        return resolved

    raise ValueError(f"Unsupported log level: {log_level}")


def configure_logging(log_level: str | int) -> None:
    resolved_log_level = _resolve_log_level(log_level)
    logging.basicConfig(level=resolved_log_level)
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(resolved_log_level),
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
    )


def get_logger() -> structlog.stdlib.BoundLogger:
    return structlog.get_logger()
