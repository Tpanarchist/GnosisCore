from gnosiscore.core.field import Field
from gnosiscore.core.reality_graph import RealityGraph
from gnosiscore.core.transformer_iface import LLMTransformer

transformer = LLMTransformer()
g = RealityGraph.from_yaml("configs/tree_of_patterns.yml", transformer=transformer)
f = Field(frames=[g])

for i in range(3):
    print(f"\n— Tick {i+1}")
    f.tick()
