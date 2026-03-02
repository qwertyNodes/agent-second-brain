"""Handler for /remind command — explicit reminder scheduling."""

import logging

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from d_brain.config import get_settings
from d_brain.services.reminder import ReminderStorage, parse_reminder_datetime

router = Router(name="remind")
logger = logging.getLogger(__name__)


@router.message(Command("remind"))
async def cmd_remind(message: Message, command: CommandObject) -> None:
    """Schedule a reminder.

    Usage: /remind HH:MM текст напоминания
    Example: /remind 21:00 Позвонить Ивану
    """
    if not message.from_user:
        return

    if not command.args:
        await message.answer(
            "⏰ <b>Напоминание</b>\n\n"
            "Использование: /remind HH:MM текст\n"
            "Пример: /remind 21:00 Позвонить Ивану\n\n"
            "Или скажи в режиме <b>✨ Запрос</b>:\n"
            "«Напомни в 21:00 позвонить Ивану»"
        )
        return

    parts = command.args.split(None, 1)
    if len(parts) < 2:
        await message.answer(
            "❌ Укажи время и текст напоминания\n"
            "Пример: /remind 21:00 Позвонить Ивану"
        )
        return

    time_str, reminder_text = parts[0], parts[1]
    remind_at = parse_reminder_datetime(time_str)

    if remind_at is None:
        await message.answer(
            f"❌ Не удалось распознать время: <code>{time_str}</code>\n"
            "Используй формат HH:MM, например: 21:00"
        )
        return

    settings = get_settings()
    storage = ReminderStorage(settings.vault_path)
    reminder_id = storage.add_reminder(message.from_user.id, remind_at, reminder_text)

    time_formatted = remind_at.strftime("%H:%M")
    await message.answer(
        f"⏰ Напоминание установлено на <b>{time_formatted}</b>\n"
        f"<i>{reminder_text}</i>\n\n"
        f"ID: <code>{reminder_id}</code>"
    )
    logger.info("Reminder %s set for user %s at %s", reminder_id, message.from_user.id, remind_at)
