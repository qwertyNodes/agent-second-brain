"""Markdown document upload handler."""

import logging
from datetime import datetime

from aiogram import Bot, Router
from aiogram.types import Message

from d_brain.config import get_settings
from d_brain.services.docs import DocsStorage
from d_brain.services.session import SessionStore
from d_brain.services.storage import VaultStorage

router = Router(name="document")
logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 5_000_000  # 5 MB


@router.message(
    lambda m: (
        m.document is not None
        and m.document.file_name is not None
        and m.document.file_name.endswith(".md")
    )
)
async def handle_document(message: Message, bot: Bot) -> None:
    """Handle .md document uploads — save to vault/docs/ and index."""
    if not message.document or not message.from_user:
        return

    if message.document.file_size and message.document.file_size > MAX_FILE_SIZE:
        await message.answer("❌ Файл слишком большой (максимум 5 МБ)")
        return

    try:
        file = await bot.get_file(message.document.file_id)
        if not file.file_path:
            await message.answer("❌ Не удалось скачать файл")
            return

        file_bytes_io = await bot.download_file(file.file_path)
        if not file_bytes_io:
            await message.answer("❌ Не удалось скачать файл")
            return

        content = file_bytes_io.read()
        timestamp = datetime.fromtimestamp(message.date.timestamp())
        day = timestamp.date()
        original_filename = message.document.file_name  # already checked not None

        settings = get_settings()
        docs = DocsStorage(settings.vault_path)
        saved_filename, title = docs.save_doc(
            content,
            original_filename,
            day,
            timestamp,
            caption=message.caption,
        )

        # Add wiki-link entry to daily file
        storage = VaultStorage(settings.vault_path)
        daily_content = f"[[docs/{saved_filename}]]"
        if message.caption:
            daily_content += f"\n\n{message.caption}"
        storage.append_to_daily(daily_content, timestamp, "[doc]")

        # Log to session
        session = SessionStore(settings.vault_path)
        session.append(
            message.from_user.id,
            "doc",
            filename=saved_filename,
            title=title,
            caption=message.caption,
            msg_id=message.message_id,
        )

        await message.answer(f"📄 Сохранено: <b>{title}</b>")
        logger.info("Document saved: %s", saved_filename)

    except Exception as e:
        logger.exception("Error processing document")
        await message.answer(f"❌ Ошибка при сохранении файла: {e}")
