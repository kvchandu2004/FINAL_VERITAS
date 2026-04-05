from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routers import auth, manuscripts, reports, dashboard
from app.database import engine
from app.models import user, manuscript, report
import logging
from app.database import engine
print(engine.url)

# Create all tables
user.Base.metadata.create_all(bind=engine)
manuscript.Base.metadata.create_all(bind=engine)
report.Base.metadata.create_all(bind=engine)

# Create app only ONCE
app = FastAPI(
    title="VERITAS API",
    version="1.0.0",
    description="AI-Powered Platform for Proactive Research Integrity Analysis",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Routers
app.include_router(auth.router)
app.include_router(manuscripts.router)
app.include_router(reports.router)
app.include_router(dashboard.router)

#Root route
@app.get("/")
async def root():
    return {"message": "VERITAS Backend is running!"}

# Exception handler
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
