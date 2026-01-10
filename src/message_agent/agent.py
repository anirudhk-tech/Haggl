"""
Message Agent - Conversational SMS Agent with OpenAI

Handles incoming SMS messages, maintains conversation history,
and generates responses using OpenAI's SDK.
"""

import os
import logging
from typing import Optional
from datetime import datetime

from .schemas import (
    IncomingSMS,
    OutgoingSMS,
    ConversationMessage,
    ConversationState,
    MessageRole,
)
from .tools import send_sms

logger = logging.getLogger(__name__)

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# System prompt for the message agent
SYSTEM_PROMPT = """You are a helpful assistant for Haggl, a platform that helps 
restaurants and bakeries order ingredients from local vendors.

You can help users with:
- Getting information about available vendors
- Checking order status
- Answering questions about pricing and delivery
- General inquiries about our service

Keep responses concise and friendly - remember this is SMS, so be brief!
"""


class MessageAgent:
    """
    Conversational agent that handles SMS messages.
    
    Maintains conversation history per phone number and uses
    OpenAI to generate contextual responses.
    """
    
    def __init__(self):
        self._conversations: dict[str, ConversationState] = {}
        self._openai_client = None
    
    def _get_openai_client(self):
        """Lazy initialization of OpenAI client."""
        if self._openai_client is None:
            # TODO: Initialize actual OpenAI client
            # from openai import OpenAI
            # self._openai_client = OpenAI(api_key=OPENAI_API_KEY)
            logger.info("[STUB] OpenAI client would be initialized here")
        return self._openai_client
    
    def _get_or_create_conversation(self, phone_number: str) -> ConversationState:
        """Get existing conversation or create new one."""
        if phone_number not in self._conversations:
            self._conversations[phone_number] = ConversationState(
                phone_number=phone_number,
                messages=[
                    ConversationMessage(
                        role=MessageRole.SYSTEM,
                        content=SYSTEM_PROMPT,
                        timestamp=datetime.utcnow().isoformat(),
                    )
                ],
            )
            logger.info(f"Created new conversation for {phone_number}")
        return self._conversations[phone_number]
    
    async def process_message(self, incoming: IncomingSMS) -> str:
        """
        Process an incoming SMS and generate a response.
        
        Args:
            incoming: IncomingSMS with sender info and message body
            
        Returns:
            Response text to send back
        """
        logger.info(f"Processing message from {incoming.from_number}: {incoming.body}")
        
        # Get or create conversation state
        conversation = self._get_or_create_conversation(incoming.from_number)
        
        # Add user message to history
        conversation.messages.append(
            ConversationMessage(
                role=MessageRole.USER,
                content=incoming.body,
                timestamp=datetime.utcnow().isoformat(),
            )
        )
        
        # Generate response using OpenAI
        response_text = await self._generate_response(conversation)
        
        # Add assistant response to history
        conversation.messages.append(
            ConversationMessage(
                role=MessageRole.ASSISTANT,
                content=response_text,
                timestamp=datetime.utcnow().isoformat(),
            )
        )
        
        return response_text
    
    async def _generate_response(self, conversation: ConversationState) -> str:
        """
        Generate a response using OpenAI.
        
        Args:
            conversation: Current conversation state with history
            
        Returns:
            Generated response text
        """
        if not OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not configured, using stub response")
            return self._stub_response(conversation)
        
        # TODO: Implement actual OpenAI call
        # client = self._get_openai_client()
        # messages = [
        #     {"role": msg.role.value, "content": msg.content}
        #     for msg in conversation.messages
        # ]
        # response = client.chat.completions.create(
        #     model=OPENAI_MODEL,
        #     messages=messages,
        # )
        # return response.choices[0].message.content
        
        return self._stub_response(conversation)
    
    def _stub_response(self, conversation: ConversationState) -> str:
        """Generate a stub response for testing."""
        last_message = conversation.messages[-1].content if conversation.messages else ""
        return f"[STUB] Received your message: '{last_message[:50]}...'. OpenAI integration pending."
    
    async def send_response(self, to_number: str, response_text: str) -> dict:
        """
        Send a response SMS via Twilio.
        
        Args:
            to_number: Recipient phone number
            response_text: Message to send
            
        Returns:
            Result from Twilio send
        """
        outgoing = OutgoingSMS(to_number=to_number, body=response_text)
        return await send_sms(outgoing)
    
    def get_conversation_history(self, phone_number: str) -> Optional[ConversationState]:
        """Get conversation history for a phone number."""
        return self._conversations.get(phone_number)
    
    def clear_conversation(self, phone_number: str) -> bool:
        """Clear conversation history for a phone number."""
        if phone_number in self._conversations:
            del self._conversations[phone_number]
            logger.info(f"Cleared conversation for {phone_number}")
            return True
        return False
    
    def clear_all_conversations(self) -> None:
        """Clear all conversation histories."""
        self._conversations.clear()
        logger.info("Cleared all conversations")


# Global message agent instance
_message_agent: Optional[MessageAgent] = None


def get_message_agent() -> MessageAgent:
    """Get or create the global message agent instance."""
    global _message_agent
    if _message_agent is None:
        _message_agent = MessageAgent()
    return _message_agent
