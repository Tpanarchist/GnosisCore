import pytest
from uuid import uuid4
from datetime import datetime, timezone
from gnosiscore.primitives.models import Metadata, Attention, Qualia

def make_metadata():
    now = datetime.now(timezone.utc)
    return Metadata(created_at=now, updated_at=now, provenance=[], confidence=0.95)

def test_attention_construction():
    attn = Attention(
        id=uuid4(),
        metadata=make_metadata(),
        subject=uuid4(),
        object=uuid4(),
        intensity=0.7,
        duration=5.0,
        content={"reason": "test"}
    )
    assert attn.intensity == 0.7
    assert attn.duration == 5.0
    assert "reason" in attn.content

def test_qualia_construction():
    qual = Qualia(
        id=uuid4(),
        metadata=make_metadata(),
        valence=0.9,
        intensity=0.8,
        modality="emotional",
        about=uuid4(),
        content={"emotion": "joy"}
    )
    assert qual.valence == 0.9
    assert qual.intensity == 0.8
    assert qual.modality == "emotional"
    assert qual.content["emotion"] == "joy"

def test_attention_type_validation():
    with pytest.raises(ValueError):
        Attention(
            id=uuid4(),
            metadata=make_metadata(),
            subject=uuid4(),
            object=uuid4(),
            intensity=1.5,  # Invalid: >1.0
            duration=None
        )

def test_qualia_valence_range():
    with pytest.raises(ValueError):
        Qualia(
            id=uuid4(),
            metadata=make_metadata(),
            valence=1.5,  # Invalid: >1.0
            intensity=0.9,
            modality="visual",
            about=uuid4()
        )

def test_attention_json_roundtrip():
    attn = Attention(
        id=uuid4(),
        metadata=make_metadata(),
        subject=uuid4(),
        object=uuid4(),
        intensity=0.5,
        duration=2.0,
        content={"reason": "json"}
    )
    data = attn.model_dump_json()
    attn2 = Attention.model_validate_json(data)
    assert attn2 == attn

def test_qualia_json_roundtrip():
    qual = Qualia(
        id=uuid4(),
        metadata=make_metadata(),
        valence=-0.5,
        intensity=0.4,
        modality="cognitive",
        about=uuid4(),
        content={"context": "test"}
    )
    data = qual.model_dump_json()
    qual2 = Qualia.model_validate_json(data)
    assert qual2 == qual
