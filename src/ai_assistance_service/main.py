from __future__ import annotations

from fastapi import FastAPI
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

    app = FastAPI(title="AI Assistance Service API")
    session_manager = SessionManager(settings.database_url, settings.database_echo)
    app.state.session_manager = session_manager
    app.state.settings = settings

    app.include_router(api_router, prefix="/api/v1")

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(request, exc):
        return JSONResponse(status_code=400, content={"detail": "Invalid request payload"})

    @app.on_event("startup")
    async def startup() -> None:
        await session_manager.init_models()
        if settings.kafka_enabled:
            consumer = AiCommentConsumer(settings, session_manager)
            await consumer.start()
            app.state.kafka_consumer = consumer

    @app.on_event("shutdown")
    async def shutdown() -> None:
        consumer = getattr(app.state, "kafka_consumer", None)
        if consumer is not None:
            await consumer.stop()
        await session_manager.dispose()

    return app


app = create_app()
