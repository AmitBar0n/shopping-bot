from telegram import Bot
from config import AMIT_ID, PARTNER_ID


async def notify_other(bot: Bot, sender_id: int, message: str) -> None:
    """Send message to the user who is NOT the sender."""
    target_id = PARTNER_ID if sender_id == AMIT_ID else AMIT_ID
    try:
        await bot.send_message(chat_id=target_id, text=message)
    except Exception:
        pass  # Don't crash the bot if notification fails
