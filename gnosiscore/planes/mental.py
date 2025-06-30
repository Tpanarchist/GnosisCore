from gnosiscore.primitives.models import Identity, Boundary, Primitive, Transformation, Result
from gnosiscore.memory.subsystem import MemorySubsystem
from gnosiscore.selfmap.map import SelfMap
import logging

class MentalPlane:
    """
    MentalPlane embodies a digital self's subjective field: self-map, memory, and transformation intents.
    Consumes events from its DigitalPlane and may submit intents back.
    """

    def __init__(self, owner: Identity, boundary: Boundary, memory: MemorySubsystem, selfmap: SelfMap, metaphysical_plane=None):
        self.owner = owner
        self.boundary = boundary
        self.memory = memory
        self.selfmap = selfmap
        self.event_loop_id = str(owner.id)
        self.metaphysical_plane = metaphysical_plane  # AsyncMetaphysicalPlane instance

    async def get_archetype(self, id):
        """
        Await metaphysical_plane.get_archetype(id)
        """
        if self.metaphysical_plane is None:
            raise RuntimeError("No metaphysical_plane attached")
        return await self.metaphysical_plane.get_archetype(id)

    async def search_archetypes(self, **kwargs):
        """
        Await metaphysical_plane.query_archetypes(**kwargs)
        """
        if self.metaphysical_plane is None:
            raise RuntimeError("No metaphysical_plane attached")
        return await self.metaphysical_plane.query_archetypes(**kwargs)

    async def subscribe_to_archetypes(self, filter_fn, callback):
        """
        Register with metaphysical_plane.subscribe()
        """
        if self.metaphysical_plane is None:
            raise RuntimeError("No metaphysical_plane attached")
        await self.metaphysical_plane.subscribe(callback, filter_fn)

    async def instantiate_archetype(self, archetype_id, customizer=None):
        """
        Get, customize, store locally with provenance.
        """
        if self.metaphysical_plane is None:
            raise RuntimeError("No metaphysical_plane attached")
        primitive = await self.metaphysical_plane.instantiate_archetype(archetype_id, customizer)
        # Add to memory and selfmap, record provenance
        self.memory.insert_memory(primitive)
        self.selfmap.add_node(primitive)
        return primitive

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

    def submit_intent(self, transformation: Transformation, digital_plane, callback=None) -> Result:
        """
        Submit a Transformation as an Intent to the DigitalPlane.
        Returns a pending Result. Optionally registers a callback for result delivery.
        """
        from gnosiscore.primitives.models import Intent
        from uuid import uuid4
        from datetime import datetime, timezone

        intent = Intent(
            id=uuid4(),
            transformation=transformation,
            submitted_at=datetime.now(timezone.utc),
            version=1,
        )
        return digital_plane.submit_intent(intent, self, callback=callback)

    def on_result(self, result: Result) -> None:
        """
        Callback for receiving a Result from DigitalPlane.
        Override or extend as needed.
        """
        # Default: log or store result
        import logging
        logging.info(f"MentalPlane received result: {result}")

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
