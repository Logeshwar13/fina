"""
API Package
Enhanced API features including versioning, WebSocket support, and authentication.
"""

from .versioning import APIVersion
from .websocket import WebSocketManager
from .auth import APIKeyManager, get_current_user

__all__ = [
    'APIVersion',
    'WebSocketManager',
    'APIKeyManager',
    'get_current_user'
]
