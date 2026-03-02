"""Text message handler."""

import logging
from datetime import datetime

from aiogram import Router
from aiogram.types import Message

from d_brain.config import get_settings
from d_brain.services.session import SessionStore
from d_brain.services.storage import VaultStorage

router = Router(name="text")
logger = logging.getLogger(__name__)


@router.message(lambda m: m.text is not None and not m.text.startswith("/"))
async def handle_text(message: Message) -> None:
    """Handle text messages (excluding commands)."""
    if not message.text or not message.from_user:
        return

    settings = get_settings()
    storage = VaultStorage(settings.vault_path)

    timestamp = datetime.fromtimestamp(message.date.timestamp())

    # Extract quoted context if user replied to a message
    quote: str | None = None
    if message.reply_to_message:
        quote = message.reply_to_message.text or message.reply_to_message.caption

    if quote:
        content = f"> {quote}\n\n{message.text}"
        msg_type = "[text, цитата]"
    else:
        content = message.text
        msg_type = "[text]"

    storage.append_to_daily(content, timestamp, msg_type)

    # Log to session
    session = SessionStore(settings.vault_path)
    session.append(
        message.from_user.id,
        "text",
        text=message.text,
        quoted=quote,
        msg_id=message.message_id,
    )

    response = "✓ Сохранено (с цитатой)" if quote else "✓ Сохранено"
    await message.answer(response)
    logger.info("Text message saved: %d chars", len(message.text))
