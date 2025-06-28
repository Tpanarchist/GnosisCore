from .base import StatePatternBase

class Proliferation(StatePatternBase):
    def __init__(self, transformer=None):
        super().__init__("Proliferation", transformer=transformer)

    def on_enter(self, form=None, context=None):
        super().on_enter(form, context)
