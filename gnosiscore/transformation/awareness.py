from gnosiscore.transformation.base import Transformation

import asyncio
from gnosiscore.transformation.base import Transformation

from gnosiscore.planes.awareness import AwarenessLoop

class Awareness(Transformation):
    def __init__(self, memory, observer, subject, registry=None, **kwargs):
        super().__init__(**kwargs)
        self.memory = memory
        self.observer = observer
        self.subject = subject
        self.registry = registry
        # Instantiate the plane
        autobiography = getattr(subject, "autobiography", None)
        self.awareness_plane = AwarenessLoop(observer=observer, autobiographical=autobiography)

    async def act(self, state):
        # Update plane state before reasoning
        await self.awareness_plane.tick()
        # Awareness-specific prompt and schema
        plane_state = self.awareness_plane.get_current_state()
        context = self.memory.query_recent() if hasattr(self.memory, "query_recent") else []
        # Gather last mood, emotion, and qualia from memory or logs
        last_mood = getattr(self.subject, "mood", None)
        # Track last two emotions and actions for diversity enforcement
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
        # Few-shot exemplar for emotion dynamics
        exemplar = (
            "Example output:\n"
            '{\n'
            '  "focus": "unexpected spike in user activity",\n'
            '  "salience": 0.9,\n'
            '  "novelty": 0.8,\n'
            '  "emotion": "curiosity",\n'
            '  "reason": "Sudden change detected in activity logs.",\n'
            '  "priority": "high",\n'
            '  "actions": [ {"type": "invoke_observer", "target": "observer", "args": [], "kwargs": {}} ],\n'
            '  "suggestions": ["Investigate cause of spike"]\n'
            '}'
        )
        prompt = (
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
            "Return ONLY valid JSON with this schema:\n"
            "{\n"
            '  "focus": <string>,\n'
            '  "salience": <float>,\n'
            '  "novelty": <float>,\n'
            '  "emotion": <string>,  // Must be different than last 2 unless justified. Choose from possible_emotions.\n'
            '  "reason": <string>,\n'
            '  "priority": <"high"|"medium"|"low">,\n'
            '  "actions": [ {"type": <string>, "target": <string>, "args": <list>, "kwargs": <dict>} ],\n'
            '  "suggestions": [<string>, ...]\n'
            "}\n"
            "If emotion is unchanged from the last two cycles, explain why in 'reason'. "
            "If anything in memory or qualia is emotionally salient, surface it in your focus. "
            "Be diverse and creative in emotion selection, not just 'curiosity' or 'neutral'.\n"
            f"{exemplar}\n"
            "Be terse and specific. Focus on what is most important to notice right now."
        )
        from gnosiscore.primitives.models import Primitive, Metadata
        from uuid import uuid4
        from datetime import datetime, timezone

        # Use transformation registry handler if available
        if self.registry:
            from gnosiscore.primitives.models import Transformation as TransformationPrimitive, LLMParams
            handler = self.registry.handle if hasattr(self.registry, "handle") else self.registry
            llm_params = LLMParams(
                model="gpt-4o-mini",
                system_prompt=None,
                user_prompt=prompt,
                temperature=0.2,
                max_tokens=256,
            )
            transformation = TransformationPrimitive.create(
                id=uuid4(),
                metadata=Metadata(
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                    provenance=[self.subject.id],
                    confidence=1.0,
                ),
                operation="awareness",
                target=None,
                parameters={"context": context},
                llm_params=llm_params,
            )
            llm_result = await handler(transformation)
            decision_content = getattr(llm_result, "output", llm_result)
            if decision_content is None:
                decision_content = {"output": ""}
        else:
            decision_content = self.llm_transform(context, prompt=prompt)
            if decision_content is None:
                decision_content = {"output": ""}

        import json
        from gnosiscore.transformation.dispatcher import ActionDispatcher

        # Parse LLM output and dispatch actions
        actions = []
        try:
            if isinstance(decision_content, str):
                parsed = json.loads(decision_content)
            else:
                parsed = decision_content
            actions = parsed.get("actions", [])
        except Exception as e:
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
