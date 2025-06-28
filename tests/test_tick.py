from gnosiscore.core.field import Field
from gnosiscore.core.reality_graph import RealityGraph
from gnosiscore.core.delta import Delta

def test_single_tick():
    g = RealityGraph.from_yaml("configs/tree_of_patterns.yml")
    f = Field(frames=[g])
    f.tick()
    # simply assert no exception

def test_graph_loads():
    g = RealityGraph.from_yaml("configs/tree_of_patterns.yml")
    assert len(g.states) == 10
    assert len(g.flows) == 7

def test_delta_magnitude():
    d = Delta("A", "B")
    assert d.magnitude() == 1
