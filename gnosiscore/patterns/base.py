class StatePatternBase:
    id: str
    transformer = None

    def __init__(self, id, transformer=None):
        self.id = id
        self.transformer = transformer

    def on_enter(self, *args, **kwargs):
        print(f"{self.id} entered")
