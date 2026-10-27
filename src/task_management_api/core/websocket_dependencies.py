from uuid import UUID

from fastapi import WebSocket, Depends, WebSocketException, status
from sqlalchemy.ext.asyncio import AsyncSession

from task_management_api.db.session import get_db
from task_management_api.users.model import User
from task_management_api.users.repository import UserRepository
from task_management_api.core.token import TokenService


async def get_websocket_user(
    websocket: WebSocket,
    session: AsyncSession = Depends(get_db),
) -> User | None:

    token = websocket.query_params.get("token")

    if not token:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Authentication token is required"
        )

    try:
        payload = TokenService.decode_access_token(token)

        subject = payload.get("sub")

        if subject is None:
            raise ValueError(
                "Invalid token subject"
            )

        user_id = UUID(subject)

    except (ValueError, TypeError):
        print("Invalid token")
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Could not validate credentials",
        ) from None

    user = await UserRepository.get_by_id(
        session,
        user_id
    )

    if user is None:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="User not found",
        )
        
    if not user.is_active:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="User account is inactive",
        )

    return user