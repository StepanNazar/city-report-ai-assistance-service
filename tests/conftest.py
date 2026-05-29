from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from ai_assistance_service.config import AppSettings
from ai_assistance_service.main import create_app


@pytest.fixture
async def fastapi_app(tmp_path: Path) -> AsyncIterator:
    settings = AppSettings(
        database_url=f"sqlite+aiosqlite:///{tmp_path}/test.db",
        kafka_enabled=False,
    )
    app = create_app(settings)
    yield app


@pytest.fixture
async def client(fastapi_app) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=fastapi_app, lifespan="on")
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def session(fastapi_app) -> AsyncIterator:
    async with fastapi_app.state.session_manager.session_factory() as session:
        yield session
