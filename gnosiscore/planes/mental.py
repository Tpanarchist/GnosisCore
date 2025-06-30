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

    async def adaptive_recall(
        self,
        top_n: int = 5,
        modality: str = None,
        min_salience: float = 0.0,
        since: datetime = None,
        qualia_weight: float = 0.5,
        attention_bias: "Attention" = None,
    ) -> list["Primitive"]:
        """
        Retrieve the most relevant memories/nodes, scored by a blend of salience, recency, and qualia/valence.
        """
        from gnosiscore.primitives.models import Primitive, Qualia
        import math

        # Gather candidates from memory and selfmap
        candidates = self.memory.query()
        candidates += self.selfmap.all_nodes()

        now = datetime.now(timezone.utc)
        scored = []
        for node in candidates:
            salience = float(node.content.get("salience", 1.0))
            if salience < min_salience:
                continue
            if modality and node.content.get("modality") != modality:
                continue
            if since and node.metadata.updated_at < since:
                continue

            # Recency score (0-1, 1=now)
            recency = 1.0 - min(1.0, (now - node.metadata.updated_at).total_seconds() / (60 * 60 * 24))
            # Qualia score: average valence*intensity for recent qualia about this node
            qualia = [q for q in self.qualia_log if getattr(q, "about", None) == node.id]
            qualia_score = 0.0
            if qualia:
                qualia_score = sum(q.valence * q.intensity for q in qualia) / len(qualia)
            # Blend: salience * (1-qualia_weight) + qualia_score * qualia_weight + recency*0.1
            score = (
                salience * (1 - qualia_weight)
                + qualia_score * qualia_weight
                + recency * 0.1
            )
            # Optionally bias by attention
            if attention_bias:
                if hasattr(attention_bias, "object") and attention_bias.object == node.id:
                    score += 0.2
                if hasattr(attention_bias, "modality") and node.content.get("modality") == getattr(attention_bias, "modality", None):
                    score += 0.1
            scored.append((score, node))
        # Sort and return top_n
        scored.sort(reverse=True, key=lambda x: x[0])
        return [n for _, n in scored[:top_n]]

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

    def decay_salience(self, decay_rate: float = 0.01, floor: float = 0.0):
        """
        Proxy to feedback_manager.decay_salience.
        Returns a list of SalienceDecayEvent.
        """
        return self.feedback_manager.decay_salience(decay_rate=decay_rate, floor=floor)

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

    def get_emotional_drive(self):
        """
        Returns summary stats (dominant valence, modality, intensity, recent qualia, updated_at).
        """
        from gnosiscore.primitives.models import EmotionalDriveSummary, Qualia
        from datetime import datetime, timezone

        if not self.qualia_log:
            return EmotionalDriveSummary(
                dominant_valence=0.0,
                dominant_modality="none",
                intensity=0.0,
                recent_qualia=[],
                updated_at=datetime.now(timezone.utc),
            )
        # Dominant valence: mean of last N qualia
        N = 10
        recent = self.qualia_log[-N:]
        dominant_valence = sum(q.valence for q in recent) / len(recent)
        # Dominant modality: most frequent in recent qualia
        modality_counts = {}
        for q in recent:
            modality_counts[q.modality] = modality_counts.get(q.modality, 0) + 1
        dominant_modality = max(modality_counts, key=modality_counts.get)
        # Intensity: mean of recent
        intensity = sum(q.intensity for q in recent) / len(recent)
        updated_at = recent[-1].metadata.updated_at if hasattr(recent[-1], "metadata") else datetime.now(timezone.utc)
        return EmotionalDriveSummary(
            dominant_valence=dominant_valence,
            dominant_modality=dominant_modality,
            intensity=intensity,
            recent_qualia=recent,
            updated_at=updated_at,
        )

    def prioritize_by_emotion(self, candidates: list, drive_bias: float = 0.5) -> list:
        """
        Reorders/reweights candidates by current emotional state.
        """
        drive = self.get_emotional_drive()
        if drive.dominant_modality == "none":
            return candidates
        def score(node):
            # Score boost for matching dominant modality
            modality_match = 1.0 if node.content.get("modality") == drive.dominant_modality else 0.0
            # Score boost for matching valence sign (if node has qualia)
            qualia = [q for q in self.qualia_log if getattr(q, "about", None) == node.id]
            if qualia:
                avg_valence = sum(q.valence for q in qualia) / len(qualia)
                valence_match = 1.0 if (avg_valence * drive.dominant_valence) > 0 else 0.0
            else:
                valence_match = 0.0
            return drive_bias * (modality_match + valence_match)
        return sorted(candidates, key=score, reverse=True)

    def self_reflection(self):
        """
        Summarize top qualia, salience, and emotional shifts; adjust next-cycle attention or recall bias.
        Returns a dict summary.
        """
        # Top qualia (by intensity)
        top_qualia = sorted(self.qualia_log, key=lambda q: abs(q.intensity), reverse=True)[:5]
        # Top salient memories/nodes
        salient_mems = self.feedback_manager.get_salient_memories(top_n=5)
        salient_nodes = self.feedback_manager.get_salient_nodes(top_n=5)
        # Emotional shift: compare last 5 vs previous 5 qualia
        N = 5
        if len(self.qualia_log) >= 2 * N:
            prev = self.qualia_log[-2*N:-N]
            recent = self.qualia_log[-N:]
            prev_val = sum(q.valence for q in prev) / N
            recent_val = sum(q.valence for q in recent) / N
            shift = recent_val - prev_val
        else:
            shift = 0.0
        return {
            "top_qualia": top_qualia,
            "salient_memories": salient_mems,
            "salient_nodes": salient_nodes,
            "emotional_shift": shift,
        }

    def goal_replanning(self, negative_threshold: float = -0.5):
        """
        If dominant qualia trend negative, propose new transformation/intents to shift state.
        Returns True if replanning triggered.
        """
        drive = self.get_emotional_drive()
        if drive.dominant_valence < negative_threshold:
            # Example: propose a positive transformation intent (details domain-specific)
            # This is a placeholder for actual intent logic
            return True
        return False

    def salience_qualia_sync(self):
        """
        Ensure all transformations/memories influencing qualia are flagged for adaptive recall or re-evaluation.
        Returns list of node IDs to flag.
        """
        flagged = set()
        for q in self.qualia_log:
            flagged.add(q.about)
        return list(flagged)

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
