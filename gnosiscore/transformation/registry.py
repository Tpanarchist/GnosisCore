from typing import Callable, Awaitable, Dict, Optional
from gnosiscore.primitives.models import Transformation, Result, LLMParams, PluginInfo
import httpx
import os
from uuid import uuid4
from datetime import datetime, timezone

class TransformationHandlerRegistry:
    def __init__(self):
        self._handlers: Dict[str, Callable[[Transformation], Awaitable[Result]]] = {}
        self._plugins: Dict[str, PluginInfo] = {}
        self._llm_handler = self._default_llm_handler

    def register(self, operation: str, handler: Callable[[Transformation], Awaitable[Result]], plugin_info: Optional[PluginInfo] = None):
        self._handlers[operation] = handler
        if plugin_info:
            self._plugins[operation] = plugin_info

    def unregister(self, operation: str):
        self._handlers.pop(operation, None)
        self._plugins.pop(operation, None)

    def enable_plugin(self, operation: str):
        if operation in self._plugins:
            self._plugins[operation].enabled = True

    def disable_plugin(self, operation: str):
        if operation in self._plugins:
            self._plugins[operation].enabled = False

    def get_plugin_info(self, operation: str) -> Optional[PluginInfo]:
        return self._plugins.get(operation)

    def list_plugins(self) -> Dict[str, PluginInfo]:
        return dict(self._plugins)

    async def handle(self, transformation: Transformation) -> Result:
        content = transformation.content
        llm_params_dict = content.get("llm_params")
        if llm_params_dict:
            return await self._llm_handler(transformation)
        op = content.get("operation")
        if not isinstance(op, str):
            return Result(
                id=uuid4(),
                intent_id=transformation.id,
                status="failure",
                output=None,
                error="Operation must be a string",
                timestamp=datetime.now(timezone.utc)
            )
        handler = self._handlers.get(op)
        if handler:
            return await handler(transformation)
        return Result(
            id=uuid4(),
            intent_id=transformation.id,
            status="failure",
            output=None,
            error=f"No handler registered for operation '{op}'",
            timestamp=datetime.now(timezone.utc)
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
                timestamp=datetime.now(timezone.utc)
            )
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return Result(
                id=uuid4(),
                intent_id=transformation.id,
                status="failure",
                output=None,
                error="OPENAI_API_KEY not set",
                timestamp=datetime.now(timezone.utc)
            )
        async with httpx.AsyncClient() as client:
            try:
                extra_params = params.extra_params if params.extra_params else {}
                payload = {
                    "model": params.model,
                    "messages": [
                        {"role": "system", "content": params.system_prompt or ""},
                        {"role": "user", "content": params.user_prompt},
                    ],
                    "temperature": params.temperature,
                    "max_tokens": params.max_tokens,
                }
                # Only add extra_params keys that do not conflict with required keys
                for k, v in extra_params.items():
                    if k not in payload:
                        payload[k] = v
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json=payload
                )
                resp.raise_for_status()
                result = resp.json()
                return Result(
                    id=uuid4(),
                    intent_id=transformation.id,
                    status="success",
                    output={"llm_response": result},
                    error=None,
                    timestamp=datetime.now(timezone.utc)
                )
            except Exception as e:
                return Result(
                    id=uuid4(),
                    intent_id=transformation.id,
                    status="failure",
                    output=None,
                    error=str(e),
                    timestamp=datetime.now(timezone.utc)
                )
