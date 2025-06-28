from .base import StatePatternBase

class Pulse(StatePatternBase):
    def __init__(self, transformer=None):
        super().__init__("Pulse", transformer=transformer)

    def on_enter(self, form=None, context=None):
        super().on_enter(form, context)
