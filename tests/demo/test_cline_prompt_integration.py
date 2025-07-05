import asyncio
from types import SimpleNamespace

from gnosiscore.transformation.digital_self import DigitalSelf

class DummySelfMap:
    def neighbors(self, node_id):
        return ["neighbor-1", "neighbor-2"]
    def get_node(self, node_id):
        return SimpleNamespace(id=node_id, label=f"Label-{node_id}", type="Sefirah")
    def all_connections(self):
        return [
            SimpleNamespace(content={"source": "node-1", "name": "Guidance"}, type="path", id="conn-1"),
            SimpleNamespace(content={"source": "node-1", "name": "Synthesis"}, type="path", id="conn-2"),
        ]

class DummyMemory:
    def query_recent(self):
        return ["Memory1", "Memory2"]

async def main():
    node = SimpleNamespace(id="node-1", label="Netzach", type="Sefirah", content={"emotion": "hope"})
    dummy_selfmap = DummySelfMap()
    dummy_memory = DummyMemory()
    available_actions = [
        {"type": "invoke_path", "target": "Guidance", "args": [], "kwargs": {}},
        {"type": "reflect", "target": "self", "args": [], "kwargs": {}},
    ]
    digital_self = DigitalSelf(None, None, None, None, selfmap=dummy_selfmap, memory=dummy_memory)
    result = await digital_self.run_cline_node(node, "Mental", available_actions)
    print("LLM Output:", result)

if __name__ == "__main__":
    asyncio.run(main())
