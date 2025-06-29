from typing import Dict, Set, Optional, Callable
from uuid import UUID
from threading import Lock

from gnosiscore.primitives.models import Boundary, Primitive

# Forward reference for MentalPlane (to avoid circular import)
from gnosiscore.primitives.models import Primitive
class MentalPlane:
    def on_event(self, event: Primitive) -> None:
        pass

class DigitalPlane:
    """
    DigitalPlane hosts all digital entities and their state.
    Enforces boundaries, manages spatial/temporal structures,
    and propagates events to subscribed MentalPlanes.
    """
    def __init__(self, id: UUID, boundary: Boundary):
        self.id = id
        self.boundary = boundary
        self._entities: Dict[UUID, Primitive] = {}
        self._subscribers: Set[MentalPlane] = set()
        self._lock = Lock()
        self.on_persist: Optional[Callable[[Primitive], None]] = None

    def register_entity(self, primitive: Primitive) -> None:
        with self._lock:
            # TODO: Implement boundary enforcement logic
            self._entities[primitive.id] = primitive
            if self.on_persist:
                self.on_persist(primitive)

    def get_entity(self, entity_id: UUID) -> Primitive:
        with self._lock:
            return self._entities[entity_id]

    def remove_entity(self, entity_id: UUID) -> None:
        with self._lock:
            if entity_id in self._entities:
                del self._entities[entity_id]

    def publish_event(self, event: Primitive) -> None:
        with self._lock:
            for subscriber in self._subscribers:
                subscriber.on_event(event)

    def subscribe(self, mental_plane: 'MentalPlane') -> None:
        with self._lock:
            self._subscribers.add(mental_plane)

    def unsubscribe(self, mental_plane: 'MentalPlane') -> None:
        with self._lock:
            self._subscribers.discard(mental_plane)
