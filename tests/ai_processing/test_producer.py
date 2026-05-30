from __future__ import annotations

import json
from uuid import uuid4

import pytest

from ai_assistance_service.ai_processing_module import producer as producer_module
from ai_assistance_service.ai_processing_module.producer import KafkaAiCommentProducer
from ai_assistance_service.ai_processing_module.schemas import AiCommentGenerated


class FakeAIOKafkaProducer:
    def __init__(self, bootstrap_servers: str) -> None:
        self.bootstrap_servers = bootstrap_servers
        self.started = False
        self.stopped = False
        self.sent_messages: list[tuple[str, bytes]] = []

    async def start(self) -> None:
        self.started = True

    async def stop(self) -> None:
        self.stopped = True

    async def send_and_wait(self, topic: str, payload: bytes) -> None:
        self.sent_messages.append((topic, payload))


@pytest.mark.asyncio
async def test_send_serializes_uuid_fields_as_json_strings(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_producer = FakeAIOKafkaProducer("kafka:29092")
    monkeypatch.setattr(producer_module, "AIOKafkaProducer", lambda bootstrap_servers: fake_producer)

    producer = KafkaAiCommentProducer("kafka:29092", "ai.comment.generated")
    event = AiCommentGenerated(
        aiRequestId=uuid4(),
        reportId=uuid4(),
        generatedComment="Generated comment",
    )

    await producer.send(event)

    assert len(fake_producer.sent_messages) == 1
    topic, raw_payload = fake_producer.sent_messages[0]
    assert topic == "ai.comment.generated"

    payload = json.loads(raw_payload.decode("utf-8"))
    assert isinstance(payload["aiRequestId"], str)
    assert isinstance(payload["reportId"], str)
    assert payload["generatedComment"] == "Generated comment"


