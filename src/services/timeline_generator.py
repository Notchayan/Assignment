from datetime import datetime
from typing import List, Dict
from src.models.timeline_event import TimelineEvent
from src.config.database import db
import logging
import redis
import json

logger = logging.getLogger("TimelineGenerator")

class TimelineGenerator:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.event_cache_ttl = 3600  # 1 hour

    async def generate_events(self, merchant_id: str, risk_profile: Dict, summaries: Dict) -> List[TimelineEvent]:
        """Generate timeline events based on risk profile and transaction summaries."""
        events = []
        cache_key = f"timeline_events:{merchant_id}"
        
        # Check cache first
        cached_events = self.redis_client.get(cache_key)
        if cached_events:
            return [TimelineEvent(**event) for event in json.loads(cached_events)]
        
        # Generate daily summary events
        for date, summary in summaries.items():
            event = TimelineEvent(
                merchant_id=merchant_id,
                event_type="DAILY_SUMMARY",
                timestamp=datetime.fromisoformat(date),
                description=f"Daily Summary: {summary['count']} transactions, "
                          f"Total: ${summary['total_amount']:,.2f}",
                severity="INFO"
            )
            events.append(event)
        
        # Process risk-based events
        if risk_profile["risk_score"] > 70:
            event = TimelineEvent(
                merchant_id=merchant_id,
                event_type="HIGH_RISK_ALERT",
                timestamp=datetime.utcnow(),
                description=f"High risk score detected: {risk_profile['risk_score']}",
                severity="HIGH",
                metadata={"risk_factors": risk_profile["risk_factors"]}
            )
            events.append(event)
        
        # Cache the events
        if events:
            await db.timeline_events.insert_many([event.dict() for event in events])
            self.redis_client.setex(
                cache_key,
                self.event_cache_ttl,
                json.dumps([event.dict() for event in events])
            )
        
        return events

    async def get_merchant_timeline(self, merchant_id: str, start_date: datetime, end_date: datetime) -> List[TimelineEvent]:
        """Retrieve timeline events for a merchant within a date range."""
        events = await db.timeline_events.find({
            "merchant_id": merchant_id,
            "timestamp": {"$gte": start_date, "$lte": end_date}
        }).sort("timestamp", -1).to_list(None)
        
        return [TimelineEvent(**event) for event in events]
