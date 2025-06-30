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


class AsyncMetaphysicalPlane:
    """
    AsyncMetaphysicalPlane is an async/thread-safe, atemporal substrate for archetype (Pattern) events.
    Supports async subscriptions and at-least-once delivery to all registered subscribers.
    """
    def __init__(self):
        self._subscribers: set[Callable[[Pattern], Awaitable[None]]] = set()
        self._lock = asyncio.Lock()
        self._archetypes: dict[UUID, Pattern] = {}

    async def subscribe(self, callback: Callable[[Pattern], Awaitable[None]]) -> None:
        async with self._lock:
            self._subscribers.add(callback)

    async def unsubscribe(self, callback: Callable[[Pattern], Awaitable[None]]) -> None:
        async with self._lock:
            self._subscribers.discard(callback)

    async def publish_archetype(self, archetype: Pattern) -> None:
        async with self._lock:
            if archetype.id in self._archetypes:
                raise ValueError("Archetype with this UUID already exists. Use a new UUID for new versions.")
            self._archetypes[archetype.id] = archetype
            subscribers = list(self._subscribers)
        # Deliver outside lock for isolation
        for callback in subscribers:
            try:
                await callback(archetype)
            except Exception:
                # Swallow/log errors in subscriber callbacks
                pass

    async def get_archetype(self, id: UUID) -> Pattern:
        async with self._lock:
            if id not in self._archetypes:
                raise KeyError(f"Archetype with id {id} not found")
            return self._archetypes[id]
