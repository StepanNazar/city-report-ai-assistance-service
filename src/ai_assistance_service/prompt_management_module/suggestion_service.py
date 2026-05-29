from uuid import UUID

from ai_assistance_service.exceptions import SuggestionNotFoundError
from ai_assistance_service.observability_module.logger import get_logger
from ai_assistance_service.persistence_module.models import PromptSuggestionStatus
from ai_assistance_service.persistence_module.repositories import SuggestionRepository


class SuggestionService:
    def __init__(self, repository: SuggestionRepository) -> None:
        self._repository = repository
        self._logger = get_logger()

    async def create_suggestion(
        self, locality_id: UUID, suggestion_text: str, author_user_id: UUID | None
    ):
        suggestion = await self._repository.create(locality_id, author_user_id, suggestion_text)
        self._logger.info("prompt_suggestion_submitted", suggestion_id=str(suggestion.id))
        return suggestion

    async def list_suggestions(
        self,
        status: PromptSuggestionStatus | None,
        page: int,
        page_size: int,
    ):
        suggestions, total_items = await self._repository.list(status, page, page_size)
        total_pages = max(1, (total_items + page_size - 1) // page_size)
        return suggestions, total_items, total_pages

    async def review_suggestion(
        self,
        suggestion_id: UUID,
        status: PromptSuggestionStatus,
        reviewer_user_id: UUID | None,
    ):
        suggestion = await self._repository.get_by_id(suggestion_id)
        if suggestion is None:
            raise SuggestionNotFoundError(suggestion_id)

        suggestion = await self._repository.review(suggestion, status, reviewer_user_id)
        self._logger.info("prompt_suggestion_reviewed", suggestion_id=str(suggestion.id))
        return suggestion
