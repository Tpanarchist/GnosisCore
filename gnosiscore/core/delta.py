class Delta:
    def __init__(self, before, after):
        self.before = before
        self.after = after

    def magnitude(self):
        return 0 if self.before is None else 1
