from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import user_bot


def test_checker_unavailable_warning_is_rate_limited(monkeypatch):
    monkeypatch.setattr(user_bot, "_checker_unavailable_log_ts", {})

    assert user_bot._should_log_checker_unavailable(42, now=100.0)
    assert not user_bot._should_log_checker_unavailable(42, now=159.9)
    assert user_bot._should_log_checker_unavailable(42, now=160.0)
