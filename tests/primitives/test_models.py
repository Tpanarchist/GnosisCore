import pytest
from uuid import uuid4
from datetime import datetime, timezone
from typing import Type, Dict, Any
from gnosiscore.primitives.models import (
    Metadata, Perception, Boundary, Identity, Connection, Value, Pattern,
    Moment, Memory, Transformation, Label, Reference, State, Process, Belief, Primitive
)

PRIMITIVES = [ # type: ignore
    Perception, Boundary, Identity, Connection, Value, Pattern,
    Moment, Memory, Transformation, Label, Reference, State, Process, Belief
]

def valid_content(primitive_cls: Type[Primitive]) -> Dict[str, Any]:
    # Minimal valid content for each primitive type
    if primitive_cls is Perception:
        return {"modality": "visual", "data": {}, "source": uuid4()}
    if primitive_cls is Boundary:
        return {"boundary_type": "test", "parent": None, "scope": [], "policies": {}}
    if primitive_cls is Identity:
        return {"unique_id": uuid4(), "roles": [], "traits": {}}
    if primitive_cls is Connection:
        return {"relation_type": "test", "source": uuid4(), "target": uuid4(), "directed": True}
    if primitive_cls is Value:
        return {"target": uuid4(), "magnitude": 1.0, "context": {}} # type: ignore
    if primitive_cls is Pattern:
        return {"structure": {}, "classification": "test", "instances": []} # type: ignore
    if primitive_cls is Moment:
        return {"start_time": datetime.now(timezone.utc), "end_time": None, "moment_type": "test"} # type: ignore
    if primitive_cls is Memory:
        return {"memory_type": "test", "data": {}, "temporal_context": uuid4(), "value": None, "linked_beliefs": []} # type: ignore
    if primitive_cls is Transformation:
        return {"name": "test", "version": "1.0", "parameters": {}} # type: ignore
    if primitive_cls is Label:
        return {"text": "label", "category": "test", "parent": None} # type: ignore
    if primitive_cls is Reference:
        return {"source": uuid4(), "target": uuid4(), "reference_type": "test"} # type: ignore
    if primitive_cls is State:
        return {"attributes": {}, "validity_period": None} # type: ignore
    if primitive_cls is Process:
        return {"inputs": [], "outputs": [], "state": "init", "owner": uuid4(), "timeline": []} # type: ignore
    if primitive_cls is Belief:
        return {"proposition": "test", "confidence": 1.0, "provenance": [], "belief_type": "test"} # type: ignore
    return {} # type: ignore

def test_successful_instantiation() -> None:
    meta = Metadata(
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        confidence=1.0
    ) # type: ignore
    for primitive_cls in PRIMITIVES: # type: ignore
        obj = primitive_cls(  # type: ignore
            id=uuid4(),
            metadata=meta,
            content=valid_content(primitive_cls)  # type: ignore
        )
        assert obj.id  # type: ignore
        assert obj.metadata  # type: ignore
        assert obj.content  # type: ignore

def test_json_serialization_roundtrip() -> None:
    meta = Metadata(
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        confidence=1.0
    )
    for primitive_cls in PRIMITIVES:
        obj = primitive_cls(
            id=uuid4(),
            metadata=meta,
            content=valid_content(primitive_cls)
        )
        data = obj.json()
        obj2 = primitive_cls.parse_raw(data)  # type: ignore
        assert obj2.id == obj.id  # type: ignore
        assert obj2.metadata == obj.metadata  # type: ignore
        assert obj2.content == obj.content  # type: ignore

@pytest.mark.parametrize("primitive_cls", PRIMITIVES)
def test_missing_required_fields(primitive_cls: Type[Primitive]) -> None:
    meta = Metadata(
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        confidence=1.0
    )
    # Missing id
    with pytest.raises(Exception):
        primitive_cls(  # type: ignore
            metadata=meta,
            content=valid_content(primitive_cls)  # type: ignore
        )
    # Missing metadata
    with pytest.raises(Exception):
        primitive_cls(  # type: ignore
            id=uuid4(),
            content=valid_content(primitive_cls)  # type: ignore
        )
    # Missing content
    with pytest.raises(Exception):
        primitive_cls(  # type: ignore
            id=uuid4(),
            metadata=meta
        )
