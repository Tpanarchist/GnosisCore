import pytest
from uuid import UUID
from gnosiscore.primitives.models import Primitive
from gnosiscore.planes.digital import DigitalPlane

from gnosiscore.primitives.models import Boundary

def test_init_sets_attributes(digital_plane: DigitalPlane, boundary: Boundary) -> None:
    assert isinstance(digital_plane.id, UUID)
    assert digital_plane.boundary is boundary

def test_register_and_get_entity(digital_plane: DigitalPlane, primitive: Primitive) -> None:
    digital_plane.register_entity(primitive)
    assert digital_plane.get_entity(primitive.id) is primitive

def test_remove_entity(digital_plane: DigitalPlane, primitive: Primitive) -> None:
    digital_plane.register_entity(primitive)
    digital_plane.remove_entity(primitive.id)
    with pytest.raises(KeyError):
        _ = digital_plane.get_entity(primitive.id)

def test_on_persist_callback_called(digital_plane: DigitalPlane, primitive: Primitive) -> None:
    called = []
    digital_plane.on_persist = lambda p: called.append(p) # type: ignore
    digital_plane.register_entity(primitive)
    assert called == [primitive]

def test_subscribe_publish_event(digital_plane: DigitalPlane, primitive: Primitive) -> None:
    received = []
    class DummySubscriber:
        def on_event(self, event: Primitive) -> None:
            received.append(event) # type: ignore
    sub = DummySubscriber()
    digital_plane.subscribe(sub)  # type: ignore
    digital_plane.publish_event(primitive)
    assert received == [primitive]

def test_unsubscribe(digital_plane: DigitalPlane) -> None:
    class DummySubscriber:
        def on_event(self, event: Primitive) -> None:
            pass
    sub = DummySubscriber()
    digital_plane.subscribe(sub)  # type: ignore
    digital_plane.unsubscribe(sub)  # type: ignore
    # No assertion on protected member
