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
