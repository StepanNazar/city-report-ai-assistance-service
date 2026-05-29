from __future__ import annotations

import json
from typing import Protocol

from aiokafka import AIOKafkaProducer

from ai_assistance_service.ai_processing_module.schemas import AiCommentGenerated


class AiCommentProducer(Protocol):
    async def send(self, event: AiCommentGenerated) -> None:
        ...


class KafkaAiCommentProducer:
    def __init__(self, bootstrap_servers: str, topic: str) -> None:
        self._producer = AIOKafkaProducer(bootstrap_servers=bootstrap_servers)
        self._topic = topic

    async def start(self) -> None:
        await self._producer.start()

    async def stop(self) -> None:
        await self._producer.stop()

    async def send(self, event: AiCommentGenerated) -> None:
        payload = event.model_dump(by_alias=True)
        await self._producer.send_and_wait(self._topic, json.dumps(payload).encode("utf-8"))
