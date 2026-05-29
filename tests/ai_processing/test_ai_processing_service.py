from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from ai_assistance_service.ai_processing_module.ai_processing_service import AiProcessingService
from ai_assistance_service.ai_processing_module.schemas import AiCommentRequested
from ai_assistance_service.exceptions import PromptInjectionError
from ai_assistance_service.persistence_module.models import PendingAiResult
from ai_assistance_service.persistence_module.repositories import PendingResultRepository, PromptRepository


class FakeLlmClient:
    def __init__(self) -> None:
        self.called = False

    async def generate_comment(self, locality_prompt: str, report_title: str, report_description: str) -> str:
        self.called = True
        return "Generated comment"


class FakeGuard:
    def __init__(self, safe: bool) -> None:
        self.safe = safe

    async def is_safe(self, content: str) -> bool:
        return self.safe


class TestAiProcessingService:
    @pytest.mark.asyncio
    async def test_reuses_existing_pending_comment(self, session: AsyncSession) -> None:
        ai_request_id = uuid4()
        session.add(PendingAiResult(ai_request_id=ai_request_id, generated_comment="Cached comment"))
        await session.commit()
        request = AiCommentRequested(
            aiRequestId=ai_request_id,
            reportId=uuid4(),
            localityId=uuid4(),
            reportTitle="Title",
            reportDescription="Description",
        )
        llm_client = FakeLlmClient()
        service = AiProcessingService(
            PromptRepository(session),
            PendingResultRepository(session),
            llm_client,
            FakeGuard(safe=True),
        )

        comment = await service.get_or_generate_comment(request)

        assert comment == "Cached comment"
        assert llm_client.called is False

    @pytest.mark.asyncio
    async def test_raises_when_prompt_injection_detected(self, session: AsyncSession) -> None:
        request = AiCommentRequested(
            aiRequestId=uuid4(),
            reportId=uuid4(),
            localityId=uuid4(),
            reportTitle="Title",
            reportDescription="Description",
        )

        service = AiProcessingService(
            PromptRepository(session),
            PendingResultRepository(session),
            FakeLlmClient(),
            FakeGuard(safe=False),
        )

        with pytest.raises(PromptInjectionError) as exc_info:
            await service.get_or_generate_comment(request)

        assert exc_info.value.ai_request_id == request.ai_request_id
