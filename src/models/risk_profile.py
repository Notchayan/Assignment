from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class RiskPatternType(str, Enum):
    LATE_NIGHT = "late_night_trading"
    VELOCITY_SPIKE = "sudden_activity_spike"
    SPLIT_TRANSACTIONS = "split_transactions"
    ROUND_AMOUNT = "round_amount_pattern"
    CUSTOMER_CONCENTRATION = "customer_concentration"

class PatternCharacteristics(BaseModel):
    time_window: Optional[str]
    volume_percentage: Optional[float]
    min_daily_transactions: Optional[int]
    pattern_duration: Optional[str]
    normal_daily_txns: Optional[str]
    spike_daily_txns: Optional[str]
    spike_duration: Optional[str]
    pattern_frequency: Optional[str]
    amount_pattern: Optional[List[float]]
    frequency: Optional[str]
    customer_count: Optional[str]
    volume_concentration: Optional[str]
    regular_frequency: Optional[str]
    relationship: Optional[str]

class RiskPattern(BaseModel):
    name: RiskPatternType
    characteristics: PatternCharacteristics
    red_flags: List[str]
    confidence_score: float = Field(0.0, ge=0.0, le=1.0)
    detection_time: datetime = Field(default_factory=datetime.utcnow)
    supporting_evidence: List[str] = []
    transaction_ids: List[str] = []

class RiskProfileResponse(BaseModel):
    merchant_id: str
    overall_risk_score: float = Field(..., ge=0.0, le=100.0)
    detected_patterns: List[RiskPattern]
    last_updated: datetime
    risk_factors: List[str]
    monitoring_status: str
    review_required: bool
