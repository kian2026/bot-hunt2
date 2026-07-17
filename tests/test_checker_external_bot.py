import asyncio
import datetime
from pathlib import Path
import sys
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from telegram_checker.checker import SmartCheckStrategy
import telegram_checker.checker as checker_module


class ExternalBotClient:
    def __init__(self):
        self.events = []

    async def send_message(self, _bot_username, phone):
        self.events.append(("send", phone))

    async def get_messages(self, _bot_username, limit):
        self.events.append(("read", limit))
        return [
            SimpleNamespace(
                out=False,
                date=datetime.datetime.now(datetime.timezone.utc),
                text="📊 ✅",
            )
        ]


def test_external_bot_checks_are_serialized_for_a_shared_client(monkeypatch):
    original_sleep = asyncio.sleep

    async def yield_immediately(_seconds):
        await original_sleep(0)

    monkeypatch.setattr(checker_module.asyncio, "sleep", yield_immediately)
    strategy = SmartCheckStrategy()
    client = ExternalBotClient()

    async def run_checks():
        return await asyncio.gather(
            strategy._check_via_external_bot(client, "+100", "checker_bot"),
            strategy._check_via_external_bot(client, "+200", "checker_bot"),
        )

    results = asyncio.run(run_checks())

    assert [result["phone"] for result in results] == ["+100", "+200"]
    assert client.events == [
        ("send", "+100"),
        ("read", 3),
        ("send", "+200"),
        ("read", 3),
    ]
