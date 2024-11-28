from fastapi import FastAPI
from src.routes.merchant_routes import router as merchant_router
from src.routes.risk_routes import router as risk_router
from src.routes.transaction_routes import router as transaction_router
from src.config.database import db
from src.routes.merchant_routes import validation_middleware
from motor.motor_asyncio import AsyncIOMotorClient
from src.middleware.validation import validation_middleware
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("MainApp")

app = FastAPI(
    title="Merchant Risk Analysis API",
    description="API for analyzing merchant risk patterns and transactions",
    version="1.0.0"
)

app.middleware("http")(validation_middleware)

@app.on_event("startup")
async def startup_db_client():
    try:
        await db.connect_to_mongodb()
        logger.info("Connected to MongoDB successfully.")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        # Optionally, exit the application
        import sys
        sys.exit(1)

@app.on_event("shutdown")
async def shutdown_db_client():
    await db.close_mongodb_connection()

app.include_router(merchant_router, prefix="/api")
app.include_router(risk_router, prefix="/api")
app.include_router(transaction_router, prefix="/api")
