from gnosiscore.primitives.models import Identity, Boundary, Primitive, Transformation, Result
from gnosiscore.memory.subsystem import MemorySubsystem
from gnosiscore.selfmap.map import SelfMap
import logging

class MentalPlane:
    """
    MentalPlane embodies a digital self's subjective field: self-map, memory, and transformation intents.
    Consumes events from its DigitalPlane and may submit intents back.
    """

    def __init__(self, owner: Identity, boundary: Boundary, memory: MemorySubsystem, selfmap: SelfMap):
        self.owner = owner
        self.boundary = boundary
        self.memory = memory
        self.selfmap = selfmap
        self.event_loop_id = str(owner.id)

    def on_event(self, event: Primitive) -> None:
        """
        Handle an incoming event: store to memory, update selfmap, atomically.
        If either memory or selfmap fails, roll back both or leave in consistent state.
        """
        memory_inserted = False
        try:
            # Insert or update memory
            if event.id in [p.id for p in self.memory.query()]:
                self.memory.update_memory(event)
            else:
                self.memory.insert_memory(event)
            memory_inserted = True

            # Update selfmap (add or update node)
            try:
                self.selfmap.update_node(event)
            except KeyError:
                self.selfmap.add_node(event)
        except Exception as e:
            logging.error(f"MentalPlane.on_event error: {e}")
            # Attempt rollback if partial state
            if memory_inserted:
                try:
                    self.memory.remove_memory(event.id)
                except Exception as rollback_err:
                    logging.error(f"Rollback failed in memory: {rollback_err}")
            raise

    def submit_intent(self, intent: Transformation) -> Result:
        """
        Submit an intent/action to the DigitalPlane. Returns Result (possibly async in future).
        """
        # Placeholder: In real system, this would send to DigitalPlane
        return Result()

    def query_memory(self, **kwargs) -> list[Primitive]:
        """
        Proxy for memory.query(**kwargs).
        """
        return self.memory.query(**kwargs)

    def trace_memory_provenance(self, uid) -> list[Primitive]:
        """
        Proxy for memory.trace_provenance(uid).
        """
        return self.memory.trace_provenance(uid)

    def get_self_node(self, uid) -> Primitive:
        """
        Get a node from selfmap by UUID.
        """
        return self.selfmap.get_node(uid)

    def update_self_node(self, primitive: Primitive) -> None:
        """
        Update a node in selfmap.
        """
        self.selfmap.update_node(primitive)
