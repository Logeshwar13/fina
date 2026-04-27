"""
API Versioning
Provides API version management and routing.
"""

from enum import Enum
from typing import Optional
from fastapi import Header, HTTPException, status


class APIVersion(str, Enum):
    """API version enum"""
    V1 = "v1"
    V2 = "v2"


class VersionManager:
    """Manages API versioning"""
    
    CURRENT_VERSION = APIVersion.V1
    SUPPORTED_VERSIONS = [APIVersion.V1]
    DEPRECATED_VERSIONS = []
    
    @classmethod
    def is_supported(cls, version: str) -> bool:
        """Check if version is supported"""
        try:
            api_version = APIVersion(version)
            return api_version in cls.SUPPORTED_VERSIONS
        except ValueError:
            return False
    
    @classmethod
    def is_deprecated(cls, version: str) -> bool:
        """Check if version is deprecated"""
        try:
            api_version = APIVersion(version)
            return api_version in cls.DEPRECATED_VERSIONS
        except ValueError:
            return False
    
    @classmethod
    def get_version_info(cls) -> dict:
        """Get version information"""
        return {
            "current": cls.CURRENT_VERSION.value,
            "supported": [v.value for v in cls.SUPPORTED_VERSIONS],
            "deprecated": [v.value for v in cls.DEPRECATED_VERSIONS]
        }


async def get_api_version(
    x_api_version: Optional[str] = Header(None),
    accept_version: Optional[str] = Header(None)
) -> APIVersion:
    """
    Get API version from headers.
    
    Args:
        x_api_version: Version from X-API-Version header
        accept_version: Version from Accept-Version header
        
    Returns:
        APIVersion enum
        
    Raises:
        HTTPException: If version is not supported
    """
    # Try X-API-Version header first
    version_str = x_api_version or accept_version
    
    # Default to current version if not specified
    if not version_str:
        return VersionManager.CURRENT_VERSION
    
    # Validate version
    if not VersionManager.is_supported(version_str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"API version '{version_str}' is not supported. "
                   f"Supported versions: {[v.value for v in VersionManager.SUPPORTED_VERSIONS]}"
        )
    
    # Warn if deprecated
    if VersionManager.is_deprecated(version_str):
        # In production, you might want to log this or add a warning header
        pass
    
    return APIVersion(version_str)


def version_prefix(version: APIVersion) -> str:
    """Get URL prefix for version"""
    return f"/api/{version.value}"


# Version-specific feature flags
FEATURES = {
    APIVersion.V1: {
        "websocket": True,
        "streaming": False,
        "batch_operations": False,
        "webhooks": False
    },
    APIVersion.V2: {
        "websocket": True,
        "streaming": True,
        "batch_operations": True,
        "webhooks": True
    }
}


def is_feature_enabled(version: APIVersion, feature: str) -> bool:
    """Check if feature is enabled for version"""
    return FEATURES.get(version, {}).get(feature, False)
