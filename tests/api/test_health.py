import pytest
from httpx import AsyncClient


class TestGetHealth:
    @pytest.mark.asyncio
    async def test_returns_ok_for_user_role(self, client: AsyncClient) -> None:
        headers = {"X-User-Role": "USER"}

        response = await client.get("/api/v1/health", headers=headers)

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
