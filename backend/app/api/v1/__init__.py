from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.schools import router as schools_router
from app.api.v1.books import router as books_router
from app.api.v1.papers import router as papers_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(schools_router)
api_router.include_router(books_router)
api_router.include_router(papers_router)
