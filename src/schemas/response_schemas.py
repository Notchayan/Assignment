from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

class TransactionResponse(BaseModel):
    transaction_id: str
    merchant_id: str
    timestamp: datetime
    amount: float
    customer_id: str
    device_id: str
    customer_location: str
    payment_method: str
    status: str
    product_category: str
    platform: str
    velocity_flag: bool
    amount_flag: bool
    time_flag: bool
    device_flag: bool
    created_at: datetime

class RiskProfileResponse(BaseModel):
    merchant_id: str
    overall_risk_score: float = Field(..., ge=0.0, le=100.0)
    detected_patterns: List[RiskPattern]
    last_updated: datetime
    risk_factors: List[str]
    monitoring_status: str
    review_required: bool
