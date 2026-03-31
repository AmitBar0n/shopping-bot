import pytest
import os
import sys
from unittest.mock import AsyncMock
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


@pytest.mark.asyncio
async def test_notify_sends_to_partner(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "x")
    monkeypatch.setenv("AMIT_ID", "100")
    monkeypatch.setenv("PARTNER_ID", "200")
    monkeypatch.setenv("AMIT_NAME", "עמית")
    monkeypatch.setenv("PARTNER_NAME", "ירדן")
    import importlib
    import config
    import notifications
    importlib.reload(config)
    importlib.reload(notifications)

    mock_bot = AsyncMock()
    await notifications.notify_other(mock_bot, sender_id=100, message="בדיקה")
    mock_bot.send_message.assert_awaited_once_with(chat_id=200, text="בדיקה")


@pytest.mark.asyncio
async def test_notify_sends_to_amit(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "x")
    monkeypatch.setenv("AMIT_ID", "100")
    monkeypatch.setenv("PARTNER_ID", "200")
    monkeypatch.setenv("AMIT_NAME", "עמית")
    monkeypatch.setenv("PARTNER_NAME", "ירדן")
    import importlib
    import config
    import notifications
    importlib.reload(config)
    importlib.reload(notifications)

    mock_bot = AsyncMock()
    await notifications.notify_other(mock_bot, sender_id=200, message="בדיקה")
    mock_bot.send_message.assert_awaited_once_with(chat_id=100, text="בדיקה")
