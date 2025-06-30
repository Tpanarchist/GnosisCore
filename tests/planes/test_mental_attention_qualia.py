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
        self._mem = {}
    def query(self, **kwargs):
        custom = kwargs.get("custom")
        values = list(self._mem.values())
        if custom:
            return [m for m in values if custom(m)]
        return values
    def insert_memory(self, primitive):
        self._mem[primitive.id] = primitive
    def update_memory(self, primitive):
        self._mem[primitive.id] = primitive
    def remove_memory(self, uid):
        if uid in self._mem:
            del self._mem[uid]
    def get_memory(self, uid):
        if uid in self._mem:
            return self._mem[uid]
        raise KeyError

class DummySelfMap(SelfMap):
    def __init__(self):
        self._nodes = {}
    def all_nodes(self):
        return list(self._nodes.values())
    def add_node(self, primitive):
        self._nodes[primitive.id] = primitive
    def update_node(self, primitive):
        self._nodes[primitive.id] = primitive
    def get_node(self, uid):
        if uid in self._nodes:
            return self._nodes[uid]
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

def make_primitive(
    id=None,
    salience=1.0,
    modality="default",
    updated_at=None,
    extra_content=None,
):
    content = {"salience": salience, "modality": modality}
    if extra_content:
        content.update(extra_content)
    return Primitive(
        id=id or uuid4(),
        metadata=Metadata(
            created_at=datetime.now(timezone.utc),
            updated_at=updated_at or datetime.now(timezone.utc),
        ),
        content=content,
    )

@pytest.mark.asyncio
async def test_adaptive_recall_top_n_salience_recency_qualia(mental_plane):
    # Insert primitives with varying salience and recency
    now = datetime.now(timezone.utc)
    ids = [uuid4() for _ in range(4)]
    prims = [
        make_primitive(id=ids[0], salience=0.2, modality="visual", updated_at=now),
        make_primitive(id=ids[1], salience=0.9, modality="visual", updated_at=now),
        make_primitive(id=ids[2], salience=0.7, modality="audio", updated_at=now),
        make_primitive(id=ids[3], salience=0.8, modality="visual", updated_at=now),
    ]
    for p in prims:
        mental_plane.memory.insert_memory(p)
        mental_plane.selfmap.add_node(p)
    # Add qualia: positive for ids[1], negative for ids[3]
    qpos = Qualia(
        id=uuid4(),
        metadata=Metadata(created_at=now, updated_at=now),
        valence=1.0,
        intensity=1.0,
        modality="visual",
        about=ids[1],
        content={},
    )
    qneg = Qualia(
        id=uuid4(),
        metadata=Metadata(created_at=now, updated_at=now),
        valence=-1.0,
        intensity=1.0,
        modality="visual",
        about=ids[3],
        content={},
    )
    mental_plane.qualia_log.extend([qpos, qneg])
    # Should return top 3 by salience+qualia+recency
    results = await mental_plane.adaptive_recall(top_n=3)
    result_ids = [p.id for p in results]
    assert ids[1] in result_ids  # high salience, positive qualia
    assert len(result_ids) == 3

@pytest.mark.asyncio
async def test_adaptive_recall_modality_and_thresholds(mental_plane):
    now = datetime.now(timezone.utc)
    prims = [
        make_primitive(salience=0.6, modality="visual", updated_at=now),
        make_primitive(salience=0.4, modality="audio", updated_at=now),
        make_primitive(salience=0.8, modality="visual", updated_at=now),
    ]
    for p in prims:
        mental_plane.memory.insert_memory(p)
        mental_plane.selfmap.add_node(p)
    # Modality filter
    results = await mental_plane.adaptive_recall(modality="visual")
    assert all(p.content["modality"] == "visual" for p in results)
    # Min salience
    results = await mental_plane.adaptive_recall(min_salience=0.7)
    assert all(p.content["salience"] >= 0.7 for p in results)
    # Recency filter
    old_time = now.replace(year=now.year - 1)
    old_prim = make_primitive(salience=0.9, modality="visual", updated_at=old_time)
    mental_plane.memory.insert_memory(old_prim)
    mental_plane.selfmap.add_node(old_prim)
    results = await mental_plane.adaptive_recall(since=now)
    assert all(p.metadata.updated_at >= now for p in results)

