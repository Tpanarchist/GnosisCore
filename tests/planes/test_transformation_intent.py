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

def test_submit_intent_returns_pending(mental_plane, digital_plane, transformation):
    result = mental_plane.submit_intent(transformation, digital_plane)
    assert result.status == "pending"
    assert result.intent_id is not None

def test_result_completion_success(mental_plane, digital_plane, transformation):
    result = mental_plane.submit_intent(transformation, digital_plane)
    digital_plane.process_intents()
    final = digital_plane.poll_result(result.intent_id)
    assert final.status == "success"
    assert "operation" in final.output["transformation"]

def test_result_completion_failure(mental_plane, digital_plane, transformation, monkeypatch):
    # Patch DigitalPlane._execute_intent to raise
    def fail_execute(intent): raise Exception("fail")
    monkeypatch.setattr(digital_plane, "_execute_intent", fail_execute)
    result = mental_plane.submit_intent(transformation, digital_plane)
    digital_plane.process_intents()
    final = digital_plane.poll_result(result.intent_id)
    assert final.status == "failure"
    assert final.error == "fail"

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

def test_concurrent_intent_submission(mental_plane, digital_plane, transformation):
    # Submit multiple intents
    results = []
    for _ in range(5):
        t = Transformation.create(
            id=uuid4(),
            metadata=Metadata(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
            operation="add_node",
            target=uuid4(),
            parameters={"foo": "bar"}
        )
        results.append(mental_plane.submit_intent(t, digital_plane))
    digital_plane.process_intents()
    for r in results:
        final = digital_plane.poll_result(r.intent_id)
        assert final.status == "success"

def test_intent_result_provenance(mental_plane, digital_plane, transformation):
    result = mental_plane.submit_intent(transformation, digital_plane)
    digital_plane.process_intents()
    final = digital_plane.poll_result(result.intent_id)
    assert final.intent_id == result.intent_id
    assert final.timestamp is not None

def test_callback_on_result_delivery(mental_plane, digital_plane, transformation):
    called = []
    def cb(result):
        called.append(result)
    mental_plane.submit_intent(transformation, digital_plane, callback=cb)
    digital_plane.process_intents()
    assert called
    assert called[0].status == "success"

def test_polling_for_result(mental_plane, digital_plane, transformation):
    result = mental_plane.submit_intent(transformation, digital_plane)
    digital_plane.process_intents()
    polled = digital_plane.poll_result(result.intent_id)
    assert polled.status == "success"

def test_result_error_propagation(mental_plane, digital_plane, transformation, monkeypatch):
    def fail_execute(intent): raise Exception("fail")
    monkeypatch.setattr(digital_plane, "_execute_intent", fail_execute)
    result = mental_plane.submit_intent(transformation, digital_plane)
    digital_plane.process_intents()
    final = digital_plane.poll_result(result.intent_id)
    assert final.status == "failure"
    assert final.error == "fail"

def test_queue_ordering(mental_plane, digital_plane):
    ids = []
    for i in range(3):
        t = Transformation.create(
            id=uuid4(),
            metadata=Metadata(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
            operation=f"op{i}",
            target=uuid4(),
            parameters={}
        )
        r = mental_plane.submit_intent(t, digital_plane)
        ids.append((r.intent_id, f"op{i}"))
    digital_plane.process_intents()
    for intent_id, opname in ids:
        final = digital_plane.poll_result(intent_id)
        assert final.output["transformation"]["operation"] == opname

def test_llm_transformation_local_fallback(mental_plane, digital_plane):
    # Should use local logic if llm_params is None
    t = Transformation.create(
        id=uuid4(),
        metadata=Metadata(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
        operation="plain",
        target=uuid4(),
        parameters={},
        llm_params=None
    )
    result = mental_plane.submit_intent(t, digital_plane)
    digital_plane.process_intents()
    final = digital_plane.poll_result(result.intent_id)
    print("\n[Local Transformation Result]", final.status, final.output, final.error)
    assert final.status == "success"
    assert "transformation" in final.output

def test_llm_transformation_live(monkeypatch, mental_plane, digital_plane):
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
        # Monkeypatch httpx.Client.post to simulate OpenAI response
        class DummyResp:
            def raise_for_status(self): pass
            def json(self): return {"choices": [{"message": {"content": "hello"}}]}
        class DummyClient:
            def __enter__(self): return self
            def __exit__(self, exc_type, exc_val, exc_tb): pass
            def post(self, url, headers, json): return DummyResp()
        monkeypatch.setattr("httpx.Client", lambda *a, **kw: DummyClient())
    result = mental_plane.submit_intent(t, digital_plane)
    digital_plane.process_intents()
    final = digital_plane.poll_result(result.intent_id)
    print("\n[LLM Transformation Result]", final.status, final.output, final.error)
    assert final.status == "success"
    assert "llm_response" in final.output

def test_llm_transformation_bad_params(monkeypatch, mental_plane, digital_plane):
    # Should raise ValidationError at LLMParams construction
    import pydantic
    with pytest.raises(pydantic.ValidationError):
        LLMParams(
            model="gpt-3.5-turbo",
            system_prompt="You are a test agent.",
            user_prompt="Say hello.",
            temperature="not-a-float",  # Bad param (will raise)
        )

def test_llm_transformation_credentials_absent(monkeypatch, mental_plane, digital_plane):
    # Unset API key and test error
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
    result = mental_plane.submit_intent(t, digital_plane)
    digital_plane.process_intents()
    final = digital_plane.poll_result(result.intent_id)
    print("\n[LLM Credentials Absent Result]", final.status, final.output, final.error)
    assert final.status == "failure"
    assert "OPENAI_API_KEY" in final.error

def test_llm_transformation_provenance(mental_plane, digital_plane):
    # Provenance should be present in output for both local and LLM
    t = Transformation.create(
        id=uuid4(),
        metadata=Metadata(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
        operation="plain",
        target=uuid4(),
        parameters={},
        llm_params=None
    )
    result = mental_plane.submit_intent(t, digital_plane)
    digital_plane.process_intents()
    final = digital_plane.poll_result(result.intent_id)
    print("\n[Provenance Test Result]", final.status, final.output, final.error)
    assert final.output["transformation"]["operation"] == "plain"
