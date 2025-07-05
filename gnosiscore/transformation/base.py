class Transformation:
    """
    Base class for all transformation archetypes (Awareness, Observer, Mental, etc).
    Provides LLM-driven transformation interface.
    """

    def __init__(self, **kwargs):
        pass

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
