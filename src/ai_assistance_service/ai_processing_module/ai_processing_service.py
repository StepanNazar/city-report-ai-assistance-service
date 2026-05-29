from __future__ import annotations

from uuid import UUID

from ai_assistance_service.ai_processing_module.llm_client import LlmClient
from ai_assistance_service.ai_processing_module.prompt_injection_guard import PromptInjectionGuard
from ai_assistance_service.ai_processing_module.schemas import AiCommentRequested
from ai_assistance_service.exceptions import PromptInjectionError
from ai_assistance_service.observability_module.logger import get_logger
from ai_assistance_service.persistence_module.repositories import PendingResultRepository, PromptRepository


class AiProcessingService:
    def __init__(
        self,
        prompt_repository: PromptRepository,
        pending_repository: PendingResultRepository,
        llm_client: LlmClient,
        guard: PromptInjectionGuard,
    ) -> None:
        self._prompt_repository = prompt_repository
        self._pending_repository = pending_repository
        self._llm_client = llm_client
        self._guard = guard
        self._logger = get_logger()

    async def get_or_generate_comment(self, request: AiCommentRequested) -> str:
        pending = await self._pending_repository.get_by_request_id(request.ai_request_id)
        if pending is not None:
            self._logger.info("ai_comment_reused", ai_request_id=str(request.ai_request_id))
            return pending.generated_comment

        prompt = await self._prompt_repository.get_by_locality(request.locality_id)
        locality_prompt = prompt.prompt_text if prompt is not None else ""

        content = f"{request.report_title}\n{request.report_description}"
        if not await self._guard.is_safe(content):
            self._logger.warning("prompt_injection_detected", ai_request_id=str(request.ai_request_id))
            raise PromptInjectionError(request.ai_request_id)

        comment = await self._llm_client.generate_comment(
            locality_prompt,
            request.report_title,
            request.report_description,
        )
        await self._pending_repository.create(request.ai_request_id, comment)
        self._logger.info("ai_comment_generated", ai_request_id=str(request.ai_request_id))
        return comment

    async def delete_pending_result(self, ai_request_id: UUID) -> None:
        pending = await self._pending_repository.get_by_request_id(ai_request_id)
        if pending is not None:
            await self._pending_repository.delete(pending)
            self._logger.info("ai_comment_pending_deleted", ai_request_id=str(ai_request_id))
