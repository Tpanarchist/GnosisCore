"""
LearningFeedbackManager: Emotional Feedback Loop for Salience-Weighted Memory and SelfMap

Listens for new Qualia, updates salience scores for memory/selfmap entries,
and provides APIs for salience-weighted recall and attention.

Extensible via plugin hooks for custom learning strategies.
"""

from typing import Optional, Callable, List
from gnosiscore.primitives.models import Qualia, Primitive
from gnosiscore.memory.subsystem import MemorySubsystem
from gnosiscore.selfmap.map import SelfMap

class LearningFeedbackManager:
    """
    Integrates Qualia-driven feedback into memory and selfmap.
    Updates 'salience' scores for entries and provides salience-weighted recall APIs.
    """

    def __init__(
        self,
        memory: MemorySubsystem,
        selfmap: SelfMap,
        salience_update_fn: Optional[Callable[[float, float, float], float]] = None,
        salience_decay: float = 0.99,
        min_salience: float = 0.0,
        max_salience: float = 10.0,
    ):
        """
        Args:
            memory: MemorySubsystem instance.
            selfmap: SelfMap instance.
            salience_update_fn: Optional custom function (old_salience, valence, intensity) -> new_salience.
            salience_decay: Decay factor applied on each update (default: 0.99).
            min_salience: Lower bound for salience.
            max_salience: Upper bound for salience.
        """
        self.memory = memory
        self.selfmap = selfmap
        self.salience_update_fn = salience_update_fn
        self.salience_decay = salience_decay
        self.min_salience = min_salience
        self.max_salience = max_salience

    def on_qualia(self, qualia: Qualia) -> None:
        """
        Update salience for the memory/selfmap entry referenced by qualia.about.
        """
        target_id = qualia.about

        # Only proceed if target_id is a UUID
        from uuid import UUID
        if isinstance(target_id, UUID):
            # Try memory
            try:
                primitive = self.memory.get_memory(target_id)
                new_primitive = self._update_salience(primitive, qualia)
                self.memory.update_memory(new_primitive)
            except Exception:
                pass

            # Try selfmap node
            try:
                primitive = self.selfmap.get_node(target_id)
                new_primitive = self._update_salience(primitive, qualia)
                self.selfmap.update_node(new_primitive)
            except Exception:
                pass

    def _update_salience(self, primitive: Primitive, qualia: Qualia) -> Primitive:
        """
        Compute new salience for a primitive based on qualia.
        """
        content = dict(primitive.content)
        old_salience = float(content.get("salience", 1.0))
        if self.salience_update_fn:
            new_salience = self.salience_update_fn(old_salience, qualia.valence, qualia.intensity)
        else:
            # Default: exponential moving average with decay and valence*intensity
            delta = qualia.valence * qualia.intensity
            new_salience = old_salience * self.salience_decay + delta
        new_salience = max(self.min_salience, min(self.max_salience, new_salience))
        content["salience"] = new_salience
        # Return a new Primitive with updated content (Pydantic is immutable by default)
        return primitive.model_copy(update={"content": content})

    def get_salient_memories(self, top_n: int = 10) -> List[Primitive]:
        """
        Return top_n memories ordered by salience (descending).
        """
        memories = self.memory.query()
        memories = sorted(memories, key=lambda m: float(m.content.get("salience", 1.0)), reverse=True)
        return memories[:top_n]

    def get_salient_nodes(self, top_n: int = 10) -> List[Primitive]:
        """
        Return top_n selfmap nodes ordered by salience (descending).
        """
        nodes = self.selfmap.all_nodes()
        nodes = sorted(nodes, key=lambda n: float(n.content.get("salience", 1.0)), reverse=True)
        return nodes[:top_n]
