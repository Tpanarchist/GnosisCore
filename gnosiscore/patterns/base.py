class StatePatternBase:
    id: str
    transformer = None

    def __init__(self, id, transformer=None):
        self.id = id
        self.transformer = transformer

    def on_enter(self, form=None, context=None, **kwargs):
        print(f"{self.id} entered")
        # Example: update context with entry log
        if context is None:
            context = {}
        context.setdefault("visited", []).append(self.id)
        # Example: let form remember this pattern
        if form is not None:
            form.memory = self.id
        return context
