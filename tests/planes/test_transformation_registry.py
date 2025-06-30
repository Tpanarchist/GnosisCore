import pytest
import asyncio
from uuid import uuid4
from datetime import datetime, timezone
from gnosiscore.primitives.models import Transformation, Metadata, Result, LLMParams
from gnosiscore.transformation.registry import TransformationHandlerRegistry

@pytest.mark.asyncio
async def test_register_and_dispatch_local_handler():
    registry = TransformationHandlerRegistry()
    async def add_handler(trans: Transformation) -> Result:
        return Result(
            id=uuid4(),
            intent_id=trans.id,
            status="success",
            output={"added": True},
            error=None,
            timestamp=datetime.now(timezone.utc)
        )
    registry.register("add_node", add_handler)
    t = Transformation.create(
        id=uuid4(),
        metadata=Metadata(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
        operation="add_node",
        target=uuid4(),
        parameters={}
    )
    result = await registry.handle(t)
    assert result.status == "success"
    assert result.output["added"]

@pytest.mark.asyncio
async def test_unregister_and_fallback():
    registry = TransformationHandlerRegistry()
    async def dummy_handler(trans): 
        return Result(
            id=uuid4(),
            intent_id=trans.id,
            status="success",
            output=None,
            error=None,
            timestamp=datetime.now(timezone.utc)
        )
    registry.register("dummy", dummy_handler)
    registry.unregister("dummy")
    t = Transformation.create(
        id=uuid4(),
        metadata=Metadata(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
        operation="dummy",
        target=uuid4(),
        parameters={}
    )
    result = await registry.handle(t)
    assert result.status == "failure"
    assert "No handler registered" in result.error

@pytest.mark.asyncio
async def test_llm_handler(monkeypatch):
    registry = TransformationHandlerRegistry()
    params = LLMParams(
        model="gpt-4o-mini",
        system_prompt="You are a test agent.",
        user_prompt="Say hi.",
        temperature=0.1,
        max_tokens=8,
    )
    t = Transformation.create(
        id=uuid4(),
        metadata=Metadata(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
        operation="llm",
        target=uuid4(),
        parameters={},
        llm_params=params
    )
    # Patch out httpx.AsyncClient
    class DummyResp:
        def raise_for_status(self): pass
        def json(self): return {"choices": [{"message": {"content": "hello"}}]}
    class DummyClient:
        async def __aenter__(self): return self
        async def __aexit__(self, *a): pass
        async def post(self, *a, **kw): return DummyResp()
    monkeypatch.setattr("httpx.AsyncClient", lambda *a, **kw: DummyClient())
    result = await registry.handle(t)
    assert result.status == "success"
    assert "llm_response" in result.output

@pytest.mark.asyncio
async def test_no_api_key(monkeypatch):
    registry = TransformationHandlerRegistry()
    params = LLMParams(
        model="gpt-4o-mini",
        system_prompt="Test",
        user_prompt="Test",
        temperature=0.1,
        max_tokens=8,
    )
    t = Transformation.create(
        id=uuid4(),
        metadata=Metadata(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
        operation="llm",
        target=uuid4(),
        parameters={},
        llm_params=params
    )
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = await registry.handle(t)
    assert result.status == "failure"
    assert "OPENAI_API_KEY" in result.error
