from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable

from aiokafka import AIOKafkaConsumer
from sqlalchemy.ext.asyncio import AsyncSession

from ai_assistance_service.ai_processing_module.ai_processing_service import AiProcessingService
from ai_assistance_service.ai_processing_module.llm_client import GeminiLlmClient
from ai_assistance_service.ai_processing_module.prompt_injection_guard import GeminiPromptInjectionGuard
from ai_assistance_service.ai_processing_module.producer import KafkaAiCommentProducer
from ai_assistance_service.ai_processing_module.schemas import AiCommentGenerated, AiCommentRequested
from ai_assistance_service.config import AppSettings
from ai_assistance_service.observability_module.logger import get_logger
from ai_assistance_service.persistence_module.database import SessionManager
from ai_assistance_service.persistence_module.repositories import PendingResultRepository, PromptRepository


class AiCommentConsumer:
    def __init__(self, settings: AppSettings, session_manager: SessionManager) -> None:
        self._settings = settings
        self._session_manager = session_manager
        self._logger = get_logger()
        self._consumer = AIOKafkaConsumer(
            "ai.comment.requested",
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id=settings.kafka_consumer_group,
            enable_auto_commit=False,
        )
        self._producer = KafkaAiCommentProducer(settings.kafka_bootstrap_servers, "ai.comment.generated")
        self._task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        await self._producer.start()
        await self._consumer.start()
        self._task = asyncio.create_task(self._consume_loop())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        await self._consumer.stop()
        await self._producer.stop()

    async def _consume_loop(self) -> None:
        async for message in self._consumer:
            try:
                await self._process_message(message.value)
            except Exception as exc:
                self._logger.error(\"ai_comment_processing_error\", error=str(exc))

    async def _process_message(self, payload: bytes) -> None:
        request = AiCommentRequested.model_validate(json.loads(payload.decode("utf-8")))

        await self._retry(lambda: self._handle_request(request))

    async def _handle_request(self, request: AiCommentRequested) -> None:
        async with self._session_manager.session_factory() as session:
            await self._process_with_session(session, request)

    async def _process_with_session(self, session: AsyncSession, request: AiCommentRequested) -> None:
        prompt_repository = PromptRepository(session)
        pending_repository = PendingResultRepository(session)
        llm_client = GeminiLlmClient(
            api_key=self._settings.gemini_api_key or "",
            model=self._settings.gemini_model,
        )
        guard = GeminiPromptInjectionGuard(
            api_key=self._settings.gemini_api_key or "",
            model=self._settings.gemini_model,
        )
        processing_service = AiProcessingService(
            prompt_repository,
            pending_repository,
            llm_client,
            guard,
        )

        comment = await processing_service.get_or_generate_comment(request)
        event = AiCommentGenerated(
            ai_request_id=request.ai_request_id,
            report_id=request.report_id,
            generated_comment=comment,
        )
        await self._producer.send(event)
        await self._consumer.commit()
        await processing_service.delete_pending_result(request.ai_request_id)
        self._logger.info("ai_comment_published", ai_request_id=str(request.ai_request_id))

    async def _retry(self, operation: Callable[[], Awaitable[None]], attempts: int = 3) -> None:
        delay = 1.0
        for attempt in range(attempts):
            try:
                await operation()
                return
            except Exception as exc:
                self._logger.warning("ai_comment_processing_failed", error=str(exc), attempt=attempt + 1)
                if attempt == attempts - 1:
                    raise
                await asyncio.sleep(delay)
                delay *= 2
