# src/core/gnosis_core.py

from core.primitive_awareness import PrimitiveAwareness

class GnosisCore:
    def __init__(self):
        """
        Initializes the GnosisCore framework, with Primitive Awareness as the foundational component.
        This class will expand to incorporate other components, such as emotional processing and memory.
        """
        # Initialize the Primitive Awareness module
        self.primitive_awareness = PrimitiveAwareness()
        print("GnosisCore initialized with Primitive Awareness module.")

    def observe_state(self, state):
        """
        Passes a state to the Primitive Awareness component for observation.
        """
        print(f"Observing state: {state}")
        self.primitive_awareness.observe_state(state)

    def predict_next_state(self):
        """
        Retrieves the next state prediction from the Primitive Awareness component.
        """
        predicted_state = self.primitive_awareness.predict_next_state()
        print(f"GnosisCore predicted next state: {predicted_state}")
        return predicted_state

    def learn_from_feedback(self, actual_next_state):
        """
        Provides feedback to the Primitive Awareness component to allow it to learn and adjust.
        """
        print(f"Learning from feedback. Actual next state: {actual_next_state}")
        self.primitive_awareness.learn_from_feedback(actual_next_state)

# Example usage
if __name__ == "__main__":
    core = GnosisCore()
    core.observe_state("initial_state")
    core.predict_next_state()
    core.learn_from_feedback("some_next_state")
    core.observe_state("some_next_state")
    core.predict_next_state()
    core.learn_from_feedback("another_state")
