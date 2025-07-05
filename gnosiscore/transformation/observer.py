from gnosiscore.transformation.base import Transformation

import asyncio
from gnosiscore.transformation.base import Transformation

class Observer(Transformation):
    def __init__(self, memory, awareness, subject, registry=None, **kwargs):
        super().__init__(**kwargs)
        self.memory = memory
        self.awareness = awareness
        self.subject = subject
        self.registry = registry

    async def observe(self, state, subject):
        # Observer-specific prompt and schema
        recent_memory = self.memory.query_recent() if hasattr(self.memory, "query_recent") else []
        prompt = (
            "ROLE: Observer\n"
            "You are the Observer process in a digital mind. Your job is to reflect on the current state, detect patterns, spot anomalies, and summarize what is happening.\n"
            "You do NOT simply notice or plan; you analyze, compare, and suggest improvements or warnings.\n"
            "Given the following:\n"
            f"- Awareness output: {state}\n"
            f"- Recent memory: {recent_memory}\n"
            "Return ONLY valid JSON with this schema:\n"
            "{\n"
            '  "summary": <string>,\n'
            '  "patterns": [<string>, ...],\n'
            '  "conflicts": [<string>, ...],\n'
            '  "suggestions": [<string>, ...],\n'
            '  "actions": [ {"type": <string>, "target": <string>, "args": <list>, "kwargs": <dict>} ]\n'
            "}\n"
            "Be analytical and concise. Focus on what is unusual, important, or actionable in the current state."
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
                    provenance=[subject.id],
                    confidence=1.0,
                ),
                operation="observer",
                target=None,
                parameters={"context": state},
                llm_params=llm_params,
            )
            llm_result = await handler(transformation)
            reflection_content = getattr(llm_result, "output", llm_result)
            if reflection_content is None:
                reflection_content = {"output": ""}
        else:
            reflection_content = self.llm_transform(state, prompt=prompt)
            if reflection_content is None:
                reflection_content = {"output": ""}

        import json
        from gnosiscore.transformation.dispatcher import ActionDispatcher

        # Parse LLM output and dispatch actions
        actions = []
        try:
            if isinstance(reflection_content, str):
                parsed = json.loads(reflection_content)
            else:
                parsed = reflection_content
            actions = parsed.get("actions", [])
        except Exception as e:
            actions = []
        dispatcher = ActionDispatcher()
        dispatcher.dispatch_actions(actions)

        reflection = Primitive(
            id=uuid4(),
            type="observer-reflection",
            content=reflection_content,
            metadata=Metadata(
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                provenance=[subject.id],
                confidence=1.0,
            ),
        )
        if hasattr(self.memory, "insert_memory"):
            self.memory.insert_memory(reflection)
        # Observer can trigger Awareness recursively if pattern warrants
        if self.should_recurse(reflection):
            if asyncio.iscoroutinefunction(self.awareness.act):
                await self.awareness.act(state)
            else:
                self.awareness.act(state)
        return reflection

    def should_recurse(self, reflection):
        # Stub: In real use, analyze reflection for recursion triggers
        # For demo, randomly decide not to recurse
        return False
