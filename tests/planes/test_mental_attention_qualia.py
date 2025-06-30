import pytest
import asyncio
from uuid import uuid4
from datetime import datetime, timezone
from gnosiscore.primitives.models import (
    Metadata, Attention, Qualia, Result, Identity, Boundary, Primitive, Transformation
)
from gnosiscore.planes.mental import MentalPlane
from gnosiscore.memory.subsystem import MemorySubsystem
from gnosiscore.selfmap.map import SelfMap

class DummyMemory(MemorySubsystem):
    def __init__(self):
        self._mem = []
    def query(self, **kwargs):
        custom = kwargs.get("custom")
        if custom:
            return [m for m in self._mem if custom(m)]
        return list(self._mem)
    def insert_memory(self, primitive):
        self._mem.append(primitive)
    def update_memory(self, primitive):
        for i, m in enumerate(self._mem):
            if m.id == primitive.id:
                self._mem[i] = primitive
    def remove_memory(self, uid):
        self._mem = [m for m in self._mem if m.id != uid]

class DummySelfMap(SelfMap):
    def __init__(self):
        self._nodes = []
    def all_nodes(self):
        return list(self._nodes)
    def add_node(self, primitive):
        self._nodes.append(primitive)
    def update_node(self, primitive):
        for i, n in enumerate(self._nodes):
            if n.id == primitive.id:
                self._nodes[i] = primitive
    def get_node(self, uid):
        for n in self._nodes:
            if n.id == uid:
                return n
        raise KeyError

@pytest.fixture
def mental_plane():
    owner = Identity(
        id=uuid4(),
        metadata=Metadata(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
        content={}
    )
    boundary = Boundary(
        id=uuid4(),
        metadata=Metadata(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
        content={}
    )
    memory = DummyMemory()
    selfmap = DummySelfMap()
    return MentalPlane(owner, boundary, memory, selfmap)

def make_primitive():
    return Primitive(
        id=uuid4(),
        metadata=Metadata(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
        content={"test": True}
    )

@pytest.mark.asyncio
async def test_attend_filters_memory_and_selfmap(mental_plane):
    # Add primitives to memory and selfmap
    mem_prim = make_primitive()
    selfmap_prim = make_primitive()
    mental_plane.memory.insert_memory(mem_prim)
    mental_plane.selfmap.add_node(selfmap_prim)

    # Attention to memory primitive
    attn_mem = Attention(
        id=uuid4(),
        metadata=Metadata(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
        subject=mem_prim.id,
        object="",
        intensity=1.0,
        duration=1.0,
        content={}
    )
    results = await mental_plane.attend(attn_mem)
    assert mem_prim in results

    # Attention to selfmap primitive
    attn_selfmap = Attention(
        id=uuid4(),
        metadata=Metadata(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
        subject="",
        object=selfmap_prim.id,
        intensity=1.0,
        duration=1.0,
        content={}
    )
    results = await mental_plane.attend(attn_selfmap)
    assert selfmap_prim in results

    # Attention to all selfmap nodes
    attn_all = Attention(
        id=uuid4(),
        metadata=Metadata(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
        subject="",
        object="all",
        intensity=1.0,
        duration=1.0,
        content={}
    )
    results = await mental_plane.attend(attn_all)
    assert selfmap_prim in results

def test_record_qualia_and_emotional_state(mental_plane):
    # Simulate a result
    result = Result(
        id=uuid4(),
        intent_id=uuid4(),
        status="success",
        output={"confidence": 0.8},
        error=None,
        timestamp=datetime.now(timezone.utc)
    )
    about = uuid4()
    mental_plane.record_qualia(result, about=about, modality="testmodality")
    assert len(mental_plane.qualia_log) == 1
    qualia = mental_plane.qualia_log[0]
    assert qualia.valence == 1.0
    assert qualia.intensity == 0.8
    assert qualia.modality == "testmodality"
    assert qualia.about == about

    # Emotional state summary
    state = mental_plane.get_emotional_state()
    assert state["count"] == 1
    assert state["average_valence"] == 1.0
    assert state["average_intensity"] == 0.8
    assert state["by_modality"]["testmodality"] == 1

def test_on_event_attention_and_qualia(mental_plane):
    # Attention event triggers attend (should not raise)
    attn = Attention(
        id=uuid4(),
        metadata=Metadata(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
        subject="",
        object="all",
        intensity=1.0,
        duration=1.0,
        content={}
    )
    # Should not raise
    mental_plane.on_event(attn)

    # Qualia event is logged
    qualia = Qualia(
        id=uuid4(),
        metadata=Metadata(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
        valence=0.5,
        intensity=0.7,
        modality="event",
        about=uuid4(),
        content={}
    )
    mental_plane.on_event(qualia)
    assert qualia in mental_plane.qualia_log

def test_on_result_records_qualia(mental_plane):
    result = Result(
        id=uuid4(),
        intent_id=uuid4(),
        status="failure",
        output=None,
        error="fail",
        timestamp=datetime.now(timezone.utc)
    )
    mental_plane.on_result(result)
    assert len(mental_plane.qualia_log) == 1
    qualia = mental_plane.qualia_log[0]
    assert qualia.valence == -1.0
    assert qualia.modality == "transformation"
