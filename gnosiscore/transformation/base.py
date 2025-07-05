from gnosiscore.selfmap.prompt_builder import SelfmapPromptBuilder
from typing import Optional, Dict, Any, List
from uuid import UUID

class Transformation:
    """
    Base class for all transformation archetypes (Awareness, Observer, Mental, etc).
    Provides LLM-driven transformation interface and selfmap/prompt integration.
    """

    def __init__(self, selfmap=None, current_node_id=None, memory=None, registry=None, **kwargs):
        self.selfmap = selfmap
        self.current_node_id = current_node_id
        self.memory = memory
        self.registry = registry
        self.prompt_builder = SelfmapPromptBuilder(selfmap, memory=memory) if selfmap else None

    async def constrained_llm_transform(
        self,
        plane: str,
        available_actions: List[Dict[str, Any]],
        role_specific_prompt: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform LLM transformation with full selfmap constraints.
        """
        if not self.selfmap or not self.current_node_id or not self.prompt_builder:
            # Fallback to stub
            return {"status": "no_selfmap", "output": None}

        node = self.selfmap.get_node(self.current_node_id)
        prompt_data = self.prompt_builder.build_prompt(node, plane, available_actions)
        prompt = prompt_data["prompt"]
        context = prompt_data["context"]

        # Merge in additional context if provided
        if additional_context:
            context.update(additional_context)

        # Optionally append a role-specific prompt
        if role_specific_prompt:
            prompt = f"{prompt}\n\n{role_specific_prompt}"

        # Call LLM through registry if available
        if self.registry:
            from gnosiscore.primitives.models import Transformation as TransformationPrimitive, LLMParams, Metadata
            from uuid import uuid4
            from datetime import datetime, timezone

            llm_params = LLMParams(
                model="gpt-4o-mini",
                system_prompt="You are a constrained agent in a symbolic cognitive system.",
                user_prompt=prompt,
                temperature=0.3,
                max_tokens=512,
            )

            transformation = TransformationPrimitive.create(
                id=uuid4(),
                metadata=Metadata(
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                    provenance=[self.current_node_id],
                    confidence=1.0,
                ),
                operation=f"{self.__class__.__name__.lower()}_transform",
                target=self.current_node_id,
                parameters={
                    "context": context,
                    "role_prompt": role_specific_prompt
                },
                llm_params=llm_params,
            )

            result = await self.registry.handle(transformation)
            return self.parse_llm_result(result, available_actions)
        else:
            # Fallback for testing
            return {"status": "no_registry", "context": context}

    def parse_llm_result(self, result, available_actions) -> Dict[str, Any]:
        """Parse and validate LLM result against constraints."""
        import json
        try:
            if hasattr(result, 'output') and result.output:
                llm_response = result.output.get('llm_response', {})
                choices = llm_response.get('choices', [])
                if choices:
                    content = choices[0].get('message', {}).get('content', '')
                    parsed = json.loads(content)
                    # Validate action is allowed
                    allowed_action_names = [a['type'] + ':' + a['target'] for a in available_actions]
                    for action in parsed.get("actions", []):
                        action_name = action.get('type') + ':' + action.get('target')
                        if action_name not in allowed_action_names:
                            raise ValueError(f"Action {action_name} not allowed")
                    return parsed
        except Exception as e:
            import logging
            logging.error(f"Failed to parse LLM result: {e}")
            return {"error": str(e), "raw_result": str(result)}

    def llm_transform(self, context, prompt):
        """
        Stub for LLM-driven transformation.
        In production, this would call an LLM API with the prompt and context.
        """
        # For now, just return a dict with prompt and context for demo/testing.
        return {
            "llm_prompt": prompt,
            "context": context,
            "output": f"Stub output for: {prompt}"
        }
