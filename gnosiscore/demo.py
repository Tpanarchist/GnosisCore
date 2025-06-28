from gnosiscore.core.reality_graph import RealityGraph
from gnosiscore.patterns.origin import OriginPattern
from gnosiscore.patterns.pulse import PulsePattern
from gnosiscore.patterns.formulation import FormulationPattern
from gnosiscore.patterns.proliferation import ProliferationPattern
from gnosiscore.patterns.pruning import PruningPattern
from gnosiscore.patterns.awareness import AwarenessPattern
from gnosiscore.patterns.memory import MemoryPattern
from gnosiscore.patterns.persistence import PersistencePattern
from gnosiscore.patterns.representation import RepresentationPattern
from gnosiscore.patterns.imprint import ImprintPattern
from gnosiscore.forms.form_base import Form
from gnosiscore.flows.flow_pattern import FlowPattern
from gnosiscore.llm.transformer import StubTransformer

class CognitiveBrain:
    def __init__(self):
        self.transformer = StubTransformer()
        # Instantiate patterns
        self.patterns = {
            "Origin": OriginPattern("Origin", transformer=self.transformer),
            "Pulse": PulsePattern("Pulse", transformer=self.transformer),
            "Formulation": FormulationPattern("Formulation", transformer=self.transformer),
            "Proliferation": ProliferationPattern("Proliferation", transformer=self.transformer),
            "Pruning": PruningPattern("Pruning", transformer=self.transformer),
            "Awareness": AwarenessPattern("Awareness", transformer=self.transformer),
            "Memory": MemoryPattern("Memory", transformer=self.transformer),
            "Persistence": PersistencePattern("Persistence", transformer=self.transformer),
            "Representation": RepresentationPattern("Representation", transformer=self.transformer),
            "Imprint": ImprintPattern("Imprint", transformer=self.transformer),
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
            Form("MemoryForm", memory={"thought": "I remember ice cream"}),
            Form("SensationForm", memory={"thought": "I'm hungry"}),
            Form("GoalForm", memory={"thought": "I want dessert"}),
        ]
        self.graph = RealityGraph(states=self.patterns, flows=self.flows)
        self.graph.forms = self.forms

    def run(self, ticks=3):
        print("=== CognitiveBrain Demo: Emergent Thought Simulation ===")
        for t in range(ticks):
            print(f"\n--- Tick {t+1} ---")
            self.graph.step()
            for form in self.forms:
                print(f"Form: {form.name}, Memory: {form.memory}")
        # Check for emergent decision
        for form in self.forms:
            mem = form.memory.get("thought", "").lower()
            if "ice cream" in mem and "hungry" in mem and "dessert" in mem:
                print("\nEmergent Decision: Get ice cream!")
                break
        else:
            print("\nNo emergent decision detected.")

if __name__ == "__main__":
    brain = CognitiveBrain()
    brain.run(ticks=5)
