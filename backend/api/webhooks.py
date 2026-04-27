"""
Webhook System
Provides webhook registration and event notifications.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from datetime import datetime
import httpx
import hashlib
import hmac
import uuid

from .auth import get_current_user, require_authentication


router = APIRouter(prefix="/api/v1/webhooks", tags=["Webhooks"])


class WebhookEvent:
    """Webhook event types"""
    TRANSACTION_CREATED = "transaction.created"
    TRANSACTION_UPDATED = "transaction.updated"
    BUDGET_EXCEEDED = "budget.exceeded"
    FRAUD_DETECTED = "fraud.detected"
    RISK_SCORE_CHANGED = "risk_score.changed"
    INSURANCE_EXPIRING = "insurance.expiring"


class WebhookConfig(BaseModel):
    """Webhook configuration"""
    webhook_id: Optional[str] = None
    url: HttpUrl
    events: List[str]
    secret: Optional[str] = None
    active: bool = True
    description: Optional[str] = None


class Webhook(BaseModel):
    """Webhook model"""
    webhook_id: str
    user_id: str
    url: str
    events: List[str]
    secret: str
    active: bool
    created_at: datetime
    last_triggered: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0
    description: Optional[str] = None


class WebhookDelivery(BaseModel):
    """Webhook delivery record"""
    delivery_id: str
    webhook_id: str
    event_type: str
    payload: Dict[str, Any]
    status_code: Optional[int] = None
    success: bool
    error: Optional[str] = None
    delivered_at: datetime
    response_time: Optional[float] = None


class WebhookManager:
    """Manages webhooks"""
    
    def __init__(self):
        # In-memory storage (in production, use database)
        self.webhooks: Dict[str, Webhook] = {}
        self.deliveries: List[WebhookDelivery] = []
    
    def create_webhook(
        self,
        user_id: str,
        config: WebhookConfig
    ) -> Webhook:
        """
        Create a new webhook.
        
        Args:
            user_id: User ID
            config: Webhook configuration
            
        Returns:
            Created webhook
        """
        webhook_id = f"wh_{uuid.uuid4().hex[:16]}"
        secret = config.secret or f"whsec_{uuid.uuid4().hex}"
        
        webhook = Webhook(
            webhook_id=webhook_id,
            user_id=user_id,
            url=str(config.url),
            events=config.events,
            secret=secret,
            active=config.active,
            created_at=datetime.utcnow(),
            description=config.description
        )
        
        self.webhooks[webhook_id] = webhook
        return webhook
    
    def get_webhook(self, webhook_id: str) -> Optional[Webhook]:
        """Get webhook by ID"""
        return self.webhooks.get(webhook_id)
    
    def list_webhooks(self, user_id: str) -> List[Webhook]:
        """List webhooks for a user"""
        return [
            wh for wh in self.webhooks.values()
            if wh.user_id == user_id
        ]
    
    def update_webhook(
        self,
        webhook_id: str,
        config: WebhookConfig
    ) -> Optional[Webhook]:
        """Update webhook configuration"""
        webhook = self.webhooks.get(webhook_id)
        if not webhook:
            return None
        
        webhook.url = str(config.url)
        webhook.events = config.events
        webhook.active = config.active
        if config.description:
            webhook.description = config.description
        
        return webhook
    
    def delete_webhook(self, webhook_id: str) -> bool:
        """Delete webhook"""
        if webhook_id in self.webhooks:
            del self.webhooks[webhook_id]
            return True
        return False
    
    async def trigger_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        user_id: Optional[str] = None
    ):
        """
        Trigger webhook event.
        
        Args:
            event_type: Event type
            payload: Event payload
            user_id: User ID (if None, triggers for all users)
        """
        # Find matching webhooks
        matching_webhooks = [
            wh for wh in self.webhooks.values()
            if wh.active and event_type in wh.events
            and (user_id is None or wh.user_id == user_id)
        ]
        
        # Deliver to each webhook
        for webhook in matching_webhooks:
            await self._deliver_webhook(webhook, event_type, payload)
    
    async def _deliver_webhook(
        self,
        webhook: Webhook,
        event_type: str,
        payload: Dict[str, Any]
    ):
        """
        Deliver webhook to endpoint.
        
        Args:
            webhook: Webhook configuration
            event_type: Event type
            payload: Event payload
        """
        delivery_id = f"del_{uuid.uuid4().hex[:16]}"
        start_time = datetime.utcnow()
        
        # Prepare payload
        webhook_payload = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": payload
        }
        
        # Generate signature
        signature = self._generate_signature(webhook.secret, webhook_payload)
        
        try:
            # Send webhook
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    webhook.url,
                    json=webhook_payload,
                    headers={
                        "Content-Type": "application/json",
                        "X-Webhook-Signature": signature,
                        "X-Webhook-ID": webhook.webhook_id,
                        "X-Event-Type": event_type
                    }
                )
                
                response_time = (datetime.utcnow() - start_time).total_seconds()
                success = 200 <= response.status_code < 300
                
                # Record delivery
                delivery = WebhookDelivery(
                    delivery_id=delivery_id,
                    webhook_id=webhook.webhook_id,
                    event_type=event_type,
                    payload=webhook_payload,
                    status_code=response.status_code,
                    success=success,
                    delivered_at=datetime.utcnow(),
                    response_time=response_time
                )
                
                self.deliveries.append(delivery)
                
                # Update webhook stats
                webhook.last_triggered = datetime.utcnow()
                if success:
                    webhook.success_count += 1
                else:
                    webhook.failure_count += 1
                
        except Exception as e:
            # Record failed delivery
            delivery = WebhookDelivery(
                delivery_id=delivery_id,
                webhook_id=webhook.webhook_id,
                event_type=event_type,
                payload=webhook_payload,
                success=False,
                error=str(e),
                delivered_at=datetime.utcnow()
            )
            
            self.deliveries.append(delivery)
            webhook.failure_count += 1
    
    def _generate_signature(self, secret: str, payload: Dict[str, Any]) -> str:
        """Generate HMAC signature for webhook"""
        import json
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    def get_deliveries(
        self,
        webhook_id: str,
        limit: int = 50
    ) -> List[WebhookDelivery]:
        """Get delivery history for a webhook"""
        deliveries = [
            d for d in self.deliveries
            if d.webhook_id == webhook_id
        ]
        return sorted(deliveries, key=lambda d: d.delivered_at, reverse=True)[:limit]


# Global webhook manager
webhook_manager = WebhookManager()


@router.post("/", response_model=Webhook)
async def create_webhook(
    config: WebhookConfig,
    current_user: Dict[str, Any] = Depends(require_authentication)
):
    """Create a new webhook"""
    webhook = webhook_manager.create_webhook(
        user_id=current_user["user_id"],
        config=config
    )
    return webhook


@router.get("/", response_model=List[Webhook])
async def list_webhooks(
    current_user: Dict[str, Any] = Depends(require_authentication)
):
    """List all webhooks for current user"""
    webhooks = webhook_manager.list_webhooks(current_user["user_id"])
    return webhooks


@router.get("/{webhook_id}", response_model=Webhook)
async def get_webhook(
    webhook_id: str,
    current_user: Dict[str, Any] = Depends(require_authentication)
):
    """Get webhook by ID"""
    webhook = webhook_manager.get_webhook(webhook_id)
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    if webhook.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return webhook


@router.put("/{webhook_id}", response_model=Webhook)
async def update_webhook(
    webhook_id: str,
    config: WebhookConfig,
    current_user: Dict[str, Any] = Depends(require_authentication)
):
    """Update webhook configuration"""
    webhook = webhook_manager.get_webhook(webhook_id)
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    if webhook.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    updated = webhook_manager.update_webhook(webhook_id, config)
    return updated


@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: str,
    current_user: Dict[str, Any] = Depends(require_authentication)
):
    """Delete webhook"""
    webhook = webhook_manager.get_webhook(webhook_id)
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    if webhook.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    webhook_manager.delete_webhook(webhook_id)
    return {"message": "Webhook deleted"}


@router.get("/{webhook_id}/deliveries", response_model=List[WebhookDelivery])
async def get_webhook_deliveries(
    webhook_id: str,
    limit: int = 50,
    current_user: Dict[str, Any] = Depends(require_authentication)
):
    """Get delivery history for a webhook"""
    webhook = webhook_manager.get_webhook(webhook_id)
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    if webhook.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    deliveries = webhook_manager.get_deliveries(webhook_id, limit)
    return deliveries


@router.post("/test/{webhook_id}")
async def test_webhook(
    webhook_id: str,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(require_authentication)
):
    """Send a test event to webhook"""
    webhook = webhook_manager.get_webhook(webhook_id)
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    if webhook.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Send test event in background
    test_payload = {
        "test": True,
        "message": "This is a test webhook delivery",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    background_tasks.add_task(
        webhook_manager._deliver_webhook,
        webhook,
        "test.event",
        test_payload
    )
    
    return {"message": "Test webhook queued for delivery"}


@router.get("/events/types")
async def get_event_types():
    """Get available webhook event types"""
    return {
        "events": [
            {"type": "transaction.created", "description": "New transaction created"},
            {"type": "transaction.updated", "description": "Transaction updated"},
            {"type": "budget.exceeded", "description": "Budget limit exceeded"},
            {"type": "fraud.detected", "description": "Fraudulent transaction detected"},
            {"type": "risk_score.changed", "description": "Risk score changed significantly"},
            {"type": "insurance.expiring", "description": "Insurance policy expiring soon"}
        ]
    }
