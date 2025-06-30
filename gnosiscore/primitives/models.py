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
from typing import Any, Dict, ClassVar
from typing import Literal
from uuid import UUID
from datetime import datetime

class Metadata(BaseModel):
    """Metadata for all primitives, including provenance and confidence."""
    created_at: datetime = Field(..., description="Timestamp of creation")
    updated_at: datetime = Field(..., description="Timestamp of last update")
    provenance: list[UUID] = Field(default_factory=list, description="References for provenance") # type: ignore
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

from typing import Optional, Dict, Union
class Attention(Primitive):
    """Primitive representing an attention (focus) event."""
    type: ClassVar[Literal["Attention"]] = "Attention"
    subject: Union[UUID, str] = Field(..., description="What is attending (agent/process ID)")
    object: Union[UUID, str] = Field(..., description="What is attended (entity, pattern, memory, etc.)")
    intensity: float = Field(1.0, ge=0.0, le=1.0, description="Degree of focus (0.0–1.0)")
    duration: Optional[float] = Field(None, description="Duration of attention in seconds")

class Qualia(Primitive):
    """Primitive representing a unit of subjective experience."""
    type: ClassVar[Literal["Qualia"]] = "Qualia"
    valence: float = Field(..., ge=-1.0, le=1.0, description="Subjective value: -1.0 (pain) to 1.0 (pleasure)")
    intensity: float = Field(..., ge=0.0, le=1.0, description="Intensity of experience (0.0–1.0)")
    modality: str = Field(..., description="Modality (e.g., 'visual', 'emotional', etc.)")
    about: Union[UUID, str] = Field(..., description="What the qualia is about (memory, entity, etc.)")

class LLMParams(BaseModel):
    model: str = Field(..., description="Model name, e.g. 'gpt-4o-mini'")
    system_prompt: Optional[str] = None
    user_prompt: str
    temperature: Optional[float] = 0.2
    max_tokens: Optional[int] = 256
    top_p: Optional[float] = None
    stop: Optional[str] = None
    extra_params: Dict[str, Any] = Field(default_factory=dict)

class Transformation(Primitive):
    """Primitive representing a transformation or operation.

    content fields:
        - operation: str (e.g., "add_node", "update_value", "remove_entity")
        - target: UUID or list[UUID] (references affected)
        - parameters: dict (arbitrary operation details)
        - llm_params: Optional[LLMParams] (OpenAI API config, or None for local logic)
        - (optional: initiator, provenance, timestamp, etc.)
    """
    type: ClassVar[Literal["Transformation"]] = "Transformation"

    @classmethod
    def create(
        cls,
        id: UUID,
        metadata: Metadata,
        operation: str,
        target: Any,
        parameters: dict[str, Any],
        llm_params: Optional["LLMParams"] = None,
        **kwargs: Any
    ):
        content: dict[str, Any] = {
            "operation": operation,
            "target": target,
            "parameters": parameters,
        }
        if llm_params is not None:
            content["llm_params"] = llm_params.model_dump()
        content.update(kwargs)
        return cls(id=id, metadata=metadata, content=content)

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

from pydantic import ConfigDict

class Intent(BaseModel):
    """Intent: An immutable submission of a Transformation for execution."""
    id: UUID = Field(..., description="Unique identifier for the intent")
    transformation: Transformation = Field(..., description="Transformation to execute")
    submitted_at: datetime = Field(..., description="Submission timestamp")
    version: int = Field(1, description="Version number (incremented for new intents)")

    model_config = ConfigDict(frozen=True)

class Result(BaseModel):
    """Result: Outcome of an intent execution."""
    id: UUID = Field(..., description="Unique identifier for the result")
    intent_id: UUID = Field(..., description="UUID of the submitted intent/transformation")
    status: Literal["success", "failure", "pending"] = Field(..., description="Result status")
    output: dict[str, Any] | None = Field(None, description="Result data, new Primitives, logs")
    error: str | None = Field(None, description="Error message if failed")
    timestamp: datetime = Field(..., description="Completion timestamp")

# Example usage:
# from gnosiscore.primitives.models import Perception
# perception = Perception(
#     id=UUID("123e4567-e89b-12d3-a456-426614174000"),
#     metadata=Metadata(created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
#     content={"modality": "visual", "data": {"pixels": [...]}, "source": UUID("...")}
# )
