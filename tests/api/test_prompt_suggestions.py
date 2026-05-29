from uuid import uuid4

import pytest

from ai_assistance_service.persistence_module.models import PromptSuggestion, PromptSuggestionStatus


class TestPostPromptSuggestion:
    @pytest.mark.asyncio
    async def test_creates_pending_suggestion(self, client) -> None:
        payload = {"localityId": str(uuid4()), "suggestionText": "Local advice"}

        response = await client.post(
            "/api/v1/prompt-suggestions",
            json=payload,
            headers={"X-User-Role": "USER", "X-User-Id": str(uuid4())},
        )

        assert response.status_code == 201
        assert response.json()["status"] == "PENDING"


class TestGetPromptSuggestions:
    @pytest.mark.asyncio
    async def test_returns_paginated_results(self, client, session) -> None:
        suggestion = PromptSuggestion(
            locality_id=uuid4(),
            author_user_id=uuid4(),
            suggestion_text="Advice",
            status=PromptSuggestionStatus.PENDING,
        )
        session.add(suggestion)
        await session.commit()

        response = await client.get(
            "/api/v1/prompt-suggestions",
            headers={"X-User-Role": "MODERATOR"},
        )

        assert response.status_code == 200
        assert response.json()["totalItems"] == 1


class TestPatchPromptSuggestionReview:
    @pytest.mark.asyncio
    async def test_updates_status(self, client, session) -> None:
        suggestion = PromptSuggestion(
            locality_id=uuid4(),
            author_user_id=uuid4(),
            suggestion_text="Advice",
            status=PromptSuggestionStatus.PENDING,
        )
        session.add(suggestion)
        await session.commit()
        payload = {"status": "APPROVED"}

        response = await client.patch(
            f"/api/v1/prompt-suggestions/{suggestion.id}/review",
            json=payload,
            headers={"X-User-Role": "MODERATOR", "X-User-Id": str(uuid4())},
        )

        assert response.status_code == 200
        assert response.json()["status"] == "APPROVED"
