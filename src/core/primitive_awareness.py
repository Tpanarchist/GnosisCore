import sys
import os
from collections import deque, defaultdict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

class PrimitiveAwareness:
    def __init__(self, history_length=3):
        """
        Initializes the PrimitiveAwareness class with a set history length for pattern recognition.
        """
        self.current_state = None
        self.next_state = None
        self.state_history = deque(maxlen=history_length)  # Limited history for pattern tracking
        self.patterns = defaultdict(lambda: {"next_state": None, "weight": 0})  # Patterns with weights

    def observe_state(self, state):
        """
        Receives the current state, stores it in history, and updates the pattern tracker.
        """
        self.current_state = state
        self.state_history.append(state)
        print(f"Current state observed: {self.current_state}")
        self._update_patterns()

    def _update_patterns(self):
        """
        Updates the patterns dictionary with the current history sequence.
        """
        if len(self.state_history) < self.state_history.maxlen:
            return  # Wait until the history is full to start pattern recognition

        # Convert history to a tuple (hashable) for pattern storage
        history_tuple = tuple(self.state_history)
        
        # If the pattern is new, initialize its next state and weight
        if not self.patterns[history_tuple]["next_state"]:
            self.patterns[history_tuple]["next_state"] = self.current_state
            self.patterns[history_tuple]["weight"] += 1  # Initialize with a weight of 1
        else:
            # Increment the weight if the pattern exists
            self.patterns[history_tuple]["weight"] += 1

    def predict_next_state(self):
        """
        Predicts the next state based on recognized patterns in the state history.
        """
        if len(self.state_history) < self.state_history.maxlen:
            print("Not enough history for pattern-based prediction.")
            return self.current_state  # Temporary fallback to current state

        history_tuple = tuple(self.state_history)
        
        # Check if we have a pattern match
        if history_tuple in self.patterns and self.patterns[history_tuple]["next_state"]:
            # Predict based on the pattern with the highest weight
            self.next_state = self.patterns[history_tuple]["next_state"]
            print(f"Predicted next state from pattern (weighted): {self.next_state}")
        else:
            self.next_state = self.current_state  # Fallback
            print(f"No pattern match found. Predicted next state: {self.next_state}")
        
        return self.next_state

    def learn_from_feedback(self, actual_next_state):
        """
        Adjusts the prediction model based on feedback from the actual next state.
        """
        history_tuple = tuple(self.state_history)
        
        # If the prediction was incorrect, update the pattern with new next state and reset weight
        if actual_next_state != self.next_state:
            print(f"Prediction was inaccurate. Learning new pattern for: {history_tuple}")
            self.patterns[history_tuple] = {"next_state": actual_next_state, "weight": 1}
        else:
            # Increment weight for accurate predictions
            self.patterns[history_tuple]["weight"] += 1
            print("Prediction was accurate, reinforcing the pattern.")

# Example usage
if __name__ == "__main__":
    awareness = PrimitiveAwareness()
    awareness.observe_state("initial_state")
    awareness.predict_next_state()
    awareness.learn_from_feedback("some_next_state")
    awareness.observe_state("some_next_state")
    awareness.predict_next_state()
    awareness.learn_from_feedback("another_state")
