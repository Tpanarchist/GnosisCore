import pytest
import threading
from uuid import uuid4, UUID
from gnosiscore.selfmap.map import SelfMap
from gnosiscore.primitives.models import Primitive, Connection, Metadata
from datetime import datetime, timezone

from typing import Optional
def make_primitive(ts: Optional[datetime] = None) -> Primitive:
    ts = ts or datetime.now(timezone.utc)
    return Primitive(id=uuid4(), metadata=Metadata(created_at=ts, updated_at=ts, provenance=[], confidence=1.0), content={})

def make_connection(source: UUID, target: UUID) -> Connection:
    ts = datetime.now(timezone.utc)
    return Connection(id=uuid4(), metadata=Metadata(created_at=ts, updated_at=ts, provenance=[], confidence=1.0), content={"source": source, "target": target})

@pytest.fixture
def empty_selfmap() -> SelfMap:
    return SelfMap()

def test_add_and_get_node(empty_selfmap: SelfMap) -> None:
    sm: SelfMap = empty_selfmap
    node: Primitive = make_primitive()
    sm.add_node(node)
    got: Primitive = sm.get_node(node.id)
    assert got.id == node.id

def test_duplicate_node_raises(empty_selfmap: SelfMap) -> None:
    sm: SelfMap = empty_selfmap
    node: Primitive = make_primitive()
    sm.add_node(node)
    with pytest.raises(ValueError):
        sm.add_node(node)

def test_update_node(empty_selfmap: SelfMap) -> None:
    sm: SelfMap = empty_selfmap
    node: Primitive = make_primitive()
    sm.add_node(node)
    node2: Primitive = node.model_copy(update={"content": {"foo": 42}})
    sm.update_node(node2)
    got: Primitive = sm.get_node(node.id)
    assert got.content["foo"] == 42

def test_remove_node_and_edges(empty_selfmap: SelfMap) -> None:
    sm: SelfMap = empty_selfmap
    n1: Primitive
    n2: Primitive
    n1, n2 = make_primitive(), make_primitive()
    sm.add_node(n1)
    sm.add_node(n2)
    c: Connection = make_connection(n1.id, n2.id)
    sm.add_connection(c)
    sm.remove_node(n1.id)
    assert n2.id in sm._nodes
    assert c.id not in sm._connections

def test_add_and_remove_connection(empty_selfmap: SelfMap) -> None:
    sm: SelfMap = empty_selfmap
    n1: Primitive
    n2: Primitive
    n1, n2 = make_primitive(), make_primitive()
    sm.add_node(n1)
    sm.add_node(n2)
    c: Connection = make_connection(n1.id, n2.id)
    sm.add_connection(c)
    assert c.id in sm._connections
    sm.remove_connection(c.id)
    assert c.id not in sm._connections

def test_neighbors(empty_selfmap: SelfMap) -> None:
    sm: SelfMap = empty_selfmap
    n1: Primitive
    n2: Primitive
    n3: Primitive
    n1, n2, n3 = make_primitive(), make_primitive(), make_primitive()
    sm.add_node(n1)
    sm.add_node(n2)
    sm.add_node(n3)
    sm.add_connection(make_connection(n1.id, n2.id))
    sm.add_connection(make_connection(n1.id, n3.id))
    assert sm.neighbors(n1.id) == {n2.id, n3.id}

def test_traverse(empty_selfmap: SelfMap) -> None:
    sm: SelfMap = empty_selfmap
    nodes: list[Primitive] = [make_primitive() for _ in range(5)]
    for node in nodes:
        sm.add_node(node)
    # 0->1->2, 0->3, 3->4
    sm.add_connection(make_connection(nodes[0].id, nodes[1].id))
    sm.add_connection(make_connection(nodes[1].id, nodes[2].id))
    sm.add_connection(make_connection(nodes[0].id, nodes[3].id))
    sm.add_connection(make_connection(nodes[3].id, nodes[4].id))
    ids = {n.id for n in sm.traverse(nodes[0].id, depth=2)}
    assert nodes[2].id in ids
    assert nodes[4].id in ids

def test_thread_safety() -> None:
    sm: SelfMap = SelfMap()
    nodes: list[Primitive] = [make_primitive() for _ in range(100)]
    def add(n: Primitive) -> None:
        sm.add_node(n)
    threads: list[threading.Thread] = [threading.Thread(target=add, args=(n,)) for n in nodes]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    all_ids = set(n.id for n in nodes)
    got_ids = set(n.id for n in sm.all_nodes())
    assert all_ids == got_ids

def test_remove_nonexistent_node_raises(empty_selfmap: SelfMap) -> None:
    sm: SelfMap = empty_selfmap
    fake_id = uuid4()
    with pytest.raises(KeyError):
        sm.remove_node(fake_id)

