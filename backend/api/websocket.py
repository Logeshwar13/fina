"""
WebSocket Manager
Provides real-time communication for streaming responses and live updates.
"""

from typing import Dict, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
from datetime import datetime
import uuid


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        # Active connections by connection_id
        self.active_connections: Dict[str, WebSocket] = {}
        # User to connections mapping
        self.user_connections: Dict[str, Set[str]] = {}
        # Connection metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str) -> str:
        """
        Accept and register a new WebSocket connection.
        
        Args:
            websocket: WebSocket instance
            user_id: User ID
            
        Returns:
            Connection ID
        """
        await websocket.accept()
        
        # Generate connection ID
        connection_id = str(uuid.uuid4())
        
        # Register connection
        self.active_connections[connection_id] = websocket
        
        # Add to user connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)
        
        # Store metadata
        self.connection_metadata[connection_id] = {
            "user_id": user_id,
            "connected_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat()
        }
        
        return connection_id
    
    def disconnect(self, connection_id: str):
        """
        Remove a WebSocket connection.
        
        Args:
            connection_id: Connection ID
        """
        if connection_id in self.active_connections:
            # Get user_id before removing
            metadata = self.connection_metadata.get(connection_id, {})
            user_id = metadata.get("user_id")
            
            # Remove from active connections
            del self.active_connections[connection_id]
            
            # Remove from user connections
            if user_id and user_id in self.user_connections:
                self.user_connections[user_id].discard(connection_id)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            
            # Remove metadata
            if connection_id in self.connection_metadata:
                del self.connection_metadata[connection_id]
    
    async def send_message(self, connection_id: str, message: Dict[str, Any]):
        """
        Send message to a specific connection.
        
        Args:
            connection_id: Connection ID
            message: Message to send
        """
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_json(message)
                # Update last activity
                if connection_id in self.connection_metadata:
                    self.connection_metadata[connection_id]["last_activity"] = datetime.utcnow().isoformat()
            except Exception as e:
                print(f"Error sending message to {connection_id}: {e}")
                self.disconnect(connection_id)
    
    async def send_to_user(self, user_id: str, message: Dict[str, Any]):
        """
        Send message to all connections of a user.
        
        Args:
            user_id: User ID
            message: Message to send
        """
        if user_id in self.user_connections:
            connection_ids = list(self.user_connections[user_id])
            for connection_id in connection_ids:
                await self.send_message(connection_id, message)
    
    async def broadcast(self, message: Dict[str, Any], exclude: Optional[Set[str]] = None):
        """
        Broadcast message to all connections.
        
        Args:
            message: Message to send
            exclude: Set of connection IDs to exclude
        """
        exclude = exclude or set()
        connection_ids = [cid for cid in self.active_connections.keys() if cid not in exclude]
        
        for connection_id in connection_ids:
            await self.send_message(connection_id, message)
    
    def get_user_connections(self, user_id: str) -> int:
        """
        Get number of active connections for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of connections
        """
        return len(self.user_connections.get(user_id, set()))
    
    def get_total_connections(self) -> int:
        """
        Get total number of active connections.
        
        Returns:
            Number of connections
        """
        return len(self.active_connections)
    
    def get_connection_info(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """
        Get connection metadata.
        
        Args:
            connection_id: Connection ID
            
        Returns:
            Connection metadata or None
        """
        return self.connection_metadata.get(connection_id)


class WebSocketManager:
    """High-level WebSocket manager for streaming AI responses"""
    
    def __init__(self):
        self.connection_manager = ConnectionManager()
    
    async def handle_connection(self, websocket: WebSocket, user_id: str):
        """
        Handle a WebSocket connection lifecycle.
        
        Args:
            websocket: WebSocket instance
            user_id: User ID
        """
        connection_id = await self.connection_manager.connect(websocket, user_id)
        
        try:
            # Send welcome message
            await self.connection_manager.send_message(connection_id, {
                "type": "connection",
                "status": "connected",
                "connection_id": connection_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Listen for messages
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                await self.handle_message(connection_id, user_id, message)
                
        except WebSocketDisconnect:
            self.connection_manager.disconnect(connection_id)
        except Exception as e:
            print(f"WebSocket error: {e}")
            self.connection_manager.disconnect(connection_id)
    
    async def handle_message(self, connection_id: str, user_id: str, message: Dict[str, Any]):
        """
        Handle incoming WebSocket message.
        
        Args:
            connection_id: Connection ID
            user_id: User ID
            message: Message data
        """
        message_type = message.get("type")
        
        if message_type == "ping":
            # Respond to ping
            await self.connection_manager.send_message(connection_id, {
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        elif message_type == "query":
            # Handle AI query (will be implemented with streaming)
            await self.handle_query(connection_id, user_id, message)
        
        else:
            # Unknown message type
            await self.connection_manager.send_message(connection_id, {
                "type": "error",
                "error": f"Unknown message type: {message_type}",
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def handle_query(self, connection_id: str, user_id: str, message: Dict[str, Any]):
        """
        Handle AI query with streaming response.
        
        Args:
            connection_id: Connection ID
            user_id: User ID
            message: Query message
        """
        query = message.get("query", "")
        
        # Send acknowledgment
        await self.connection_manager.send_message(connection_id, {
            "type": "query_received",
            "query": query,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # TODO: Integrate with agent coordinator for streaming
        # For now, send a placeholder response
        await self.connection_manager.send_message(connection_id, {
            "type": "response",
            "response": f"Processing query: {query}",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def stream_response(self, connection_id: str, response_generator):
        """
        Stream AI response chunks to client.
        
        Args:
            connection_id: Connection ID
            response_generator: Async generator yielding response chunks
        """
        try:
            async for chunk in response_generator:
                await self.connection_manager.send_message(connection_id, {
                    "type": "chunk",
                    "content": chunk,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            # Send completion message
            await self.connection_manager.send_message(connection_id, {
                "type": "complete",
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            await self.connection_manager.send_message(connection_id, {
                "type": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def notify_user(self, user_id: str, notification: Dict[str, Any]):
        """
        Send notification to all user connections.
        
        Args:
            user_id: User ID
            notification: Notification data
        """
        await self.connection_manager.send_to_user(user_id, {
            "type": "notification",
            "data": notification,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get WebSocket statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            "total_connections": self.connection_manager.get_total_connections(),
            "unique_users": len(self.connection_manager.user_connections),
            "connections_by_user": {
                user_id: len(connections)
                for user_id, connections in self.connection_manager.user_connections.items()
            }
        }


# Global WebSocket manager instance
websocket_manager = WebSocketManager()
