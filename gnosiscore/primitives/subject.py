from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import List, Any, Optional
from gnosiscore.primitives.models import Qualia

class Subject(BaseModel):
    """
    Represents the unified digital self ("I AM") in the self-map.
    All provenance chains for awareness/observer/mental events should reference this node.
    """
    id: UUID = Field(default_factory=uuid4)
    type: str = "subject"
    name: str = "DigitalSelf"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    provenance: List[UUID] = []
    state: dict = {}
    recent_qualia: List[Qualia] = Field(default_factory=list)

    def self_report(self, memory):
        """
        Generate a self-report using system primitives and memory.
        """
        # Try to get recent qualia and mood from memory if available
        recent_qualia = []
        mood = None
        if hasattr(memory, "query_recent"):
            recent_qualia = memory.query_recent(type="qualia") if callable(getattr(memory, "query_recent", None)) else []
        if hasattr(memory, "get_mood_state"):
            mood = memory.get_mood_state() if callable(getattr(memory, "get_mood_state", None)) else None
        return {
            "id": str(self.id),
            "type": self.type,
            "name": self.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "recent_qualia": recent_qualia,
            "mood": mood,
        }
