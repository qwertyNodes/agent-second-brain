"""Telegram bot initialization and polling."""

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from d_brain.config import Settings

logger = logging.getLogger(__name__)


def create_bot(settings: Settings) -> Bot:
    """Create and configure the Telegram bot."""
    return Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    """Create and configure the dispatcher with routers."""
    from d_brain.bot.handlers import buttons, chat, commands, do, document, forward, photo, process, remind, text, voice, weekly

    # Use memory storage for FSM (required for /do and chat state)
    dp = Dispatcher(storage=MemoryStorage())

    # Register routers - ORDER MATTERS
    dp.include_router(commands.router)
    dp.include_router(process.router)
    dp.include_router(weekly.router)
    dp.include_router(do.router)    # DoCommandState.waiting_for_input — before voice/text
    dp.include_router(chat.router)  # ChatState.active — before buttons/voice/text
    dp.include_router(buttons.router)  # Reply keyboard buttons
    dp.include_router(voice.router)
    dp.include_router(photo.router)
    dp.include_router(forward.router)
    dp.include_router(document.router)  # .md file uploads — before text catch-all
    dp.include_router(remind.router)    # /remind command
    dp.include_router(text.router)  # Must be last (catch-all for text)
    return dp


MiddlewareHandler = Callable[[Update, dict[str, Any]], Awaitable[Any]]
MiddlewareType = Callable[[MiddlewareHandler, Update, dict[str, Any]], Awaitable[Any]]


def create_auth_middleware(settings: Settings) -> MiddlewareType:
    """Create middleware to check user authorization."""

    async def auth_middleware(
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        # If explicitly allowed all users, just bypass check
        if settings.allow_all_users:
            return await handler(event, data)

        user = None
        if event.message:
            user = event.message.from_user
        elif event.callback_query:
            user = event.callback_query.from_user

        # If no users allowed and not allow_all_users -> deny everyone
        if not settings.allowed_user_ids:
            logger.warning("Access denied: no allowed_user_ids configured and allow_all_users is False")
            return None

        # Check if user is in allowed list
        if user and user.id not in settings.allowed_user_ids:
            logger.warning("Unauthorized access attempt from user %s", user.id)
            return None

        return await handler(event, data)

    return auth_middleware


def create_scheduler(bot: Bot, settings: Settings) -> AsyncIOScheduler:
    """Create APScheduler with reminder delivery job."""
    from d_brain.services.reminder import ReminderStorage

    scheduler = AsyncIOScheduler()

    async def check_reminders() -> None:
        """Check for due reminders and send them via bot."""
        storage = ReminderStorage(settings.vault_path)
        for reminder in storage.get_due():
            try:
                await bot.send_message(
                    chat_id=reminder["user_id"],
                    text=f"⏰ <b>Напоминание</b>\n\n{reminder['text']}",
                )
                storage.mark_sent(reminder["id"])
                logger.info("Sent reminder %s to user %s", reminder["id"], reminder["user_id"])
            except Exception:
                logger.exception("Failed to send reminder %s", reminder["id"])
                # Not marked as sent — will retry next cycle

    scheduler.add_job(
        check_reminders,
        trigger="interval",
        minutes=1,
        id="check_reminders",
        replace_existing=True,
    )
    return scheduler


async def run_bot(settings: Settings) -> None:
    """Run the bot with polling."""
    bot = create_bot(settings)
    dp = create_dispatcher()

    # Always add auth middleware for security (it handles allow_all_users internally)
    dp.update.middleware(create_auth_middleware(settings))

    # Start reminder scheduler
    scheduler = create_scheduler(bot, settings)
    scheduler.start()
    logger.info("Reminder scheduler started (checking every minute)")

    logger.info("Starting bot polling...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()
