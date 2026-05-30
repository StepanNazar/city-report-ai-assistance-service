from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI


class LlmClient(Protocol):
    async def generate_comment(
        self, locality_prompt: str, report_title: str, report_description: str
    ) -> str:
        ...


@dataclass(frozen=True)
class GeminiLlmClient:
    api_key: str
    model: str

    async def generate_comment(
        self, locality_prompt: str, report_title: str, report_description: str
    ) -> str:
        llm = ChatGoogleGenerativeAI(model=self.model, google_api_key=self.api_key)
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a city assistance advisor. Use the locality prompt and report data to draft a helpful public recommendation.",
                ),
                (
                    "human",
                    "Locality prompt: {locality_prompt}\nReport title: {report_title}\nReport description: {report_description}",
                ),
            ]
        )
        chain = prompt | llm | StrOutputParser()
        return await chain.ainvoke(
            {
                "locality_prompt": locality_prompt,
                "report_title": report_title,
                "report_description": report_description,
            }
        )
