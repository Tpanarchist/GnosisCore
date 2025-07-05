from gnosiscore.transformation.base import Transformation

import asyncio
from gnosiscore.transformation.base import Transformation

from gnosiscore.planes.mental import MentalPlane

class Mental(Transformation):
    def __init__(self, memory, subject, registry=None, selfmap=None, boundary=None, metaphysical_plane=None, **kwargs):
        super().__init__(**kwargs)
        self.memory = memory
        self.subject = subject
        self.registry = registry
        # Compose with MentalPlane
        # Use subject as owner, boundary if provided, else None, selfmap if provided, else None
        self.mental_plane = MentalPlane(
            owner=subject,
            boundary=boundary,
            memory=memory,
            selfmap=selfmap,
            metaphysical_plane=metaphysical_plane
        )

    async def think(self, input):
        # Mind-specific prompt and schema, referencing plane state
        plane_state = self.mental_plane.get_emotional_state()
        qualia_log = self.mental_plane.export_qualia_log(limit=5)
        prompt = (
            "ROLE: Mind\n"
            "You are the Mind process in a digital being. Your job is to think, feel, form intentions, and plan actions based on current awareness and observer reflection.\n"
            "You do NOT simply notice or reflect; you synthesize, decide, and set intentions.\n"
            "Given the following:\n"
            f"- Mental plane emotional state: {plane_state}\n"
            f"- Recent qualia: {qualia_log}\n"
            f"- Input from observer/awareness: {input}\n"
            "Return ONLY valid JSON with this schema:\n"
            "{\n"
            '  "thought": <string>,\n'
            '  "emotion": <string>,\n'
            '  "intention": <string>,\n'
            '  "actions": [ {"type": <string>, "target": <string>, "args": <list>, "kwargs": <dict>} ]\n'
            "}\n"
            "Be specific, intentional, and context-aware. Your output should reflect the current emotional and cognitive state."
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
                operation="mental",
                target=None,
                parameters={"context": input},
                llm_params=llm_params,
            )
            llm_result = await handler(transformation)
            output_content = getattr(llm_result, "output", llm_result)
            if output_content is None:
                output_content = {"output": ""}
        else:
            output_content = self.llm_transform(input, prompt=prompt)
            if output_content is None:
                output_content = {"output": ""}

        import json
        from gnosiscore.transformation.dispatcher import ActionDispatcher

        # Parse LLM output and dispatch actions
        actions = []
        try:
            if isinstance(output_content, str):
                parsed = json.loads(output_content)
            else:
                parsed = output_content
            actions = parsed.get("actions", [])
        except Exception as e:
            actions = []
        dispatcher = ActionDispatcher()
        dispatcher.dispatch_actions(actions)

        output = Primitive(
            id=uuid4(),
            type="mental-output",
            content=output_content,
            metadata=Metadata(
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                provenance=[self.subject.id],
                confidence=1.0,
            ),
        )
        if hasattr(self.memory, "insert_memory"):
            self.memory.insert_memory(output)
        return output
