from datetime import datetime, timedelta
from typing import Dict, List
from collections import defaultdict
import logging
from src.config.database import db
from src.models.transaction import Transaction
from src.utils.exceptions import GeneralAPIError

logger = logging.getLogger("TransactionSummarizer")

class TransactionSummarizer:
    async def generate_daily_summary(self, merchant_id: str, start_date: datetime, end_date: datetime) -> Dict:
        """Generate daily transaction summaries for a merchant."""
        try:
            daily_summaries = defaultdict(lambda: {"count": 0, "total_amount": 0.0})
            
            transactions = await db.transactions.find({
                "merchant_id": merchant_id,
                "timestamp": {"$gte": start_date, "$lte": end_date}
            }).to_list(None)

            for txn in transactions:
                date_key = txn['timestamp'].date().isoformat()
                daily_summaries[date_key]["count"] += 1
                daily_summaries[date_key]["total_amount"] += txn['amount']

            return dict(daily_summaries)

    async def analyze_peak_times(self, merchant_id: str, days: int = 30) -> Dict:
        """Identify peak transaction times for a merchant."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        hourly_stats = defaultdict(lambda: {"count": 0, "total_amount": 0.0})
        
        pipeline = [
            {
                "$match": {
                    "merchant_id": merchant_id,
                    "timestamp": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": {"$hour": "$timestamp"},
                    "count": {"$sum": 1},
                    "total_amount": {"$sum": "$amount"}
                }
            }
        ]
        
        results = await db.transactions.aggregate(pipeline).to_list(None)
        
        for result in results:
            hour = result["_id"]
            hourly_stats[hour] = {
                "count": result["count"],
                "total_amount": result["total_amount"]
            }
        
        return dict(hourly_stats)

    async def summarize_by_category(self, merchant_id: str, days: int = 30) -> Dict:
        """Summarize transactions by category."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        pipeline = [
            {
                "$match": {
                    "merchant_id": merchant_id,
                    "timestamp": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": "$category",
                    "count": {"$sum": 1},
                    "total_amount": {"$sum": "$amount"}
                }
            }
        ]
        
        results = await db.transactions.aggregate(pipeline).to_list(None)
        return {r["_id"]: {"count": r["count"], "total_amount": r["total_amount"]} for r in results}
