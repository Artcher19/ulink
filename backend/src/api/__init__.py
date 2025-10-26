from api.links import router as links_router
from api.admin import router as admin_router
from fastapi import APIRouter


base_router = APIRouter()
base_router.include_router(links_router)
base_router.include_router(admin_router)


