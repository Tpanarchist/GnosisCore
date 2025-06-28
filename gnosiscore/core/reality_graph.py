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
        flows = [FlowPattern(states[f["from"]], states[f["to"]], transformer=transformer) for f in data["flows"]]
        return cls(states, flows)

    def step(self):
        # Improved: Traverse flows for each form, accumulate state/context
        for form in self.forms:
            context = {}
            for flow in self.flows:
                # Let form perceive the source pattern
                if hasattr(flow.source, "id"):
                    form.perceive(flow.source.id)
                # Pass both context and form through the flow, accumulate context
                context = flow.propagate(context=context, form=form)
            # Print or store the final context for demonstration
            print(f"RealityGraph.step() final context for form '{form.name}': {context}")
