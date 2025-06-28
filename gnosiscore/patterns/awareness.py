from .base import StatePatternBase

class Awareness(StatePatternBase):
    def __init__(self, transformer=None):
        super().__init__("Awareness", transformer=transformer)
        self.prompt_template = (
            "Compare previous state '{previous}' with current '{current}'. "
            "What is the meaningful difference?"
        )

    def on_enter(self, previous=None, current=None, form=None, context=None):
        print(f"{self.id} entered")
        prompt = self.prompt_template.format(
            previous=previous or "",
            current=current or self.id
        )
        if self.transformer:
            output = self.transformer(prompt)
            print(f"LLM Output: {output['response']}")
        else:
            print(f"{self.id} entered (no transformer)")
