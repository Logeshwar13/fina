# FinA API Documentation

Complete API reference for the FinA backend.

## Base URL

```
http://localhost:8000
```

## Authentication

All endpoints require authentication via Supabase JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

---

## AI Chat Endpoints

### POST /ai/chat

Send a query to the multi-agent AI system.

**Request Body:**
```json
{
  "query": "What are my recent transactions?",
  "user_id": "ad200e5a-3d99-4d9f-850b-22ae2563bcc4"
}
```

**Response:**
```json
{
  "success": true,
  "response": "You have 21 transactions...",
  "agents_used": ["budget_agent", "transaction_agent"],
  "execution_time": 2.45,
  "metadata": {
    "plan": "...",
    "observations": "..."
  }
}
```

### DELETE /ai/chat/history/{user_id}

Clear chat history for a user.

**Response:**
```json
{
  "success": true,
  "message": "Chat history cleared"
}
```

---

## Transaction Endpoints

### GET /transactions

Get user's transactions with optional filters.

**Query Parameters:**
- `user_id` (required): User ID
- `limit` (optional): Max transactions (default: 50)
- `type` (optional): "expense", "income", or "all"
- `category` (optional): Filter by category
- `start_date` (optional): ISO date string
- `end_date` (optional): ISO date string

**Response:**
```json
{
  "transactions": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "amount": 649,
      "type": "expense",
      "category": "Food & Dining",
      "description": "Lunch at KFC",
      "timestamp": "2026-04-27T12:30:00Z",
      "is_fraud": false
    }
  ],
  "count": 21
}
```

### POST /transactions

Create a new transaction.

**Request Body:**
```json
{
  "user_id": "uuid",
  "amount": 5000,
  "type": "expense",
  "category": "Investments",
  "description": "Gold ETF purchase"
}
```

---

## Budget Endpoints

### GET /budgets

Get user's budgets with spending status.

**Query Parameters:**
- `user_id` (required)

**Response:**
```json
{
  "budgets": [
    {
      "category": "Food & Dining",
      "limit": 10000,
      "spent": 5000,
      "remaining": 5000,
      "percentage_used": 50,
      "status": "healthy"
    }
  ]
}
```

### POST /budgets

Create a new budget.

**Request Body:**
```json
{
  "user_id": "uuid",
  "category": "Healthcare",
  "limit_amount": 10000
}
```

### PUT /budgets

Update an existing budget.

**Request Body:**
```json
{
  "user_id": "uuid",
  "category": "Healthcare",
  "limit_amount": 15000
}
```

---

## Risk Endpoints

### GET /risk/score

Get user's financial health risk score.

**Query Parameters:**
- `user_id` (required)

**Response:**
```json
{
  "score": 75,
  "grade": "B",
  "label": "Good",
  "breakdown": {
    "income_stability": 85,
    "expense_ratio": 70,
    "savings_rate": 80,
    "debt_ratio": 65
  }
}
```

---

## Fraud Endpoints

### GET /fraud/alerts

Get flagged fraudulent transactions.

**Query Parameters:**
- `user_id` (required)
- `limit` (optional): Max alerts (default: 10)

**Response:**
```json
{
  "fraud_count": 2,
  "flagged_transactions": [...],
  "total_amount_at_risk": 15000
}
```

---

## Insurance Endpoints

### GET /insurance/policies

Get user's insurance policies.

**Query Parameters:**
- `user_id` (required)

**Response:**
```json
{
  "policies": [
    {
      "id": "uuid",
      "policy_type": "health",
      "provider": "ABC Insurance",
      "coverage_amount": 500000,
      "premium_amount": 12000
    }
  ]
}
```

---

## Health & Monitoring

### GET /health

Check application health.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-28T10:00:00Z",
  "services": {
    "database": "connected",
    "llm": "available",
    "rag": "ready"
  }
}
```

### GET /metrics

Get Prometheus metrics (plain text format).

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "success": false,
  "error": "Error message",
  "detail": "Detailed error information",
  "timestamp": "2026-04-28T10:00:00Z"
}
```

### Common HTTP Status Codes

- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Missing or invalid authentication
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

---

## Rate Limiting

Default rate limits:
- 100 requests per minute per IP
- 1000 requests per hour per user

---

## MCP Tools

The AI agents have access to 15 tools for transaction management, budgets, risk analysis, fraud detection, and insurance.

---

For complete API documentation, visit: http://localhost:8000/docs

**Last Updated**: April 28, 2026
