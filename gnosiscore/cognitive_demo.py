from gnosiscore.core.reality_graph import RealityGraph
from gnosiscore.patterns.origin import Origin
from gnosiscore.patterns.pulse import Pulse
from gnosiscore.patterns.formulation import Formulation
from gnosiscore.patterns.proliferation import Proliferation
from gnosiscore.patterns.pruning import Pruning
# Custom Awareness to fix .transform() usage
from gnosiscore.patterns.awareness import Awareness as AwarenessBase
from gnosiscore.patterns.memory import Memory
from gnosiscore.patterns.persistence import Persistence
from gnosiscore.patterns.representation import Representation
from gnosiscore.patterns.imprint import Imprint
from gnosiscore.forms.form_base import Form
from gnosiscore.flows.flow_pattern import FlowPattern
from gnosiscore.llm.transformer import StubTransformer

class CognitiveBrain:
    def __init__(self):
        self.transformer = StubTransformer()
        # Instantiate patterns
        self.patterns = {
            "Origin": Origin(transformer=self.transformer),
            "Pulse": Pulse(transformer=self.transformer),
            "Formulation": Formulation(transformer=self.transformer),
            "Proliferation": Proliferation(transformer=self.transformer),
            "Pruning": Pruning(transformer=self.transformer),
            "Awareness": self.CustomAwareness(transformer=self.transformer),
            "Memory": Memory(transformer=self.transformer),
            "Persistence": Persistence(transformer=self.transformer),
            "Representation": Representation(transformer=self.transformer),
            "Imprint": Imprint(transformer=self.transformer),
        }
        # Define flows (simplified for demo)
        self.flows = [
            FlowPattern(self.patterns["Origin"], self.patterns["Pulse"], transformer=self.transformer),
            FlowPattern(self.patterns["Pulse"], self.patterns["Formulation"], transformer=self.transformer),
            FlowPattern(self.patterns["Formulation"], self.patterns["Proliferation"], transformer=self.transformer),
            FlowPattern(self.patterns["Proliferation"], self.patterns["Pruning"], transformer=self.transformer),
            FlowPattern(self.patterns["Pruning"], self.patterns["Awareness"], transformer=self.transformer),
            FlowPattern(self.patterns["Awareness"], self.patterns["Memory"], transformer=self.transformer),
            FlowPattern(self.patterns["Memory"], self.patterns["Persistence"], transformer=self.transformer),
            FlowPattern(self.patterns["Persistence"], self.patterns["Representation"], transformer=self.transformer),
            FlowPattern(self.patterns["Representation"], self.patterns["Imprint"], transformer=self.transformer),
        ]
        # Forms: memory, sensation, goal
        self.forms = [
            Form("MemoryForm"),
            Form("SensationForm"),
            Form("GoalForm"),
        ]
        # Set initial "thoughts" in a separate attribute for demo purposes
        self.form_thoughts = {
            "MemoryForm": "I remember ice cream",
            "SensationForm": "I'm hungry",
            "GoalForm": "I want dessert",
        }
        for form in self.forms:
            form.thought = self.form_thoughts[form.name]
        self.graph = RealityGraph(states=self.patterns, flows=self.flows)
        self.graph.forms = self.forms

    class CustomAwareness(AwarenessBase):
        def on_enter(self, form=None, context=None):
            # Use .transform() instead of calling the transformer
            if self.transformer:
                prompt = f"Form: {getattr(form, 'name', None)}, Context: {context}"
                output = self.transformer.transform(form, context)
                print(f"Awareness (fixed): {output['response']}")
            return super().on_enter(form, context)

    def run(self, ticks=5):
        print("=== CognitiveBrain Demo: Emergent Thought Simulation ===")
        for t in range(ticks):
            print(f"\n--- Tick {t+1} ---")
            self.graph.step()
            for form in self.forms:
                print(f"Form: {form.name}, Memory: {form.memory}, Thought: {getattr(form, 'thought', None)}")
        # Check for emergent decision
        thoughts = [getattr(form, "thought", "").lower() for form in self.forms]
        if all(x in " ".join(thoughts) for x in ["ice cream", "hungry", "dessert"]):
            print("\nEmergent Decision: Get ice cream!")
        else:
            print("\nNo emergent decision detected.")

if __name__ == "__main__":
    brain = CognitiveBrain()
    brain.run(ticks=5)
