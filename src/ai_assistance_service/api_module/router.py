from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ai_assistance_service.api_module.dependencies import UserRole, require_roles
from ai_assistance_service.api_module.schemas import (
    CreatePromptRequest,
    CreatePromptSuggestionRequest,
    HealthResponse,
    LocalityPromptResponse,
    PaginatedPromptSuggestionsResponse,
    PromptSuggestionResponse,
    ReviewPromptSuggestionRequest,
    UpdatePromptRequest,
)
from ai_assistance_service.exceptions import PromptAlreadyExistsError, PromptNotFoundError, SuggestionNotFoundError
from ai_assistance_service.persistence_module.database import get_session
from ai_assistance_service.persistence_module.models import PromptSuggestionStatus
from ai_assistance_service.persistence_module.repositories import PromptRepository, SuggestionRepository
from ai_assistance_service.prompt_management_module.prompt_service import PromptService
from ai_assistance_service.prompt_management_module.suggestion_service import SuggestionService

router = APIRouter()


def get_prompt_service(session: AsyncSession = Depends(get_session)) -> PromptService:
    return PromptService(PromptRepository(session))


def get_suggestion_service(session: AsyncSession = Depends(get_session)) -> SuggestionService:
    return SuggestionService(SuggestionRepository(session))


@router.get(
    "/health",
    response_model=HealthResponse,
)
async def health_check(
    _: object = Depends(require_roles(UserRole.USER, UserRole.MODERATOR, UserRole.ADMIN)),
) -> HealthResponse:
    return HealthResponse(status="ok")


@router.get(
    "/prompts/{locality_id}",
    response_model=LocalityPromptResponse,
)
async def retrieve_prompt(
    locality_id: UUID,
    service: PromptService = Depends(get_prompt_service),
    _: object = Depends(require_roles(UserRole.MODERATOR, UserRole.ADMIN)),
) -> LocalityPromptResponse:
    try:
        prompt = await service.get_prompt(locality_id)
    except PromptNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return LocalityPromptResponse.model_validate(
        {
            "id": prompt.locality_id,
            "localityId": prompt.locality_id,
            "promptText": prompt.prompt_text,
            "createdByUserId": prompt.created_by_user_id,
            "updatedByUserId": prompt.updated_by_user_id,
            "createdAt": prompt.created_at,
            "updatedAt": prompt.updated_at,
        }
    )


@router.post(
    "/prompts/{locality_id}",
    response_model=LocalityPromptResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_prompt(
    locality_id: UUID,
    payload: CreatePromptRequest,
    service: PromptService = Depends(get_prompt_service),
    context=Depends(require_roles(UserRole.MODERATOR, UserRole.ADMIN)),
) -> LocalityPromptResponse:
    try:
        prompt = await service.create_prompt(locality_id, payload.prompt_text, context.user_id)
    except PromptAlreadyExistsError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return LocalityPromptResponse.model_validate(
        {
            "id": prompt.locality_id,
            "localityId": prompt.locality_id,
            "promptText": prompt.prompt_text,
            "createdByUserId": prompt.created_by_user_id,
            "updatedByUserId": prompt.updated_by_user_id,
            "createdAt": prompt.created_at,
            "updatedAt": prompt.updated_at,
        }
    )


@router.put(
    "/prompts/{locality_id}",
    response_model=LocalityPromptResponse,
)
async def update_prompt(
    locality_id: UUID,
    payload: UpdatePromptRequest,
    service: PromptService = Depends(get_prompt_service),
    context=Depends(require_roles(UserRole.MODERATOR, UserRole.ADMIN)),
) -> LocalityPromptResponse:
    try:
        prompt = await service.update_prompt(locality_id, payload.prompt_text, context.user_id)
    except PromptNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return LocalityPromptResponse.model_validate(
        {
            "id": prompt.locality_id,
            "localityId": prompt.locality_id,
            "promptText": prompt.prompt_text,
            "createdByUserId": prompt.created_by_user_id,
            "updatedByUserId": prompt.updated_by_user_id,
            "createdAt": prompt.created_at,
            "updatedAt": prompt.updated_at,
        }
    )


@router.post(
    "/prompt-suggestions",
    response_model=PromptSuggestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_prompt_suggestion(
    payload: CreatePromptSuggestionRequest,
    service: SuggestionService = Depends(get_suggestion_service),
    context=Depends(require_roles(UserRole.USER, UserRole.ADMIN)),
) -> PromptSuggestionResponse:
    suggestion = await service.create_suggestion(
        payload.locality_id,
        payload.suggestion_text,
        context.user_id,
    )
    return PromptSuggestionResponse.model_validate(suggestion)


@router.get(
    "/prompt-suggestions",
    response_model=PaginatedPromptSuggestionsResponse,
)
async def retrieve_prompt_suggestions(
    status: PromptSuggestionStatus | None = None,
    page: int = 1,
    page_size: int = 20,
    service: SuggestionService = Depends(get_suggestion_service),
    _: object = Depends(require_roles(UserRole.MODERATOR, UserRole.ADMIN)),
) -> PaginatedPromptSuggestionsResponse:
    page_size = min(max(page_size, 1), 100)
    page = max(page, 1)

    suggestions, total_items, total_pages = await service.list_suggestions(status, page, page_size)

    return PaginatedPromptSuggestionsResponse(
        items=[PromptSuggestionResponse.model_validate(item) for item in suggestions],
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
    )


@router.patch(
    "/prompt-suggestions/{suggestion_id}/review",
    response_model=PromptSuggestionResponse,
)
async def review_prompt_suggestion(
    suggestion_id: UUID,
    payload: ReviewPromptSuggestionRequest,
    service: SuggestionService = Depends(get_suggestion_service),
    context=Depends(require_roles(UserRole.MODERATOR, UserRole.ADMIN)),
) -> PromptSuggestionResponse:
    try:
        suggestion = await service.review_suggestion(
            suggestion_id,
            payload.status,
            context.user_id,
        )
    except SuggestionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return PromptSuggestionResponse.model_validate(suggestion)
