from app.users.schema import User, Message


def user_register(user: User) -> Message:
    
    return Message(message="user registered successfully")