@pytest.mark.asyncio
async def test_adaptive_recall_attention_bias(mental_plane):
    now = datetime.now(timezone.utc)
    ids = [uuid4() for _ in range(2)]
    prims = [
        make_primitive(id=ids[0], salience=0.5, modality="visual", updated_at=now),
        make_primitive(id=ids[1], salience=0.5, modality="visual", updated_at=now),
    ]
    for p in prims:
        mental_plane.memory.insert_memory(p)
        mental_plane.selfmap.add_node(p)
    attn = Attention(
        id=uuid4(),
        metadata=Metadata(created_at=now, updated_at=now),
        subject="",
        object=ids[1],
        intensity=1.0,
        duration=1.0,
        content={},
    )
    results = await mental_plane.adaptive_recall(top_n=1, attention_bias=attn)
    assert results[0].id == ids[1]

@pytest.mark.asyncio
async def test_adaptive_recall_edge_cases(mental_plane):
    # Empty memory/selfmap
    results = await mental_plane.adaptive_recall()
    assert results == []
    # All below threshold
    now = datetime.now(timezone.utc)
    prim = make_primitive(salience=0.1, modality="visual", updated_at=now)
    mental_plane.memory.insert_memory(prim)
    mental_plane.selfmap.add_node(prim)
    results = await mental_plane.adaptive_recall(min_salience=0.5)
    assert results == []

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

def test_learning_feedback_salience_update_and_recall(mental_plane):
    # Insert separate primitives with the same id into memory and selfmap
    shared_id = uuid4()
    prim_mem = make_primitive(id=shared_id)
    prim_selfmap = make_primitive(id=shared_id)
    mental_plane.memory.insert_memory(prim_mem)
    mental_plane.selfmap.add_node(prim_selfmap)

    # Positive qualia: should increase salience
    result_pos = Result(
        id=uuid4(),
        intent_id=uuid4(),
        status="success",
        output={"confidence": 1.0},
        error=None,
        timestamp=datetime.now(timezone.utc)
    )
    mental_plane.record_qualia(result_pos, about=shared_id, modality="testmodality")
    # Check salience increased from default (1.0)
    mem = mental_plane.memory.query(custom=lambda m: m.id == shared_id)[0]
    node = [n for n in mental_plane.selfmap.all_nodes() if n.id == shared_id][0]
    assert mem.content.get("salience", 1.0) > 1.0
    assert node.content.get("salience", 1.0) > 1.0

    # Negative qualia: should decrease salience
    result_neg = Result(
        id=uuid4(),
        intent_id=uuid4(),
        status="failure",
        output={"confidence": 1.0},
        error="fail",
        timestamp=datetime.now(timezone.utc)
    )
    mental_plane.record_qualia(result_neg, about=shared_id, modality="testmodality")
    mem2 = mental_plane.memory.query(custom=lambda m: m.id == shared_id)[0]
    node2 = [n for n in mental_plane.selfmap.all_nodes() if n.id == shared_id][0]
    assert mem2.content.get("salience", 1.0) < mem.content.get("salience", 1.0)
    assert node2.content.get("salience", 1.0) < node.content.get("salience", 1.0)

    # Salience-weighted recall
    salient_mems = mental_plane.feedback_manager.get_salient_memories(top_n=1)
    salient_nodes = mental_plane.feedback_manager.get_salient_nodes(top_n=1)
    assert salient_mems[0].id == shared_id
    assert salient_nodes[0].id == shared_id

def test_salience_decay_and_floor(mental_plane):
    # Insert primitives with known salience
    prim1 = make_primitive(salience=0.8)
    prim2 = make_primitive(salience=0.2)
    mental_plane.memory.insert_memory(prim1)
    mental_plane.memory.insert_memory(prim2)
    mental_plane.selfmap.add_node(prim1)
    mental_plane.selfmap.add_node(prim2)
    # Decay with floor
    events = mental_plane.decay_salience(decay_rate=0.1, floor=0.15)
    for e in events:
        assert e.after <= e.before
        assert e.after >= 0.15
    # No double decay: call again, values decrease further but not below floor
    events2 = mental_plane.decay_salience(decay_rate=0.1, floor=0.15)
    for e in events2:
        assert e.after <= e.before
        assert e.after >= 0.15
    # Floor test: salience at floor does not drop
    prim3 = make_primitive(salience=0.15)
    mental_plane.memory.insert_memory(prim3)
    mental_plane.selfmap.add_node(prim3)
    events3 = mental_plane.decay_salience(decay_rate=0.1, floor=0.15)
    for e in events3:
        assert e.after >= 0.15
    # Reinforcement: manually increase salience, decay again, stays higher
    prim1.content["salience"] = 0.9
    events4 = mental_plane.decay_salience(decay_rate=0.1, floor=0.15)
    found = [e for e in events4 if e.node_id == prim1.id]
    assert found and found[0].after > 0.15

