# Groq Setup Guide - FREE & FAST LLM

## Why Groq?

✅ **FREE** - No credit card required  
✅ **FAST** - 500+ tokens/second (10x faster than OpenAI)  
✅ **POWERFUL** - Llama 3.1 70B, Mixtral 8x7B  
✅ **COMPATIBLE** - OpenAI-compatible API  

## Step 1: Get Your Free API Key

1. Go to https://console.groq.com
2. Sign up (free, no credit card)
3. Go to "API Keys" section
4. Click "Create API Key"
5. Copy your key (starts with `gsk_...`)

## Step 2: Configure FinA

Add to your `backend/.env`:

```bash
GROQ_API_KEY=gsk_your_key_here
MCP_PROVIDER=groq
MCP_MODEL=llama-3.3-70b-versatile
```

## Step 3: Install Dependencies

```bash
cd backend
pip install openai sentence-transformers
```

## Step 4: Test It

```python
from mcp import ModelLayer

# Initialize with Groq
model = ModelLayer(provider="groq")

# Generate response
response = await model.generate(
    messages=[
        {"role": "system", "content": "You are a financial assistant"},
        {"role": "user", "content": "What's my spending this month?"}
    ]
)

print(response["content"])
```

## Available Groq Models

### Recommended for FinA:

**llama-3.3-70b-versatile** (Default - Updated Model)
- Best balance of speed and quality
- Great for financial analysis
- 128K context window

**mixtral-8x7b-32768**
- Faster than Llama
- Good for simple queries
- 32K context window

**llama-3.1-8b-instant**
- Fastest option
- Good for quick responses
- 128K context window

### How to Change Model:

```python
# In code
model = ModelLayer(provider="groq", model="mixtral-8x7b-32768")

# Or in .env
MCP_MODEL=mixtral-8x7b-32768
```

## Features Supported

✅ Chat completions  
✅ Function calling / Tool use  
✅ Streaming (not implemented yet)  
✅ System prompts  
✅ Temperature control  

❌ Embeddings (uses sentence-transformers fallback)  
❌ Vision (text-only)  

## Rate Limits (Free Tier)

- **Requests:** 30 per minute
- **Tokens:** 6,000 per minute
- **Daily:** 14,400 requests

More than enough for development and testing!

## Embeddings with Groq

Groq doesn't have embeddings API, so we use sentence-transformers:

```python
# Automatically handled by ModelLayer
embeddings = await model.generate_embeddings([
    "Transaction 1",
    "Transaction 2"
])

# Uses all-MiniLM-L6-v2 (384 dimensions)
# Fast and works offline!
```

## Performance Comparison

| Provider | Speed | Cost | Quality |
|----------|-------|------|---------|
| Groq (Llama 3.1 70B) | 500 tok/s | FREE | ⭐⭐⭐⭐ |
| OpenAI (GPT-4) | 40 tok/s | $0.03/1K | ⭐⭐⭐⭐⭐ |
| Anthropic (Claude) | 50 tok/s | $0.015/1K | ⭐⭐⭐⭐⭐ |

## Example: Complete Flow

```python
import asyncio
from mcp import ModelLayer, tool_registry, guardrails

async def main():
    # Initialize with Groq
    model = ModelLayer(provider="groq")
    
    # Validate input
    is_valid, errors = guardrails.validate_input({
        "user_id": "user-123",
        "query": "Show my transactions"
    })
    
    if not is_valid:
        print(f"Invalid input: {errors}")
        return
    
    # Get tools
    tools = tool_registry.get_tool_schemas(format="openai")
    
    # Generate with tools
    response = await model.generate(
        messages=[
            {"role": "system", "content": "You are a financial assistant"},
            {"role": "user", "content": "What did I spend on food last month?"}
        ],
        tools=tools,
        temperature=0.7
    )
    
    print(f"Response: {response['content']}")
    print(f"Tool calls: {len(response['tool_calls'])}")
    
    # Validate output
    is_safe, error, modified = guardrails.validate_output(response["content"])
    print(f"Safe: {is_safe}")

asyncio.run(main())
```

## Troubleshooting

### "GROQ_API_KEY not found"
- Make sure you added it to `backend/.env`
- Restart your server after adding

### "Rate limit exceeded"
- Free tier: 30 requests/minute
- Wait a minute and try again
- Or upgrade to paid tier

### "Model not found"
- Check model name spelling
- Available: llama-3.3-70b-versatile, mixtral-8x7b-32768, llama-3.1-8b-instant

### Embeddings error
- Install: `pip install sentence-transformers`
- First run downloads model (~80MB)

## Tips for Best Results

1. **Use llama-3.3-70b-versatile** for complex financial analysis
2. **Use mixtral-8x7b-32768** for faster simple queries
3. **Keep temperature at 0.7** for balanced responses
4. **Use system prompts** to guide behavior
5. **Enable function calling** for tool use

## Upgrade to Paid (Optional)

If you need more:
- Higher rate limits
- Priority access
- Dedicated support

Visit: https://console.groq.com/settings/billing

But free tier is perfect for development!

---

**Ready to use Groq with FinA!** 🚀

Just set your `GROQ_API_KEY` in `.env` and you're good to go!
