# tests/test_gnosis_core.py

from core.gnosis_core import GnosisCore

def test_observe_state():
    """
    Test the observe_state function to ensure it sets the current state in PrimitiveAwareness.
    """
    core = GnosisCore()
    initial_state = "initial_state"
    core.observe_state(initial_state)
    assert core.primitive_awareness.current_state == initial_state, "observe_state failed to set the correct state in PrimitiveAwareness."

def test_predict_next_state():
    """
    Test predict_next_state to verify that it returns the expected prediction from PrimitiveAwareness.
    """
    core = GnosisCore()
    core.observe_state("initial_state")
    predicted_state = core.predict_next_state()
    assert predicted_state == "initial_state", "predict_next_state did not return the expected initial prediction."

def test_learn_from_feedback():
    """
    Test learn_from_feedback to ensure it properly updates predictions in PrimitiveAwareness.
    """
    core = GnosisCore()
    core.observe_state("state1")
    core.observe_state("state2")
    core.observe_state("state3")

    # Make an initial prediction and then learn from feedback
    core.predict_next_state()
    core.learn_from_feedback("state4")

    # Repeat the pattern to check if it has learned
    core.observe_state("state2")
    core.observe_state("state3")
    core.observe_state("state4")
    predicted_state = core.predict_next_state()
    assert predicted_state == "state4", "learn_from_feedback did not update the pattern learning correctly."

if __name__ == "__main__":
    test_observe_state()
    print("test_observe_state passed")
    
    test_predict_next_state()
    print("test_predict_next_state passed")
    
    test_learn_from_feedback()
    print("test_learn_from_feedback passed")
