"""Free conversational chat mode handler."""

import asyncio
import logging

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from d_brain.bot.formatters import format_process_report
from d_brain.bot.states import ChatState
from d_brain.config import get_settings
from d_brain.services.processor import ClaudeProcessor
from d_brain.services.session import SessionStore
from d_brain.services.transcription import DeepgramTranscriber

router = Router(name="chat")
logger = logging.getLogger(__name__)


def _get_end_chat_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard with end session button."""
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="✅ Завершить сессию", callback_data="end_chat")
        ]]
    )


@router.message(ChatState.active)
async def handle_chat_message(message: Message, bot: Bot, state: FSMContext) -> None:
    """Handle messages in free chat mode — route to Claude."""
    if not message.from_user:
        return

    user_id = message.from_user.id
    prompt: str | None = None

    # Handle voice in chat mode
    if message.voice:
        await message.chat.do(action="typing")
        settings = get_settings()
        transcriber = DeepgramTranscriber(settings.deepgram_api_key)
        try:
            file = await bot.get_file(message.voice.file_id)
            if not file.file_path:
                await message.answer("❌ Не удалось скачать голосовое")
                return
            file_bytes = await bot.download_file(file.file_path)
            if not file_bytes:
                await message.answer("❌ Не удалось скачать голосовое")
                return
            audio_bytes = file_bytes.read()
            prompt = await transcriber.transcribe(audio_bytes)
            if not prompt:
                await message.answer("❌ Не удалось распознать речь")
                return
            await message.answer(f"🎤 <i>{prompt}</i>")
        except Exception as e:
            logger.exception("Failed to transcribe voice in chat mode")
            await message.answer(f"❌ Ошибка транскрипции: {e}")
            return

    elif message.text:
        prompt = message.text

    else:
        await message.answer("❌ В режиме диалога можно отправлять текст или голосовые сообщения")
        return

    # Include quoted context if user replied to a bot message
    quote: str | None = None
    if message.reply_to_message:
        quote = message.reply_to_message.text or message.reply_to_message.caption
    if quote:
        full_prompt = f"[Контекст из предыдущего ответа: {quote}]\n\n{prompt}"
    else:
        full_prompt = prompt

    await message.chat.do(action="typing")
    status_msg = await message.answer("⏳ Думаю...")

    settings = get_settings()
    processor = ClaudeProcessor(settings.vault_path, settings.todoist_api_key)

    report = await asyncio.to_thread(processor.execute_prompt, full_prompt, user_id)

    # Save any scheduled reminders from Claude's response
    if report.get("reminders") and message.from_user:
        _save_reminders(report["reminders"], user_id, settings.vault_path)

    formatted = format_process_report(report)
    try:
        await status_msg.edit_text(formatted, reply_markup=_get_end_chat_keyboard())
    except Exception:
        await status_msg.edit_text(formatted, parse_mode=None, reply_markup=_get_end_chat_keyboard())

    # Log to session
    session = SessionStore(settings.vault_path)
    session.append(user_id, "chat", text=prompt, msg_id=message.message_id)


@router.callback_query(F.data == "end_chat")
async def callback_end_chat(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle end chat session button."""
    await state.clear()
    if callback.message:
        await callback.message.answer("💬 Сессия завершена. Режим сохранения включён.")
    await callback.answer()


def _save_reminders(reminders: list[tuple[str, str]], user_id: int, vault_path: object) -> None:
    """Save extracted reminders from Claude response. Gracefully ignores errors."""
    try:
        from pathlib import Path

        from d_brain.services.reminder import ReminderStorage, parse_reminder_datetime

        storage = ReminderStorage(Path(str(vault_path)))
        for dt_str, text in reminders:
            dt = parse_reminder_datetime(dt_str)
            if dt:
                storage.add_reminder(user_id, dt, text)
    except Exception:
        logger.exception("Failed to save reminders from chat response")
