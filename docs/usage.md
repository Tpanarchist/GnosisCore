# Usage Examples

This guide provides practical examples for using GnosisCore components and patterns.

## Basic Setup

```python
from gnosiscore.patterns.memory import MemoryPattern
from gnosiscore.patterns.awareness import AwarenessPattern
from gnosiscore.flows.flow_pattern import FlowPattern

# Initialize patterns
memory = MemoryPattern()
awareness = AwarenessPattern()

# Compose a flow
flow = FlowPattern(patterns=[memory, awareness])

# Run a step
flow.tick()
```

## Using the RealityGraph

```python
from gnosiscore.core.reality_graph import RealityGraph

graph = RealityGraph()
entity_id = graph.add_entity({"name": "Agent1"})
graph.set_relation(entity_id, "role", "agent")
```

## Integrating a Transformer Model

```python
from gnosiscore.llm.transformer import TransformerModel

model = TransformerModel(model_name="gpt-3")
response = model.generate("What is GnosisCore?")
print(response)
```

## Persistence Example

```python
from gnosiscore.patterns.persistence import PersistencePattern

persistence = PersistencePattern(filepath="memory.db")
persistence.save({"key": "value"})
data = persistence.load()
```

## Running the Demo

```sh
python gnosiscore/demo.py
```

---

For more advanced usage, see the source code and [Module Reference](modules.md).
