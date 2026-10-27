import jwt
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidTokenError as PyJWTInvalidTokenError,
)

from task_management_api.core.exceptions import (
    TokenExpiredError,
    InvalidTokenError,
)

from datetime import datetime, timezone, timedelta

from task_management_api.core.config import settings


class TokenService:
    
    @staticmethod
    def create_access_token(subject: str) -> str:
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
        
        payload = {
            "sub": subject,
            "iat": now,
            "exp": expires_at,
        }
        
        return jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )
        
    @staticmethod
    def decode_access_token(token: str) -> dict:
        try:
            return jwt.decode(
                token,
                # Keep your existing key and algorithm arguments here
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )

        except ExpiredSignatureError as exc:
            raise TokenExpiredError(
                "Access token has expired"
            ) from exc

        except PyJWTInvalidTokenError as exc:
            raise InvalidTokenError(
                "Invalid access token"
            ) from exc        
    