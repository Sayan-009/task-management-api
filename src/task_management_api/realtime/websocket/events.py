from enum import Enum


class WebSocketEvent(str, Enum):
    MESSAGE_CREATED="message_created"
    MESSAGE_UPDATED="message_updated"
    MESSAGE_DELETED="message_deleted"
    
    MARK_MESSAGES_READ="mark_messages_read"
    MESSAGES_READ="messages_read"
    
    TYPING_START="typing_start"
    TYPING_STOP="typing_stop"
    USER_TYPING_STARTED="user_typing_started"
    USER_TYPING_STOPPED="user_typing_stopped"
    
    USER_ONLINE="user_online"
    USER_OFFLINE="user_offline"
    PRESENCE_SNAPSHOT="presence_snapshot"