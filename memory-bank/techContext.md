# Technical Context

## Technologies Used
- Programming Languages: Python (core logic), TypeScript/JavaScript (APIs, integration)
- Data Formats: JSON, YAML (for schemas and messaging)
- Databases: Document and graph databases for memory and self-map storage
- Communication: WebSocket for asynchronous messaging
- Security: JWT authentication, cryptographic signing, role-based access control
- Pydantic for all models and validation
- OpenAI API integration for LLM-backed transformations

## Development Setup
- Modular monorepo structure with clear separation of subsystems
- Automated testing and continuous integration pipelines
- Plugin registry for transformation subsystem extensibility
- API endpoints for subsystem integration and external access
- Pytest for all tests, with ≥90% coverage goal
- Flake8 and mypy for linting and static analysis

## Technical Constraints
- Strict boundary enforcement between planes for privacy and integrity
- All inter-plane messages must be cryptographically signed and auditable
- Memory and self-map updates must support transactional integrity and rollback
- Subsystems must be extensible and support versioning

## Dependencies
- Python 3.11+ (core framework)
- Node.js (for integration utilities and APIs)
- WebSocket libraries (e.g., websockets, socket.io)
- JWT libraries for authentication
- Graph and document database drivers (e.g., Neo4j, MongoDB)
- Pydantic
- Pytest
- Flake8, mypy
- OpenAI API client (for LLM integration)
