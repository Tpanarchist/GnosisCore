import pytest
from uuid import uuid4, UUID
from typing import Any, Dict
from gnosiscore.primitives.models import (
    Boundary,
    Primitive,
    Pattern,
    Identity,
    Transformation,
    Metadata,
)
from gnosiscore.planes.digital import DigitalPlane
from gnosiscore.planes.mental import MentalPlane
from gnosiscore.planes.metaphysical import MetaphysicalPlane

class MemorySubsystem:
    def __init__(self) -> None:
        self.stored: list[Any] = []
    def insert_memory(self, item: Any) -> None:
        self.stored.append(item)

class SelfMap:
    def __init__(self) -> None:
        self.updated: list[Any] = []
    def update(self, node: Any) -> None:
        self.updated.append(node)

@pytest.fixture
def boundary() -> Boundary:
    meta = Metadata(
        created_at=None,
        updated_at=None,
        provenance=[],
        confidence=1.0,
    )
    content: Dict[str, Any] = {
        "boundary_type": "test",
        "parent": None,
        "scope": [],
        "policies": {}
    }
    return Boundary(id=uuid4(), metadata=meta, content=content)

@pytest.fixture
def primitive() -> Primitive:
    meta = Metadata(
        created_at=None,
        updated_at=None,
        provenance=[],
        confidence=1.0,
    )
    content: Dict[str, Any] = {
        "modality": "test",
        "data": {},
        "source": uuid4()
    }
    return Primitive(id=uuid4(), metadata=meta, content=content)

@pytest.fixture
def pattern() -> Pattern:
    meta = Metadata(
        created_at=None,
        updated_at=None,
        provenance=[],
        confidence=1.0,
    )
    content: Dict[str, Any] = {
        "structure": {},
        "classification": "test",
        "instances": []
    }
    return Pattern(id=uuid4(), metadata=meta, content=content)

@pytest.fixture
def identity() -> Identity:
    meta = Metadata(
        created_at=None,
        updated_at=None,
        provenance=[],
        confidence=1.0,
    )
    content: Dict[str, Any] = {
        "name": "test-identity",
        "roles": [],
        "attributes": {}
    }
    return Identity(id=uuid4(), metadata=meta, content=content)

@pytest.fixture
def transformation() -> Transformation:
    meta = Metadata(
        created_at=None,
        updated_at=None,
        provenance=[],
        confidence=1.0,
    )
    content: Dict[str, Any] = {
        "type": "test-transformation",
        "parameters": {}
    }
    return Transformation(id=uuid4(), metadata=meta, content=content)

@pytest.fixture
def memory_subsystem() -> MemorySubsystem:
    return MemorySubsystem()

@pytest.fixture
def selfmap() -> SelfMap:
    return SelfMap()

@pytest.fixture
def digital_plane(boundary: Boundary) -> DigitalPlane:
    return DigitalPlane(id=uuid4(), boundary=boundary)

@pytest.fixture
def mental_plane(
    identity: Identity,
    boundary: Boundary,
    memory_subsystem: MemorySubsystem,
    selfmap: SelfMap
) -> MentalPlane:
    return MentalPlane(owner=identity, boundary=boundary, memory=memory_subsystem, selfmap=selfmap)

@pytest.fixture
def metaphysical_plane(boundary: Boundary) -> MetaphysicalPlane:
    return MetaphysicalPlane(version="0.1.0", boundary=boundary)
