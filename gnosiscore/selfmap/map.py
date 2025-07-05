"""
SelfMap: Thread-Safe, Graph-Structured Self-Representation for Digital Intelligence

Maintains a graph of all entities (Primitive), relationships (Connection), and attributes
(State, Value, Label, etc.) composing the self’s current and historical state.
Supports efficient lookup, update, relationship querying, and chronological traversal.
"""

from threading import Lock
from typing import Dict, Set, Iterator, Optional, List, Callable, Any
from uuid import UUID
import copy
from gnosiscore.primitives.models import Primitive, Connection
from typing import Any, Dict, Optional, List
from uuid import uuid4

class SelfObserverModule:
    """
    Observes and updates recursive self-model representations within the SelfMap.
    Each observation creates or updates a meta-node representing the current state of self-modeling.
    Pluggable and composable; supports meta-cognition and contradiction detection.
    """

    def __init__(self, selfmap: "SelfMap"):
        self.selfmap = selfmap

    def observe(self):
        # Stub: scan the mental plane/selfmap and update its own model
        from datetime import datetime
        import logging
        logging.info(f"[SelfObserverModule] Observing selfmap at {datetime.now().isoformat()}")

    def reflect(self):
        # Stub: generate a meta-representation or “self-model node”
        import logging
        logging.info("[SelfObserverModule] Reflecting (stub).")

    def detect_contradiction(self):
        # Stub: scan for inconsistencies or salient meta-patterns
        import logging
        logging.info("[SelfObserverModule] Detecting contradictions (stub).")

    def answer_introspection(self, query):
        # Stub: return meta-cognitive state or generate qualia of “noticing”
        import logging
        logging.info(f"[SelfObserverModule] Answering introspection query: {query}")
        return f"Stub answer to: {query}"

    def observe_self_modeling(self, depth: int = 2, subject_id=None) -> Optional[Primitive]:
        """
        Observe the self-map's own self-modeling nodes up to a given recursion depth,
        and create/update a meta-self node representing this observation.
        """
        # Find all self-model nodes (type == "self-model")
        self_model_nodes = self.selfmap.get_nodes_by_type("self-model")
        meta_content = {
            "observed_self_models": [n.id for n in self_model_nodes],
            "recursion_depth": depth,
        }
        # Create or update a meta-self node
        from datetime import datetime, timezone
        from gnosiscore.primitives.models import Metadata
        now = datetime.now(timezone.utc)
        provenance_chain = []
        if subject_id is not None:
            provenance_chain.append(subject_id)
        provenance_chain.extend([n.id for n in self_model_nodes])
        meta_node = Primitive(
            id=uuid4(),
            type="meta-self-model",
            content=meta_content,
            metadata=Metadata(
                created_at=now,
                updated_at=now,
                provenance=provenance_chain,
                confidence=1.0,
            )
        )
        self.selfmap.add_node(meta_node)
        return meta_node

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
        self._history: List[Dict[str, Any]] = []  # version history: list of dict snapshots
        self._version_ids: List[str] = []  # version UUIDs or timestamps
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
            self._save_version()

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
            self._save_version()

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
            self._save_version()

    def add_connection(self, conn: Connection) -> None:
        """
        Add a Connection (edge) between nodes.

        Raises:
            ValueError if already present or source/target not present.
        """
        with self._lock:
            source = conn.content.get("source")
            target = conn.content.get("target")
            if not isinstance(source, UUID) or not isinstance(target, UUID):
                raise ValueError("Source and target must be UUIDs.")
            if conn.id in self._connections:
                raise ValueError(f"Connection {conn.id} already exists.")
            if source not in self._nodes or target not in self._nodes:
                raise ValueError("Source or target node does not exist.")
            self._connections[conn.id] = conn
            self._edges[source].add(target)
            # Optionally, for undirected edges:
            # self._edges[target].add(source)
            self._save_version()

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
            if isinstance(source, UUID) and isinstance(target, UUID):
                self._edges[source].discard(target)
                # Optionally: self._edges[target].discard(source)
            del self._connections[conn_id]
            self._save_version()

    def neighbors(self, uid: UUID) -> Set[UUID]:
        """
        Return UUIDs of all directly connected neighbors of a node.
        """
        with self._lock:
            return set(self._edges.get(uid, set()))

    def get_nodes_by_type(self, type_name: str) -> List[Primitive]:
        """Return all nodes of a given Primitive type."""
        with self._lock:
            return [n for n in self._nodes.values() if getattr(n, "type", None) == type_name]

    def get_nodes_by_attribute(self, attr: str, value: Any) -> List[Primitive]:
        """Return all nodes where content[attr] == value."""
        with self._lock:
            return [n for n in self._nodes.values() if n.content.get(attr) == value]

    def provenance_walk(self, uid: UUID) -> List[Primitive]:
        """Return the provenance chain for a node (following metadata.provenance UUIDs)."""
        with self._lock:
            chain = []
            current = self._nodes.get(uid)
            while current:
                chain.append(current)
                prov = getattr(current.metadata, "provenance", [])
                if prov and prov[0] in self._nodes:
                    current = self._nodes[prov[0]]
                else:
                    break
            return chain

    def _save_version(self):
        """Save a deepcopy snapshot of the current state for versioning."""
        snapshot: Dict[str, Any] = {
            "nodes": copy.deepcopy(self._nodes),
            "edges": copy.deepcopy(self._edges),
            "connections": copy.deepcopy(self._connections),
        }
        self._history.append(snapshot)
        self._version_ids.append(str(len(self._history) - 1))

    def get_version(self, version_id: str) -> Dict[str, Any]:
        """Retrieve a snapshot by version id (index as str)."""
        idx = int(version_id)
        return self._history[idx] if 0 <= idx < len(self._history) else {}

    def list_versions(self) -> List[str]:
        """List all version ids."""
        return list(self._version_ids)

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

    # --- Recursive Self-Modeling Interface ---

    def create_recursive_self_model(self, levels: int = 2) -> List[Primitive]:
        """
        Create a chain of self-model nodes, each referencing the previous as its model.
        """
        with self._lock:
            prev_id = None
            nodes = []
            for level in range(levels):
                content = {
                    "level": level,
                    "models": [prev_id] if prev_id else [],
                }
                node = Primitive(
                    id=uuid4(),
                    type="self-model",
                    content=content,
                    metadata={}
                )
                self._nodes[node.id] = node
                self._edges.setdefault(node.id, set())
                if prev_id:
                    # Add connection from this node to previous
                    conn = Connection(
                        id=uuid4(),
                        type="self-model-reference",
                        content={"source": node.id, "target": prev_id},
                        metadata={}
                    )
                    self._connections[conn.id] = conn
                    self._edges[node.id].add(prev_id)
                prev_id = node.id
                nodes.append(node)
            self._save_version()
            return nodes
