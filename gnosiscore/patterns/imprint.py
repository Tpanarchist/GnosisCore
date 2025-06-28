from .base import StatePatternBase

class Imprint(StatePatternBase):
    def __init__(self, transformer=None):
        super().__init__("Imprint", transformer=transformer)
        self.prompt_template = (
            "What lasting effect does '{current}' have on the system?"
        )

    def on_enter(self, current=None, form=None, context=None):
        print(f"{self.id} entered")
        prompt = self.prompt_template.format(
            current=current or self.id
        )
        if self.transformer:
            output = self.transformer(prompt)
            print(f"LLM Output: {output['response']}")
        else:
            print(f"{self.id} entered (no transformer)")
