from app.users.schema import (
    UserRegistraionRequest,
    MessageResponse
)


def register_user(reqest: UserRegistraionRequest) -> MessageResponse:
    return MessageResponse(message="user registered successfully")