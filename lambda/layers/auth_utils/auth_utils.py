"""
Authentication utilities for password hashing and JWT token generation
"""
import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, Any

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'secret-key')
JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
JWT_EXPIRATION_HOURS = int(os.environ.get('JWT_EXPIRATION_HOURS', 24))


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash
    
    Args:
        password: Plain text password to verify
        hashed_password: Previously hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    return bcrypt.checkpw(
        password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def generate_access_token(user_id: str, email: str, additional_claims: Dict[str, Any] = None) -> str:
    """
    Generate a JWT access token
    
    Args:
        user_id: Unique user identifier
        email: User's email address
        additional_claims: Optional additional claims to include in token
        
    Returns:
        JWT token string
    """
    payload = {
        'sub': user_id,
        'email': email,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'token_type': 'Bearer'
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def verify_access_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a JWT access token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload if valid
        
    Raises:
        jwt.ExpiredSignatureError: If token has expired
        jwt.InvalidTokenError: If token is invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")


def create_oauth_response(access_token: str) -> Dict[str, Any]:
    """
    Create an OAuth 2.0 compliant token response
    
    Args:
        access_token: The JWT access token
        
    Returns:
        OAuth 2.0 token response dictionary
    """
    return {
        'access_token': access_token,
        'token_type': 'Bearer',
        'expires_in': JWT_EXPIRATION_HOURS * 3600,  # Convert hours to seconds
        'scope': 'read write'
    }
