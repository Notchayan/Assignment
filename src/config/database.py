from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel
from typing import Optional

class Database:
    client: Optional[AsyncIOMotorClient] = None
    
    def __init__(self):
        self.merchant_db = None
        self.merchant_collection = None
        self.transaction_collection = None
        self.risk_pattern_collection = None

    async def connect_to_mongodb(self):
        """Connect to MongoDB."""
        try:
            self.client = AsyncIOMotorClient("mongodb://localhost:27017")
            self.merchant_db = self.client.merchant_risk_db
            
            # Initialize collections
            self.merchant_collection = self.merchant_db.merchants
            self.transaction_collection = self.merchant_db.transactions
            self.risk_pattern_collection = self.merchant_db.risk_patterns
            
            # Create indexes
            await self.create_indexes()
            print("Successfully connected to MongoDB")
            
        except Exception as e:
            print(f"Could not connect to MongoDB: {e}")
            raise e

    async def create_indexes(self):
        """Create necessary indexes for collections."""
        # Merchant indexes
        await self.merchant_collection.create_index("merchant_id", unique=True)
        await self.merchant_collection.create_index("business_type")
        await self.merchant_collection.create_index("registration_date")

        # Transaction indexes
        await self.transaction_collection.create_index("transaction_id", unique=True)
        await self.transaction_collection.create_index("merchant_id")
        await self.transaction_collection.create_index("timestamp")
        await self.transaction_collection.create_index([
            ("merchant_id", 1),
            ("timestamp", -1)
        ])

        # Risk pattern indexes
        await self.risk_pattern_collection.create_index("pattern_id", unique=True)
        await self.risk_pattern_collection.create_index("name", unique=True)

    async def close_mongodb_connection(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            print("MongoDB connection closed")

# Create a database instance
db = Database()
