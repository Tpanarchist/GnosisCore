import yaml
from gnosiscore.flows.flow_pattern import FlowPattern

from gnosiscore.forms.form_base import Form

class RealityGraph:
    def __init__(self, states, flows):
        self.states = states
        self.flows = flows
        self.forms = [Form("FormA")]

    @classmethod
    def from_yaml(cls, path, transformer=None):
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        # Import pattern classes
        states = {}
        for name, info in data["states"].items():
            if not isinstance(info, dict) or "impl" not in info:
                raise ValueError(f"State '{name}' must be a dict with an 'impl' key, got: {info!r}")
            module_path, class_name = info["impl"].rsplit(".", 1)
            module = __import__(f"gnosiscore.{module_path}", fromlist=[class_name])
            states[name] = getattr(module, class_name)(transformer=transformer)
        flows = [FlowPattern(f["from"], f["to"], transformer=transformer) for f in data["flows"]]
        return cls(states, flows)

    def step(self):
        # Data-driven traversal using flows
        for flow in self.flows:
            if hasattr(self.states[flow.source], "on_enter"):
                self.states[flow.source].on_enter()
            flow.propagate(None)
            if hasattr(self.states[flow.target], "on_enter"):
                self.states[flow.target].on_enter()
