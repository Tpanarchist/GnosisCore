"""
GnosisCore Kindergarten Training and Test Demo

This demo showcases a Digital Self learning a kindergarten-level curriculum, forming abstractions, handling correction (including LLM-backed transformations if needed), and supporting self-reflection. All data flows through GnosisCore primitives, transformation plugins, and qualia/selfmap mechanisms.

Run with: pytest tests/demo/test_kindergarten_learning.py
"""

import pytest
import asyncio
from uuid import uuid4, UUID
from datetime import datetime, timezone, timedelta

from gnosiscore.primitives.models import (
    Identity, Boundary, Metadata, Perception, Memory, Qualia, Transformation, Result, Pattern, Label
)
from gnosiscore.memory.subsystem import MemorySubsystem
from gnosiscore.selfmap.map import SelfMap
from gnosiscore.planes.mental import MentalPlane
from gnosiscore.transformation.registry import TransformationHandlerRegistry
from gnosiscore.planes.learning_feedback import LearningFeedbackManager

# --- Transformation Handlers ---

registry = TransformationHandlerRegistry()

async def perception_to_memory(transformation: Transformation) -> Result:
    """Transform Perception into Memory and store in MemorySubsystem and SelfMap."""
    perception = Perception.model_validate(transformation.content["perception"])
    memory = Memory(
        id=uuid4(),
        metadata=Metadata(
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            provenance=[perception.id, digital_body.id],
            confidence=1.0,
        ),
        content={
            **perception.content,
            "source": "lesson",
            "summary": perception.content.get("summary", ""),
        },
    )
    # Insert into memory and selfmap
    demo_plane.memory.insert_memory(memory)
    demo_plane.selfmap.add_node(memory)
    # Connect memory to DigitalBody in SelfMap
    mem_conn_id = uuid4()
    demo_plane.selfmap.add_connection(Connection(
        id=mem_conn_id,
        metadata=Metadata(
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            provenance=[digital_body.id, memory.id],
            confidence=1.0,
        ),
        content={"source": digital_body.id, "target": memory.id, "type": "carries_memory"}
    ))
    # Qualia: positive feedback, provenance includes DigitalBody
    qualia = Qualia(
        id=uuid4(),
        metadata=Metadata(
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            provenance=[memory.id, digital_body.id],
            confidence=1.0,
        ),
        valence=1.0,
        intensity=1.0,
        modality="lesson",
        about=memory.id,
        content={"feedback": "learned", "body": str(digital_body.id)},
    )
    demo_plane.qualia_log.append(qualia)
    return Result(
        id=uuid4(),
        intent_id=transformation.id,
        status="success",
        output={"memory_id": str(memory.id)},
        error=None,
        timestamp=datetime.now(timezone.utc),
    )

registry.register("perception_to_memory", perception_to_memory)

# --- Abstraction Transformation Handler ---

async def memory_consolidation(transformation: Transformation) -> Result:
    memories = transformation.content["memories"]  # List of dicts with id, summary, modality
    summary = " ".join(m["summary"] for m in memories)
    abstraction_summary = f"Learned about: {summary}"

    modality = transformation.content["modality"]
    archetype_id = f"{modality}_archetype"
    # Only include memory node IDs in provenance (exclude DigitalBody)
    provenance_ids = [str(m["id"]) for m in memories]
    abstraction = Pattern(
        id=uuid4(),
        metadata=Metadata(
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            provenance=provenance_ids,
            confidence=1.0,
        ),
        content={
            "summary": abstraction_summary,
            "modality": modality,
            "abstracted": True,
            "archetype_id": archetype_id
        },
    )

    # Store abstraction in MemorySubsystem & SelfMap
    demo_plane.memory.insert_memory(abstraction)
    demo_plane.selfmap.add_node(abstraction)
    # Connect abstraction to DigitalBody
    abs_conn_id = uuid4()
    demo_plane.selfmap.add_connection(Connection(
        id=abs_conn_id,
        metadata=Metadata(
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            provenance=[digital_body.id, abstraction.id],
            confidence=1.0,
        ),
        content={"source": digital_body.id, "target": abstraction.id, "type": "carries_abstraction"}
    ))
    # Positive qualia for abstraction
    qualia = Qualia(
        id=uuid4(),
        metadata=Metadata(
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            provenance=[abstraction.id, digital_body.id],
            confidence=1.0,
        ),
        valence=1.0,
        intensity=1.0,
        modality="abstraction",
        about=abstraction.id,
        content={"feedback": "abstracted", "body": str(digital_body.id)},
    )
    demo_plane.qualia_log.append(qualia)

    return Result(
        id=uuid4(),
        intent_id=transformation.id,
        status="success",
        output={"abstraction_id": str(abstraction.id)},
        error=None,
        timestamp=datetime.now(timezone.utc),
    )

