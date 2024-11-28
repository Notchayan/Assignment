from fastapi import APIRouter, HTTPException
from src.config.database import db
from src.models.transaction import TransactionRequest, TransactionResponse
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(transaction: TransactionRequest):
    transaction_data = transaction.dict()
    transaction_data["transaction_id"] = f"TXN-{uuid.uuid4().hex}"
    transaction_data["created_at"] = datetime.utcnow()
    await db.transactions.insert_one(transaction_data)
    return transaction_data

@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: str):
    transaction = await db.transactions.find_one({"transaction_id": transaction_id})
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.get("/transactions")
async def list_transactions(merchant_id: str):
    transactions = await db.transactions.find({"merchant_id": merchant_id}).to_list(None)
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found for this merchant")
    return transactions
