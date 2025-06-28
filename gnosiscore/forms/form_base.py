from gnosiscore.core.delta import Delta

class Form:
    def __init__(self, name: str):
        self.name = name
        self.memory = None   # last pattern id

    def perceive(self, pattern_id: str) -> Delta:
        delta = Delta(self.memory, pattern_id)
        self.memory = pattern_id
        return delta
