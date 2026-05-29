from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import Uuid


class Base(DeclarativeBase):
    pass


class PromptSuggestionStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class LocalityPrompt(Base):
    __tablename__ = "locality_ai_prompts"

    locality_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    prompt_text: Mapped[str] = mapped_column(Text)
    created_by_user_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    updated_by_user_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class PromptSuggestion(Base):
    __tablename__ = "prompt_suggestions"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    locality_id: Mapped[UUID] = mapped_column(Uuid)
    author_user_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    suggestion_text: Mapped[str] = mapped_column(Text)
    status: Mapped[PromptSuggestionStatus] = mapped_column(
        Enum(PromptSuggestionStatus, name="prompt_suggestion_status"),
        default=PromptSuggestionStatus.PENDING,
    )
    reviewed_by_user_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PendingAiResult(Base):
    __tablename__ = "pending_ai_results"

    ai_request_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    generated_comment: Mapped[str] = mapped_column(Text)
