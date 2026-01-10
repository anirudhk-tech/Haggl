"""Pydantic schemas for the Message Agent."""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class MessageRole(str, Enum):
    """Role in a conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationMessage(BaseModel):
    """A single message in a conversation."""
    role: MessageRole
    content: str
    timestamp: Optional[str] = None


class IncomingSMS(BaseModel):
    """Incoming SMS from Twilio webhook."""
    from_number: str = Field(description="Sender phone number in E.164 format")
    to_number: str = Field(description="Recipient phone number (our Twilio number)")
    body: str = Field(description="Message content")
    message_sid: Optional[str] = Field(default=None, description="Twilio message SID")


class OutgoingSMS(BaseModel):
    """Outgoing SMS to send via Twilio."""
    to_number: str = Field(description="Recipient phone number in E.164 format")
    body: str = Field(description="Message content")


class ConversationState(BaseModel):
    """State of a conversation with a user."""
    phone_number: str = Field(description="User's phone number")
    messages: list[ConversationMessage] = Field(default_factory=list)
    context: dict = Field(default_factory=dict, description="Additional context for the conversation")
