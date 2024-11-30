from src.config.database import db

async def create_merchant(merchant_data: dict):
    return await db.merchant_collection.insert_one(merchant_data)

async def get_merchant(merchant_id: str):
    return await db.merchant_collection.find_one({"merchant_id": merchant_id})
