class FlowPattern:
    def __init__(self, source, target, transformer=None):
        self.source = source
        self.target = target
        self.transformer = transformer

    def propagate(self, payload, form=None, context=None):
        print(f"Traversed {self.source} → {self.target}")
        # If source/target are pattern instances, call on_enter with transformer
        if hasattr(self.target, "on_enter"):
            self.target.on_enter(form=form, context=context)
        return payload
