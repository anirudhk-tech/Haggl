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
from .tools import send_sms, place_order_with_updates, PLACE_ORDER_FUNCTION

logger = logging.getLogger(__name__)

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# System prompt for the message agent
SYSTEM_PROMPT = """You are Haggl, an AI assistant that helps restaurant and bakery owners order ingredients from local vendors.

When a user wants to order something:
1. Ask clarifying questions if needed (quantity, timeline)
2. Use the place_order function to call a vendor and place the order
3. Let them know you're calling the vendor

EXAMPLE:
User: "I need eggs"
You: "How many dozen do you need?"
User: "20 dozen"
You: *calls place_order* "Got it! I'm calling the vendor now to order 20 dozen eggs. I'll update you once I hear back!"

Keep messages SHORT - this is SMS/WhatsApp. Be friendly and efficient.
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
        if self._openai_client is None and OPENAI_API_KEY:
            from openai import OpenAI
            self._openai_client = OpenAI(api_key=OPENAI_API_KEY)
            logger.info("OpenAI client initialized")
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
        Generate a response using OpenAI with function calling.
        
        Args:
            conversation: Current conversation state with history
            
        Returns:
            Generated response text
        """
        if not OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not configured, using stub response")
            return self._stub_response(conversation)
        
        try:
            import json
            client = self._get_openai_client()
            messages = [
                {"role": msg.role.value, "content": msg.content}
                for msg in conversation.messages
            ]
            
            # Call OpenAI with tools
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                tools=[PLACE_ORDER_FUNCTION],
                tool_choice="auto",
            )
            
            assistant_message = response.choices[0].message
            
            # Check if OpenAI wants to call a function
            if assistant_message.tool_calls:
                tool_call = assistant_message.tool_calls[0]
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                logger.info(f"OpenAI wants to call: {function_name}({function_args})")
                
                if function_name == "place_order":
                    import asyncio
                    
                    # Create callback to send status updates via WhatsApp
                    async def send_status_update(message: str):
                        await self.send_response(conversation.phone_number, message)
                    
                    # Start the order in background - don't wait for completion
                    asyncio.create_task(
                        place_order_with_updates(
                            product=function_args.get("product", "eggs"),
                            quantity=function_args.get("quantity", 1),
                            unit=function_args.get("unit", "dozen"),
                            business_name="Customer Business",
                            vendor_phone=conversation.phone_number,  # Call user's number for testing
                            on_status_update=send_status_update,
                        )
                    )
                    
                    # Return immediate acknowledgment - status updates come via callback
                    product = function_args.get("product", "eggs")
                    quantity = function_args.get("quantity", 1)
                    unit = function_args.get("unit", "dozen")
                    return f"On it! Placing order for {quantity} {unit} of {product}. I'll send you updates as the call progresses."
            
            # No function call, return regular response
            return assistant_message.content or ""
            
        except Exception as e:
            logger.exception(f"OpenAI API error: {e}")
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