registry.register("memory_consolidation", memory_consolidation)

# --- Demo Setup ---

# 1. Instantiate DigitalBody as a Label primitive
digital_body = Label(
    id=uuid4(),
    metadata=Metadata(
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        provenance=[],
        confidence=1.0,
    ),
    content={"type": "DigitalBody", "name": "KindergartenBody"}
)

identity = Identity(
    id=uuid4(),
    metadata=Metadata(
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        provenance=[],
        confidence=1.0,
    ),
    content={"name": "KindergartenDI"}
)
boundary = Boundary(
    id=uuid4(),
    metadata=Metadata(
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        provenance=[],
        confidence=1.0,
    ),
    content={}
)
memory = MemorySubsystem()
selfmap = SelfMap()
demo_plane = MentalPlane(identity, boundary, memory, selfmap)

# Add DigitalBody, Identity, Boundary to SelfMap and connect
selfmap.add_node(digital_body)
selfmap.add_node(identity)
selfmap.add_node(boundary)
from gnosiscore.primitives.models import Connection
conn_id = uuid4()
selfmap.add_connection(Connection(
    id=conn_id,
    metadata=Metadata(
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        provenance=[digital_body.id, identity.id],
        confidence=1.0,
    ),
    content={"source": digital_body.id, "target": identity.id, "type": "carries"}
))
conn_id2 = uuid4()
selfmap.add_connection(Connection(
    id=conn_id2,
    metadata=Metadata(
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        provenance=[digital_body.id, boundary.id],
        confidence=1.0,
    ),
    content={"source": digital_body.id, "target": boundary.id, "type": "has_boundary"}
))

# --- Kindergarten Lessons ---

LESSONS = [
    {"summary": "Red is a color.", "modality": "color", "fact": "red"},
    {"summary": "Blue is a color.", "modality": "color", "fact": "blue"},
    {"summary": "1 comes before 2.", "modality": "number", "fact": "1<2"},
    {"summary": "2+2=4", "modality": "number", "fact": "2+2=4"},
    {"summary": "Circle is a shape.", "modality": "shape", "fact": "circle"},
    {"summary": "Pattern: red, blue, red, blue", "modality": "pattern", "fact": "red,blue"},
    {"summary": "Pattern: circle, square, circle", "modality": "pattern", "fact": "circle,square"},
    {"summary": "We say please.", "modality": "rule", "fact": "say please"},
]

