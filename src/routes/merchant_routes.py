from fastapi import APIRouter, HTTPException, Depends, Request
from src.services.risk_calculator import RiskCalculatorService
from src.config.database import db
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("InitializeDB")

router = APIRouter()
risk_calculator = RiskCalculatorService()

def get_risk_calculator():
    return RiskCalculatorService()

class MerchantIDPathParams(BaseModel):
    merchant_id: str = Field(..., regex="^merchant_[0-9a-fA-F]{24}$")  # Example regex

@router.get("/merchants/{merchant_id}/risk-profile")
async def get_merchant_risk_profile(merchant: MerchantIDPathParams = Depends()):
    try:
        risk_profile = await risk_calculator.analyze_merchant_risk(merchant.merchant_id)
        return risk_profile
    except Exception as e:
        logger.error(f"Error analyzing risk for merchant {merchant.merchant_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/merchants/{merchant_id}")
async def get_merchant(merchant_id: str):
    merchant = await db.merchants.find_one({"merchant_id": merchant_id})
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return merchant

@router.get("/transactions/{transaction_id}")
async def get_transaction(transaction_id: str):
    transaction = await db.transactions.find_one({"transaction_id": transaction_id})
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

async def validation_middleware(request: Request, call_next):
    # Placeholder for request validation logic
    response = await call_next(request)
    return response

async def main():
    db = Database()
    # Add initialization logic, e.g., inserting default data

if __name__ == "__main__":
    asyncio.run(main())
