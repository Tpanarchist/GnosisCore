from fastapi import APIRouter, HTTPException
from uuid import UUID
from gnosiscore.planes.mental import MentalPlane

router = APIRouter()

# Dependency injection or singleton pattern for MentalPlane instance is assumed.
# Replace 'get_mental_plane()' with your actual retrieval logic.
def get_mental_plane() -> MentalPlane:
    # Placeholder: implement your MentalPlane instance retrieval here
    raise NotImplementedError("Provide a MentalPlane instance retrieval method.")

@router.get("/selfmap/snapshot")
def get_selfmap_snapshot():
    mp = get_mental_plane()
    return mp.export_selfmap_snapshot()

@router.get("/qualia/log")
def get_qualia_log():
    mp = get_mental_plane()
    return mp.export_qualia_log()

@router.get("/memory/snapshot")
def get_memory_snapshot():
    mp = get_mental_plane()
    return mp.export_memory_state()

@router.get("/provenance/{node_id}")
def get_provenance_chain(node_id: UUID):
    mp = get_mental_plane()
    try:
        return mp.export_provenance_chain(node_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# --- Contradiction Detection API ---

from fastapi import BackgroundTasks

@router.get("/contradictions/current")
async def get_current_contradictions():
    mp = get_mental_plane()
    contradictions = await mp.detect_contradictions()
    # Return as list of dicts with node IDs and content
    return [
        {
            "node1": {"id": str(n1.id), "content": n1.content},
            "node2": {"id": str(n2.id), "content": n2.content},
        }
        for n1, n2 in contradictions
    ]

@router.get("/contradictions/history")
def get_contradiction_history(limit: int = 100):
    mp = get_mental_plane()
    # Filter qualia log for contradiction modality
    contradiction_events = [
        q.model_dump()
        for q in mp.qualia_log
        if getattr(q, "modality", None) == "contradiction"
    ]
    return contradiction_events[-limit:]

@router.post("/contradictions/resolve")
async def resolve_contradictions(background_tasks: BackgroundTasks):
    mp = get_mental_plane()
    contradictions = await mp.detect_contradictions()
    # Optionally, correction can be triggered in background
    background_tasks.add_task(mp.correct_contradictions)
    return {
        "contradictions_found": len(contradictions),
        "correction_triggered": True,
    }
