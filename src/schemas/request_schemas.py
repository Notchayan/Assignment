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
