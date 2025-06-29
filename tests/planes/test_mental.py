import pytest
import threading
from uuid import uuid4
from gnosiscore.primitives.models import Primitive, Transformation, Identity, Boundary
from gnosiscore.planes.mental import MentalPlane
from gnosiscore.memory.subsystem import MemorySubsystem
from gnosiscore.selfmap.map import SelfMap, Connection

# --- Fixtures ---

from gnosiscore.primitives.models import Metadata
from datetime import datetime

@pytest.fixture
def identity():
    return Identity(
        id=uuid4(),
        metadata=Metadata(
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            provenance=[],
            confidence=1.0,
        ),
        content={}
    )

@pytest.fixture
def boundary():
    return Boundary(
        id=uuid4(),
        metadata=Metadata(
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            provenance=[],
            confidence=1.0,
        ),
        content={}
    )

@pytest.fixture
def memory():
    return MemorySubsystem()

@pytest.fixture
def selfmap():
    return SelfMap()

@pytest.fixture
def primitive():
    return Primitive(
        id=uuid4(),
        metadata=Metadata(
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            provenance=[],
            confidence=1.0,
        ),
        content={}
    )

@pytest.fixture
def transformation():
    return Transformation(
        id=uuid4(),
        metadata=Metadata(
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            provenance=[],
            confidence=1.0,
        ),
        content={}
    )

@pytest.fixture
def mental_plane(identity, boundary, memory, selfmap):
    return MentalPlane(identity, boundary, memory, selfmap)

# --- Test Cases ---

def test_on_event_adds_to_memory_and_selfmap(mental_plane, primitive):
    mental_plane.on_event(primitive)
    # Memory check
    assert primitive.id in [p.id for p in mental_plane.memory.query()]
    # SelfMap check
    assert primitive.id in [n.id for n in mental_plane.selfmap.all_nodes()]

def test_on_event_update_existing(mental_plane, primitive):
    # Insert first
    mental_plane.on_event(primitive)
    # Mutate and re-insert (should update, not insert)
    primitive.metadata.confidence = 0.5
    mental_plane.on_event(primitive)
    # Should still be present and updated
    found = [p for p in mental_plane.memory.query() if p.id == primitive.id][0]
    assert found.metadata.confidence == 0.5

def test_on_event_atomicity(mental_plane, primitive, monkeypatch):
    # Patch selfmap to raise after memory insert
    called = {"memory": False}
    orig_insert = mental_plane.memory.insert_memory
    def insert_memory(p):
        called["memory"] = True
        orig_insert(p)
    monkeypatch.setattr(mental_plane.memory, "insert_memory", insert_memory)
    monkeypatch.setattr(mental_plane.selfmap, "update_node", lambda p: (_ for _ in ()).throw(Exception("fail selfmap")))
    with pytest.raises(Exception):
        mental_plane.on_event(primitive)
    # Should not be present in memory after rollback
    assert primitive.id not in [p.id for p in mental_plane.memory.query()]

def test_on_event_thread_safety(identity, boundary):
    memory = MemorySubsystem()
    selfmap = SelfMap()
    plane = MentalPlane(identity, boundary, memory, selfmap)
    from gnosiscore.primitives.models import Metadata
    from datetime import datetime
    primitives = [
        Primitive(
            id=uuid4(),
            metadata=Metadata(
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                provenance=[],
                confidence=1.0,
            ),
            content={}
        )
        for _ in range(10)
    ]
    threads = [threading.Thread(target=plane.on_event, args=(p,)) for p in primitives]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    # All should be present
    ids = set(p.id for p in primitives)
    memory_ids = set(p.id for p in memory.query())
    selfmap_ids = set(n.id for n in selfmap.all_nodes())
    assert ids == memory_ids == selfmap_ids

def test_query_memory(mental_plane, primitive):
    mental_plane.on_event(primitive)
    results = mental_plane.query_memory()
    assert any(p.id == primitive.id for p in results)

def test_trace_memory_provenance(mental_plane, primitive):
    mental_plane.on_event(primitive)
    provenance = mental_plane.trace_memory_provenance(primitive.id)
    assert provenance[-1].id == primitive.id

def test_get_update_self_node(mental_plane, primitive):
    mental_plane.on_event(primitive)
    node = mental_plane.get_self_node(primitive.id)
    assert node.id == primitive.id
    # Update
    primitive.metadata.confidence = 0.9
    mental_plane.update_self_node(primitive)
    node2 = mental_plane.get_self_node(primitive.id)
    assert node2.metadata.confidence == 0.9

def test_selfmap_isolated(identity, boundary):
    memory1 = MemorySubsystem()
    selfmap1 = SelfMap()
    plane1 = MentalPlane(identity, boundary, memory1, selfmap1)
    memory2 = MemorySubsystem()
    selfmap2 = SelfMap()
    plane2 = MentalPlane(identity, boundary, memory2, selfmap2)
    from gnosiscore.primitives.models import Metadata
    from datetime import datetime
    p = Primitive(
        id=uuid4(),
        metadata=Metadata(
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            provenance=[],
            confidence=1.0,
        ),
        content={}
    )
    plane1.on_event(p)
    # plane2 should not see p in its selfmap
    assert p.id not in [n.id for n in plane2.selfmap.all_nodes()]

