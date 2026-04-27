"""
Enhanced API Endpoints
Provides versioned API endpoints with advanced features.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel

from .versioning import get_api_version, APIVersion, version_prefix, is_feature_enabled
from .websocket import websocket_manager
from .auth import get_current_user, require_authentication, api_key_manager
from .webhooks import webhook_manager


router = APIRouter(tags=["Enhanced API"])


class VersionInfo(BaseModel):
    """API version information"""
    current_version: str
    supported_versions: list
    deprecated_versions: list
    features: Dict[str, bool]


class APIKeyRequest(BaseModel):
    """API key creation request"""
    name: str
    expires_in_days: Optional[int] = None
    rate_limit: int = 100
    scopes: list = ["read"]


class APIKeyResponse(BaseModel):
    """API key creation response"""
    key_id: str
    api_key: str
    name: str
    expires_at: Optional[str] = None
    rate_limit: int
    scopes: list
    message: str


@router.get("/version", response_model=VersionInfo)
async def get_version_info(version: APIVersion = Depends(get_api_version)):
    """
    Get API version information.
    
    Args:
        version: API version
        
    Returns:
        Version information
    """
    from .versioning import VersionManager, FEATURES
    
    return VersionInfo(
        current_version=VersionManager.CURRENT_VERSION.value,
        supported_versions=[v.value for v in VersionManager.SUPPORTED_VERSIONS],
        deprecated_versions=[v.value for v in VersionManager.DEPRECATED_VERSIONS],
        features=FEATURES.get(version, {})
    )


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str = "anonymous"
):
    """
    WebSocket endpoint for real-time communication.
    
    Args:
        websocket: WebSocket connection
        user_id: User ID (from query parameter)
    """
    await websocket_manager.handle_connection(websocket, user_id)


@router.get("/ws/stats")
async def get_websocket_stats():
    """
    Get WebSocket statistics.
    
    Returns:
        WebSocket statistics
    """
    return websocket_manager.get_stats()


@router.post("/keys", response_model=APIKeyResponse)
async def create_api_key(
    request: APIKeyRequest,
    current_user: Dict[str, Any] = Depends(require_authentication)
):
    """
    Create a new API key.
    
    Args:
        request: API key request
        current_user: Current user
        
    Returns:
        Created API key
    """
    raw_key, api_key = api_key_manager.generate_key(
        name=request.name,
        user_id=current_user["user_id"],
        expires_in_days=request.expires_in_days,
        rate_limit=request.rate_limit,
        scopes=request.scopes
    )
    
    return APIKeyResponse(
        key_id=api_key.key_id,
        api_key=raw_key,
        name=api_key.name,
        expires_at=api_key.expires_at.isoformat() if api_key.expires_at else None,
        rate_limit=api_key.rate_limit,
        scopes=api_key.scopes,
        message="Store this API key securely. It will not be shown again."
    )


@router.get("/keys")
async def list_api_keys(
    current_user: Dict[str, Any] = Depends(require_authentication)
):
    """
    List API keys for current user.
    
    Args:
        current_user: Current user
        
    Returns:
        List of API keys (without secrets)
    """
    keys = api_key_manager.list_keys(current_user["user_id"])
    
    return {
        "keys": [
            {
                "key_id": key.key_id,
                "name": key.name,
                "created_at": key.created_at.isoformat(),
                "expires_at": key.expires_at.isoformat() if key.expires_at else None,
                "last_used": key.last_used.isoformat() if key.last_used else None,
                "is_active": key.is_active,
                "rate_limit": key.rate_limit,
                "scopes": key.scopes
            }
            for key in keys
        ],
        "total": len(keys)
    }


@router.delete("/keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: Dict[str, Any] = Depends(require_authentication)
):
    """
    Revoke an API key.
    
    Args:
        key_id: Key ID
        current_user: Current user
        
    Returns:
        Success message
    """
    # Verify ownership
    key_info = api_key_manager.get_key_info(key_id)
    if not key_info or key_info.user_id != current_user["user_id"]:
        raise HTTPException(status_code=404, detail="API key not found")
    
    success = api_key_manager.revoke_key(key_id)
    
    if success:
        return {"message": "API key revoked successfully"}
    else:
        raise HTTPException(status_code=404, detail="API key not found")


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0"
    }


@router.get("/features")
async def get_features(version: APIVersion = Depends(get_api_version)):
    """
    Get available features for API version.
    
    Args:
        version: API version
        
    Returns:
        Feature flags
    """
    from .versioning import FEATURES
    
    return {
        "version": version.value,
        "features": FEATURES.get(version, {})
    }
