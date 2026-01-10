"""Conversation storage operations."""

import logging
from datetime import datetime
from typing import Optional

from .database import get_collection
from .schemas import ConversationDocument, MessageDocument

logger = logging.getLogger(__name__)

COLLECTION = "conversations"


def save_conversation(conversation: ConversationDocument) -> bool:
    """
    Save or update a conversation.
    
    Args:
        conversation: ConversationDocument to save
        
    Returns:
        True if successful
    """
    collection = get_collection(COLLECTION)
    if collection is None:
        logger.warning("No database connection - conversation not saved")
        return False
    
    try:
        conversation.updated_at = datetime.utcnow()
        collection.update_one(
            {"phone_number": conversation.phone_number},
            {"$set": conversation.model_dump()},
            upsert=True
        )
        logger.debug(f"Saved conversation for: {conversation.phone_number}")
        return True
    except Exception as e:
        logger.error(f"Failed to save conversation: {e}")
        return False


def get_conversation(phone_number: str) -> Optional[ConversationDocument]:
    """Get a conversation by phone number."""
    collection = get_collection(COLLECTION)
    if collection is None:
        return None
    
    try:
        doc = collection.find_one({"phone_number": phone_number})
        if doc:
            doc.pop("_id", None)
            return ConversationDocument(**doc)
        return None
    except Exception as e:
        logger.error(f"Failed to get conversation: {e}")
        return None


def append_message(
    phone_number: str,
    role: str,
    content: str
) -> bool:
    """
    Append a message to a conversation.
    
    Creates the conversation if it doesn't exist.
    
    Args:
        phone_number: User's phone number
        role: Message role (user, assistant, system)
        content: Message content
        
    Returns:
        True if successful
    """
    collection = get_collection(COLLECTION)
    if collection is None:
        logger.warning("No database connection - message not saved")
        return False
    
    try:
        message = MessageDocument(
            role=role,
            content=content,
            timestamp=datetime.utcnow()
        )
        
        result = collection.update_one(
            {"phone_number": phone_number},
            {
                "$push": {"messages": message.model_dump()},
                "$set": {"updated_at": datetime.utcnow()},
                "$setOnInsert": {"created_at": datetime.utcnow()}
            },
            upsert=True
        )
        
        return result.modified_count > 0 or result.upserted_id is not None
    except Exception as e:
        logger.error(f"Failed to append message: {e}")
        return False


def update_context(phone_number: str, context: dict) -> bool:
    """
    Update the context for a conversation.
    
    Args:
        phone_number: User's phone number
        context: Context dict to merge
        
    Returns:
        True if successful
    """
    collection = get_collection(COLLECTION)
    if collection is None:
        return False
    
    try:
        # Build update for nested context fields
        update = {"updated_at": datetime.utcnow()}
        for key, value in context.items():
            update[f"context.{key}"] = value
        
        collection.update_one(
            {"phone_number": phone_number},
            {"$set": update},
            upsert=True
        )
        return True
    except Exception as e:
        logger.error(f"Failed to update context: {e}")
        return False


def clear_conversation(phone_number: str) -> bool:
    """Delete a conversation."""
    collection = get_collection(COLLECTION)
    if collection is None:
        return False
    
    try:
        collection.delete_one({"phone_number": phone_number})
        logger.info(f"Cleared conversation for: {phone_number}")
        return True
    except Exception as e:
        logger.error(f"Failed to clear conversation: {e}")
        return False
