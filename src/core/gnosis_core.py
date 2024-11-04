# src/core/gnosis_core.py

import sys
import os
from core.primitive_awareness import PrimitiveAwareness

class GnosisCore:
    def __init__(self):
        """
        Initializes the GnosisCore framework and its core components, beginning with PrimitiveAwareness.
        """
        # Initialize PrimitiveAwareness for state observation and pattern prediction
        self.primitive_awareness = PrimitiveAwareness()
        print("GnosisCore initialized with PrimitiveAwareness module.")

    def observe_state(self, state):
        """
        Observes the current state and passes it to PrimitiveAwareness for pattern tracking and learning.
        """
        print(f"GnosisCore observing state: {state}")
        self.primitive_awareness.observe_state(state)

    def predict_next_state(self):
        """
        Uses PrimitiveAwareness to predict the next state based on observed patterns.
        """
        predicted_state = self.primitive_awareness.predict_next_state()
        print(f"GnosisCore predicted next state: {predicted_state}")
        return predicted_state

    def learn_from_feedback(self, actual_next_state):
        """
        Provides feedback to PrimitiveAwareness for learning from the actual next state.
        """
        print(f"GnosisCore learning from feedback. Actual next state: {actual_next_state}")
        self.primitive_awareness.learn_from_feedback(actual_next_state)

# Example usage within the module
if __name__ == "__main__":
    core = GnosisCore()
    core.observe_state("initial_state")
    core.predict_next_state()
    core.learn_from_feedback("some_next_state")
    core.observe_state("some_next_state")
    core.predict_next_state()
    core.learn_from_feedback("another_state")
