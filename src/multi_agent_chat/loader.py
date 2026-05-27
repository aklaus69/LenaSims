"""
Loader module for loading agent configurations from JSON files.
"""

import json
from pathlib import Path

from .models import AgentConfig


def load_agent(file_path: str | Path) -> AgentConfig:
    """
    Load a single agent configuration from a JSON file.

    Args:
        file_path: Path to the JSON file containing agent configuration

    Returns:
        AgentConfig object loaded from the file

    Raises:
        FileNotFoundError: If the file does not exist
        json.JSONDecodeError: If the file is not valid JSON
        ValueError: If the JSON does not match AgentConfig schema
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Agent config file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return AgentConfig.model_validate(data)


def load_all_agents(directory: str | Path) -> list[AgentConfig]:
    """
    Load all agent configurations from a directory.

    Loads all .json files from the specified directory and returns them
    as a list of AgentConfig objects.

    Args:
        directory: Path to the directory containing agent JSON files

    Returns:
        List of AgentConfig objects, one for each JSON file found

    Raises:
        FileNotFoundError: If the directory does not exist
        json.JSONDecodeError: If any file is not valid JSON
        ValueError: If any JSON does not match AgentConfig schema
    """
    directory = Path(directory)

    if not directory.exists():
        raise FileNotFoundError(f"Agent config directory not found: {directory}")

    if not directory.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory}")

    agents = []

    # Sort files for consistent ordering
    for file_path in sorted(directory.glob("*.json")):
        agents.append(load_agent(file_path))

    return agents
