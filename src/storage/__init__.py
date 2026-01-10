"""Haggl Storage - Centralized MongoDB Atlas Integration."""

from .database import (
    get_database,
    get_collection,
    setup_all_indexes,
    close_connection,
)
from .schemas import (
    VendorDocument,
    ConversationDocument,
    OrderDocument,
    CallDocument,
    VendorEmbedding,
    OrderStatus,
    CallStatus,
    CallOutcomeDocument,
    EvaluationDocument,
    EvaluationStatus,
    VendorCallResult,
)
from .vendors import (
    save_vendor,
    get_vendor_by_id,
    get_vendors_by_ingredient,
    search_vendors_by_embedding,
    save_vendor_embedding,
)
from .conversations import (
    save_conversation,
    get_conversation,
    append_message,
)
from .orders import (
    save_order,
    get_order,
    update_order_status,
    get_orders_by_phone,
    create_order,
    add_vendor_to_order,
)
from .calls import (
    save_call,
    get_call,
    update_call_status,
    create_call,
    get_calls_by_order,
    get_successful_calls,
)
from .evaluations import (
    save_evaluation,
    get_evaluation,
    get_evaluation_by_order,
    update_evaluation_status,
    create_evaluation,
)
from .businesses import (
    save_business_profile,
    get_business_profile,
    get_business_by_phone,
    create_business_from_onboarding,
    update_business_preferences,
    get_business_context_for_agent,
)
from .schemas import (
    BusinessProfile,
    BusinessProduct,
    BusinessLocation,
    BusinessType,
)

__all__ = [
    # Database
    "get_database",
    "get_collection", 
    "setup_all_indexes",
    "close_connection",
    # Schemas
    "VendorDocument",
    "ConversationDocument",
    "OrderDocument",
    "CallDocument",
    "VendorEmbedding",
    "OrderStatus",
    "CallStatus",
    "CallOutcomeDocument",
    "EvaluationDocument",
    "EvaluationStatus",
    "VendorCallResult",
    # Vendors
    "save_vendor",
    "get_vendor_by_id",
    "get_vendors_by_ingredient",
    "search_vendors_by_embedding",
    "save_vendor_embedding",
    # Conversations
    "save_conversation",
    "get_conversation",
    "append_message",
    # Orders
    "save_order",
    "get_order",
    "update_order_status",
    "get_orders_by_phone",
    "create_order",
    "add_vendor_to_order",
    # Calls
    "save_call",
    "get_call",
    "update_call_status",
    "create_call",
    "get_calls_by_order",
    "get_successful_calls",
    # Evaluations
    "save_evaluation",
    "get_evaluation",
    "get_evaluation_by_order",
    "update_evaluation_status",
    "create_evaluation",
    # Businesses
    "save_business_profile",
    "get_business_profile",
    "get_business_by_phone",
    "create_business_from_onboarding",
    "update_business_preferences",
    "get_business_context_for_agent",
    "BusinessProfile",
    "BusinessProduct",
    "BusinessLocation",
    "BusinessType",
]
