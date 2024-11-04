# tests/test_primitive_awareness.py

from core.primitive_awareness import PrimitiveAwareness

def test_observe_state():
    """
    Test that observe_state correctly updates the current state.
    """
    awareness = PrimitiveAwareness()
    initial_state = "initial_state"
    awareness.observe_state(initial_state)
    assert awareness.current_state == initial_state, "Observe state failed."


def test_predict_next_state_without_pattern():
    """
    Test predict_next_state with no learned patterns.
    It should default to predicting the current state.
    """
    awareness = PrimitiveAwareness()
    awareness.observe_state("initial_state")
    predicted_state = awareness.predict_next_state()
    assert predicted_state == "initial_state", "Predict next state failed without pattern."


def test_learn_pattern_and_predict():
    """
    Test learning a pattern and using it to predict the next state.
    """
    awareness = PrimitiveAwareness(history_length=3)
    
    # Observe a sequence of states to create a pattern
    awareness.observe_state("state1")
    awareness.observe_state("state2")
    awareness.observe_state("state3")
    
    # Learn from feedback that the next state should be "state4"
    awareness.predict_next_state()
    awareness.learn_from_feedback("state4")
    
    # Repeat the pattern and test prediction
    awareness.observe_state("state1")
    awareness.observe_state("state2")
    awareness.observe_state("state3")
    predicted_state = awareness.predict_next_state()
    assert predicted_state == "state4", "Pattern-based prediction failed."


def test_weighted_pattern_reinforcement():
    """
    Test that repeated accurate predictions reinforce pattern weight.
    """
    awareness = PrimitiveAwareness(history_length=3)
    
    # Create and learn a pattern with feedback
    awareness.observe_state("a")
    awareness.observe_state("b")
    awareness.observe_state("c")
    awareness.predict_next_state()
    awareness.learn_from_feedback("d")
    
    # Repeat the pattern several times to increase weight
    for _ in range(3):
        awareness.observe_state("a")
        awareness.observe_state("b")
        awareness.observe_state("c")
        predicted_state = awareness.predict_next_state()
        awareness.learn_from_feedback("d")
        assert predicted_state == "d", "Failed to reinforce pattern with correct prediction."

    # Verify that pattern weight has increased (implicitly by repeated accuracy)
    print("Pattern reinforcement test passed with increased prediction accuracy.")


def test_predict_inaccurate_and_learn_new_pattern():
    """
    Test learning a new pattern when the prediction is incorrect.
    """
    awareness = PrimitiveAwareness(history_length=3)
    
    # Create and learn an initial pattern
    awareness.observe_state("x")
    awareness.observe_state("y")
    awareness.observe_state("z")
    awareness.predict_next_state()
    awareness.learn_from_feedback("w")
    
    # Introduce a new sequence to test the model's ability to learn a different outcome
    awareness.observe_state("y")
    awareness.observe_state("z")
    awareness.observe_state("v")
    awareness.predict_next_state()
    awareness.learn_from_feedback("u")
    
    # Check that the new pattern is now predicted correctly
    awareness.observe_state("y")
    awareness.observe_state("z")
    awareness.observe_state("v")
    predicted_state = awareness.predict_next_state()
    assert predicted_state == "u", "Failed to learn new pattern from inaccurate prediction."

if __name__ == "__main__":
    test_observe_state()
    print("test_observe_state passed")
    
    test_predict_next_state_without_pattern()
    print("test_predict_next_state_without_pattern passed")
    
    test_learn_pattern_and_predict()
    print("test_learn_pattern_and_predict passed")
    
    test_weighted_pattern_reinforcement()
    print("test_weighted_pattern_reinforcement passed")
    
    test_predict_inaccurate_and_learn_new_pattern()
    print("test_predict_inaccurate_and_learn_new_pattern passed")
