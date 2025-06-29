import pytest
import threading
from datetime import datetime, timedelta, timezone
from uuid import uuid4, UUID
from typing import List
from gnosiscore.memory.subsystem import MemorySubsystem
from gnosiscore.primitives.models import Primitive, Memory, Metadata

def make_memory(ts: datetime, provenance: List[UUID] = None, confidence: float = 1.0) -> Memory:
    """Helper to make a Memory primitive with a given timestamp, provenance, and confidence."""
    return Memory(
        id=uuid4(),
        metadata=Metadata(
            created_at=ts,
            updated_at=ts,
            provenance=provenance or [],
            confidence=confidence,
        ),
        content={"note": f"memory@{ts.isoformat()}"}
    )

@pytest.fixture
def empty_subsystem():
    return MemorySubsystem()

@pytest.fixture
def three_memories():
    now = datetime.now(timezone.utc)
    earlier = now - timedelta(hours=1)
    later = now + timedelta(hours=1)
    m1 = make_memory(earlier)
    m2 = make_memory(now)
    m3 = make_memory(later)
    return m1, m2, m3

def test_insert_and_iter_chronological(empty_subsystem, three_memories):
    """Inserts out-of-order, iterates in chronological order."""
    ms = empty_subsystem
    m1, m2, m3 = three_memories
    # Insert in mixed order
    ms.insert_memory(m2)
    ms.insert_memory(m3)
    ms.insert_memory(m1)
    out = list(ms.iter_chronological())
    assert [x.id for x in out] == [m1.id, m2.id, m3.id]
    # Check ordering after repeated insertion
    ms.remove_memory(m2.id)
    ms.insert_memory(m2)
    out2 = list(ms.iter_chronological())
    assert [x.id for x in out2] == [m1.id, m2.id, m3.id]

def test_insert_duplicate_raises(empty_subsystem, three_memories):
    ms = empty_subsystem
    m1, m2, _ = three_memories
    ms.insert_memory(m1)
    with pytest.raises(ValueError):
        ms.insert_memory(m1)
    # Insert with same id, different object
    m1b = make_memory(m1.metadata.created_at)
    object.__setattr__(m1b, "id", m1.id)  # force same UUID
    with pytest.raises(ValueError):
        ms.insert_memory(m1b)

def test_update_moves_if_created_at_changes(empty_subsystem, three_memories):
    ms = empty_subsystem
    m1, m2, m3 = three_memories
    ms.insert_memory(m1)
    ms.insert_memory(m2)
    ms.insert_memory(m3)
    # Move m2 to be the latest
    new_time = m3.metadata.created_at + timedelta(seconds=1)
    m2_new = m2.model_copy(update={"metadata": m2.metadata.model_copy(update={"created_at": new_time})})
    ms.update_memory(m2_new)
    out = list(ms.iter_chronological())
    # m2 should now be last
    assert [x.id for x in out] == [m1.id, m3.id, m2.id]
    # Move back to middle
    m2_orig = m2.model_copy(update={"metadata": m2.metadata.model_copy(update={"created_at": m2.metadata.created_at})})
    ms.update_memory(m2_orig)
    out2 = list(ms.iter_chronological())
    assert [x.id for x in out2] == [m1.id, m2.id, m3.id]

def test_get_and_remove(empty_subsystem, three_memories):
    ms = empty_subsystem
    m1, m2, m3 = three_memories
    ms.insert_memory(m1)
    ms.insert_memory(m2)
    ms.insert_memory(m3)
    # Get works
    got = ms.get_memory(m2.id)
    assert got.id == m2.id
    # Remove works
    ms.remove_memory(m2.id)
    with pytest.raises(KeyError):
        ms.get_memory(m2.id)
    # Removing again fails
    with pytest.raises(KeyError):
        ms.remove_memory(m2.id)

