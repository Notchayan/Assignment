from datetime import datetime
from typing import Dict, List
from src.config.database import db
from src.models.transaction import Transaction
from src.services.data_generator import DataGenerator

class TransactionProcessor:
    def __init__(self):
        self.data_generator = DataGenerator()

    async def process_transaction(self, transaction_data: Dict) -> Transaction:
        transaction = Transaction(**transaction_data)
        
        # Calculate risk score
        risk_score = self._calculate_transaction_risk(transaction)
        transaction.risk_score = risk_score
        
        # Flag suspicious transactions
        self._flag_suspicious_transaction(transaction)
        
        # Save transaction to database
        await db.transactions.insert_one(transaction.dict())
        
        return transaction

    def _calculate_transaction_risk(self, transaction: Transaction) -> float:
        # Use DataGenerator to calculate risk
        return self.data_generator._calculate_transaction_risk(
            amount=transaction.amount,
            merchant={"merchant_id": transaction.merchant_id, "avg_ticket": 100, "risk_score": 0.5},
            customer_id=transaction.customer_id,
            timestamp=transaction.timestamp
        )

    def _flag_suspicious_transaction(self, transaction: Transaction):
        # Example flagging logic
        if transaction.amount > 10000:
            transaction.amount_flag = True
        if transaction.timestamp.hour >= 23 or transaction.timestamp.hour <= 4:
            transaction.time_flag = True
        # Add more flagging logic as needed
