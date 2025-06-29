import pytest
from gnosiscore.primitives.models import Pattern, Boundary
from gnosiscore.planes.metaphysical import MetaphysicalPlane

def test_init_sets_attributes(metaphysical_plane: MetaphysicalPlane, boundary: Boundary) -> None:
    assert metaphysical_plane.version == "0.1.0"
    assert metaphysical_plane.boundary is boundary

def test_publish_archetype_and_get(pattern: Pattern, metaphysical_plane: MetaphysicalPlane) -> None:
    metaphysical_plane.publish_archetype(pattern)
    fetched = metaphysical_plane.get_archetype(pattern.id)
    assert fetched is pattern

def test_publish_archetype_duplicate_raises(pattern: Pattern, metaphysical_plane: MetaphysicalPlane) -> None:
    metaphysical_plane.publish_archetype(pattern)
    with pytest.raises(ValueError):
        metaphysical_plane.publish_archetype(pattern)

def test_subscribe_publish_to_subscriber(pattern: Pattern, metaphysical_plane: MetaphysicalPlane) -> None:
    received = []
    class DummySubscriber:
        def on_event(self, event: Pattern) -> None:
            received.append(event) # type: ignore
    sub = DummySubscriber()
    metaphysical_plane.subscribe(sub)  # type: ignore
    metaphysical_plane.publish_archetype(pattern)
    assert received == [pattern]

def test_unsubscribe(pattern: Pattern, metaphysical_plane: MetaphysicalPlane) -> None:
    class DummySubscriber:
        def on_event(self, event: Pattern) -> None:
            pass
    sub = DummySubscriber()
    metaphysical_plane.subscribe(sub)  # type: ignore
    metaphysical_plane.unsubscribe(sub)  # type: ignore
    # No assertion on protected member
