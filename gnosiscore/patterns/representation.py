from .base import StatePatternBase

class Representation(StatePatternBase):
    def __init__(self, transformer=None):
        super().__init__("Representation", transformer=transformer)
        self.prompt_template = (
            "How would you summarize the current state '{current}' for external communication?"
        )

    def on_enter(self, current=None, form=None, context=None):
        print(f"{self.id} entered")
        prompt = self.prompt_template.format(
            current=current or self.id
        )
        if self.transformer:
            output = self.transformer.transform(form, context)
            print(f"LLM Output: {output['response']}")
        else:
            print(f"{self.id} entered (no transformer)")
