import asyncio
from pathlib import Path
import sys
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import telegram_checker.checker as checker_module
from telegram_checker.checker import SmartCheckStrategy


class FakePhoneNumberBannedError(Exception):
    pass


class BannedPhoneClient:
    async def __call__(self, _request):
        raise FakePhoneNumberBannedError("PHONE_NUMBER_BANNED")


def test_banned_target_number_does_not_disable_checker(monkeypatch):
    disabled_accounts = []

    async def disable_account(account_id):
        disabled_accounts.append(account_id)

    monkeypatch.setattr(checker_module, "PhoneNumberBannedError", FakePhoneNumberBannedError)
    monkeypatch.setattr(
        checker_module.types,
        "InputPhoneContact",
        lambda **_kwargs: object(),
    )
    monkeypatch.setattr(
        checker_module.functions,
        "contacts",
        SimpleNamespace(ImportContactsRequest=lambda **_kwargs: object()),
    )
    monkeypatch.setattr(checker_module.account_manager, "disable_account", disable_account)

    result = asyncio.run(
        SmartCheckStrategy().check(
            BannedPhoneClient(),
            "+15550000000",
            {"id": 7, "api_id": 1, "api_hash": "hash"},
        )
    )

    assert result["status"] == "BANNED"
    assert disabled_accounts == []
