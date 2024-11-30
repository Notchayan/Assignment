from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.routes.merchant_routes import router as merchant_router
from src.routes.risk_routes import router as risk_router
from src.routes.transaction_routes import router as transaction_router
from src.config.database import db
from src.middleware.validation import validation_middleware
from src.middleware.exception_handler import custom_exception_handler, validation_exception_handler
import logging
from src.utils.exceptions import DatabaseConnectionError, MerchantNotFoundError, RiskProfileNotFoundError, InvalidTransactionError, GeneralAPIError
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

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

# Register Middleware
app.middleware("http")(validation_middleware)

# Register Routers
app.include_router(merchant_router, prefix="/api")
app.include_router(risk_router, prefix="/api")
app.include_router(transaction_router, prefix="/api")

# Exception Handlers
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(DatabaseConnectionError, custom_exception_handler)
app.add_exception_handler(MerchantNotFoundError, custom_exception_handler)
app.add_exception_handler(RiskProfileNotFoundError, custom_exception_handler)
app.add_exception_handler(InvalidTransactionError, custom_exception_handler)
app.add_exception_handler(GeneralAPIError, custom_exception_handler)

@app.on_event("startup")
async def startup_db_client():
    try:
        await db.connect_to_mongodb()
        logger.info("Connected to MongoDB successfully.")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise DatabaseConnectionError(detail=str(e))

@app.on_event("shutdown")
async def shutdown_db_client():
    try:
        await db.close_mongodb_connection()
        logger.info("Disconnected from MongoDB successfully.")
    except Exception as e:
        logger.error(f"Error disconnecting from MongoDB: {e}")
        # Not raising exception on shutdown
