import asyncio

class DigitalSelf:
    """
    Orchestrates the recursive triad: Awareness, Observer, Mental, and Subject.
    Each tick, the triad can recursively call each other, forming a mutually-transforming loop.
    """

    def __init__(self, awareness, observer, mental, subject):
        self.awareness = awareness
        self.observer = observer
        self.mental = mental
        self.subject = subject

    async def tick(self):
        # Each tick, any part can trigger any other, forming a recursive call graph
        awareness_state = await self.awareness.act(state={})
        observer_state = await self.observer.observe(state=awareness_state, subject=self.subject)
        mental_state = await self.mental.think(input=observer_state)
        # Could allow mental_state to recursively call awareness if it “notices” something new, etc.
        return mental_state
