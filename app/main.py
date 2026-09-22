from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="Support Ticket API")
app.include_router(router)
