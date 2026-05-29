from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from ai_assistance_service.persistence_module.models import Base


class SessionManager:
    def __init__(self, database_url: str, echo: bool) -> None:
        self._engine: AsyncEngine = create_async_engine(database_url, echo=echo)
        self._session_factory = async_sessionmaker(self._engine, expire_on_commit=False)

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        return self._session_factory

    async def init_models(self) -> None:
        async with self._engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def dispose(self) -> None:
        await self._engine.dispose()


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    session_manager: SessionManager = request.app.state.session_manager
    session: AsyncSession = session_manager.session_factory()
    try:
        yield session
    finally:
        await session.close()
