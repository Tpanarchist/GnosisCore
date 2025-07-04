"""
GnosisCore Lived Experience Demo

Simulates a digital subject's ongoing experience, introspection, and self-modification.
Runs multiple cycles, injecting perception, abstraction, spontaneous thought, and narrating inner state.
"""

import random
import time
from uuid import uuid4
from datetime import datetime, timezone

from gnosiscore.primitives.models import Identity, Boundary, Primitive, Memory, Metadata
from gnosiscore.memory.subsystem import MemorySubsystem
from gnosiscore.selfmap.map import SelfMap, SelfObserverModule
from gnosiscore.selfmap.autobiography import AutobiographicalModule
from gnosiscore.planes.awareness import AwarenessLoop
from gnosiscore.planes.mental import MentalPlane, EmotionalFeedbackSystem
from gnosiscore.planes.metaphysical import MetaphysicalPlane, QualiaGenerator, PhenomenalBinder

# --- Initialization ---

identity = Identity(
    id=uuid4(),
    name="GnosisCoreSubject",
    metadata=Metadata(
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        provenance=[],
        confidence=1.0,
    ),
)
boundary = Boundary(
    id=uuid4(),
    name="DefaultBoundary",
    metadata=Metadata(
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        provenance=[],
        confidence=1.0,
    ),
)
memory = MemorySubsystem()
selfmap = SelfMap()
metaphysical_plane = MetaphysicalPlane(version="1.0", boundary=boundary)
observer = SelfObserverModule(selfmap)
qualia_generator = QualiaGenerator()
phenomenal_binder = PhenomenalBinder()
emotional_feedback = EmotionalFeedbackSystem(memory)

mental_plane = MentalPlane(
    owner=identity,
    boundary=boundary,
    memory=memory,
    selfmap=selfmap,
    metaphysical_plane=None  # Not async for this demo
)

# --- Demo Parameters ---
CYCLES = 7
random.seed(42)

# --- Trace Storage ---
autobiographical = AutobiographicalModule()

def narrate(msg):
    print(msg)
    autobiographical.log_experience(f"{datetime.now(timezone.utc).isoformat()} | {msg}")

# --- Demo Loop ---
import asyncio

class DemoAwarenessLoop(AwarenessLoop):
    def __init__(self, observer, autobiographical, cycles, **kwargs):
        super().__init__(observer, autobiographical, **kwargs)
        self.cycles = cycles
        self.current_cycle = 0

    async def tick(self):
        self.current_cycle += 1
        cycle = self.current_cycle
        narrate(f"\n--- Cycle {cycle} ---")

        # 1. Perception: inject a new event
        perception_content = {
            "stimulus": random.choice(["light", "sound", "touch", "idea"]),
            "intensity": random.uniform(0.5, 1.5),
            "status": random.choice(["success", "failure"]),
            "cycle": cycle,
        }
        perception = Primitive(
            id=uuid4(),
            type="perception",
            content=perception_content,
            metadata=Metadata(
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                provenance=[],
                confidence=1.0,
            ),
        )
        mental_plane.on_event(perception)
        narrate(f"Perceived: {perception_content}")

        # 2. Abstraction: summarize recent perceptions
        if cycle % 2 == 0:
            memories = memory.query(type="perception", custom=lambda m: m.content.get("cycle") == cycle)
            summary = f"Abstracted {len(memories)} perceptions at cycle {cycle}."
            abstraction = Memory(
                id=uuid4(),
                metadata=Metadata(
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                    provenance=[m.id for m in memories],
                    confidence=1.0,
                ),
                content={
                    "summary": summary,
                    "modality": "abstraction",
                    "cycle": cycle,
                }
            )
            memory.insert_memory(abstraction)
            selfmap.add_node(abstraction)
            narrate(f"Abstraction: {summary}")

        # 3. Spontaneous Thought: random chance
        if random.random() < 0.5:
            thought_content = {
                "thought": random.choice(["What if?", "I wonder...", "Could I change?", "Why did that happen?"]),
                "cycle": cycle,
            }
            thought = Primitive(
                id=uuid4(),
                type="spontaneous-thought",
                content=thought_content,
                metadata=Metadata(
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                    provenance=[],
                    confidence=1.0,
                ),
            )
            mental_plane.on_event(thought)
            narrate(f"Spontaneous Thought: {thought_content['thought']}")

        # 4. Qualia & Emotional Feedback
        qualia = qualia_generator.generate_qualia(perception)
        phenomenal = phenomenal_binder.bind(qualia, self_state={"cycle": cycle})
        feedback = emotional_feedback.process_emotional_feedback(perception)
        narrate(f"Qualia: {qualia.content} | Emotional Feedback: {feedback['regulatory_response']}")

        # 5. Recursive Self-Modification (meta-self observation)
        meta_self = observer.observe_self_modeling(depth=2)
        narrate(f"Meta-self observed: {meta_self.content}")

        # 6. Meta-cognitive awareness
        emotional_state = mental_plane.get_emotional_state()
        narrate(f"Meta-cognition: I notice my emotional state is {emotional_state}")

        # Maintain the 'now'
        self._current_state = {"now": f"cycle_{cycle}"}

    async def run(self):
        self._running = True
        while self._running and self.current_cycle < self.cycles:
            await self.tick()
            await asyncio.sleep(self.cycle_interval)
        self._running = False

# Run the triad-driven demo loop
async def main():
    loop = DemoAwarenessLoop(observer, autobiographical, cycles=CYCLES, cycle_interval=0)
    await loop.run()

asyncio.run(main())

# --- Final Autobiography Trace ---
narrate("\n=== Final Inner Autobiography Trace ===")
for entry in autobiographical.replay():
    print(entry)
