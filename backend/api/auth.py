"""
API Authentication
Provides API key management and authentication.
"""

from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, status, Depends
from datetime import datetime, timedelta
import secrets
import hashlib
from pydantic import BaseModel


class APIKey(BaseModel):
    """API key model"""
    key_id: str
    key_hash: str
    name: str
    user_id: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    is_active: bool = True
    rate_limit: int = 100  # requests per minute
    scopes: list = []  # permissions


class APIKeyManager:
    """Manages API keys"""
    
    def __init__(self):
        # In-memory storage (in production, use database)
        self.keys: Dict[str, APIKey] = {}
        self._load_default_keys()
    
    def _load_default_keys(self):
        """Load default API keys for testing"""
        # Create a test key
        test_key = "test_key_12345"
        key_hash = self._hash_key(test_key)
        
        self.keys[key_hash] = APIKey(
            key_id="test_001",
            key_hash=key_hash,
            name="Test API Key",
            user_id="test_user",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=365),
            is_active=True,
            rate_limit=1000,
            scopes=["read", "write", "admin"]
        )
    
    def _hash_key(self, key: str) -> str:
        """Hash API key"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    def generate_key(
        self,
        name: str,
        user_id: str,
        expires_in_days: Optional[int] = None,
        rate_limit: int = 100,
        scopes: list = None
    ) -> tuple[str, APIKey]:
        """
        Generate a new API key.
        
        Args:
            name: Key name/description
            user_id: User ID
            expires_in_days: Expiration in days (None = no expiration)
            rate_limit: Rate limit (requests per minute)
            scopes: List of permission scopes
            
        Returns:
            Tuple of (raw_key, api_key_object)
        """
        # Generate random key
        raw_key = f"fina_{secrets.token_urlsafe(32)}"
        key_hash = self._hash_key(raw_key)
        
        # Create API key object
        api_key = APIKey(
            key_id=f"key_{secrets.token_hex(8)}",
            key_hash=key_hash,
            name=name,
            user_id=user_id,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=expires_in_days) if expires_in_days else None,
            is_active=True,
            rate_limit=rate_limit,
            scopes=scopes or ["read"]
        )
        
        # Store key
        self.keys[key_hash] = api_key
        
        return raw_key, api_key
    
    def validate_key(self, raw_key: str) -> Optional[APIKey]:
        """
        Validate API key.
        
        Args:
            raw_key: Raw API key
            
        Returns:
            APIKey object if valid, None otherwise
        """
        key_hash = self._hash_key(raw_key)
        api_key = self.keys.get(key_hash)
        
        if not api_key:
            return None
        
        # Check if active
        if not api_key.is_active:
            return None
        
        # Check expiration
        if api_key.expires_at and datetime.utcnow() > api_key.expires_at:
            return None
        
        # Update last used
        api_key.last_used = datetime.utcnow()
        
        return api_key
    
    def revoke_key(self, key_id: str) -> bool:
        """
        Revoke an API key.
        
        Args:
            key_id: Key ID
            
        Returns:
            True if revoked, False if not found
        """
        for api_key in self.keys.values():
            if api_key.key_id == key_id:
                api_key.is_active = False
                return True
        return False
    
    def list_keys(self, user_id: str) -> list[APIKey]:
        """
        List API keys for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of API keys
        """
        return [
            api_key for api_key in self.keys.values()
            if api_key.user_id == user_id
        ]
    
    def get_key_info(self, key_id: str) -> Optional[APIKey]:
        """
        Get API key information.
        
        Args:
            key_id: Key ID
            
        Returns:
            APIKey object or None
        """
        for api_key in self.keys.values():
            if api_key.key_id == key_id:
                return api_key
        return None


# Global API key manager
api_key_manager = APIKeyManager()


async def get_api_key(
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None)
) -> Optional[str]:
    """
    Extract API key from headers.
    
    Args:
        x_api_key: API key from X-API-Key header
        authorization: API key from Authorization header (Bearer token)
        
    Returns:
        API key or None
    """
    # Try X-API-Key header first
    if x_api_key:
        return x_api_key
    
    # Try Authorization header (Bearer token)
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:]  # Remove "Bearer " prefix
    
    return None


async def get_current_user(api_key: Optional[str] = Depends(get_api_key)) -> Dict[str, Any]:
    """
    Get current user from API key.
    
    Args:
        api_key: API key from headers
        
    Returns:
        User information
        
    Raises:
        HTTPException: If authentication fails
    """
    # Allow unauthenticated access for now (optional authentication)
    if not api_key:
        return {
            "user_id": "anonymous",
            "authenticated": False,
            "scopes": ["read"]
        }
    
    # Validate API key
    validated_key = api_key_manager.validate_key(api_key)
    
    if not validated_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return {
        "user_id": validated_key.user_id,
        "key_id": validated_key.key_id,
        "authenticated": True,
        "scopes": validated_key.scopes,
        "rate_limit": validated_key.rate_limit
    }


async def require_authentication(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Require authentication (no anonymous access).
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        User information
        
    Raises:
        HTTPException: If not authenticated
    """
    if not current_user.get("authenticated"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return current_user


async def require_scope(required_scope: str):
    """
    Require specific scope/permission.
    
    Args:
        required_scope: Required scope
        
    Returns:
        Dependency function
    """
    async def check_scope(current_user: Dict[str, Any] = Depends(require_authentication)):
        scopes = current_user.get("scopes", [])
        
        if required_scope not in scopes and "admin" not in scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required scope: {required_scope}"
            )
        
        return current_user
    
    return check_scope
