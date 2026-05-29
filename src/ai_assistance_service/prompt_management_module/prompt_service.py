from uuid import UUID

from ai_assistance_service.exceptions import PromptAlreadyExistsError, PromptNotFoundError
from ai_assistance_service.observability_module.logger import get_logger
from ai_assistance_service.persistence_module.repositories import PromptRepository


class PromptService:
    def __init__(self, repository: PromptRepository) -> None:
        self._repository = repository
        self._logger = get_logger()

    async def get_prompt(self, locality_id: UUID):
        prompt = await self._repository.get_by_locality(locality_id)
        if prompt is None:
            raise PromptNotFoundError(locality_id)
        return prompt

    async def create_prompt(self, locality_id: UUID, prompt_text: str, user_id: UUID | None):
        existing = await self._repository.get_by_locality(locality_id)
        if existing is not None:
            raise PromptAlreadyExistsError(locality_id)

        prompt = await self._repository.create(locality_id, prompt_text, user_id)
        self._logger.info("prompt_created", locality_id=str(locality_id))
        return prompt

    async def update_prompt(self, locality_id: UUID, prompt_text: str, user_id: UUID | None):
        prompt = await self._repository.get_by_locality(locality_id)
        if prompt is None:
            raise PromptNotFoundError(locality_id)

        prompt = await self._repository.update(prompt, prompt_text, user_id)
        self._logger.info("prompt_updated", locality_id=str(locality_id))
        return prompt