def test_query_filters(empty_subsystem, three_memories):
    ms = empty_subsystem
    m1, m2, m3 = three_memories
    ms.insert_memory(m1)
    ms.insert_memory(m2)
    ms.insert_memory(m3)
    # Insert a different type for testing
    now = datetime.now(timezone.utc)
    fake = Primitive(
        id=uuid4(),
        metadata=Metadata(
            created_at=now,
            updated_at=now,
            provenance=[],
            confidence=0.8
        ),
        content={}
    )
    ms.insert_memory(fake)
    # by type
    res = ms.query(type="Memory")
    assert all(x.__class__.__name__ == "Memory" for x in res)
    # by time
    after = m2.metadata.created_at
    res2 = ms.query(after=after)
    assert all(x.metadata.created_at >= after for x in res2)
    before = m2.metadata.created_at
    res3 = ms.query(before=before)
    assert all(x.metadata.created_at < before for x in res3)
    # by confidence
    res4 = ms.query(min_confidence=0.9)
    assert all(x.metadata.confidence >= 0.9 for x in res4)
    # custom
    res5 = ms.query(custom=lambda m: "note" in m.content)
    assert all("note" in x.content for x in res5)

def test_trace_provenance_chain(empty_subsystem):
    ms = empty_subsystem
    # Create a chain: m1 -> m2 -> m3
    t0 = datetime.now(timezone.utc)
    m1 = make_memory(t0)
    m2 = make_memory(t0 + timedelta(seconds=10), provenance=[m1.id])
    m3 = make_memory(t0 + timedelta(seconds=20), provenance=[m2.id])
    ms.insert_memory(m1)
    ms.insert_memory(m2)
    ms.insert_memory(m3)
    chain = ms.trace_provenance(m3.id)
    assert [m.id for m in chain] == [m1.id, m2.id, m3.id]
    # Missing UUIDs are skipped
    m4 = make_memory(t0 + timedelta(seconds=30), provenance=[uuid4()])
    ms.insert_memory(m4)
    chain2 = ms.trace_provenance(m4.id)
    assert chain2[-1].id == m4.id

def test_trace_provenance_cycle(empty_subsystem):
    ms = empty_subsystem
    t0 = datetime.now(timezone.utc)
    m1 = make_memory(t0)
    m2 = make_memory(t0 + timedelta(seconds=10), provenance=[m1.id])
    # introduce a cycle
    object.__setattr__(m1, "metadata", m1.metadata.model_copy(update={"provenance": [m2.id]}))
    ms.insert_memory(m1)
    ms.insert_memory(m2)
    # Should not infinite loop
    chain = ms.trace_provenance(m2.id)
    assert m1.id in [m.id for m in chain]
    assert m2.id in [m.id for m in chain]
    assert len(chain) == 2

def test_serialization_roundtrip(empty_subsystem, three_memories):
    ms = empty_subsystem
    m1, m2, m3 = three_memories
    ms.insert_memory(m1)
    ms.insert_memory(m2)
    ms.insert_memory(m3)
    data = ms.to_json()
    ms2 = MemorySubsystem()
    ms2.from_json(data)
    orig = [m.id for m in ms.iter_chronological()]
    loaded = [m.id for m in ms2.iter_chronological()]
    assert orig == loaded
    # And contents are equal
    for a, b in zip(ms.iter_chronological(), ms2.iter_chronological()):
        assert a.metadata.created_at == b.metadata.created_at
        assert a.content == b.content

def test_thread_safety_of_insert_and_update():
    ms = MemorySubsystem()
    now = datetime.now(timezone.utc)
    mems = [make_memory(now + timedelta(seconds=i)) for i in range(100)]
    # Insert in parallel
    def insert(m):
        ms.insert_memory(m)
    threads = [threading.Thread(target=insert, args=(m,)) for m in mems]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    # Check all present and ordered
    out = list(ms.iter_chronological())
    assert len(out) == 100
    ts = [m.metadata.created_at for m in out]
    assert ts == sorted(ts)
