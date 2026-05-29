from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from ai_assistance_service.persistence_module.models import PromptSuggestionStatus


class CreatePromptRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    prompt_text: str = Field(alias="promptText", min_length=1, max_length=10000)


class UpdatePromptRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    prompt_text: str = Field(alias="promptText", min_length=1, max_length=10000)


class LocalityPromptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    locality_id: UUID = Field(alias="localityId")
    prompt_text: str = Field(alias="promptText")
    created_by_user_id: UUID | None = Field(alias="createdByUserId")
    updated_by_user_id: UUID | None = Field(alias="updatedByUserId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class CreatePromptSuggestionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    locality_id: UUID = Field(alias="localityId")
    suggestion_text: str = Field(alias="suggestionText", min_length=1, max_length=5000)


class ReviewPromptSuggestionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    status: PromptSuggestionStatus


class PromptSuggestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    locality_id: UUID = Field(alias="localityId")
    author_user_id: UUID | None = Field(alias="authorUserId")
    suggestion_text: str = Field(alias="suggestionText")
    status: PromptSuggestionStatus
    reviewed_by_user_id: UUID | None = Field(alias="reviewedByUserId")
    reviewed_at: datetime | None = Field(alias="reviewedAt")
    created_at: datetime = Field(alias="createdAt")


class PaginatedPromptSuggestionsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[PromptSuggestionResponse]
    page: int
    page_size: int = Field(alias="pageSize")
    total_items: int = Field(alias="totalItems")
    total_pages: int = Field(alias="totalPages")


class HealthResponse(BaseModel):
    status: str
