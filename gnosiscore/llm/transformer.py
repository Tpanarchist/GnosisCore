from abc import ABC, abstractmethod

class BaseTransformer(ABC):
    """
    Abstract base class for LLM transformer interfaces.
    """

    @abstractmethod
    def transform(self, form, context=None):
        """
        Transform the form using LLM output.
        Args:
            form: The Form object to process.
            context: Optional context or metadata.
        Returns:
            LLM response (string or structured).
        """
        pass

class StubTransformer(BaseTransformer):
    """
    Stub transformer for local/dev testing.
    Returns canned responses.
    """

    def transform(self, form, context=None):
        return {
            "response": "Stub LLM output.",
            "form_id": getattr(form, "id", None),
            "context": context
        }

class GPT4OMiniTransformer(BaseTransformer):
    """
    Transformer for GPT-4o-mini (stub for now).
    Implement real API call and error/cost handling as needed.
    """

    def __init__(self, api_key=None):
        self.api_key = api_key

    def transform(self, form, context=None):
        # TODO: Implement real API call
        return {
            "response": "[GPT-4o-mini] This is a placeholder response.",
            "form_id": getattr(form, "id", None),
            "context": context
        }
