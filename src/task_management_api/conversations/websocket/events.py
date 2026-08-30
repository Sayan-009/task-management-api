from enum import Enum


class WebSocketEvent(str, Enum):
    MESSAGE_CREATED="message_created"
    MESSAGE_UPDATED="message_updated"
    MESSAGE_DELETED="message_deleted"
    MARK_MESSAGES_READ="mark_messages_read"
    MESSAGES_READ="messages_read"