from fastapi import FastAPI, HTTPException
from app.core.exceptions import http_exception_handler

from app.db.database import engine, Base

from app.models.user import User  
from app.models.campaign import Campaign, CampaignMember   
from app.models.campaign_task import CampaignTask

from app.routers.auth import router as router
from app.routers.users import router as users_router
from app.routers.campaign import router as campaign_rt
from app.routers.campaign_task import router as campaign_task

app = FastAPI(
    title="Marketing Campaign Management API",
    version="1.0.0"
)

app.add_exception_handler(HTTPException, http_exception_handler)

app.include_router(router)
app.include_router(users_router)
app.include_router(campaign_rt)
app.include_router(campaign_task)


Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Chào mừng đến với API Marketing Campaign Management"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected"
    }

