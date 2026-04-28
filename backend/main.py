from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models, database
from routers import pools

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="SNU Pool API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pools.router)

@app.get("/")
def root():
    return {"message": "Welcome to SNU Pool API"}

@app.head("/health")
def health_check():
    return {"status": "ok"}
