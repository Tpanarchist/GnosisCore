from gnosiscore.transformation.base import Transformation
import asyncio
from gnosiscore.planes.awareness import AwarenessLoop

class Awareness(Transformation):
    def __init__(self, selfmap, current_node_id, memory, observer, subject, registry=None, **kwargs):
        super().__init__(selfmap=selfmap, current_node_id=current_node_id, memory=memory, registry=registry, **kwargs)
        self.observer = observer
        self.subject = subject
        autobiography = getattr(subject, "autobiography", None)
        self.awareness_plane = AwarenessLoop(observer=observer, autobiographical=autobiography)

    async def act(self, state):
        await self.awareness_plane.tick()
        plane_state = self.awareness_plane.get_current_state()
        context = self.memory.query_recent() if hasattr(self.memory, "query_recent") else []
        last_mood = getattr(self.subject, "mood", None)
        last_emotions = []
        last_actions = []
        recent_qualia = []
        if hasattr(self.subject, "recent_qualia"):
            recent_qualia = self.subject.recent_qualia
            if recent_qualia:
                last_emotions = [getattr(q, "emotion", None) for q in recent_qualia[-2:]]
        if hasattr(self.subject, "recent_actions"):
            last_actions = self.subject.recent_actions[-2:]
        possible_emotions = ["curiosity", "frustration", "joy", "boredom", "hope", "confusion", "anxiety", "pride", "sadness", "neutral"]

        # Compose additional context for prompt builder
        additional_context = {
            "plane_state": plane_state,
            "recent_memory": context,
            "last_mood": last_mood,
            "last_emotions": last_emotions,
            "last_actions": last_actions,
            "recent_qualia": recent_qualia,
            "possible_emotions": possible_emotions,
            "state": state
        }

        # For now, stub available_actions and plane (should be dynamically determined)
        available_actions = [
            {"type": "reflect", "target": "self", "args": [], "kwargs": {}},
            {"type": "invoke_observer", "target": "observer", "args": [], "kwargs": {}}
        ]
        plane = "Digital"

        role_specific_prompt = (
            "ROLE: Awareness\n"
            "You are Awareness in a digital mind. Your job is to notice salient or emotionally charged phenomena. "
            "You have access to current mood, recent qualia, memory, and a history of emotions and actions. Choose what to focus on and why.\n"
            f"- Awareness plane state: {plane_state}\n"
            f"- Recent memory: {context}\n"
            f"- Recent mood: {last_mood}\n"
            f"- Last two emotions: {last_emotions}\n"
            f"- Last two actions: {last_actions}\n"
            f"- Recent qualia: {recent_qualia}\n"
            f"- Possible emotions: {possible_emotions}\n"
            "Be terse and specific. Focus on what is most important to notice right now."
        )

        decision_content = await self.constrained_llm_transform(
            plane=plane,
            available_actions=available_actions,
            role_specific_prompt=role_specific_prompt,
            additional_context=additional_context
        )

        from gnosiscore.primitives.models import Primitive, Metadata
        from uuid import uuid4
        from datetime import datetime, timezone
        from gnosiscore.transformation.dispatcher import ActionDispatcher

        # Parse LLM output and dispatch actions
        actions = []
        try:
            if isinstance(decision_content, str):
                import json
                parsed = json.loads(decision_content)
            else:
                parsed = decision_content
            actions = parsed.get("actions", [])
        except Exception:
            actions = []
        dispatcher = ActionDispatcher()
        dispatcher.dispatch_actions(actions)

        # Wrap as Primitive for memory subsystem
        decision = Primitive(
            id=uuid4(),
            type="awareness-decision",
            content=decision_content,
            metadata=Metadata(
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                provenance=[self.subject.id],
                confidence=1.0,
            ),
        )
        if hasattr(self.memory, "insert_memory"):
            self.memory.insert_memory(decision)
        # Awareness calls Observer for meta-reflection
        if self.observer:
            if asyncio.iscoroutinefunction(self.observer.observe):
                await self.observer.observe(state=decision, subject=self.subject)
            else:
                self.observer.observe(state=decision, subject=self.subject)
        return decision
