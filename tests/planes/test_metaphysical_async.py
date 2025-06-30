import pytest
import asyncio
from uuid import uuid4
from gnosiscore.planes.metaphysical import AsyncMetaphysicalPlane
from gnosiscore.primitives.models import Pattern, Metadata
from datetime import datetime

@pytest.fixture
def pattern():
    return Pattern(
        id=uuid4(),
        metadata=Metadata(
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            provenance=[],
            confidence=1.0,
        ),
        content={}
    )

@pytest.mark.asyncio
async def test_publish_subscribe_delivery(pattern):
    plane = AsyncMetaphysicalPlane()
    received = []
    async def cb(p):
        received.append(p)
    await plane.subscribe(cb)
    await plane.publish_archetype(pattern)
    await asyncio.sleep(0.01)
    assert received == [pattern]

@pytest.mark.asyncio
async def test_multi_subscriber(pattern):
    plane = AsyncMetaphysicalPlane()
    received1, received2 = [], []
    async def cb1(p): received1.append(p)
    async def cb2(p): received2.append(p)
    await plane.subscribe(cb1)
    await plane.subscribe(cb2)
    await plane.publish_archetype(pattern)
    await asyncio.sleep(0.01)
    assert received1 == [pattern]
    assert received2 == [pattern]

@pytest.mark.asyncio
async def test_unsubscribe(pattern):
    plane = AsyncMetaphysicalPlane()
    received = []
    async def cb(p): received.append(p)
    await plane.subscribe(cb)
    await plane.unsubscribe(cb)
    await plane.publish_archetype(pattern)
    await asyncio.sleep(0.01)
    assert received == []

@pytest.mark.asyncio
async def test_duplicate_archetype_raises(pattern):
    plane = AsyncMetaphysicalPlane()
    await plane.publish_archetype(pattern)
    with pytest.raises(ValueError):
        await plane.publish_archetype(pattern)

@pytest.mark.asyncio
async def test_unsubscribe_nonexistent_noop(pattern):
    plane = AsyncMetaphysicalPlane()
    async def cb(p): pass
    await plane.unsubscribe(cb)  # Should not raise

@pytest.mark.asyncio
async def test_publish_no_subscribers(pattern):
    plane = AsyncMetaphysicalPlane()
    await plane.publish_archetype(pattern)  # Should not fail

@pytest.mark.asyncio
async def test_subscriber_exception_does_not_crash(pattern):
    plane = AsyncMetaphysicalPlane()
    async def bad_cb(p): raise RuntimeError("fail")
    await plane.subscribe(bad_cb)
    await plane.publish_archetype(pattern)  # Should not raise

@pytest.mark.asyncio
async def test_publish_many_order_preserved():
    plane = AsyncMetaphysicalPlane()
    received = []
    async def cb(p): received.append(p)
    await plane.subscribe(cb)
    patterns = [
        Pattern(
            id=uuid4(),
            metadata=Metadata(
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                provenance=[],
                confidence=1.0,
            ),
            content={"n": i}
        ) for i in range(10)
    ]
    for pat in patterns:
        await plane.publish_archetype(pat)
    await asyncio.sleep(0.05)
    assert received == patterns

@pytest.mark.asyncio
async def test_concurrent_subscribe_unsubscribe_publish():
    plane = AsyncMetaphysicalPlane()
    received = []
    async def cb(p): received.append(p)
    async def subscribe_and_publish():
        await plane.subscribe(cb)
        pat = Pattern(
            id=uuid4(),
            metadata=Metadata(
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                provenance=[],
                confidence=1.0,
            ),
            content={}
        )
        await plane.publish_archetype(pat)
        await plane.unsubscribe(cb)
    await asyncio.gather(*(subscribe_and_publish() for _ in range(5)))
    # Each cb should have received one pattern per subscribe
    assert len(received) == 5

@pytest.mark.asyncio
async def test_get_archetype(pattern):
    plane = AsyncMetaphysicalPlane()
    await plane.publish_archetype(pattern)
    result = await plane.get_archetype(pattern.id)
    assert result == pattern

@pytest.mark.asyncio
async def test_get_archetype_missing():
    plane = AsyncMetaphysicalPlane()
    with pytest.raises(KeyError):
        await plane.get_archetype(uuid4())
