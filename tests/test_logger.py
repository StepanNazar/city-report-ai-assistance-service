import logging

import pytest

from ai_assistance_service.observability_module.logger import _resolve_log_level, configure_logging


@pytest.mark.parametrize(
    ("raw_log_level", "expected"),
    [
        ("INFO", logging.INFO),
        ("info", logging.INFO),
        ("  warning ", logging.WARNING),
        ("20", logging.INFO),
        (logging.DEBUG, logging.DEBUG),
    ],
)
def test_resolve_log_level_accepts_common_inputs(raw_log_level: str | int, expected: int) -> None:
    assert _resolve_log_level(raw_log_level) == expected


def test_resolve_log_level_rejects_unknown_values() -> None:
    with pytest.raises(ValueError, match="Unsupported log level"):
        _resolve_log_level("NOT_A_LEVEL")


def test_configure_logging_supports_named_level() -> None:
    configure_logging("INFO")

