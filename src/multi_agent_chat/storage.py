"""
JSON/JSONL storage for conversations.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from .models import Conversation


class ConversationStorage:
    """Storage manager for saving and loading conversations as JSON/JSONL."""

    def __init__(self, base_dir: str | Path = "conversations") -> None:
        """
        Initialize the conversation storage.

        Args:
            base_dir: Base directory for storing conversations
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, conversation: Conversation, filename: str | None = None) -> Path:
        """
        Save a conversation as JSON.

        Args:
            conversation: The conversation to save
            filename: Optional filename (uses conversation.id.json if not provided)

        Returns:
            Path to the saved file
        """
        if filename is None:
            filename = f"{conversation.id}.json"

        filepath = self.base_dir / filename

        # Convert to dict and handle datetime serialization
        data = conversation.model_dump()
        data = self._serialize_datetimes(data)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return filepath

    def save_jsonl(self, conversations: list[Conversation], filename: str) -> Path:
        """
        Save multiple conversations as JSONL (one JSON per line).

        Args:
            conversations: List of conversations to save
            filename: Filename for the JSONL file

        Returns:
            Path to the saved file
        """
        filepath = self.base_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            for conversation in conversations:
                data = conversation.model_dump()
                data = self._serialize_datetimes(data)
                f.write(json.dumps(data, ensure_ascii=False) + "\n")

        return filepath

    def load(self, filename: str) -> Conversation:
        """
        Load a conversation from JSON.

        Args:
            filename: Filename of the saved conversation

        Returns:
            The loaded conversation

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the JSON is invalid
        """
        filepath = self.base_dir / filename

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        return Conversation.model_validate(data)

    def load_jsonl(self, filename: str) -> list[Conversation]:
        """
        Load multiple conversations from JSONL.

        Args:
            filename: Filename of the JSONL file

        Returns:
            List of loaded conversations

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If any JSON line is invalid
        """
        filepath = self.base_dir / filename
        conversations = []

        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                conversations.append(Conversation.model_validate(data))

        return conversations

    def list_all(self, extension: str = ".json") -> list[dict]:
        """
        List all saved conversations.

        Args:
            extension: File extension to filter by (default: .json)

        Returns:
            List of dictionaries with info about each saved conversation:
            - filename: The file name
            - id: The conversation ID from the filename
            - size_bytes: File size in bytes
            - modified_at: Last modification time
        """
        conversations = []

        for filepath in self.base_dir.glob(f"*{extension}"):
            stat = filepath.stat()
            conversations.append({
                "filename": filepath.name,
                "id": filepath.stem,
                "size_bytes": stat.st_size,
                "modified_at": datetime.fromtimestamp(stat.st_mtime),
            })

        # Sort by modified time (newest first)
        conversations.sort(key=lambda x: x["modified_at"], reverse=True)

        return conversations

    def delete(self, filename: str) -> bool:
        """
        Delete a saved conversation.

        Args:
            filename: Filename of the conversation to delete

        Returns:
            True if deleted, False if file didn't exist
        """
        filepath = self.base_dir / filename

        if filepath.exists():
            filepath.unlink()
            return True
        return False

    def exists(self, filename: str) -> bool:
        """
        Check if a conversation file exists.

        Args:
            filename: Filename to check

        Returns:
            True if the file exists
        """
        return (self.base_dir / filename).exists()

    def _serialize_datetimes(self, data: dict | list) -> dict | list:
        """
        Recursively serialize datetime objects to ISO format strings.

        Args:
            data: Dictionary or list containing datetime objects

        Returns:
            Data with datetimes serialized as strings
        """
        if isinstance(data, dict):
            return {
                key: value.isoformat() if isinstance(value, datetime) else
                self._serialize_datetimes(value) if isinstance(value, (dict, list)) else value
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [
                item.isoformat() if isinstance(item, datetime) else
                self._serialize_datetimes(item) if isinstance(item, (dict, list)) else item
                for item in data
            ]
        return data
