from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, constr
from pymongo import MongoClient
from pydantic.networks import HttpUrl

# Enums for constrained fields
class BusinessType(str, Enum):
    ELECTRONICS = "electronics"
    FASHION = "fashion"
    GROCERY = "grocery"
    HEALTHCARE = "healthcare"
    HOSPITALITY = "hospitality"
    OTHER = "other"

class BusinessModel(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    HYBRID = "hybrid"

class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    UPI = "upi"
    NET_BANKING = "net_banking"
    WALLET = "wallet"

class TransactionStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PENDING = "pending"

class Platform(str, Enum):
    WEB = "web"
    MOBILE = "mobile"
    POS = "pos"

# Pydantic models for data validation
class MerchantProfile(BaseModel):
    merchant_id: str = Field(..., description="Unique identifier for merchant")
    business_name: str = Field(..., min_length=1, max_length=100)
    business_type: BusinessType
    registration_date: datetime
    business_model: BusinessModel
    product_category: str
    average_ticket_size: float = Field(..., gt=0)
    gst_status: bool
    pan_number: constr(regex=r'^[A-Z]{5}[0-9]{4}[A-Z]$')
    epfo_registered: bool
    registered_address: str
    city: str
    state: str
    reported_revenue: float = Field(..., ge=0)
    employee_count: int = Field(..., ge=0)
    bank_account: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Transaction(BaseModel):
    transaction_id: str = Field(..., description="Unique identifier for transaction")
    merchant_id: str = Field(..., description="Reference to merchant")
    timestamp: datetime
    amount: float = Field(..., gt=0)
    customer_id: str
    device_id: str
    customer_location: str
    payment_method: PaymentMethod
    status: TransactionStatus
    product_category: str
    platform: Platform
    velocity_flag: bool = False
    amount_flag: bool = False
    time_flag: bool = False
    device_flag: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RiskPattern(BaseModel):
    pattern_id: str = Field(..., description="Unique identifier for risk pattern")
    name: str
    characteristics: dict
    red_flags: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# MongoDB connection and initialization
class Database:
    def __init__(self, connection_string: str = "mongodb://localhost:27017/"):
        self.client = MongoClient(connection_string)
        self.db = self.client.merchant_risk_db
        self.setup_collections()
        self.create_indexes()

    def setup_collections(self):
        """Initialize database collections"""
        self.merchants = self.db.merchants
        self.transactions = self.db.transactions
        self.risk_patterns = self.db.risk_patterns

    def create_indexes(self):
        """Create necessary indexes for better query performance"""
        # Merchant indexes
        self.merchants.create_index("merchant_id", unique=True)
        self.merchants.create_index("business_type")
        self.merchants.create_index("registration_date")

        # Transaction indexes
        self.transactions.create_index("transaction_id", unique=True)
        self.transactions.create_index("merchant_id")
        self.transactions.create_index("timestamp")
        self.transactions.create_index([("merchant_id", 1), ("timestamp", -1)])
        
        # Risk pattern indexes
        self.risk_patterns.create_index("pattern_id", unique=True)
        self.risk_patterns.create_index("name", unique=True)

# Initialize database connection
db = Database()
