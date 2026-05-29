from uuid import uuid4

import pytest

from ai_assistance_service.persistence_module.models import LocalityPrompt


class TestGetPrompt:
    @pytest.mark.asyncio
    async def test_returns_404_when_prompt_missing(self, client) -> None:
        locality_id = uuid4()

        response = await client.get(
            f"/api/v1/prompts/{locality_id}",
            headers={"X-User-Role": "MODERATOR"},
        )

        assert response.status_code == 404


class TestPostPrompt:
    @pytest.mark.asyncio
    async def test_creates_prompt_for_moderator(self, client) -> None:
        locality_id = uuid4()
        payload = {"promptText": "Use local hotline."}

        response = await client.post(
            f"/api/v1/prompts/{locality_id}",
            json=payload,
            headers={"X-User-Role": "MODERATOR", "X-User-Id": str(uuid4())},
        )

        assert response.status_code == 201
        assert response.json()["localityId"] == str(locality_id)

    @pytest.mark.asyncio
    async def test_returns_403_for_user_role(self, client) -> None:
        locality_id = uuid4()
        payload = {"promptText": "Use local hotline."}

        response = await client.post(
            f"/api/v1/prompts/{locality_id}",
            json=payload,
            headers={"X-User-Role": "USER"},
        )

        assert response.status_code == 403


class TestPutPrompt:
    @pytest.mark.asyncio
    async def test_updates_existing_prompt(self, client, session) -> None:
        locality_id = uuid4()
        user_id = uuid4()
        session.add(
            LocalityPrompt(
                locality_id=locality_id,
                prompt_text="Old prompt",
                created_by_user_id=user_id,
                updated_by_user_id=user_id,
            )
        )
        await session.commit()
        payload = {"promptText": "New prompt"}

        response = await client.put(
            f"/api/v1/prompts/{locality_id}",
            json=payload,
            headers={"X-User-Role": "ADMIN", "X-User-Id": str(uuid4())},
        )

        assert response.status_code == 200
        assert response.json()["promptText"] == "New prompt"

    @pytest.mark.asyncio
    async def test_returns_404_when_prompt_missing(self, client) -> None:
        locality_id = uuid4()
        payload = {"promptText": "New prompt"}

        response = await client.put(
            f"/api/v1/prompts/{locality_id}",
            json=payload,
            headers={"X-User-Role": "ADMIN"},
        )

        assert response.status_code == 404
