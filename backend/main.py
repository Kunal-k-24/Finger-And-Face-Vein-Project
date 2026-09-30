from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from backend.routers import auth, enroll, verify, admin, federated
from backend.config import settings

app = FastAPI(
    title="Privacy-Preserving Multibiometric Authentication API",
    description="Backend API for Face and Vein Biometrics with Homomorphic Encryption and Differential Privacy",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(enroll.router)
app.include_router(verify.router)
app.include_router(admin.router)
app.include_router(federated.router)

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "db_url": settings.DATABASE_URL.replace(settings.POSTGRES_PASSWORD, "****")}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
