class FlowPattern:
    def __init__(self, source, target, transformer=None):
        self.source = source
        self.target = target
        self.transformer = transformer

    def propagate(self, context=None, form=None):
        print(f"Traversed {self.source} → {self.target}")
        # Pass context to target pattern, allow mutation
        if hasattr(self.target, "on_enter"):
            result = self.target.on_enter(form=form, context=context)
            # If on_enter returns a new context, use it
            if result is not None:
                context = result
        return context
