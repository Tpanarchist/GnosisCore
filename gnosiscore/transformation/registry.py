import asyncio
from typing import Callable, Awaitable, Dict, Optional, Any
from gnosiscore.primitives.models import Transformation, Result, LLMParams
import httpx
import os
from uuid import uuid4
from datetime import datetime

class TransformationHandlerRegistry:
    def __init__(self):
        self._handlers: Dict[str, Callable[[Transformation], Awaitable[Result]]] = {}
        self._llm_handler = self._default_llm_handler

    def register(self, operation: str, handler: Callable[[Transformation], Awaitable[Result]]):
        self._handlers[operation] = handler

    def unregister(self, operation: str):
        self._handlers.pop(operation, None)

    async def handle(self, transformation: Transformation) -> Result:
        content = transformation.content
        llm_params_dict = content.get("llm_params")
        if llm_params_dict:
            return await self._llm_handler(transformation)
        op = content.get("operation")
        handler = self._handlers.get(op)
        if handler:
            return await handler(transformation)
        return Result(
            id=uuid4(),
            intent_id=transformation.id,
            status="failure",
            output=None,
            error=f"No handler registered for operation '{op}'",
            timestamp=datetime.utcnow()
        )

    async def _default_llm_handler(self, transformation: Transformation) -> Result:
        content = transformation.content
        llm_params_dict = content.get("llm_params")
        try:
            params = LLMParams(**llm_params_dict)
        except Exception as e:
            return Result(
                id=uuid4(),
                intent_id=transformation.id,
                status="failure",
                output=None,
                error=f"Invalid llm_params: {e}",
                timestamp=datetime.utcnow()
            )
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return Result(
                id=uuid4(),
                intent_id=transformation.id,
                status="failure",
                output=None,
                error="OPENAI_API_KEY not set",
                timestamp=datetime.utcnow()
            )
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": params.model,
                        "messages": [
                            {"role": "system", "content": params.system_prompt or ""},
                            {"role": "user", "content": params.user_prompt},
                        ],
                        "temperature": params.temperature,
                        "max_tokens": params.max_tokens,
                        **params.extra_params,
                    }
                )
                resp.raise_for_status()
                result = resp.json()
                return Result(
                    id=uuid4(),
                    intent_id=transformation.id,
                    status="success",
                    output={"llm_response": result},
                    error=None,
                    timestamp=datetime.utcnow()
                )
            except Exception as e:
                return Result(
                    id=uuid4(),
                    intent_id=transformation.id,
                    status="failure",
                    output=None,
                    error=str(e),
                    timestamp=datetime.utcnow()
                )
