from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from ai_assistance_service.ai_processing_module.consumer import AiCommentConsumer
from ai_assistance_service.api_module.router import router as api_router
from ai_assistance_service.config import AppSettings
from ai_assistance_service.observability_module.logger import configure_logging
from ai_assistance_service.persistence_module.database import SessionManager


def create_app(settings: AppSettings | None = None) -> FastAPI:
    settings = settings or AppSettings()
    configure_logging(settings.log_level)

    session_manager = SessionManager(settings.database_url, settings.database_echo)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await session_manager.init_models()
        if settings.kafka_enabled:
            consumer = AiCommentConsumer(settings, session_manager)
            await consumer.start()
            app.state.kafka_consumer = consumer
        yield
        consumer = getattr(app.state, "kafka_consumer", None)
        if consumer is not None:
            await consumer.stop()
        await session_manager.dispose()

    app = FastAPI(title="AI Assistance Service API", lifespan=lifespan)
    app.state.session_manager = session_manager
    app.state.settings = settings

    app.include_router(api_router, prefix="/api/v1")

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": "Invalid request payload"})

    return app


app = create_app()
