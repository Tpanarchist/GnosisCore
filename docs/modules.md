# Module Reference

This reference describes the main modules and files in GnosisCore, summarizing their purpose and key components.

## gnosiscore/core/

- **field.py**: Core data field abstractions.
- **delta.py**: Change tracking and delta computation utilities.
- **reality_graph.py**: Implements the RealityGraph, a central structure for managing entities and their relationships.
- **transformer_iface.py**: Interface definitions for transformer-based models.

## gnosiscore/patterns/

- **base.py**: Base class for all patterns.
- **memory.py**: Implements memory pattern for storing and recalling information.
- **awareness.py**: Pattern for awareness and context tracking.
- **persistence.py**: Persistence mechanisms for saving and loading state.
- **representation.py**: Handles data and knowledge representation.
- **imprint.py**: Pattern for imprinting knowledge or data.
- **formulation.py**: Pattern for formulating new knowledge or responses.
- **origin.py**: Handles origin tracking for data/patterns.
- **proliferation.py**: Pattern for proliferating knowledge or data.
- **pruning.py**: Pattern for pruning or forgetting information.
- **pulse.py**: Pattern for periodic or event-driven actions.

## gnosiscore/flows/

- **flow_pattern.py**: Defines flow composition and orchestration logic.

## gnosiscore/forms/

- **form_base.py**: Base abstractions for structured data forms.

## gnosiscore/llm/

- **transformer.py**: Integration and interface for transformer-based LLMs.

## gnosiscore/demo.py

- Example script demonstrating usage of core patterns and flows.

## configs/

- **tree_of_patterns.yml**: Example configuration for pattern trees and system setup.

## tests/

- **test_tick.py**: Unit tests for core tick/step logic.

---

For more details on each module, see the source code and [Architecture & Design Patterns](architecture.md).
