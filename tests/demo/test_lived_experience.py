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
from gnosiscore.primitives.subject import Subject
from gnosiscore.memory.subsystem import MemorySubsystem
from gnosiscore.selfmap.map import SelfMap
from gnosiscore.transformation.awareness import Awareness
from gnosiscore.transformation.observer import Observer
from gnosiscore.transformation.mental import Mental
from gnosiscore.transformation.digital_self import DigitalSelf
from gnosiscore.transformation.registry import TransformationHandlerRegistry
import asyncio

# --- Initialization ---

memory = MemorySubsystem()
selfmap = SelfMap()
subject = Subject()
selfmap.add_node(subject)

# --- Demo Parameters ---
CYCLES = 7
random.seed(42)

# --- Triad Setup ---
memory = MemorySubsystem()
selfmap = SelfMap()
subject = Subject()
selfmap.add_node(subject)

# Instantiate transformation registry
registry = TransformationHandlerRegistry()

# Instantiate triad modules with registry
awareness = Awareness(memory=memory, observer=None, subject=subject, registry=registry)
observer = Observer(memory=memory, awareness=awareness, subject=subject, registry=registry)
awareness.observer = observer  # circular reference
mental = Mental(memory=memory, subject=subject, registry=registry, selfmap=selfmap, boundary=None)

# Orchestrator
digital_self = DigitalSelf(awareness=awareness, observer=observer, mental=mental, subject=subject)

# --- Demo Loop ---
import pytest

async def main():
    tick_outputs = []
    key_fields = ["thought", "emotion", "intention", "actions"]

    import json

    def extract_fields(result_content):
        # Extract LLM JSON from nested structure
        llm_resp = result_content.get("llm_response", {})
        choices = llm_resp.get("choices", [])
        if choices:
            msg = choices[0].get("message", {})
            content = msg.get("content", "")
            # Remove markdown code block if present
            if content.startswith("```json"):
                content = content.split("```json", 1)[1]
            if content.startswith("\n"):
                content = content[1:]
            if content.endswith("```"):
                content = content[:-3]
            try:
                parsed = json.loads(content)
                return {k: parsed.get(k) for k in ["thought", "emotion", "intention", "actions"]}
            except Exception:
                return {"thought": None, "emotion": None, "intention": None, "actions": None}
        return {"thought": None, "emotion": None, "intention": None, "actions": None}

    extracted_outputs = []

    for cycle in range(1, CYCLES + 1):
        print(f"\n--- Cycle {cycle} ---")
        result = await digital_self.tick()
        print(f"Tick result: {result}")
        fields = extract_fields(result.content)
        extracted_outputs.append(fields)

    # --- Assert: At least one key field changes across cycles ---
    for field in key_fields:
        values = [str(output.get(field)) for output in extracted_outputs]
        assert len(set(values)) > 1, f"Field '{field}' did not change across cycles: {values}"

    # --- Subject Self-Report ---
    print("\n=== Subject Self-Report ===")
    if hasattr(subject, "self_report"):
        report = subject.self_report(memory)
        print(report)
        assert report is not None and str(report).strip() != "", "Subject self-report is empty"
    else:
        print("Subject self-report not implemented.")
        assert False, "Subject self-report not implemented."

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
