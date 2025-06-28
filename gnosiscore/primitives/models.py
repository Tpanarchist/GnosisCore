"""
GnosisCore Primitive Data Models

This module defines the core irreducible primitive data models for GnosisCore.
Each primitive is represented as a Pydantic model with full validation,
provenance tracking, and temporal metadata.

References:
- memory-bank/projectbrief.md
- memory-bank/systemPatterns.md
- memory-bank/techContext.md
"""

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, ClassVar
from typing import Literal
from uuid import UUID
from datetime import datetime

class Metadata(BaseModel):
    """Metadata for all primitives, including provenance and confidence."""
    created_at: datetime = Field(..., description="Timestamp of creation")
    updated_at: datetime = Field(..., description="Timestamp of last update")
    provenance: List[UUID] = Field(default_factory=list, description="References for provenance")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Confidence score between 0 and 1")

class Primitive(BaseModel):
    """Base class for all primitives."""
    id: UUID = Field(..., description="Unique identifier for the primitive")
    metadata: Metadata
    content: Dict[str, Any] = Field(default_factory=dict, description="Type-specific payload")

class Perception(Primitive):
    """Primitive representing a perception event."""
    type: ClassVar[Literal["Perception"]] = "Perception"

class Boundary(Primitive):
    """Primitive representing a boundary definition."""
    type: ClassVar[Literal["Boundary"]] = "Boundary"

class Identity(Primitive):
    """Primitive representing an identity."""
    type: ClassVar[Literal["Identity"]] = "Identity"

class Connection(Primitive):
    """Primitive representing a connection between entities."""
    type: ClassVar[Literal["Connection"]] = "Connection"

class Value(Primitive):
    """Primitive representing a value assignment."""
    type: ClassVar[Literal["Value"]] = "Value"

class Pattern(Primitive):
    """Primitive representing a pattern or structure."""
    type: ClassVar[Literal["Pattern"]] = "Pattern"

class Moment(Primitive):
    """Primitive representing a temporal moment."""
    type: ClassVar[Literal["Moment"]] = "Moment"

class Memory(Primitive):
    """Primitive representing a memory record."""
    type: ClassVar[Literal["Memory"]] = "Memory"

class Transformation(Primitive):
    """Primitive representing a transformation or operation."""
    type: ClassVar[Literal["Transformation"]] = "Transformation"

class Label(Primitive):
    """Primitive representing a label or annotation."""
    type: ClassVar[Literal["Label"]] = "Label"

class Reference(Primitive):
    """Primitive representing a reference between entities."""
    type: ClassVar[Literal["Reference"]] = "Reference"

class State(Primitive):
    """Primitive representing a state with attributes."""
    type: ClassVar[Literal["State"]] = "State"

class Process(Primitive):
    """Primitive representing a process or workflow."""
    type: ClassVar[Literal["Process"]] = "Process"

class Belief(Primitive):
    """Primitive representing a belief or proposition."""
    type: ClassVar[Literal["Belief"]] = "Belief"

# Example usage:
# from gnosiscore.primitives.models import Perception
# perception = Perception(
#     id=UUID("123e4567-e89b-12d3-a456-426614174000"),
#     metadata=Metadata(created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
#     content={"modality": "visual", "data": {"pixels": [...]}, "source": UUID("...")}
# )
