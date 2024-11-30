from typing import Optional, List
from src.config.database import db
from src.models.transaction import TransactionResponse


class TransactionRepository:
    async def get_transaction(self, transaction_id: str) -> Optional[TransactionResponse]:
        """Fetch a transaction by its ID."""
        transaction_data = await db.transactions.find_one({"transaction_id": transaction_id})
        if transaction_data:
            return TransactionResponse(**transaction_data)
        return None

    async def list_transactions(self, merchant_id: str) -> List[TransactionResponse]:
        """List all transactions for a given merchant."""
        transactions_data = await db.transactions.find({"merchant_id": merchant_id}).to_list(None)
        return [TransactionResponse(**txn) for txn in transactions_data]

    async def save_transaction(self, transaction: TransactionResponse) -> None:
        """Save a transaction to the database."""
        await db.transactions.insert_one(transaction.dict())
