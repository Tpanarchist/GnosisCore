# tests/test_primitive_awareness.py

from core.primitive_awareness import PrimitiveAwareness


def test_observe_state():
    awareness = PrimitiveAwareness()
    initial_state = "initial_state"
    awareness.observe_state(initial_state)
    assert awareness.current_state == initial_state, "Observe state failed."

def test_predict_next_state():
    awareness = PrimitiveAwareness()
    awareness.observe_state("initial_state")
    predicted_state = awareness.predict_next_state()
    assert predicted_state == "initial_state", "Predict next state failed."

def test_learn_from_feedback():
    awareness = PrimitiveAwareness()
    awareness.observe_state("initial_state")
    awareness.predict_next_state()
    feedback = "different_state"
    awareness.learn_from_feedback(feedback)
    # Since learn_from_feedback is a placeholder, we just ensure it runs without errors.

if __name__ == "__main__":
    test_observe_state()
    print("test_observe_state passed")
    test_predict_next_state()
    print("test_predict_next_state passed")
    test_learn_from_feedback()
    print("test_learn_from_feedback passed")
