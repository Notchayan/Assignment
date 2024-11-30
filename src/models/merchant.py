from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Merchant(BaseModel):
    merchant_id: str = Field(..., description="Unique identifier for the merchant")
    name: str = Field(..., description="Name of the merchant")
    business_type: str = Field(..., description="Type of business the merchant operates")
    registration_date: datetime = Field(..., description="Date when the merchant was registered")
    risk_score: Optional[float] = Field(0.0, ge=0.0, le=100.0, description="Current risk score of the merchant")
    avg_ticket: Optional[float] = Field(0.0, description="Average transaction amount for the merchant")
    contact_email: Optional[str] = Field(None, description="Contact email for the merchant")
    contact_phone: Optional[str] = Field(None, description="Contact phone number for the merchant")
