from openai import OpenAI
import asyncio
import json
import time
from typing import Optional, List, Dict, Any, AsyncGenerator
from constants import *

# Initialize client
# Only initialize if we have a real API key or we're not testing
if OPENAI_API_KEY != 'test-key-for-testing' or not os.getenv('TESTING'):
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    client = None


TEXT_MODELS_LIST = OPENAI_TEXT_MODELS.split(",")
VISION_MODELS = OPENAI_IMG_TEXT_MODELS.split(",")

class GPTError(Exception):
    """Base exception for GPT-related errors"""
    pass

class RateLimitError(GPTError):
    pass

class ContextLengthError(GPTError):
    pass

def _validate_messages(messages: List[Dict[str, str]]) -> None:
    """Validate message structure with minimal checks"""
    if not messages:
        raise ValueError("Messages list cannot be empty")
    
    for msg in messages:
        if "role" not in msg or "content" not in msg:
            raise ValueError("Each message must have 'role' and 'content'")
        if not isinstance(msg["content"], (str, list)):
            raise ValueError("Content must be string or list")

def _get_model(models_list: List[str], percentage: float) -> str:
    """Get model from list based on percentage"""
    percentage = max(0.0, min(1.0, percentage))
    index = max(0, int(percentage * (len(models_list) - 1)))
    return models_list[index]

# ---------- BASE CALL ----------
async def call_openai(
    messages: List[Dict[str, str]],
    model_detail_percentage: float = 0.1,
    temperature: float = TEMPERATURE,
    max_tokens: int = MAX_TOKENS,
    json_mode: bool = False,
    stream: bool = False
) -> Any:

    # Input validation
    _validate_messages(messages)
    
    model = _get_model(TEXT_MODELS_LIST, model_detail_percentage)
    print(f"[GPT] Using model: {model}")

    # Minimal payload - only essential parameters
    base_payload = {
        "model": model,
        "messages": messages,
    }

    print(f"[GPT MODEL]: {model}")

    # Handle parameter name based on model
    if (model  in ['gpt-4o', 'gpt-4-turbo', 'o1','o3-mini']):
        base_payload["max_completion_tokens"] = max_tokens
    else:
        base_payload["max_tokens"] = max_tokens
        base_payload["temperature"] =temperature


    if json_mode:
        base_payload["response_format"] = {"type": "json_object"}

    for attempt in range(RETRIES):
        try:
            start_time = time.time()
            response = client.chat.completions.create(
                **base_payload,
                stream=stream
            )

            if stream:
                async def stream_generator():
                    for chunk in response:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, "content") and delta.content:
                            yield delta.content
                return stream_generator()

            result = response.choices[0].message.content
            duration = time.time() - start_time
            print(f"[GPT] Call completed in {duration:.2f}s")
            return result,model

        except Exception as e:
            print(f"[GPT ERROR] Attempt {attempt+1}/{RETRIES}: {e}")
            if attempt == RETRIES - 1:  # Last attempt
                raise GPTError(f"OpenAI failed after {RETRIES} retries: {e}")
            await asyncio.sleep(0.5 * (attempt + 1))

async def call_openai_vision(
    messages: List[Dict[str, Any]],
    images: List[str] = None,
    model_detail_percentage: float = 0.3,
    temperature: float = TEMPERATURE,
    max_tokens: int = MAX_TOKENS,
    json_mode: bool = False,
    stream: bool = False
):
    """Minimal vision call implementation"""
    images = images or []
    
    model = _get_model(VISION_MODELS, model_detail_percentage)
    print(f"[GPT-VISION] Using model: {model}")

    # Build content efficiently
    content_blocks = []
    
    # Add text content from user messages only
    for msg in messages:
        if msg["role"] == "user":
            content = msg.get("content", "")
            if isinstance(content, str) and content.strip():
                content_blocks.append({"type": "text", "text": content.strip()})
            elif isinstance(content, list):
                content_blocks.extend(content)

    # Add images with minimal data
    for img in images:
        if img.startswith("http"):
            content_blocks.append({
                "type": "image_url",
                "image_url": {"url": img, "detail": "low"}  # Use low detail to save tokens
            })
        else:
            content_blocks.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img}",
                    "detail": "low"
                }
            })

    # Single user message with all content
    model_messages = [{"role": "user", "content": content_blocks}]

    payload = {
        "model": model,
        "messages": model_messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream
    }

    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    for attempt in range(RETRIES):
        try:
            start_time = time.time()
            response = client.chat.completions.create(**payload)

            if stream:
                async def stream_gen():
                    for chunk in response:
                        delta = chunk.choices[0].delta
                        if delta and getattr(delta, "content", None):
                            yield delta.content
                return stream_gen()

            result = response.choices[0].message.content
            duration = time.time() - start_time
            print(f"[GPT-VISION] Call completed in {duration:.2f}s")
            print(f"[RESULT]: {result}")
            return result,model

        except Exception as e:
            print(f"[GPT-VISION ERROR] Attempt {attempt+1}: {e}")
            if attempt == RETRIES - 1:
                raise GPTError(f"Vision request failed after {RETRIES} retries: {e}")
            await asyncio.sleep(0.5 * (attempt + 1))

