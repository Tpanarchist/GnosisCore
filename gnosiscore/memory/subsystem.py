"""
MemorySubsystem: Thread-safe, Chronologically-Ordered Memory Registry

Implements a registry for Primitive (usually Memory) objects, ordered by metadata.created_at.
All operations are thread-safe. Registry is always ordered by created_at (ascending).
"""

from collections import OrderedDict
from threading import Lock
from typing import Iterator, List, Optional, Callable
from gnosiscore.primitives.models import Primitive
from datetime import datetime
from uuid import UUID
import json

class MemorySubsystem:
    """
    Thread-safe, chronologically-ordered registry for Primitive objects.

    Maintains insertion order by Primitive.metadata.created_at (ascending).
    All operations are protected by an internal lock.
    """

    def __init__(self):
        """
        Initializes an empty, thread-safe, chronologically-ordered memory registry.
        """
        self._registry: "OrderedDict[UUID, Primitive]" = OrderedDict()
        self._lock = Lock()

    def insert_memory(self, primitive: Primitive) -> None:
        """
        Insert a new memory record.

        Args:
            primitive (Primitive): The memory primitive to insert.

        Raises:
            ValueError: If a memory with the same UUID already exists.

        Behavior:
            - Inserts the primitive such that registry order (by created_at) is preserved.
            - If primitive.created_at is equal to another, insert after all previous with same timestamp.
            - Acquires lock for thread safety.
        """
        with self._lock:
            if primitive.id in self._registry:
                raise ValueError("Duplicate UUID: use update_memory() to modify existing record.")
            self._registry[primitive.id] = primitive
            self._reorder_registry()

    def update_memory(self, primitive: Primitive) -> None:
        """
        Update an existing memory record, identified by UUID.

        Args:
            primitive (Primitive): The updated memory primitive.

        Raises:
            KeyError: If the UUID does not exist.

        Behavior:
            - Replace the item, and reposition in registry if created_at is changed, to maintain order.
            - If created_at is not changed, position is unchanged.
            - Acquires lock for thread safety.
        """
        with self._lock:
            if primitive.id not in self._registry:
                raise KeyError(f"UUID {primitive.id} not found.")
            old_created_at = self._registry[primitive.id].metadata.created_at
            self._registry[primitive.id] = primitive
            if primitive.metadata.created_at != old_created_at:
                self._reorder_registry()

    def get_memory(self, uid: UUID) -> Primitive:
        """
        Retrieve a memory record by UUID.

        Args:
            uid (UUID): The UUID of the memory to retrieve.

        Returns:
            Primitive: The memory primitive.

        Raises:
            KeyError: If not found.
        """
        with self._lock:
            if uid not in self._registry:
                raise KeyError(f"UUID {uid} not found.")
            return self._registry[uid]

    def iter_chronological(self, start: Optional[datetime]=None, end: Optional[datetime]=None) -> Iterator[Primitive]:
        """
        Yield memory records in strictly chronological order (ascending by created_at).

        Args:
            start (Optional[datetime]): If provided, only yield records with created_at >= start.
            end (Optional[datetime]): If provided, only yield records with created_at < end.

        Yields:
            Primitive: Memory primitives in order.

        Behavior:
            - Acquires lock for the duration of iteration.
            - Safe to consume as a list or generator.
        """
        with self._lock:
            for primitive in self._registry.values():
                created = primitive.metadata.created_at
                if (start is not None and created < start):
                    continue
                if (end is not None and created >= end):
                    continue
                yield primitive

    def query(
        self,
        *,
        type: Optional[str]=None,
        after: Optional[datetime]=None,
        before: Optional[datetime]=None,
        min_confidence: Optional[float]=None,
        custom: Optional[Callable[[Primitive], bool]]=None
    ) -> List[Primitive]:
        """
        Retrieve memory records filtered by any combination of:
            - type (matches Primitive.type)
            - after (created_at >= this)
            - before (created_at < this)
            - min_confidence (metadata.confidence >= this)
            - custom (a predicate taking a Primitive)

        Returns:
            List[Primitive]: Filtered memory primitives in chronological order.

        Behavior:
            - Acquires lock for thread safety.
        """
        with self._lock:
            result = []
            for primitive in self._registry.values():
                if type is not None:
                    # type is a ClassVar, so check class attribute safely
                    if getattr(primitive.__class__, "type", None) != type:
                        continue
                if after is not None and primitive.metadata.created_at < after:
                    continue
                if before is not None and primitive.metadata.created_at >= before:
                    continue
                if min_confidence is not None and primitive.metadata.confidence < min_confidence:
                    continue
                if custom is not None and not custom(primitive):
                    continue
                result.append(primitive) # type: ignore
            return result # type: ignore

    def trace_provenance(self, uid: UUID, max_depth: Optional[int]=None) -> List[Primitive]:
        """
        Follow the provenance chain (metadata.provenance: List[UUID]) backward from uid.

        Args:
            uid (UUID): The UUID to trace from.
            max_depth (Optional[int]): Maximum steps to traverse (None = unlimited).

        Returns:
            List[Primitive]: List of ancestor Primitives, oldest first, ending with the input uid.

        Behavior:
            - If any provenance UUID is missing, skip it and continue.
            - Cycles are detected (stop if a UUID repeats).
            - Acquires lock for thread safety.
        """
        with self._lock:
            chain: List[Primitive] = []
            seen: set[UUID] = set()
            current_uid = uid
            depth = 0
            while True:
                if current_uid in seen:
                    # Cycle detected
                    break
                try:
                    primitive = self._registry[current_uid]
                except KeyError:
                    break
                chain.insert(0, primitive)
                seen.add(current_uid)
                provenance = primitive.metadata.provenance
                if not provenance:
                    break
                current_uid = provenance[-1]
                depth += 1
                if max_depth is not None and depth >= max_depth:
                    break
            return chain

    def remove_memory(self, uid: UUID) -> None:
        """
        Remove a memory record by UUID.

        Args:
            uid (UUID): The UUID to remove.

        Raises:
            KeyError: If not found.

        Behavior:
            - Acquires lock for thread safety.
        """
        with self._lock:
            if uid not in self._registry:
                raise KeyError(f"UUID {uid} not found.")
            del self._registry[uid]

    def to_json(self) -> str:
        """
        Serialize the registry to JSON (using Pydantic .json()), preserving order.

        Returns:
            str: JSON string representing the registry.
        """
        with self._lock:
            # Use list to preserve order
            data = [primitive.model_dump_json() for primitive in self._registry.values()]
            return json.dumps(data)

    def from_json(self, data: str) -> None:
        """
        Load the registry from JSON, replacing existing data. Order is preserved.

        Args:
            data (str): JSON string as produced by to_json().

        Behavior:
            - Acquires lock for thread safety.
        """
        with self._lock:
            self._registry.clear()
            items = json.loads(data)
            for item_json in items:
                primitive = Primitive.model_validate_json(item_json)
                self._registry[primitive.id] = primitive
            self._reorder_registry()

    def _reorder_registry(self) -> None:
        """
        Internal: Reorder the registry by metadata.created_at (ascending).
        If created_at is equal, preserve insertion order among equals.
        """
        # Sort by (created_at, insertion order)
        sorted_items = sorted(
            self._registry.items(),
            key=lambda kv: (kv[1].metadata.created_at, )
        )
        self._registry = OrderedDict(sorted_items)
