from gnosiscore.patterns.base import StatePatternBase

class Origin(StatePatternBase):
    def __init__(self, transformer=None):
        super().__init__("Origin", transformer=transformer)

    def on_enter(self, form=None, context=None):
        super().on_enter(form, context)
