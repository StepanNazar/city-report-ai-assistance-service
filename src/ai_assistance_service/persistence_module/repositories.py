from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_assistance_service.persistence_module.models import (
    LocalityPrompt,
    PendingAiResult,
    PromptSuggestion,
    PromptSuggestionStatus,
)


class PromptRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_locality(self, locality_id: UUID) -> LocalityPrompt | None:
        result = await self._session.execute(
            select(LocalityPrompt).where(LocalityPrompt.locality_id == locality_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        locality_id: UUID,
        prompt_text: str,
        created_by_user_id: UUID | None,
    ) -> LocalityPrompt:
        prompt = LocalityPrompt(
            locality_id=locality_id,
            prompt_text=prompt_text,
            created_by_user_id=created_by_user_id,
            updated_by_user_id=created_by_user_id,
        )
        self._session.add(prompt)
        await self._session.commit()
        await self._session.refresh(prompt)
        return prompt

    async def update(
        self,
        prompt: LocalityPrompt,
        prompt_text: str,
        updated_by_user_id: UUID | None,
    ) -> LocalityPrompt:
        prompt.prompt_text = prompt_text
        prompt.updated_by_user_id = updated_by_user_id
        await self._session.commit()
        await self._session.refresh(prompt)
        return prompt


class SuggestionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        locality_id: UUID,
        author_user_id: UUID | None,
        suggestion_text: str,
    ) -> PromptSuggestion:
        suggestion = PromptSuggestion(
            locality_id=locality_id,
            author_user_id=author_user_id,
            suggestion_text=suggestion_text,
            status=PromptSuggestionStatus.PENDING,
        )
        self._session.add(suggestion)
        await self._session.commit()
        await self._session.refresh(suggestion)
        return suggestion

    async def list(
        self,
        status: PromptSuggestionStatus | None,
        page: int,
        page_size: int,
    ) -> tuple[list[PromptSuggestion], int]:
        query = select(PromptSuggestion)
        count_query = select(func.count(PromptSuggestion.id))
        if status is not None:
            query = query.where(PromptSuggestion.status == status)
            count_query = count_query.where(PromptSuggestion.status == status)

        total_result = await self._session.execute(count_query)
        total_items = int(total_result.scalar() or 0)

        result = await self._session.execute(
            query.order_by(PromptSuggestion.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars()), total_items

    async def get_by_id(self, suggestion_id: UUID) -> PromptSuggestion | None:
        result = await self._session.execute(
            select(PromptSuggestion).where(PromptSuggestion.id == suggestion_id)
        )
        return result.scalar_one_or_none()

    async def review(
        self,
        suggestion: PromptSuggestion,
        status: PromptSuggestionStatus,
        reviewed_by_user_id: UUID | None,
    ) -> PromptSuggestion:
        suggestion.status = status
        suggestion.reviewed_by_user_id = reviewed_by_user_id
        suggestion.reviewed_at = datetime.utcnow()
        await self._session.commit()
        await self._session.refresh(suggestion)
        return suggestion


class PendingResultRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_request_id(self, ai_request_id: UUID) -> PendingAiResult | None:
        result = await self._session.execute(
            select(PendingAiResult).where(PendingAiResult.ai_request_id == ai_request_id)
        )
        return result.scalar_one_or_none()

    async def create(self, ai_request_id: UUID, generated_comment: str) -> PendingAiResult:
        pending = PendingAiResult(ai_request_id=ai_request_id, generated_comment=generated_comment)
        self._session.add(pending)
        await self._session.commit()
        await self._session.refresh(pending)
        return pending

    async def delete(self, pending: PendingAiResult) -> None:
        await self._session.delete(pending)
        await self._session.commit()
