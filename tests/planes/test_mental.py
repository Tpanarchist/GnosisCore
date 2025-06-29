import pytest
from gnosiscore.primitives.models import Primitive, Transformation
from gnosiscore.planes.mental import MentalPlane, Qualia, Result

def test_on_event_updates_memory_and_selfmap(
    mental_plane: MentalPlane, primitive: Primitive
) -> None:
    mental_plane.on_event(primitive)
    assert primitive in mental_plane.memory.stored
    assert primitive in mental_plane.selfmap.updated

def test_submit_intent_returns_result(
    mental_plane: MentalPlane, transformation: Transformation
) -> None:
    result = mental_plane.submit_intent(transformation)
    assert isinstance(result, Result)

def test_introspect_returns_qualia(
    mental_plane: MentalPlane
) -> None:
    q = mental_plane.introspect()
    assert isinstance(q, Qualia)

def test_update_memory_and_selfmap_helpers(
    mental_plane: MentalPlane, primitive: Primitive
) -> None:
    mental_plane.update_memory(primitive)
    assert primitive in mental_plane.memory.stored
    mental_plane.update_selfmap(primitive)
    assert primitive in mental_plane.selfmap.updated
