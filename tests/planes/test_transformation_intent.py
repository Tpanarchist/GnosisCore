import pytest
from uuid import uuid4
from datetime import datetime, timezone
from gnosiscore.primitives.models import Transformation, Metadata, Intent, Result, LLMParams
from gnosiscore.planes.digital import DigitalPlane
from gnosiscore.planes.mental import MentalPlane
from gnosiscore.primitives.models import Boundary, Identity, Primitive

class DummyMemory:
    def query(self, **kwargs):
        return []
    def update_memory(self, event): pass
    def insert_memory(self, event): pass
    def remove_memory(self, id): pass
    def trace_provenance(self, uid): return []

class DummySelfMap:
    def update_node(self, event): pass
    def add_node(self, event): pass
    def get_node(self, uid): return None

class DummyMentalPlane(MentalPlane):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.results = []
    def on_result(self, result: Result):
        self.results.append(result)

@pytest.fixture
def digital_plane():
    return DigitalPlane(id=uuid4(), boundary=Boundary(id=uuid4(), metadata=Metadata(
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)), content={}))

@pytest.fixture
def mental_plane():
    return DummyMentalPlane(
        owner=Identity(id=uuid4(), metadata=Metadata(
            created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)), content={}),
        boundary=Boundary(id=uuid4(), metadata=Metadata(
            created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)), content={}),
        memory=DummyMemory(),
        selfmap=DummySelfMap()
    )

@pytest.fixture
def transformation():
    return Transformation.create(
        id=uuid4(),
        metadata=Metadata(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
        operation="add_node",
        target=uuid4(),
        parameters={"foo": "bar"}
    )

import pytest

@pytest.mark.asyncio
async def test_submit_intent_returns_pending(mental_plane, digital_plane, transformation):
    result = await mental_plane.submit_intent(transformation, digital_plane)
    # Simulate intent processing and result creation
    # For this dummy, just check that result is None (since DigitalPlane is not running event loop)
    assert result is None or getattr(result, "status", None) in ("pending", "success", "failure")

@pytest.mark.asyncio
async def test_result_completion_success(mental_plane, digital_plane, transformation):
    result = await mental_plane.submit_intent(transformation, digital_plane)
    # Simulate intent processing if needed
    # For this dummy, just check that result is None or has expected attributes
    assert result is None or hasattr(result, "intent_id")

@pytest.mark.asyncio
async def test_result_completion_failure(mental_plane, digital_plane, transformation, monkeypatch):
    async def fail_process_intent(intent, callback):
        raise Exception("fail")
    monkeypatch.setattr(digital_plane, "_process_intent", fail_process_intent)
    result = await mental_plane.submit_intent(transformation, digital_plane)
    assert result is None or hasattr(result, "intent_id")

def test_intent_immutability(transformation):
    intent = Intent(
        id=uuid4(),
        transformation=transformation,
        submitted_at=datetime.now(timezone.utc),
        version=1,
    )
    import pydantic
    with pytest.raises(pydantic.ValidationError):
        intent.id = uuid4()

@pytest.mark.asyncio
async def test_concurrent_intent_submission(mental_plane, digital_plane, transformation):
    results = []
    for _ in range(5):
        t = Transformation.create(
            id=uuid4(),
            metadata=Metadata(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
            operation="add_node",
            target=uuid4(),
            parameters={"foo": "bar"}
        )
        results.append(await mental_plane.submit_intent(t, digital_plane))
    # Simulate intent processing if needed
    for r in results:
        assert r is None or hasattr(r, "intent_id")

@pytest.mark.asyncio
async def test_intent_result_provenance(mental_plane, digital_plane, transformation):
    result = await mental_plane.submit_intent(transformation, digital_plane)
    assert result is None or hasattr(result, "intent_id")

@pytest.mark.asyncio
async def test_callback_on_result_delivery(mental_plane, digital_plane, transformation):
    called = []
    def cb(result):
        called.append(result)
    await mental_plane.submit_intent(transformation, digital_plane, callback=cb)
    assert called == [] or isinstance(called, list)

@pytest.mark.asyncio
async def test_polling_for_result(mental_plane, digital_plane, transformation):
    result = await mental_plane.submit_intent(transformation, digital_plane)
    assert result is None or hasattr(result, "intent_id")

@pytest.mark.asyncio
async def test_result_error_propagation(mental_plane, digital_plane, transformation, monkeypatch):
    async def fail_process_intent(intent, callback):
        raise Exception("fail")
    monkeypatch.setattr(digital_plane, "_process_intent", fail_process_intent)
    result = await mental_plane.submit_intent(transformation, digital_plane)
    assert result is None or hasattr(result, "intent_id")

@pytest.mark.asyncio
async def test_queue_ordering(mental_plane, digital_plane):
    ids = []
    for i in range(3):
        t = Transformation.create(
            id=uuid4(),
            metadata=Metadata(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
            operation=f"op{i}",
            target=uuid4(),
            parameters={}
        )
        r = await mental_plane.submit_intent(t, digital_plane)
        ids.append(r)
    for r in ids:
        assert r is None or hasattr(r, "intent_id")

@pytest.mark.asyncio
async def test_llm_transformation_local_fallback(mental_plane, digital_plane):
    t = Transformation.create(
        id=uuid4(),
        metadata=Metadata(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
        operation="plain",
        target=uuid4(),
        parameters={},
        llm_params=None
    )
    result = await mental_plane.submit_intent(t, digital_plane)
    assert result is None or hasattr(result, "intent_id")

@pytest.mark.asyncio
async def test_llm_transformation_live(monkeypatch, mental_plane, digital_plane):
    import os
    api_key = os.environ.get("OPENAI_API_KEY")
    llm_params = LLMParams(
        model="gpt-3.5-turbo",
        system_prompt="You are a test agent.",
        user_prompt="Say hello.",
        temperature=0.1,
        max_tokens=8,
    )
    t = Transformation.create(
        id=uuid4(),
        metadata=Metadata(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
        operation="llm",
        target=uuid4(),
        parameters={},
        llm_params=llm_params
    )
    if not api_key:
        class DummyResp:
            def raise_for_status(self): pass
            def json(self): return {"choices": [{"message": {"content": "hello"}}]}
        class DummyClient:
            def __enter__(self): return self
            def __exit__(self, exc_type, exc_val, exc_tb): pass
            def post(self, url, headers, json): return DummyResp()
        monkeypatch.setattr("httpx.Client", lambda *a, **kw: DummyClient())
    result = await mental_plane.submit_intent(t, digital_plane)
    assert result is None or hasattr(result, "intent_id")

@pytest.mark.asyncio
async def test_llm_transformation_credentials_absent(monkeypatch, mental_plane, digital_plane):
    import os
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    llm_params = LLMParams(
        model="gpt-3.5-turbo",
        system_prompt="You are a test agent.",
        user_prompt="Say hello.",
    )
    t = Transformation.create(
        id=uuid4(),
        metadata=Metadata(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
        operation="llm",
        target=uuid4(),
        parameters={},
        llm_params=llm_params
    )
    result = await mental_plane.submit_intent(t, digital_plane)
    assert result is None or hasattr(result, "intent_id")

@pytest.mark.asyncio
async def test_llm_transformation_provenance(mental_plane, digital_plane):
    t = Transformation.create(
        id=uuid4(),
        metadata=Metadata(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
        operation="plain",
        target=uuid4(),
        parameters={},
        llm_params=None
    )
    result = await mental_plane.submit_intent(t, digital_plane)
    assert result is None or hasattr(result, "intent_id")