def test_memory_isolated(identity, boundary):
    memory1 = MemorySubsystem()
    selfmap1 = SelfMap()
    plane1 = MentalPlane(identity, boundary, memory1, selfmap1)
    memory2 = MemorySubsystem()
    selfmap2 = SelfMap()
    plane2 = MentalPlane(identity, boundary, memory2, selfmap2)
    from gnosiscore.primitives.models import Metadata
    from datetime import datetime
    p = Primitive(
        id=uuid4(),
        metadata=Metadata(
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            provenance=[],
            confidence=1.0,
        ),
        content={}
    )
    plane1.on_event(p)
    # plane2 should not see p in its memory
    assert p.id not in [m.id for m in plane2.memory.query()]

def test_cross_plane_access_forbidden(identity, boundary):
    memory1 = MemorySubsystem()
    selfmap1 = SelfMap()
    plane1 = MentalPlane(identity, boundary, memory1, selfmap1)
    memory2 = MemorySubsystem()
    selfmap2 = SelfMap()
    plane2 = MentalPlane(identity, boundary, memory2, selfmap2)
    # Try to share memory reference (should not mutate other's memory)
    from gnosiscore.primitives.models import Metadata
    from datetime import datetime
    p = Primitive(
        id=uuid4(),
        metadata=Metadata(
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            provenance=[],
            confidence=1.0,
        ),
        content={}
    )
    plane1.on_event(p)
    # plane2 tries to insert p into its memory (should not affect plane1)
    plane2.on_event(p)
    assert p.id in [m.id for m in plane1.memory.query()]
    assert p.id in [m.id for m in plane2.memory.query()]

def test_memory_exception_propagated(mental_plane, primitive, monkeypatch):
    monkeypatch.setattr(mental_plane.memory, "insert_memory", lambda p: (_ for _ in ()).throw(Exception("fail memory")))
    with pytest.raises(Exception):
        mental_plane.on_event(primitive)
    # Should not be present in selfmap
    assert primitive.id not in [n.id for n in mental_plane.selfmap.all_nodes()]

def test_selfmap_exception_propagated(mental_plane, primitive, monkeypatch):
    monkeypatch.setattr(mental_plane.selfmap, "update_node", lambda p: (_ for _ in ()).throw(Exception("fail selfmap")))
    with pytest.raises(Exception):
        mental_plane.on_event(primitive)
    # Should not be present in memory
    assert primitive.id not in [m.id for m in mental_plane.memory.query()]

def test_submit_intent_sends_to_digital_plane(mental_plane, transformation):
    result = mental_plane.submit_intent(transformation)
    # Just check that a Result is returned (actual DigitalPlane integration is out of scope)
    from gnosiscore.primitives.models import Result
    assert isinstance(result, Result)

def test_submit_intent_thread_safe(mental_plane, transformation):
    # Submit multiple intents in parallel
    results = []
    def submit():
        results.append(mental_plane.submit_intent(transformation))
    threads = [threading.Thread(target=submit) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    from gnosiscore.primitives.models import Result
    assert all(isinstance(r, Result) for r in results)

def test_get_update_self_node_keyerror(mental_plane):
    import uuid
    fake_id = uuid.uuid4()
    # get_self_node should raise KeyError
    with pytest.raises(KeyError):
        mental_plane.get_self_node(fake_id)
    # update_self_node should raise KeyError
    from gnosiscore.primitives.models import Primitive, Metadata
    from datetime import datetime
    fake_primitive = Primitive(
        id=fake_id,
        metadata=Metadata(
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            provenance=[],
            confidence=1.0,
        ),
        content={}
    )
    with pytest.raises(KeyError):
        mental_plane.update_self_node(fake_primitive)

def test_query_memory_filters(mental_plane, primitive):
    import time
    from gnosiscore.primitives.models import Primitive, Metadata
    from datetime import datetime, timedelta
    # Insert two primitives with different types, times, confidence
    p1 = Primitive(
        id=uuid4(),
        metadata=Metadata(
            created_at=datetime.utcnow() - timedelta(hours=2),
            updated_at=datetime.utcnow() - timedelta(hours=2),
            provenance=[],
            confidence=0.9,
        ),
        content={}
    )
    p2 = Primitive(
        id=uuid4(),
        metadata=Metadata(
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            provenance=[],
            confidence=0.5,
        ),
        content={}
    )
    mental_plane.on_event(p1)
    mental_plane.on_event(p2)
    # Filter by confidence
    res = mental_plane.query_memory(min_confidence=0.8)
    assert p1.id in [x.id for x in res]
    assert p2.id not in [x.id for x in res]
    # Filter by time
    after = datetime.utcnow() - timedelta(hours=1)
    res2 = mental_plane.query_memory(after=after)
    assert p2.id in [x.id for x in res2]
    assert p1.id not in [x.id for x in res2]
    # Filter by custom predicate
    res3 = mental_plane.query_memory(custom=lambda x: x.metadata.confidence < 0.7)
    assert p2.id in [x.id for x in res3]
    assert p1.id not in [x.id for x in res3]
