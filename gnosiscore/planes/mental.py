from gnosiscore.primitives.models import Identity, Boundary, Primitive, Transformation, Result, Attention, Qualia, Metadata
from uuid import uuid4
from datetime import datetime, timezone
from gnosiscore.memory.subsystem import MemorySubsystem
from gnosiscore.selfmap.map import SelfMap
from gnosiscore.planes.learning_feedback import LearningFeedbackManager
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
        self.qualia_log: list[Qualia] = []
        self.feedback_manager = LearningFeedbackManager(memory, selfmap)

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
    async def attend(self, attention: Attention) -> list[Primitive]:
        """Query memory and/or selfmap selectively using attention parameters."""
        results = []
        # Example: use subject/object as query keys
        if hasattr(attention, "subject") and attention.subject:
            results += self.memory.query(custom=lambda m: getattr(m, "id", None) == attention.subject)
        if hasattr(attention, "object") and attention.object:
            if attention.object == "all":
                results += self.selfmap.all_nodes()
            else:
                results += [n for n in self.selfmap.all_nodes() if getattr(n, "id", None) == attention.object]
        # Optionally filter by intensity/duration as relevance
        return results

    def record_qualia(self, result: Result, about: uuid4, modality: str = "transformation"):
        valence = 1.0 if result.status == "success" else -1.0
        intensity = result.output.get("confidence", 1.0) if result.output else 0.5
        qualia = Qualia(
            id=uuid4(),
            metadata=Metadata(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
            valence=valence,
            intensity=intensity,
            modality=modality,
            about=about,
            content={"result": result.model_dump()}
        )
        self.qualia_log.append(qualia)
        self.feedback_manager.on_qualia(qualia)

    def get_emotional_state(self) -> dict:
        """Summarize recent qualia (average valence/intensity, count by modality)."""
        if not self.qualia_log:
            return {"average_valence": 0.0, "average_intensity": 0.0, "count": 0, "by_modality": {}}
        avg_valence = sum(q.valence for q in self.qualia_log) / len(self.qualia_log)
        avg_intensity = sum(q.intensity for q in self.qualia_log) / len(self.qualia_log)
        by_modality = {}
        for q in self.qualia_log:
            by_modality.setdefault(q.modality, []).append(q)
        by_modality_summary = {k: len(v) for k, v in by_modality.items()}
        return {
            "average_valence": avg_valence,
            "average_intensity": avg_intensity,
            "count": len(self.qualia_log),
            "by_modality": by_modality_summary,
        }

    def on_event(self, event: Primitive) -> None:
        """
        Handle an incoming event: store to memory, update selfmap, atomically.
        If either memory or selfmap fails, roll back both or leave in consistent state.
        """
        # Handle Attention as a special event
        if isinstance(event, Attention):
            # Optionally, could trigger focus logic or log attention
            # For now, just run attend and do nothing with result
            import asyncio
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.attend(event))
            except RuntimeError:
                # No running event loop (e.g., in sync test), run synchronously
                asyncio.run(self.attend(event))
            return
        # Handle Qualia as a special event (could influence state)
        if isinstance(event, Qualia):
            self.qualia_log.append(event)
            self.feedback_manager.on_qualia(event)
            return

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
        # Record qualia for this result
        self.record_qualia(result, about=result.intent_id, modality="transformation")

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
