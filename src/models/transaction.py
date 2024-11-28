from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class TransactionRequest(BaseModel):
    merchant_id: str = Field(..., description="Reference to merchant")
    timestamp: datetime
    amount: float = Field(..., gt=0)
    customer_id: str
    device_id: str
    customer_location: str
    payment_method: str
    status: str
    product_category: str
    platform: str

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
