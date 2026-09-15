from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.chat_router import router as chat_router
from app.api.engine_router import router as engine_router
from app.api.health_router import router as health_router
from app.core.config import settings

app = FastAPI(title="Float")

app.include_router(health_router)
app.include_router(engine_router)
app.include_router(chat_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
