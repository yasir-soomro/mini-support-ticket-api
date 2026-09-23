from fastapi import FastAPI
from app.routers.tickets import router

app = FastAPI(title="Support Ticket API")
app.include_router(router)
