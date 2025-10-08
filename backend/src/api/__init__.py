from api.links import router as links_router
from fastapi import APIRouter


base_router = APIRouter()
base_router.include_router(links_router)

