from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    current_time = datetime.now(timezone.utc)
    
    if expires_delta:
        expire = current_time + expires_delta
    else:
        expire = current_time + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    
    # Log token creation for debugging
    time_until_expiry = expire - current_time
    logger.info(f"Token created. Current time: {current_time}, Expires at: {expire}, Valid for: {time_until_expiry}")
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT access token.
    
    Args:
        token: JWT token to decode
        
    Returns:
        Decoded token data or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        # Log token info for debugging
        if 'exp' in payload:
            exp_time = datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
            current_time = datetime.now(timezone.utc)
            time_left = exp_time - current_time
            logger.debug(f"Token valid. Expires at: {exp_time}, Time left: {time_left}")
        return payload
    except jwt.ExpiredSignatureError as e:
        # Decode without verification to see expiration time
        try:
            unverified = jwt.decode(token, options={"verify_signature": False})
            if 'exp' in unverified:
                exp_time = datetime.fromtimestamp(unverified['exp'], tz=timezone.utc)
                current_time = datetime.now(timezone.utc)
                logger.warning(f"Token has expired. Expired at: {exp_time}, Current time: {current_time}")
        except Exception:
            logger.warning("Token has expired (unable to decode expiration time)")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {type(e).__name__}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error decoding token: {type(e).__name__}: {str(e)}")
        return None

