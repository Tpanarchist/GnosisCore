# tests/test_gnosis_core.py

from core.gnosis_core import GnosisCore

def test_core_initialization():
    """
    Test if GnosisCore initializes correctly with PrimitiveAwareness.
    """
    core = GnosisCore()
    assert core.primitive_awareness is not None, "PrimitiveAwareness was not initialized in GnosisCore."

def test_observe_state_integration():
    """
    Test if GnosisCore can observe a state through PrimitiveAwareness.
    """
    core = GnosisCore()
    initial_state = "initial_state"
    core.observe_state(initial_state)
    assert core.primitive_awareness.current_state == initial_state, "Failed to observe state in PrimitiveAwareness."

def test_predict_next_state_integration():
    """
    Test if GnosisCore can predict the next state through PrimitiveAwareness without patterns.
    """
    core = GnosisCore()
    core.observe_state("initial_state")
    predicted_state = core.predict_next_state()
    assert predicted_state == "initial_state", "Failed to predict next state without pattern in GnosisCore."

def test_learn_from_feedback_integration():
    """
    Test if GnosisCore can learn from feedback through PrimitiveAwareness.
    """
    core = GnosisCore()
    core.observe_state("initial_state")
    core.predict_next_state()
    feedback_state = "next_state"
    core.learn_from_feedback(feedback_state)
    # Check that feedback has been processed (the pattern should now include the next state)
    assert (tuple(core.primitive_awareness.state_history) in core.primitive_awareness.patterns), \
        "Pattern was not updated with feedback in PrimitiveAwareness."
    assert core.primitive_awareness.patterns[tuple(core.primitive_awareness.state_history)]["next_state"] == feedback_state, \
        "Failed to learn new pattern in PrimitiveAwareness through feedback."

if __name__ == "__main__":
    test_core_initialization()
    print("test_core_initialization passed")

    test_observe_state_integration()
    print("test_observe_state_integration passed")

    test_predict_next_state_integration()
    print("test_predict_next_state_integration passed")

    test_learn_from_feedback_integration()
    print("test_learn_from_feedback_integration passed")
