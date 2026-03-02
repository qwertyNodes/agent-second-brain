"""Markdown document storage and indexing service."""

import json
import logging
from datetime import date, datetime
from pathlib import Path

logger = logging.getLogger(__name__)

DOCS_DIR = "docs"
INDEX_FILE = "docs/_index.json"


class DocsStorage:
    """Service for saving and indexing .md documents in the vault."""

    def __init__(self, vault_path: Path) -> None:
        self.vault_path = Path(vault_path)
        self.docs_path = self.vault_path / DOCS_DIR
        self.index_path = self.vault_path / INDEX_FILE

    def _ensure_dirs(self) -> None:
        self.docs_path.mkdir(parents=True, exist_ok=True)

    def _load_index(self) -> list[dict]:
        if not self.index_path.exists():
            return []
        try:
            return json.loads(self.index_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            logger.warning("Could not read _index.json, starting fresh")
            return []

    def _save_index(self, entries: list[dict]) -> None:
        self.index_path.write_text(
            json.dumps(entries, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _parse_metadata(self, content: str) -> tuple[str, list[str]]:
        """Extract title and tags from first 5 lines of markdown.

        Returns (title, tags).
        Title is first # heading found, or empty string.
        Tags are from frontmatter 'tags:' line if present.
        """
        lines = content.splitlines()[:5]
        title = ""
        tags: list[str] = []

        for line in lines:
            stripped = line.strip()
            if not title and stripped.startswith("# "):
                title = stripped[2:].strip()
            if stripped.startswith("tags:"):
                raw = stripped[5:].strip().strip("[]")
                tags = [t.strip() for t in raw.split(",") if t.strip()]

        return title, tags

    def save_doc(
        self,
        content: bytes,
        original_filename: str,
        day: date,
        timestamp: datetime,
        caption: str | None = None,
    ) -> tuple[str, str]:
        """Save .md document to vault/docs/ and update index.

        Returns:
            (saved_filename, title) tuple
        """
        self._ensure_dirs()

        # Sanitize filename: keep only safe chars
        safe_name = "".join(
            c if c.isalnum() or c in "-_." else "-"
            for c in original_filename
        ).strip("-")
        saved_filename = f"{day.isoformat()}-{safe_name}"
        if not saved_filename.endswith(".md"):
            saved_filename += ".md"

        dest_path = self.docs_path / saved_filename
        text_content = content.decode("utf-8", errors="replace")

        if caption:
            text_content = text_content + f"\n\n<!-- Caption: {caption} -->\n"

        dest_path.write_text(text_content, encoding="utf-8")

        title, tags = self._parse_metadata(text_content)
        if not title:
            title = original_filename.removesuffix(".md")

        entries = self._load_index()
        entries.append({
            "filename": saved_filename,
            "title": title,
            "date": day.isoformat(),
            "tags": tags,
            "project_link": "",
            "size": len(text_content),
            "uploaded_at": timestamp.isoformat(),
            "caption": caption or "",
        })
        self._save_index(entries)

        logger.info("Saved doc: %s (title: %s)", saved_filename, title)
        return saved_filename, title

    def search_index(self, query: str) -> list[dict]:
        """Search index by title or tags (simple substring match)."""
        entries = self._load_index()
        query_lower = query.lower()
        return [
            e for e in entries
            if query_lower in e.get("title", "").lower()
            or any(query_lower in t.lower() for t in e.get("tags", []))
        ]
