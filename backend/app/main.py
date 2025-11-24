import sys
sys.path.insert(0, r'E:\pv-clean\backend')  # Path fix

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from .models import Base
from .routers.auth import router as auth_router
from .routers.logs import router as logs_router
from .routers.materials import router as materials_router
from .routers.progress import router as progress_router
from .routers.documents import router as documents_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PV Site Manager API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for easy testing (restrict in prod)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(logs_router)
app.include_router(materials_router)
app.include_router(progress_router)
app.include_router(documents_router)

@app.get("/")
def root():
    return {"message": "Welcome to 56 MW PV Site Manager API! /docs for Swagger."}