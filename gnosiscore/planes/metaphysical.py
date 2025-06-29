from typing import Dict, Set
from uuid import UUID
from threading import Lock

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
