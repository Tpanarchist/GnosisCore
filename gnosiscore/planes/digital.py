import asyncio
from typing import Dict, Set, Optional, Callable, Any, Awaitable, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timezone
from gnosiscore.primitives.models import Boundary, Primitive, Transformation, Intent, Result
from gnosiscore.transformation.registry import TransformationHandlerRegistry

# Forward reference for MentalPlane (to avoid circular import)
class MentalPlane:
    def on_event(self, event: Primitive) -> None:
        pass
    def on_result(self, result: Result) -> None:
        pass

class DigitalPlane:
    """
    DigitalPlane hosts all digital entities and their state.
    Enforces boundaries, manages spatial/temporal structures,
    and propagates events to subscribed MentalPlanes.
    Also orchestrates async intent execution via event loop.
    """
    def __init__(self, id: UUID, boundary: Boundary, concurrent: bool = False):
        self.id = id
        self.boundary = boundary
        self._entities: Dict[UUID, Primitive] = {}
        self._subscribers: Set[Any] = set()
        self.on_persist: Optional[Callable[[Primitive], None]] = None

        # Async intent processing
        self.intent_queue: asyncio.Queue[Tuple[Intent, Optional[Callable[[Result], Awaitable[None]]]]] = asyncio.Queue()
        self.result_map: Dict[UUID, Result] = {}
        self._callback_map: Dict[UUID, Callable[[Result], Awaitable[None]]] = {}
        self._event_loop_task: Optional[asyncio.Task[None]] = None
        self._async_subscribers: Set[Callable[[Result], Awaitable[None]]] = set()
        self._running = False
        self._concurrent = concurrent

        # Registry for transformation handlers
        self.handler_registry = TransformationHandlerRegistry()

    # --- Entity/event legacy sync API (unchanged) ---
    def register_entity(self, primitive: Primitive) -> None:
        self._entities[primitive.id] = primitive
        if self.on_persist:
            self.on_persist(primitive)

    def get_entity(self, entity_id: UUID) -> Primitive:
        return self._entities[entity_id]

    def remove_entity(self, entity_id: UUID) -> None:
        if entity_id in self._entities:
            del self._entities[entity_id]

    def publish_event(self, event: Primitive) -> None:
        for subscriber in self._subscribers:
            if hasattr(subscriber, "on_event"):
                subscriber.on_event(event)

    def subscribe(self, subscriber: Any) -> None:
        self._subscribers.add(subscriber)

    def unsubscribe(self, subscriber: Any) -> None:
        self._subscribers.discard(subscriber)

    # --- Async intent/event loop API ---
    async def submit_intent(self, intent: Intent, callback: Optional[Callable[[Result], Awaitable[None]]] = None):
        """
        Submit an Intent for async processing. Optionally provide an async callback.
        """
        pending_result = Result(
            id=uuid4(),
            intent_id=intent.id,
            status="pending",
            output=None,
            error=None,
            timestamp=datetime.now(timezone.utc),
        )
        self.result_map[intent.id] = pending_result
        if callback:
            self._callback_map[intent.id] = callback
        await self.intent_queue.put((intent, callback))

    async def event_loop(self):
        """
        Async event loop for processing intents.
        """
        self._running = True
        while self._running:
            try:
                item = await self.intent_queue.get()
            except Exception:
                continue
            if item is None:
                self._running = False
                self.intent_queue.task_done()
                break
            intent, callback = item
            if self._concurrent:
                asyncio.create_task(self._process_intent(intent, callback))
            else:
                await self._process_intent(intent, callback)
            self.intent_queue.task_done()

    async def _process_intent(self, intent: Intent, callback: Optional[Callable[[Result], Awaitable[None]]]):
        try:
            result = await self.handler_registry.handle(intent.transformation)
        except Exception as e:
            result = Result(
                id=uuid4(),
                intent_id=intent.id,
                status="failure",
                output=None,
                error=str(e),
                timestamp=datetime.now(timezone.utc),
            )
        self.result_map[intent.id] = result

        # Deliver result via callback if provided
        cb = callback or self._callback_map.pop(intent.id, None)
        if cb:
            await cb(result)
        # Notify async subscribers
        for subscriber in self._async_subscribers:
            await subscriber(result)

    def poll_result(self, intent_id: UUID) -> Optional[Result]:
        """
        Poll for the result of a submitted intent.
        """
        return self.result_map.get(intent_id)

    def subscribe_async(self, subscriber: Callable[[Result], Awaitable[None]]):
        """
        Subscribe an async callable to receive all Results.
        """
        self._async_subscribers.add(subscriber)

    def unsubscribe_async(self, subscriber: Callable[[Result], Awaitable[None]]):
        self._async_subscribers.discard(subscriber)

    async def shutdown(self):
        """
        Gracefully shut down the event loop.
        """
        self._running = False
        await self.intent_queue.put(None)
        if self._event_loop_task:
            await self._event_loop_task
