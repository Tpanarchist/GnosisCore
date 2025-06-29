"""
SelfMap: Thread-Safe, Graph-Structured Self-Representation for Digital Intelligence

Maintains a graph of all entities (Primitive), relationships (Connection), and attributes
(State, Value, Label, etc.) composing the self’s current and historical state.
Supports efficient lookup, update, relationship querying, and chronological traversal.
"""

from threading import Lock
from typing import Dict, Set, Iterator, Optional, List, Callable
from uuid import UUID
from gnosiscore.primitives.models import Primitive, Connection, State, Value, Label, Memory

class SelfMap:
    """
    Thread-safe, graph-structured self-representation.

    Nodes:    All Primitive entities (including self-identity, memories, attributes).
    Edges:    Connections (typed edges, can be directed or undirected).
    State:    Track current and historical attributes (State, Value, Label, etc).
    """

    def __init__(self):
        """
        Initialize an empty, thread-safe, graph-structured self map.
        """
        self._nodes: Dict[UUID, Primitive] = {}
        self._edges: Dict[UUID, Set[UUID]] = {}   # adjacency list
        self._connections: Dict[UUID, Connection] = {}  # edge UUID -> Connection
        self._lock = Lock()
        # Optionally: maintain change history/log for audit

    def add_node(self, primitive: Primitive) -> None:
        """
        Add a new node (Primitive) to the self map.

        Raises:
            ValueError if the UUID already exists.
        """
        with self._lock:
            if primitive.id in self._nodes:
                raise ValueError(f"Node {primitive.id} already exists.")
            self._nodes[primitive.id] = primitive
            self._edges.setdefault(primitive.id, set())

    def update_node(self, primitive: Primitive) -> None:
        """
        Update an existing node.

        Raises:
            KeyError if not present.
        """
        with self._lock:
            if primitive.id not in self._nodes:
                raise KeyError(f"Node {primitive.id} not found.")
            self._nodes[primitive.id] = primitive

    def get_node(self, uid: UUID) -> Primitive:
        """
        Retrieve a node by UUID.

        Raises:
            KeyError if not found.
        """
        with self._lock:
            return self._nodes[uid]

    def remove_node(self, uid: UUID) -> None:
        """
        Remove a node and all its edges.

        Raises:
            KeyError if not present.
        """
        with self._lock:
            if uid not in self._nodes:
                raise KeyError(f"Node {uid} not found.")
            del self._nodes[uid]
            # Remove edges from adjacency
            for adj in self._edges.values():
                adj.discard(uid)
            if uid in self._edges:
                del self._edges[uid]
            # Remove connections where this node is involved
            to_delete = [cid for cid, conn in self._connections.items() if conn.content.get("source") == uid or conn.content.get("target") == uid]
            for cid in to_delete:
                del self._connections[cid]

    def add_connection(self, conn: Connection) -> None:
        """
        Add a Connection (edge) between nodes.

        Raises:
            ValueError if already present or source/target not present.
        """
        with self._lock:
            source = conn.content.get("source")
            target = conn.content.get("target")
            if conn.id in self._connections:
                raise ValueError(f"Connection {conn.id} already exists.")
            if source not in self._nodes or target not in self._nodes:
                raise ValueError("Source or target node does not exist.")
            self._connections[conn.id] = conn
            self._edges[source].add(target)
            # Optionally, for undirected edges:
            # self._edges[target].add(source)

    def remove_connection(self, conn_id: UUID) -> None:
        """
        Remove a Connection (edge) by its UUID.

        Raises:
            KeyError if not found.
        """
        with self._lock:
            if conn_id not in self._connections:
                raise KeyError(f"Connection {conn_id} not found.")
            conn = self._connections[conn_id]
            source = conn.content.get("source")
            target = conn.content.get("target")
            self._edges[source].discard(target)
            # Optionally: self._edges[target].discard(source)
            del self._connections[conn_id]

    def neighbors(self, uid: UUID) -> Set[UUID]:
        """
        Return UUIDs of all directly connected neighbors of a node.
        """
        with self._lock:
            return set(self._edges.get(uid, set()))

    def traverse(self, start: UUID, depth: int = 1, filter_fn: Optional[Callable[[Primitive], bool]] = None) -> Iterator[Primitive]:
        """
        Traverse the graph starting from 'start', up to 'depth' hops.
        Optionally filter nodes by a predicate.
        """
        with self._lock:
            visited = set()
            stack = [(start, 0)]
            while stack:
                uid, d = stack.pop()
                if uid in visited or d > depth:
                    continue
                node = self._nodes[uid]
                if filter_fn is None or filter_fn(node):
                    yield node
                visited.add(uid)
                for neighbor in self._edges.get(uid, set()):
                    if neighbor not in visited:
                        stack.append((neighbor, d + 1))

    def all_nodes(self) -> List[Primitive]:
        """Return all nodes in the self map."""
        with self._lock:
            return list(self._nodes.values())

    def all_connections(self) -> List[Connection]:
        """Return all connections (edges) in the self map."""
        with self._lock:
            return list(self._connections.values())
