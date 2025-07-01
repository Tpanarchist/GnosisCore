from typing import Dict, Set, Callable, Awaitable
from uuid import UUID
from threading import Lock
import asyncio

from gnosiscore.primitives.models import Boundary, Pattern

# Forward reference for MentalPlane (to avoid circular import)
from gnosiscore.primitives.models import Primitive
class MentalPlane:
    def on_event(self, event: Primitive) -> None:
        pass

class MetaphysicalPlane:
    """
    MetaphysicalPlane is the shared, atemporal substrate of archetypes and universal patterns.
    Broadcasts symbolic templates to MentalPlanes but never accepts writes from them.
    """
    def __init__(self, version: str, boundary: Boundary):
        self.version = version
        self.boundary = boundary
        self._patterns: Dict[UUID, Pattern] = {}
        self._subscribers: Set[MentalPlane] = set()
        self._lock = Lock()

    def publish_archetype(self, archetype: Pattern) -> None:
        with self._lock:
            if archetype.id in self._patterns:
                # Prevent in-place modification: only allow new versions
                raise ValueError("Archetype with this UUID already exists. Use a new UUID for new versions.")
            self._patterns[archetype.id] = archetype
            for subscriber in self._subscribers:
                subscriber.on_event(archetype)

    def subscribe(self, mental_plane: 'MentalPlane') -> None:
        with self._lock:
            self._subscribers.add(mental_plane)

    def unsubscribe(self, mental_plane: 'MentalPlane') -> None:
        with self._lock:
            self._subscribers.discard(mental_plane)

    def get_archetype(self, archetype_id: UUID) -> Pattern:
        with self._lock:
            return self._patterns[archetype_id]

    def register_archetype(self, archetype: Pattern) -> None:
        """
        Register a new archetype guiding self-map structure or introspection.
        Alias for publish_archetype.
        """
        self.publish_archetype(archetype)

    def lookup_archetype(self, type: str = None, tags: list = None) -> list:
        """
        Query available archetypes for guiding node instantiation or pattern matching.
        """
        with self._lock:
            patterns = list(self._patterns.values())
        results = []
        for pattern in patterns:
            if type is not None:
                pattern_type = pattern.content.get("type") or getattr(pattern, "type", None)
                if pattern_type != type:
                    continue
            if tags is not None:
                pattern_tags = pattern.content.get("tags", [])
                if not set(tags).issubset(set(pattern_tags)):
                    continue
            results.append(pattern)
        return results


class AsyncMetaphysicalPlane:
    """
    AsyncMetaphysicalPlane is an async/thread-safe, atemporal substrate for archetype (Pattern) events.
    Supports async subscriptions and at-least-once delivery to all registered subscribers.
    """
    def __init__(self):
        # Subscribers: callback -> filter_fn (or None)
        self._subscribers: dict[Callable[[Pattern], Awaitable[None]], Callable[[Pattern], bool] | None] = {}
        self._lock = asyncio.Lock()
        self._archetypes: dict[UUID, Pattern] = {}

    async def query_archetypes(self, *, id: UUID = None, type: str = None, tags: list[str] = None, filter_fn: Callable[["Pattern"], bool] = None) -> list["Pattern"]:
        """
        Query archetypes by id, type, tags, or custom filter.
        """
        async with self._lock:
            patterns = list(self._archetypes.values())
        results = []
        for pattern in patterns:
            if id is not None and pattern.id != id:
                continue
            if type is not None:
                # type may be in content or as class attribute
                pattern_type = pattern.content.get("type") or getattr(pattern, "type", None)
                if pattern_type != type:
                    continue
            if tags is not None:
                pattern_tags = pattern.content.get("tags", [])
                if not set(tags).issubset(set(pattern_tags)):
                    continue
            if filter_fn is not None and not filter_fn(pattern):
                continue
            results.append(pattern)
        return results

    async def subscribe(self, callback: Callable[[Pattern], Awaitable[None]], filter_fn: Callable[[Pattern], bool] = None) -> None:
        """
        Register a subscriber callback with an optional filter function.
        """
        async with self._lock:
            self._subscribers[callback] = filter_fn

    async def unsubscribe(self, callback: Callable[[Pattern], Awaitable[None]]) -> None:
        async with self._lock:
            self._subscribers.pop(callback, None)

    async def publish_archetype(self, archetype: Pattern) -> None:
        async with self._lock:
            if archetype.id in self._archetypes:
                raise ValueError("Archetype with this UUID already exists. Use a new UUID for new versions.")
            self._archetypes[archetype.id] = archetype
            subscribers = list(self._subscribers.items())
        # Deliver outside lock for isolation
        for callback, filter_fn in subscribers:
            try:
                if filter_fn is None or filter_fn(archetype):
                    await callback(archetype)
            except Exception:
                # Swallow/log errors in subscriber callbacks
                pass

    async def get_archetype(self, id: UUID) -> Pattern:
        async with self._lock:
            if id not in self._archetypes:
                raise KeyError(f"Archetype with id {id} not found")
            return self._archetypes[id]

    async def instantiate_archetype(self, archetype_id: UUID, customizer: Callable[[Pattern], Primitive] = None) -> "Primitive":
        """
        Instantiate (clone/customize) an archetype as a new Primitive, recording provenance.
        """
        import copy
        from datetime import datetime, timezone

        async with self._lock:
            if archetype_id not in self._archetypes:
                raise KeyError(f"Archetype with id {archetype_id} not found")
            archetype = self._archetypes[archetype_id]
            new_primitive = copy.deepcopy(archetype)
        # Assign new UUID and timestamps
        from uuid import uuid4
        new_primitive.id = uuid4()
        now = datetime.now(timezone.utc)
        new_primitive.metadata.created_at = now
        new_primitive.metadata.updated_at = now
        # Set or append provenance
        provenance = list(getattr(new_primitive.metadata, "provenance", []))
        provenance.append(archetype_id)
        new_primitive.metadata.provenance = provenance
        # Apply customizer if provided
        if customizer is not None:
            new_primitive = customizer(new_primitive)
        return new_primitive
