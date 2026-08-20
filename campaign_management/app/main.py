from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import engine, Base

 
from app.models.user import User  
from app.models.campaign import Campaign  
from app.models.campaign_members import CampaignMember  
from app.models.campaign_task import CampaignTask

app = FastAPI(
    title="Marketing Campaign Management API",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Format lỗi HTTP cơ bản (400, 401, 403, 404)
@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
            "message": exc.detail
        }
    )

@app.get("/")
def root():
    return {"message": "Chào mừng đến với API Marketing Campaign Management"}

# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected"
    }