def test_emotional_drive_summary_and_prioritization(mental_plane):
    # Insert qualia with mixed valence/modalities
    now = datetime.now(timezone.utc)
    q1 = Qualia(
        id=uuid4(),
        metadata=Metadata(created_at=now, updated_at=now),
        valence=1.0,
        intensity=0.9,
        modality="visual",
        about=uuid4(),
        content={},
    )
    q2 = Qualia(
        id=uuid4(),
        metadata=Metadata(created_at=now, updated_at=now),
        valence=-0.5,
        intensity=0.7,
        modality="audio",
        about=uuid4(),
        content={},
    )
    q3 = Qualia(
        id=uuid4(),
        metadata=Metadata(created_at=now, updated_at=now),
        valence=0.8,
        intensity=0.8,
        modality="visual",
        about=uuid4(),
        content={},
    )
    mental_plane.qualia_log.extend([q1, q2, q3])
    summary = mental_plane.get_emotional_drive()
    assert summary.dominant_modality in {"visual", "audio"}
    assert abs(summary.dominant_valence) <= 1.0
    # Prioritize by emotion
    candidates = [
        make_primitive(modality="visual"),
        make_primitive(modality="audio"),
    ]
    prioritized = mental_plane.prioritize_by_emotion(candidates, drive_bias=0.7)
    assert prioritized[0].content["modality"] == summary.dominant_modality
    # Recent qualia limit
    for i in range(15):
        q = Qualia(
            id=uuid4(),
            metadata=Metadata(created_at=now, updated_at=now),
            valence=1.0,
            intensity=1.0,
            modality="visual",
            about=uuid4(),
            content={},
        )
        mental_plane.qualia_log.append(q)
    summary2 = mental_plane.get_emotional_drive()
    assert len(summary2.recent_qualia) <= 10

def test_meta_cognitive_self_reflection_and_goal_replanning(mental_plane):
    # Insert events and qualia for self_reflection
    now = datetime.now(timezone.utc)
    for i in range(10):
        q = Qualia(
            id=uuid4(),
            metadata=Metadata(created_at=now, updated_at=now),
            valence=(-1.0 if i < 5 else 1.0),
            intensity=1.0,
            modality="visual",
            about=uuid4(),
            content={},
        )
        mental_plane.qualia_log.append(q)
    summary = mental_plane.self_reflection()
    assert "top_qualia" in summary
    assert "emotional_shift" in summary
    # Goal replanning: negative trend triggers replanning
    mental_plane.qualia_log.clear()
    for i in range(10):
        q = Qualia(
            id=uuid4(),
            metadata=Metadata(created_at=now, updated_at=now),
            valence=-1.0,
            intensity=1.0,
            modality="visual",
            about=uuid4(),
            content={},
        )
        mental_plane.qualia_log.append(q)
    triggered = mental_plane.goal_replanning(negative_threshold=-0.5)
    assert triggered is True
    # Salience/qualia sync
    flagged = mental_plane.salience_qualia_sync()
    assert set(flagged) == set(q.about for q in mental_plane.qualia_log)

@pytest.mark.asyncio
async def test_full_cycle_simulation(mental_plane):
    # Insert events
    now = datetime.now(timezone.utc)
    prim = make_primitive(salience=0.9, modality="visual", updated_at=now)
    mental_plane.memory.insert_memory(prim)
    mental_plane.selfmap.add_node(prim)
    # Record qualia
    q = Qualia(
        id=uuid4(),
        metadata=Metadata(created_at=now, updated_at=now),
        valence=1.0,
        intensity=1.0,
        modality="visual",
        about=prim.id,
        content={},
    )
    mental_plane.qualia_log.append(q)
    # Adaptive recall
    results = await mental_plane.adaptive_recall(top_n=1)
    assert results and results[0].id == prim.id
    # Salience decay
    events = mental_plane.decay_salience(decay_rate=0.2, floor=0.1)
    for e in events:
        assert e.after >= 0.1
    # Emotional drive
    summary = mental_plane.get_emotional_drive()
    assert summary.dominant_modality == "visual"
    # Meta-cognitive loop
    reflection = mental_plane.self_reflection()
    assert "top_qualia" in reflection
    # Regression: recall after cycles
    results2 = await mental_plane.adaptive_recall(top_n=1)
    assert results2 and results2[0].id == prim.id
