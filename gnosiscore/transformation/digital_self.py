import asyncio

class DigitalSelf:
    """
    Orchestrates the recursive triad: Awareness, Observer, Mental, and Subject.
    Each tick, the triad can recursively call each other, forming a mutually-transforming loop.
    """

    def __init__(self, awareness, observer, mental, subject, selfmap=None, memory=None):
        self.awareness = awareness
        self.observer = observer
        self.mental = mental
        self.subject = subject
        self.selfmap = selfmap
        self.memory = memory

    async def tick(self):
        # Each tick, any part can trigger any other, forming a recursive call graph
        print("Tick: before awareness.act")
        awareness_state = await self.awareness.act(state={})
        print("Tick: after awareness.act")
        observer_state = await self.observer.observe(state=awareness_state, subject=self.subject)
        print("Tick: after observer.observe")
        mental_state = await self.mental.think(input=observer_state)
        print("Tick: after mental.think")
        # Could allow mental_state to recursively call awareness if it “notices” something new, etc.
        return mental_state

    async def run_cline_node(self, node, plane, available_actions):
        """
        Run a Cline node: generate prompt/context, call LLM, parse and dispatch actions.
        """
        from gnosiscore.selfmap.prompt_builder import SelfmapPromptBuilder
        from gnosiscore.transformation.dispatcher import ActionDispatcher
        import json

        builder = SelfmapPromptBuilder(self.selfmap, self.memory)
        prompt_data = builder.build_prompt(node, plane, available_actions)
        prompt = prompt_data["prompt"]
        context = prompt_data["context"]

        # Simulate LLM call (replace with actual LLM integration)
        # For now, just echo a valid JSON with a single action if possible
        llm_output = {
            "archetype": context["archetype"],
            "plane": context["plane"],
            "situation": {
                "neighbors": context["neighbors"],
                "active_paths": context["active_paths"],
                "recent_memory": context["recent_memory"],
                "prior_emotion": context["prior_emotion"]
            },
            "thought": "Test run: choosing first available action.",
            "emotion": context["prior_emotion"] or "neutral",
            "intention": "Demonstrate prompt builder integration.",
            "actions": [available_actions[0]] if available_actions else []
        }
        # In production, replace above with actual LLM call using prompt/context

        # Dispatch actions
        dispatcher = ActionDispatcher()
        dispatcher.dispatch_actions(llm_output.get("actions", []))
        return llm_output
