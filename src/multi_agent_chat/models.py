"""
Pydantic models for agents and conversations.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    """Represents a single message in a conversation."""

    role: str = Field(..., description="The role of the sender (e.g., 'user', 'assistant', 'system')")
    content: str = Field(..., description="The content of the message")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the message was created")
    agent_id: Optional[str] = Field(None, description="The ID of the agent that sent the message, if applicable")


class AgentConfig(BaseModel):
    """Configuration for an AI agent."""

    name: str = Field(..., description="The name of the agent")
    role: str = Field(..., description="The role/persona of the agent")
    instructions: str = Field(..., description="Instructions for the agent's behavior")
    model: str = Field(default="gpt-4o", description="The LLM model to use")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, ge=1, description="Maximum tokens to generate")


class Conversation(BaseModel):
    """Represents a conversation between agents."""

    id: str = Field(..., description="Unique conversation identifier")
    participants: list[str] = Field(default_factory=list, description="List of participating agent IDs")
    messages: list[Message] = Field(default_factory=list, description="List of messages in the conversation")
    topic: Optional[str] = Field(None, description="The topic of the conversation")
    started_at: datetime = Field(default_factory=datetime.now, description="When the conversation was started")
    ended_at: Optional[datetime] = Field(None, description="When the conversation ended")
