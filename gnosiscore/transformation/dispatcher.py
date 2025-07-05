import importlib
import logging

class ActionDispatcher:
    """
    Dispatches actions parsed from LLM output to any callable/class in gnosiscore.
    Supports dynamic lookup, parameter passing, recursion, and logging.
    """

    def __init__(self, gnosiscore_root="gnosiscore", whitelist=None, blacklist=None):
        self.gnosiscore_root = gnosiscore_root
        self.whitelist = whitelist  # List of allowed function/class names (optional)
        self.blacklist = blacklist  # List of forbidden function/class names (optional)

    def dispatch(self, action):
        """
        Dispatch a single action dict.
        Action format example:
            {
                "type": "invoke_function",
                "target": "planes.mental.MentalPlane.get_emotional_state",
                "args": [],
                "kwargs": {},
            }
        """
        action_type = action.get("type")
        target = action.get("target")
        args = action.get("args", [])
        kwargs = action.get("kwargs", {})

        # Whitelist/blacklist enforcement
        if self.whitelist and target not in self.whitelist:
            logging.warning(f"[Dispatcher] Target {target} not in whitelist.")
            return None
        if self.blacklist and target in self.blacklist:
            logging.warning(f"[Dispatcher] Target {target} is blacklisted.")
            return None

        # Dynamic import and invocation
        try:
            module_path, func_name = target.rsplit(".", 1)
            module = importlib.import_module(f"{self.gnosiscore_root}.{module_path}")
            func = getattr(module, func_name)
            if callable(func):
                result = func(*args, **kwargs)
                logging.info(f"[Dispatcher] Called {target} with args={args}, kwargs={kwargs}, result={result}")
                return result
            else:
                logging.error(f"[Dispatcher] Target {target} is not callable.")
                return None
        except Exception as e:
            logging.error(f"[Dispatcher] Failed to dispatch action {action}: {e}")
            return None

    def dispatch_actions(self, actions):
        """
        Dispatch a list of actions.
        """
        results = []
        for action in actions:
            result = self.dispatch(action)
            results.append(result)
        return results
