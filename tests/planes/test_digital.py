import pytest
import asyncio
from uuid import uuid4, UUID
from gnosiscore.primitives.models import Primitive, Boundary, Metadata, Intent, Transformation, Result
from gnosiscore.planes.digital import DigitalPlane

@pytest.mark.asyncio
async def test_async_basic_event_loop_dispatch():
    # Setup
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    boundary = Boundary(id=uuid4(), metadata=Metadata(created_at=now, updated_at=now, provenance=[], confidence=1.0), content={})
    plane = DigitalPlane(id=uuid4(), boundary=boundary)
    plane._event_loop_task = asyncio.create_task(plane.event_loop())

    # Dummy handler
    async def handler(transformation):
        return Result(
            id=uuid4(),
            intent_id=transformation.id,
            status="success",
            output={"ok": True},
            error=None,
            timestamp=datetime.now(timezone.utc)
        )
    plane.handler_registry.register("dummy", handler)

    # Create intent
    transformation = Transformation.create(
        id=uuid4(),
        metadata=Metadata(created_at=now, updated_at=now, provenance=[], confidence=1.0),
        operation="dummy",
        target=None,
        parameters={}
    )
    intent = Intent(
        id=uuid4(),
        transformation=transformation,
        submitted_at=datetime.now(timezone.utc),
        version=1
    )

    # Submit and process
    await plane.submit_intent(intent)
    await asyncio.sleep(0.1)  # Let event loop process
    result = plane.poll_result(intent.id)
    assert result is not None
    assert result.status == "success"
    assert result.output == {"ok": True}
    await plane.shutdown()
    if plane._event_loop_task:
        plane._event_loop_task.cancel()
        try:
            await plane._event_loop_task
        except asyncio.CancelledError:
            pass

@pytest.mark.asyncio
async def test_async_callback_delivery():
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    boundary = Boundary(id=uuid4(), metadata=Metadata(created_at=now, updated_at=now, provenance=[], confidence=1.0), content={})
    plane = DigitalPlane(id=uuid4(), boundary=boundary)
    plane._event_loop_task = asyncio.create_task(plane.event_loop())

    async def handler(transformation):
        return Result(
            id=uuid4(),
            intent_id=transformation.id,
            status="success",
            output={"cb": True},
            error=None,
            timestamp=datetime.now(timezone.utc)
        )
    plane.handler_registry.register("cb", handler)

    transformation = Transformation.create(
        id=uuid4(),
        metadata=Metadata(created_at=now, updated_at=now, provenance=[], confidence=1.0),
        operation="cb",
        target=None,
        parameters={}
    )
    intent = Intent(
        id=uuid4(),
        transformation=transformation,
        submitted_at=datetime.now(timezone.utc),
        version=1
    )

    called = []
    async def callback(result):
        called.append(result)

    await plane.submit_intent(intent, callback=callback)
    await asyncio.sleep(0.1)
    assert called
    assert called[0].status == "success"
    await plane.shutdown()
    if plane._event_loop_task:
        plane._event_loop_task.cancel()
        try:
            await plane._event_loop_task
        except asyncio.CancelledError:
            pass

@pytest.mark.asyncio
async def test_async_error_handling():
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    boundary = Boundary(id=uuid4(), metadata=Metadata(created_at=now, updated_at=now, provenance=[], confidence=1.0), content={})
    plane = DigitalPlane(id=uuid4(), boundary=boundary)
    plane._event_loop_task = asyncio.create_task(plane.event_loop())

    async def handler(transformation):
        raise RuntimeError("fail!")
    plane.handler_registry.register("fail", handler)

    transformation = Transformation.create(
        id=uuid4(),
        metadata=Metadata(created_at=now, updated_at=now, provenance=[], confidence=1.0),
        operation="fail",
        target=None,
        parameters={}
    )
    intent = Intent(
        id=uuid4(),
        transformation=transformation,
        submitted_at=datetime.now(timezone.utc),
        version=1
    )

    await plane.submit_intent(intent)
    await asyncio.sleep(0.1)
    result = plane.poll_result(intent.id)
    assert result is not None
    assert result.status == "failure"
    assert "fail" in result.error
    await plane.shutdown()
    if plane._event_loop_task:
        plane._event_loop_task.cancel()
        try:
            await plane._event_loop_task
        except asyncio.CancelledError:
            pass

@pytest.mark.asyncio
async def test_async_subscription_mechanism():
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    boundary = Boundary(id=uuid4(), metadata=Metadata(created_at=now, updated_at=now, provenance=[], confidence=1.0), content={})
    plane = DigitalPlane(id=uuid4(), boundary=boundary)
    plane._event_loop_task = asyncio.create_task(plane.event_loop())

    async def handler(transformation):
        return Result(
            id=uuid4(),
            intent_id=transformation.id,
            status="success",
            output={"sub": True},
            error=None,
            timestamp=datetime.now(timezone.utc)
        )
    plane.handler_registry.register("sub", handler)

    transformation = Transformation.create(
        id=uuid4(),
        metadata=Metadata(created_at=now, updated_at=now, provenance=[], confidence=1.0),
        operation="sub",
        target=None,
        parameters={}
    )
    intent = Intent(
        id=uuid4(),
        transformation=transformation,
        submitted_at=datetime.now(timezone.utc),
        version=1
    )

    received = []
    async def subscriber(result):
        received.append(result)

    plane.subscribe_async(subscriber)
    await plane.submit_intent(intent)
    await asyncio.sleep(0.1)
    assert received
    assert received[0].status == "success"
    await plane.shutdown()
    if plane._event_loop_task:
        plane._event_loop_task.cancel()
        try:
            await plane._event_loop_task
        except asyncio.CancelledError:
            pass
