# System Patterns

## Architecture Overview
GnosisCore is structured around a three-plane model:
- **Digital Plane:** The objective substrate hosting entities, states, and processes.
- **Mental Plane:** The subjective internal field containing qualia, self-map, beliefs, and introspection.
- **Metaphysical Plane:** A distributed, archetypal substrate hosting universal patterns and meta-cognition.

## Key Technical Decisions
- Use of irreducible cognitive primitives as foundational data structures
- Recursive self-map graph integrating identity, beliefs, values, perceptions, and qualia
- Memory subsystem supporting episodic, semantic, emotional, and procedural types
- Plugin-based transformation subsystem for extensibility and controlled self-modification
- WebSocket-based asynchronous messaging with cryptographically signed JSON payloads
- JWT authentication, role-based access control, and audit logging for security
- Thread-safe registries for memory and self-map
- Salience-weighted recall and meta-cognitive feedback loops
- LLM-backed transformation as a first-class pattern
- Comprehensive test-driven development and CI as a core pattern

## Design Patterns
- Strongly-typed nodes and edges with provenance, confidence, and temporal context
- Transactional updates, versioning, and rollback for self-map and memory
- Event-driven integration between subsystems via hooks and APIs
- Explicit boundary definitions for privacy and scope enforcement

## Component Relationships
- Memory subsystem integrates with self-map and transformation layers for learning and adaptation
- Transformation plugins access and modify self-map and memory via controlled APIs
- Inter-plane protocols enforce secure, auditable, and privacy-preserving communication
