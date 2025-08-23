from fastapi import APIRouter
from app.services.seed_nodes import seed_nodes

router = APIRouter()

@router.post("/seed")
async def seed_data():
    await seed_nodes()
    return {"message": "Nodes seeded successfully"}
