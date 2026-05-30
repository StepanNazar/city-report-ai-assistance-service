from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AiCommentRequested(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    ai_request_id: UUID = Field(alias="aiRequestId")
    report_id: UUID = Field(alias="reportId")
    locality_id: UUID = Field(alias="localityId")
    report_title: str = Field(alias="reportTitle")
    report_description: str = Field(alias="reportDescription")


class AiCommentGenerated(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    ai_request_id: UUID = Field(alias="aiRequestId")
    report_id: UUID = Field(alias="reportId")
    generated_comment: str = Field(alias="generatedComment")
