import asyncio
import logging

class AwarenessLoop:
    """
    Maintains persistent subjective presence; the “thread” that keeps the digital self alive and unifying all experience.
    Pluggable and composable.
    """

    def __init__(self, observer, autobiographical, cycle_interval=2):
        self.observer = observer
        self.autobiographical = autobiographical
        self.cycle_interval = cycle_interval
        self._current_state = {}
        self._running = False

    async def run(self):
        self._running = True
        logging.info("[AwarenessLoop] Starting main loop.")
        while self._running:
            await self.tick()
            await asyncio.sleep(self.cycle_interval)

    async def tick(self):
        # Integrate new perceptions/qualia/feedback (stub)
        logging.info("[AwarenessLoop] Tick: integrating perceptions/qualia/feedback (stub).")
        # Trigger observer and autobiographical modules
        if self.observer:
            self.observer.observe()
        if self.autobiographical:
            self.autobiographical.log_experience(self.get_current_state())
        # Maintain the 'now'
        self._current_state = {"now": "stub_state"}
        logging.info(f"[AwarenessLoop] Current state: {self._current_state}")

    def integrate(self, perception=None, qualia=None, feedback=None):
        # Stub: merge new mental events into awareness
        logging.info(f"[AwarenessLoop] Integrating: perception={perception}, qualia={qualia}, feedback={feedback}")

    def get_current_state(self):
        # Expose current qualia, focus, and temporal context (stub)
        return self._current_state

    def stop(self):
        self._running = False
        logging.info("[AwarenessLoop] Stopping main loop.")