def test_update_nonexistent_node_raises(empty_selfmap: SelfMap) -> None:
    sm: SelfMap = empty_selfmap
    node: Primitive = make_primitive()
    with pytest.raises(KeyError):
        sm.update_node(node)

def test_get_nonexistent_node_raises(empty_selfmap: SelfMap) -> None:
    sm: SelfMap = empty_selfmap
    fake_id = uuid4()
    with pytest.raises(KeyError):
        sm.get_node(fake_id)

def test_add_node_after_removal(empty_selfmap: SelfMap) -> None:
    sm: SelfMap = empty_selfmap
    node: Primitive = make_primitive()
    sm.add_node(node)
    sm.remove_node(node.id)
    sm.add_node(node)  # Should succeed

def test_add_connection_missing_node_raises(empty_selfmap: SelfMap) -> None:
    sm: SelfMap = empty_selfmap
    n1: Primitive = make_primitive()
    n2: Primitive = make_primitive()
    sm.add_node(n1)
    # n2 not added
    c: Connection = make_connection(n1.id, n2.id)
    with pytest.raises(ValueError):
        sm.add_connection(c)

def test_add_duplicate_connection_raises(empty_selfmap: SelfMap) -> None:
    sm: SelfMap = empty_selfmap
    n1: Primitive
    n2: Primitive
    n1, n2 = make_primitive(), make_primitive()
    sm.add_node(n1)
    sm.add_node(n2)
    c: Connection = make_connection(n1.id, n2.id)
    sm.add_connection(c)
    with pytest.raises(ValueError):
        sm.add_connection(c)

def test_remove_nonexistent_connection_raises(empty_selfmap: SelfMap) -> None:
    sm: SelfMap = empty_selfmap
    fake_id = uuid4()
    with pytest.raises(KeyError):
        sm.remove_connection(fake_id)

def test_remove_node_cleans_multiple_connections(empty_selfmap: SelfMap) -> None:
    sm: SelfMap = empty_selfmap
    n1: Primitive
    n2: Primitive
    n3: Primitive
    n1, n2, n3 = make_primitive(), make_primitive(), make_primitive()
    sm.add_node(n1)
    sm.add_node(n2)
    sm.add_node(n3)
    c1: Connection = make_connection(n1.id, n2.id)
    c2: Connection = make_connection(n2.id, n1.id)
    c3: Connection = make_connection(n1.id, n3.id)
    sm.add_connection(c1)
    sm.add_connection(c2)
    sm.add_connection(c3)
    sm.remove_node(n1.id)
    assert c1.id not in sm._connections
    assert c2.id not in sm._connections
    assert c3.id not in sm._connections
    assert n1.id not in sm._nodes

def test_self_loop_connection(empty_selfmap: SelfMap) -> None:
    sm: SelfMap = empty_selfmap
    n1: Primitive = make_primitive()
    sm.add_node(n1)
    c: Connection = make_connection(n1.id, n1.id)
    sm.add_connection(c)
    assert n1.id in sm.neighbors(n1.id)
    sm.remove_connection(c.id)
    assert n1.id not in sm.neighbors(n1.id)

def test_all_nodes_and_connections(empty_selfmap: SelfMap) -> None:
    sm: SelfMap = empty_selfmap
    n1: Primitive
    n2: Primitive
    n1, n2 = make_primitive(), make_primitive()
    sm.add_node(n1)
    sm.add_node(n2)
    c: Connection = make_connection(n1.id, n2.id)
    sm.add_connection(c)
    nodes = sm.all_nodes()
    connections = sm.all_connections()
    assert set(n.id for n in nodes) == {n1.id, n2.id}
    assert set(cn.id for cn in connections) == {c.id}

def test_neighbors_empty(empty_selfmap: SelfMap) -> None:
    sm: SelfMap = empty_selfmap
    n1: Primitive = make_primitive()
    sm.add_node(n1)
    assert sm.neighbors(n1.id) == set()

def test_traverse_with_filter(empty_selfmap: SelfMap) -> None:
    sm: SelfMap = empty_selfmap
    nodes: list[Primitive] = [make_primitive() for _ in range(3)]
    for node in nodes:
        sm.add_node(node)
    sm.add_connection(make_connection(nodes[0].id, nodes[1].id))
    sm.add_connection(make_connection(nodes[1].id, nodes[2].id))
    # Only yield nodes with even index (simulate by id ordering)
    ids = {n.id for n in sm.traverse(nodes[0].id, depth=2, filter_fn=lambda n: n.id in [nodes[0].id, nodes[2].id])}
    assert nodes[0].id in ids
    assert nodes[2].id in ids
    assert nodes[1].id not in ids

def test_traverse_empty_graph(empty_selfmap: SelfMap) -> None:
    sm: SelfMap = empty_selfmap
    fake_id = uuid4()
    with pytest.raises(KeyError):
        list(sm.traverse(fake_id, depth=1))
