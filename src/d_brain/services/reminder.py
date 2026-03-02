"""Reminder service for scheduled bot messages."""

import json
import logging
import re
import uuid
from datetime import date, datetime
from pathlib import Path

logger = logging.getLogger(__name__)

REMINDERS_FILE = ".reminders.json"

# Matches [[REMINDER: HH:MM | reminder text]] markers in Claude output
_REMINDER_PATTERN = re.compile(
    r"\[\[REMINDER:\s*([^\|]+?)\s*\|\s*([^\]]+?)\s*\]\]",
    re.IGNORECASE,
)


class ReminderStorage:
    """Manages reminders stored in vault/.reminders.json."""

    def __init__(self, vault_path: Path) -> None:
        self.vault_path = Path(vault_path)
        self.file_path = self.vault_path / REMINDERS_FILE

    def _load(self) -> list[dict]:
        if not self.file_path.exists():
            return []
        try:
            return json.loads(self.file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            logger.warning("Could not load reminders, starting fresh")
            return []

    def _save(self, reminders: list[dict]) -> None:
        self.file_path.write_text(
            json.dumps(reminders, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add_reminder(self, user_id: int, remind_at: datetime, text: str) -> str:
        """Add a new reminder. Returns reminder ID."""
        reminders = self._load()
        reminder_id = str(uuid.uuid4())[:8]
        reminders.append({
            "id": reminder_id,
            "user_id": user_id,
            "remind_at": remind_at.isoformat(),
            "text": text,
            "created_at": datetime.now().astimezone().isoformat(),
            "sent": False,
        })
        self._save(reminders)
        logger.info("Added reminder %s for user %s at %s", reminder_id, user_id, remind_at)
        return reminder_id

    def get_due(self) -> list[dict]:
        """Get all unsent reminders whose time has passed."""
        now = datetime.now().astimezone()
        reminders = self._load()
        return [
            r for r in reminders
            if not r.get("sent", False)
            and datetime.fromisoformat(r["remind_at"]) <= now
        ]

    def mark_sent(self, reminder_id: str) -> None:
        """Mark a reminder as sent."""
        reminders = self._load()
        for r in reminders:
            if r["id"] == reminder_id:
                r["sent"] = True
        self._save(reminders)

    def list_pending(self, user_id: int) -> list[dict]:
        """List pending (unsent) reminders for a user."""
        reminders = self._load()
        return [
            r for r in reminders
            if not r.get("sent", False) and r["user_id"] == user_id
        ]


def extract_reminders(text: str) -> list[tuple[str, str]]:
    """Extract [[REMINDER: datetime | text]] markers from Claude output.

    Returns list of (datetime_str, reminder_text) tuples.
    """
    return [
        (m.group(1).strip(), m.group(2).strip())
        for m in _REMINDER_PATTERN.finditer(text)
    ]


def strip_reminder_markers(text: str) -> str:
    """Remove all [[REMINDER: ...]] markers from text."""
    return _REMINDER_PATTERN.sub("", text).strip()


def parse_reminder_datetime(dt_str: str) -> datetime | None:
    """Try to parse datetime string in multiple formats.

    Supports: HH:MM, HH.MM, YYYY-MM-DD HH:MM, ISO format.
    Times without date are interpreted as today (or tomorrow if in the past).
    """
    today = date.today()
    stripped = dt_str.strip()

    # Try HH:MM and HH.MM (time only — use today's date)
    for fmt in ("%H:%M", "%H.%M"):
        try:
            t = datetime.strptime(stripped, fmt).time()
            dt = datetime.combine(today, t).astimezone()
            return dt
        except ValueError:
            pass

    # Try full ISO format
    try:
        return datetime.fromisoformat(stripped).astimezone()
    except ValueError:
        pass

    # Try YYYY-MM-DD HH:MM
    try:
        return datetime.strptime(stripped, "%Y-%m-%d %H:%M").astimezone()
    except ValueError:
        pass

    logger.warning("Could not parse reminder datetime: %s", dt_str)
    return None
