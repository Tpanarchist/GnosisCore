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

    def __init__(
        self,
        owner: Identity,
        boundary: Boundary,
        memory: MemorySubsystem,
        selfmap: SelfMap,
        metaphysical_plane=None,
        consolidation_group_window=None,
        consolidation_min_group_size=3,
        prune_min_salience=0.2,
        prune_expiry_duration=None,
        archival_mode=True,
        grouping_strategy=None,
        cycle_interval=60,
    ):
        from datetime import timedelta
        self.owner = owner
        self.boundary = boundary
        self.memory = memory
        self.selfmap = selfmap
        self.event_loop_id = str(owner.id)
        self.metaphysical_plane = metaphysical_plane  # AsyncMetaphysicalPlane instance
        self.qualia_log: list[Qualia] = []
        self.feedback_manager = LearningFeedbackManager(memory, selfmap)
        # Consolidation/pruning config
        self.consolidation_group_window = consolidation_group_window or timedelta(minutes=10)
        self.consolidation_min_group_size = consolidation_min_group_size
        self.prune_min_salience = prune_min_salience
        self.prune_expiry_duration = prune_expiry_duration or timedelta(days=30)
        self.archival_mode = archival_mode
        self.grouping_strategy = grouping_strategy  # Callable or None
        self.cycle_interval = cycle_interval

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

    # --- SelfMap API Extensions ---

    def add_to_selfmap(self, primitive: Primitive) -> None:
        """
        Add a node (Primitive) to the self-map.
        """
        self.selfmap.add_node(primitive)

    def get_from_selfmap(self, *, id=None, type_name=None, attr=None, value=None):
        """
        Retrieve nodes from self-map by id, type, or attribute.
        """
        if id is not None:
            return self.selfmap.get_node(id)
        if type_name is not None:
            return self.selfmap.get_nodes_by_type(type_name)
        if attr is not None and value is not None:
            return self.selfmap.get_nodes_by_attribute(attr, value)
        return None

    def traverse_selfmap(self, start_id, depth=1, filter_fn=None):
        """
        Traverse the self-map graph from a start node.
        """
        return list(self.selfmap.traverse(start_id, depth, filter_fn))

    def update_selfmap_node(self, node_id, updates: dict):
        """
        Update a node in the self-map with partial updates.
        """
        node = self.selfmap.get_node(node_id)
        for k, v in updates.items():
            if hasattr(node, k):
                setattr(node, k, v)
            elif k in node.content:
                node.content[k] = v
            else:
                node.content[k] = v
        self.selfmap.update_node(node)

    def selfmap_versions(self):
        """
        Return all version ids and allow retrieval of a specific version.
        """
        return {
            "versions": self.selfmap.list_versions(),
            "get_version": self.selfmap.get_version,
        }

    # --- Memory Consolidation & Pruning Cycles ---

    async def run_background_cycles(self):
        """
        Run background memory consolidation and pruning cycles asynchronously.
        """
        while True:
            await self.consolidate_memories()
            await self.prune_memories()
            await asyncio.sleep(getattr(self, "cycle_interval", 60))  # Default to 60s if not set

    async def consolidate_memories(self):
        """
        Group episodic memories into semantic/abstract knowledge.
        """
        from datetime import datetime, timezone
        from uuid import uuid4
        import itertools

        now = datetime.now(timezone.utc)
        # Gather candidates: recent, un-abstracted, un-archived episodic memories
        window_start = now - self.consolidation_group_window
        candidates = self.memory.query(
            type="Memory",
            after=window_start,
            custom=lambda m: not m.content.get("archived") and not m.content.get("abstracted"),
        )

        # Grouping: use strategy if provided, else default grouping
        def default_grouping(memories):
            # Group by (source, modality, event_type, timestamp proximity)
            groups = []
            sorted_mems = sorted(memories, key=lambda m: (m.content.get("source"), m.content.get("modality"), m.content.get("event_type"), m.metadata.created_at))
            for key, group in itertools.groupby(
                sorted_mems,
                key=lambda m: (
                    m.content.get("source"),
                    m.content.get("modality"),
                    m.content.get("event_type"),
                    # Bucket timestamps by minute
                    int(m.metadata.created_at.timestamp() // (self.consolidation_group_window.total_seconds() or 1))
                ),
            ):
                group_list = list(group)
                if len(group_list) >= self.consolidation_min_group_size:
                    groups.append(group_list)
            return groups

        grouping_fn = self.grouping_strategy or default_grouping
        groups = grouping_fn(candidates)

        for group in groups:
            # Create abstraction node
            summary = "; ".join([str(m.content.get("summary") or m.content.get("description") or m.content) for m in group])
            provenance = [m.id for m in group]
            aggregated_values = {}
            # Optionally aggregate stats/counts here
            abstraction = type(group[0])(
                id=uuid4(),
                metadata=Metadata(
                    created_at=now,
                    updated_at=now,
                    provenance=provenance,
                    confidence=min([m.metadata.confidence for m in group]),
                ),
                content={
                    "summary": summary,
                    "provenance": provenance,
                    "aggregated_values": aggregated_values,
                    "abstracted": True,
                    "modality": group[0].content.get("modality"),
                    "event_type": group[0].content.get("event_type"),
                    "source": group[0].content.get("source"),
                },
            )
            # Insert abstraction into memory and selfmap
            try:
                self.memory.insert_memory(abstraction)
                self.selfmap.add_node(abstraction)
                # Mark originals as archived and low salience
                for m in group:
                    m.content["archived"] = True
                    m.content["salience"] = min(0.01, m.content.get("salience", 1.0))
                    m.content["abstracted"] = True
                    m.metadata.updated_at = now
                    self.memory.update_memory(m)
                    try:
                        self.selfmap.update_node(m)
                    except Exception:
                        pass
                # Log as Qualia (positive valence, about = abstraction.id)
                qualia = Qualia(
                    id=uuid4(),
                    metadata=Metadata(created_at=now, updated_at=now),
                    valence=1.0,
                    intensity=1.0,
                    modality="consolidation",
                    about=abstraction.id,
                    content={"grouped": provenance, "summary": summary},
                )
                self.qualia_log.append(qualia)
            except Exception as e:
                import logging
                logging.error(f"Consolidation failed: {e}")

    async def prune_memories(self):
        """
        Prune low-value, contradictory, or expired memories.
        """
        from datetime import datetime, timezone
        from uuid import uuid4

        now = datetime.now(timezone.utc)
        # Gather all memories and selfmap nodes
        all_memories = self.memory.query()
        all_nodes = self.selfmap.all_nodes()
        # Build set of all provenance references
        all_provenance = set()
        for n in all_memories + all_nodes:
            prov = getattr(n.metadata, "provenance", [])
            all_provenance.update(prov)
        # Prune predicate
        def should_prune(node):
            if node.content.get("contradicted"):
                return True
            if node.content.get("salience", 1.0) < self.prune_min_salience:
                return True
            if node.metadata.created_at < (now - self.prune_expiry_duration):
                if node.id not in all_provenance:
                    return True
            return False

        for node in all_memories:
            if should_prune(node):
                # Only hard-delete if archival_mode is False and node is not referenced
                if not self.archival_mode and node.id not in all_provenance:
                    try:
                        self.memory.remove_memory(node.id)
                        try:
                            self.selfmap.remove_node(node.id)
                        except Exception:
                            pass
                        # Log as Qualia (negative valence, about = node.id)
                        qualia = Qualia(
                            id=uuid4(),
                            metadata=Metadata(created_at=now, updated_at=now),
                            valence=-1.0,
                            intensity=1.0,
                            modality="pruning",
                            about=node.id,
                            content={"action": "hard_delete"},
                        )
                        self.qualia_log.append(qualia)
                    except Exception as e:
                        import logging
                        logging.error(f"Pruning (hard delete) failed: {e}")
                else:
                    # Soft archive
                    try:
                        node.content["archived"] = True
                        node.metadata.updated_at = now
                        self.memory.update_memory(node)
                        try:
                            self.selfmap.update_node(node)
                        except Exception:
                            pass
                        # Log as Qualia (negative valence, about = node.id)
                        qualia = Qualia(
                            id=uuid4(),
                            metadata=Metadata(created_at=now, updated_at=now),
                            valence=-1.0,
                            intensity=1.0,
                            modality="pruning",
                            about=node.id,
                            content={"action": "archived"},
                        )
                        self.qualia_log.append(qualia)
                    except Exception as e:
                        import logging
                        logging.error(f"Pruning (archive) failed: {e}")

    def detect_contradictions(self):
        """
        Find pairs of beliefs/memories with contradictory content/values.
        Returns a list of (Primitive, Primitive) tuples.
        """
        # E.g., conflicting Belief or Value nodes
        # This is a stub; real implementation would require domain-specific logic
        contradictions = []
        nodes = self.selfmap.all_nodes()
        for i, n1 in enumerate(nodes):
            for n2 in nodes[i+1:]:
                if getattr(n1, "type", None) == getattr(n2, "type", None) == "Belief":
                    v1 = n1.content.get("value")
                    v2 = n2.content.get("value")
                    if v1 is not None and v2 is not None and v1 != v2 and n1.content.get("subject") == n2.content.get("subject"):
                        contradictions.append((n1, n2))
        return contradictions

    async def correct_contradictions(self):
        """
        Propose and enact corrections for contradictions (LLM or rule-based).
        """
        # Trigger transformation/intent for correction; optionally interact with LLM plugin
        # This is a stub; real implementation would require more logic
        contradictions = self.detect_contradictions()
        for n1, n2 in contradictions:
            # Example: mark both as 'contradicted' in content and update provenance
            n1.content["contradicted"] = True
            n2.content["contradicted"] = True
            # Optionally, add provenance links
            prov = getattr(n1.metadata, "provenance", [])
            prov2 = getattr(n2.metadata, "provenance", [])
            n1.metadata.provenance = list(set(prov + [n2.id]))
            n2.metadata.provenance = list(set(prov2 + [n1.id]))
            self.selfmap.update_node(n1)
            self.selfmap.update_node(n2)
        return contradictions

    # --- Observation/Inspection Interface ---

    def export_selfmap_snapshot(self):
        """
        Export the current self-map (nodes and connections) as a serializable dict.
        """
        return {
            "nodes": [n.model_dump() for n in self.selfmap.all_nodes()],
            "connections": [c.model_dump() for c in self.selfmap.all_connections()],
        }

    def export_qualia_log(self, limit: int = 100):
        """
        Export the most recent qualia log entries.
        """
        return [q.model_dump() for q in self.qualia_log[-limit:]]

    def export_memory_state(self):
        """
        Export all current memories as a serializable list.
        """
        return [m.model_dump() for m in self.memory.query()]

    def export_provenance_chain(self, node_id):
        """
        Export the provenance chain for a given node in the self-map.
        """
        chain = self.selfmap.provenance_walk(node_id)
        return [n.model_dump() for n in chain]
