class Field:
    def __init__(self, frames):
        self.frames = frames

    def tick(self):
        for graph in self.frames:
            graph.step()
            # Minimal Form/Delta integration
            if hasattr(graph, "forms"):
                for form in graph.forms:
                    delta = form.perceive("Origin")
                    print(f"{form.name} Δ={delta.magnitude()}")