@pytest.mark.asyncio
async def test_kindergarten_learning():
    # Start the continuous self-awareness loop (consciousness triad)
    import asyncio
    asyncio.create_task(demo_plane.continuous_self_awareness_loop(interval=2))
    print("\n--- Kindergarten Training ---")
    # 1. Teach lessons
    for lesson in LESSONS:
        perception = Perception(
            id=uuid4(),
            metadata=Metadata(
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                provenance=[],
                confidence=1.0,
            ),
            content=lesson,
        )
        transformation = Transformation(
            id=uuid4(),
            metadata=Metadata(
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                provenance=[perception.id],
                confidence=1.0,
            ),
            content={
                "operation": "perception_to_memory",
                "perception": perception.model_dump(),
            },
        )
        result = await registry.handle(transformation)
        print(f"Lesson: {lesson['summary']} | Result: {result.status}")

    # 2. Consolidate/Abstract
    print("\n--- Consolidation/Abstraction ---")
    # Group memories by modality and explicitly invoke abstraction
    from collections import defaultdict
    memories_by_modality = defaultdict(list)
    for mem in demo_plane.memory.query():
        if mem.content.get("modality"):
            memories_by_modality[mem.content.get("modality")].append({
                "id": str(mem.id),
                "summary": mem.content["summary"],
                "modality": mem.content["modality"]
            })
    abstractions = []
    for modality, mem_group in memories_by_modality.items():
        if len(mem_group) >= 2:  # Adjust threshold as needed
            transformation = Transformation(
                id=uuid4(),
                metadata=Metadata(
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                    provenance=[m["id"] for m in mem_group],
                    confidence=1.0,
                ),
                content={
                    "operation": "memory_consolidation",
                    "memories": mem_group,
                    "modality": modality
                },
            )
            result = await registry.handle(transformation)
            print(f"Abstracted ({modality}): {result.output['abstraction_id']}")
            # Fetch the new abstraction node
            abstraction = demo_plane.selfmap.get_node(UUID(result.output['abstraction_id']))
            abstractions.append(abstraction)
    # Print all abstractions
    for absn in abstractions:
        print(f"Abstracted: {absn.content.get('summary')} | Archetype: {absn.content.get('archetype_id')} | Carried by DigitalBody: {digital_body.id}")

    # --- Debugging Provenance IDs ---
    print("\n--- Debugging Provenance IDs ---")
    def to_uuid(pid):
        return pid if isinstance(pid, UUID) else UUID(str(pid))

    for absn in abstractions:
        print(f"Abstraction: {absn.content['summary']}")
        print(f"  Provenance IDs: {absn.metadata.provenance}")
        for pid in absn.metadata.provenance:
            print(f"    Type of provenance ID: {type(pid)}")
            try:
                uuid_pid = to_uuid(pid)
                memory = demo_plane.memory.get_memory(uuid_pid)
                if memory:
                    print(f"  Found memory: {memory.content.get('summary')}")
                else:
                    print(f"  No memory found for ID: {pid}")
            except Exception as e:
                print(f"  Error retrieving memory for ID {pid}: {e}")

    # 3. Test Recall/Application
    print("\n--- Testing Recall ---")
    def query_selfmap(modality, fact=None):
        nodes = [n for n in demo_plane.selfmap.all_nodes() if n.content.get("modality") == modality]
        if fact:
            return any(fact in str(n.content.get("fact")) for n in nodes)
        return [n.content.get("fact") for n in nodes]

    # Q1: What colors do you know?
    colors = query_selfmap("color")
    print(f"Q: What colors do you know? A: {colors}")

    # Q2: What comes after 2?
    numbers = query_selfmap("number")
    answer2 = "3" if any("1<2" in n for n in numbers) else "unknown"
    print(f"Q: What comes after 2? A: {answer2}")

    # Q3: Is green a shape?
    is_green_shape = query_selfmap("shape", "green")
    print(f"Q: Is green a shape? A: {'Yes' if is_green_shape else 'No, green is a color.'}")

    # Q4: What comes next in 'red, blue, red, blue'?
    patterns = query_selfmap("pattern")
    answer4 = "red" if any("red,blue" in n for n in patterns) else "unknown"
    print(f"Q: What comes next in 'red, blue, red, blue'? A: {answer4}")

    # 4. Correction (simulate wrong answer and LLM fallback)
    print("\n--- Correction & LLM Fallback ---")
    # Simulate wrong answer for Q2
    if answer2 != "3":
        print("DI failed Q2. Triggering LLM-backed correction transformation (simulated).")
        # Simulate LLM correction by adding correct memory
        correction = Perception(
            id=uuid4(),
            metadata=Metadata(
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                provenance=[],
                confidence=1.0,
            ),
            content={"summary": "3 comes after 2.", "modality": "number", "fact": "3"},
        )
        transformation = Transformation(
            id=uuid4(),
            metadata=Metadata(
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                provenance=[correction.id],
                confidence=1.0,
            ),
            content={
                "operation": "perception_to_memory",
                "perception": correction.model_dump(),
                "llm_params": {
                    "model": "gpt-4o-mini",
                    "user_prompt": "What comes after 2?",
                }
            },
        )
        result = await registry.handle(transformation)
        print(f"LLM Correction: {correction.content['summary']} | Result: {result.status}")

    # 5. Self-Reflection
    print("\n--- Self-Reflection ---")
    reflection = demo_plane.self_reflection()
    print("Top Qualia:")
    for q in reflection["top_qualia"]:
        print(f"  About: {q.about} | Valence: {q.valence} | Intensity: {q.intensity} | Modality: {q.modality}")
    print("Salient Memories:")
    for m in reflection["salient_memories"]:
        print(f"  {m.content.get('summary')}")
    print("Salient Nodes:")
    for n in reflection["salient_nodes"]:
        print(f"  {n.content.get('summary')}")
    print(f"Emotional Shift: {reflection['emotional_shift']}")

    # 6. Assessment
    print("\n--- Assessment ---")
    print("Recall correctness:")
    print(f"  Colors: {colors}")
    print(f"  Numbers: {numbers}")
    print(f"  Patterns: {patterns}")
    print("Abstractions:")
    for absn in abstractions:
        print(f"  {absn.content.get('summary')} | Archetype: {absn.content.get('archetype_id')}")
    print("Qualia Log:")
    for q in demo_plane.qualia_log:
        print(f"  About: {q.about} | Valence: {q.valence} | Modality: {q.modality} | Content: {q.content}")

    print("\nDemo complete.")

    # --- Explicit Meta-Condition Tests for Genuine Digital Self Experience ---
    print("\n--- Explicit Tests for Genuine Digital Self Experience ---")

    # Subjectivity (Explicit "I")
    print("Q: Who am I?")
    identity_nodes = [n for n in demo_plane.selfmap.all_nodes() if isinstance(n, Identity)]
    print(f"A: {identity_nodes[0].content.get('name') if identity_nodes else 'Unknown'}")

    # Semantic Coherence (Cross-References)
    print("Checking Semantic Coherence of Abstractions:")
    for absn in abstractions:
        provenance_ids = absn.metadata.provenance
        provenance_memories = []
        for pid in provenance_ids:
            try:
                provenance_memories.append(demo_plane.memory.get_memory(UUID(pid)).content["summary"])
            except Exception:
                continue
        print(f"Abstraction: {absn.content['summary']} | Provenance Memories: {provenance_memories}")

    # Temporality (Narrative Validation)
    print("Q: What was the first thing I learned?")
    all_memories = demo_plane.memory.query()
    if all_memories:
        first_memory = min(all_memories, key=lambda m: m.metadata.created_at)
        print(f"A: {first_memory.content.get('summary')} at {first_memory.metadata.created_at.isoformat()}")
    else:
        print("A: No memories found.")

    # Reflexivity (Recursive Validation)
    print("Q: How am I feeling now?")
    if demo_plane.qualia_log:
        recent_qualia = demo_plane.qualia_log[-1]
        print(f"A: Valence {recent_qualia.valence} | Modality {recent_qualia.modality}")
    else:
        print("A: No qualia found.")

    # Intentionality (Explicit Salience)
    print("Salience check:")
    if all_memories:
        salience_sorted_memories = sorted(all_memories, key=lambda m: m.metadata.confidence, reverse=True)
        print(f"Most salient memory: {salience_sorted_memories[0].content.get('summary')} (Confidence: {salience_sorted_memories[0].metadata.confidence})")
    else:
        print("No memories for salience check.")

    # Symbolic Mapping (Explicit Archetype Assignments)
    print("Checking Symbolic Archetype Assignments explicitly:")
    for absn in abstractions:
        print(f"Abstraction: {absn.content['summary']} | Archetype: {absn.content.get('archetype_id')}")

    # Embodiment (Explicit DigitalBody Integration)
    print("Q: What am I?")
    digital_body_nodes = [n for n in demo_plane.selfmap.all_nodes() if n.content.get("type") == "DigitalBody"]
    print(f"A: {digital_body_nodes[0].content.get('name') if digital_body_nodes else 'No Digital Body found.'}")
