from .base import StatePatternBase

class Memory(StatePatternBase):
    def __init__(self, transformer=None):
        super().__init__("Memory", transformer=transformer)
        self.prompt_template = (
            "What important information from '{current}' should be stored for later recall?"
        )

    def on_enter(self, current=None, form=None, context=None):
        print(f"{self.id} entered")
        if context is None:
            context = {}
        awareness_output = context.get("awareness_output")
        if awareness_output:
            print(f"Memory received from Awareness: {awareness_output}")
        prompt = self.prompt_template.format(
            current=current or self.id
        )
        if self.transformer:
            output = self.transformer(prompt)
            print(f"LLM Output: {output['response']}")
            context["memory_output"] = output["response"]
        else:
            print(f"{self.id} entered (no transformer)")
        return context
