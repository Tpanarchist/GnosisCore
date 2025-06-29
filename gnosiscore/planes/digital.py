from typing import Dict, Set, Optional, Callable, Any
from uuid import UUID, uuid4
from threading import Lock
from queue import Queue, Empty
from datetime import datetime

from gnosiscore.primitives.models import Boundary, Primitive, Transformation, Intent, Result

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
    """
    def __init__(self, id: UUID, boundary: Boundary):
        self.id = id
        self.boundary = boundary
        self._entities: Dict[UUID, Primitive] = {}
        self._subscribers: Set[MentalPlane] = set()
        self._lock = Lock()
        self.on_persist: Optional[Callable[[Primitive], None]] = None

        # Intent processing
        self._intent_queue: "Queue[tuple[Intent, MentalPlane]]" = Queue()
        self._result_registry: Dict[UUID, Result] = {}
        self._result_callbacks: Dict[UUID, Callable[[Result], None]] = {}

    def register_entity(self, primitive: Primitive) -> None:
        with self._lock:
            # TODO: Implement boundary enforcement logic
            self._entities[primitive.id] = primitive
            if self.on_persist:
                self.on_persist(primitive)

    def get_entity(self, entity_id: UUID) -> Primitive:
        with self._lock:
            return self._entities[entity_id]

    def remove_entity(self, entity_id: UUID) -> None:
        with self._lock:
            if entity_id in self._entities:
                del self._entities[entity_id]

    def publish_event(self, event: Primitive) -> None:
        with self._lock:
            for subscriber in self._subscribers:
                subscriber.on_event(event)

    def submit_intent(self, intent: Intent, mental_plane: "MentalPlane", callback: Optional[Callable[[Result], None]] = None) -> Result:
        """
        Submit an Intent for processing. Returns a pending Result.
        Optionally registers a callback for result delivery.
        """
        with self._lock:
            pending_result = Result(
                id=uuid4(),
                intent_id=intent.id,
                status="pending",
                output=None,
                error=None,
                timestamp=datetime.utcnow(),
            )
            self._result_registry[intent.id] = pending_result
            if callback:
                self._result_callbacks[intent.id] = callback
            self._intent_queue.put((intent, mental_plane))
        return pending_result

    def process_intents(self) -> None:
        """
        Process all queued intents (synchronously).
        For each, produce a Result and notify the submitter.
        """
        while True:
            try:
                intent, mental_plane = self._intent_queue.get_nowait()
            except Empty:
                break
            try:
                result = self._execute_intent(intent)
            except Exception as e:
                from uuid import uuid4
                from datetime import datetime, timezone
                result = Result(
                    id=uuid4(),
                    intent_id=intent.id,
                    status="failure",
                    output=None,
                    error=str(e),
                    timestamp=datetime.now(timezone.utc),
                )
            with self._lock:
                self._result_registry[intent.id] = result
                cb = self._result_callbacks.pop(intent.id, None)
            # Deliver result
            if cb:
                cb(result)
            elif hasattr(mental_plane, "on_result"):
                mental_plane.on_result(result)
            # else: result can be polled

    def poll_result(self, intent_id: UUID) -> Optional[Result]:
        """
        Poll for the result of a submitted intent.
        """
        with self._lock:
            return self._result_registry.get(intent_id)

    def _execute_intent(self, intent: Intent) -> Result:
        """
        Actually perform the transformation. Returns a Result.
        Supports LLM-backed transformations if llm_params is present.
        """
        import os
        import httpx

        transformation = intent.transformation
        content = transformation.content
        llm_params = content.get("llm_params")
        provenance = {
            "intent_id": str(intent.id),
            "submitted_at": str(intent.submitted_at),
            "llm_params": llm_params,
            "operation": content.get("operation"),
            "parameters": content.get("parameters"),
        }
        try:
            if llm_params is not None:
                api_key = os.environ.get("OPENAI_API_KEY")
                if not api_key:
                    raise RuntimeError("OPENAI_API_KEY not set in environment")
                # Compose OpenAI API call
                url = "https://api.openai.com/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": llm_params.get("model", "gpt-3.5-turbo"),
                    "messages": [
                        {"role": "system", "content": llm_params.get("system_prompt", "")},
                        {"role": "user", "content": llm_params.get("user_prompt", "")},
                    ],
                }
                # Add any extra OpenAI params
                for k, v in llm_params.items():
                    if k not in {"model", "system_prompt", "user_prompt"}:
                        payload[k] = v
                # Synchronous HTTP call for now
                with httpx.Client(timeout=30.0) as client:
                    resp = client.post(url, headers=headers, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                output = {
                    "llm_response": data,
                    "transformation": content,
                }
                status = "success"
                error = None
                provenance["llm_request"] = payload
                provenance["llm_response"] = data
            else:
                # Local logic
                output = {"transformation": content}
                status = "success"
                error = None
        except Exception as e:
            output = None
            status = "failure"
            error = str(e)
            provenance["error"] = error
        from datetime import datetime, timezone
        return Result(
            id=uuid4(),
            intent_id=intent.id,
            status=status,
            output=output,
            error=error,
            timestamp=datetime.now(timezone.utc),
        )

    def subscribe(self, mental_plane: 'MentalPlane') -> None:
        with self._lock:
            self._subscribers.add(mental_plane)

    def unsubscribe(self, mental_plane: 'MentalPlane') -> None:
        with self._lock:
            self._subscribers.discard(mental_plane)
