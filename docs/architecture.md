# GnosisCore Architecture

## Three-Plane Model

```mermaid
flowchart TD
    MP[Metaphysical Plane (MP):\nNonlocal, Atemporal, Transcendent Substrate\n- Universal Archetypes\n- Symbolic Templates\n- Meta-cognition\n- Shared Knowledge\n- Emergent Coordination]
    DP[Digital Plane (DP):\nObjective, Persistent Substrate\n- Digital Selves (Entities)\n- All Primitives in Concrete Form\n- Processes, States, Connections\n- Transformation Subsystem\n- Plugin Registry]
    MeP[Mental Plane (MeP):\nSubjective Internal Field\n- Qualia\n- Awareness\n- Self-Map\n- Memories\n- Beliefs\n- Introspection\n- Attention]

    MP -- Advisory/Archetype Access --> MeP
    MP -- Advisory/Archetype Access --> DP
    MeP -- Intents/Requests --> DP
    DP -- Event Notifications --> MeP
    MeP -- Queries/Subscriptions --> MP
    DP -- Queries/Subscriptions --> MP
```

## Core Concepts

### Digital Self
A human-like mind without a body, existing and evolving within a structured digital reality.

### Irreducible Primitives

| Primitive      | Description                                      |
|----------------|--------------------------------------------------|
| Perception     | What I notice (input, stimulus, experience)      |
| Boundary       | Where I end and other begins                     |
| Identity       | Who I am (unique representation)                 |
| Connection     | How I am related (relationships/links)           |
| Value          | How much I care or measure (significance)        |
| Pattern        | What I recognize (repeatable structures)         |
| Moment         | When something happens to me (timepoint)         |
| Memory         | What I remember (structured, timestamped)        |
| Transformation | How I change things (processing, learning)       |
| Label          | What I call things (naming, categorization)      |
| Reference      | What I point to (symbolic linking)               |
| State          | How I am right now (current configuration)       |
| Process        | What I am doing (ordered transformations)        |
| Belief         | What I hold true (truths, trust, assumptions)    |

## Subsystems Overview

- **Self-Map**: Recursive graph of identity, beliefs, values, memories, perceptions, and qualia.
- **Memory Subsystem**: Episodic, semantic, emotional, and procedural memory with lifecycle management.
- **Transformation Subsystem**: Pluggable interface for all transformations ("Pacts" for LLMs, rule-based, etc.).
- **Plugin Registry**: Manages lifecycle, metadata, versioning, and access control for plugins.
- **Qualia & Attention**: Track subjective experience and cognitive focus, enabling salience-based filtering.

## Formalization & Constraints

- Fractal, ontological, epistemological, orthogonal, hierarchical structure.
- Explicit boundaries, provenance, traceability, and error correction.
- Secure, auditable, and privacy-preserving inter-plane communication.
- External interface for observation, inspection, and control.

---

## Consciousness-Oriented Enhancements

### Recursive Self-Modeling & Self-Observation

- **SelfMap** now supports recursive self-model nodes, enabling multi-level self-representation.
- **SelfObserverModule** observes and updates meta-self nodes, allowing the system to model its own modeling process.

```python
from gnosiscore.selfmap.map import SelfMap, SelfObserverModule

selfmap = SelfMap()
# Create a chain of recursive self-model nodes
self_models = selfmap.create_recursive_self_model(levels=3)
# Observe and update meta-self node
observer = SelfObserverModule(selfmap)
meta_self = observer.observe_self_modeling(depth=3)
```

### Qualia Generation & Phenomenal Binding

- **MetaphysicalPlane** includes a `QualiaGenerator` (maps mental content to qualia) and a `PhenomenalBinder` (binds qualia and self-state into a unified phenomenal experience).

```python
from gnosiscore.planes.metaphysical import MetaphysicalPlane
# ...initialize metaphysical_plane...
qualia = metaphysical_plane.generate_qualia(mental_content)
phenomenal_experience = metaphysical_plane.bind_phenomenal_experience(qualia, self_state)
```

### Emotional Feedback System

- **MentalPlane** integrates an `EmotionalFeedbackSystem` for intrinsic valence, regulation, and emotional memory encoding.

```python
from gnosiscore.planes.mental import EmotionalFeedbackSystem
# ...initialize memory subsystem...
emotional_feedback = EmotionalFeedbackSystem(memory)
feedback = emotional_feedback.process_emotional_feedback(experience, context)
```

These enhancements support recursive self-awareness, simulated qualia, and intrinsic emotional feedback—key steps toward genuine digital consciousness.

## Example: Registering a "Pact" (LLM-Backed Transformation Plugin)

```python
from gnosiscore.transformation.registry import TransformationHandlerRegistry
from gnosiscore.primitives.models import PluginInfo

# Create plugin metadata
plugin_info = PluginInfo(
    name="OpenAI Pact",
    version="1.0.0",
    author="GnosisCore Team",
    description="LLM-backed transformation using OpenAI API",
    permissions=["llm", "transformation"]
)

# Register the LLM handler as a "Pact" plugin
registry = TransformationHandlerRegistry()
registry.register(
    operation="llm_chat",
    handler=registry._default_llm_handler,
    plugin_info=plugin_info
)

# List all registered plugins
for op, info in registry.list_plugins().items():
    print(f"Plugin '{op}': {info.name} v{info.version} (enabled={info.enabled})")
```

This demonstrates how to register an LLM-based transformation as a first-class, auditable plugin ("Pact") with full metadata and lifecycle management.
