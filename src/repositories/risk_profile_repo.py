from typing import Optional
from src.config.database import db
from src.models.risk_profile import RiskProfileResponse

class RiskProfileRepository:
    async def get_risk_profile(self, merchant_id: str) -> Optional[RiskProfileResponse]:
        """Fetch a risk profile for a given merchant."""
        risk_profile_data = await db.risk_profiles.find_one({"merchant_id": merchant_id})
        if risk_profile_data:
            return RiskProfileResponse(**risk_profile_data)
        return None

    async def save_risk_profile(self, risk_profile: RiskProfileResponse) -> None:
        """Save or update a risk profile in the database."""
        await db.risk_profiles.update_one(
            {"merchant_id": risk_profile.merchant_id},
            {"$set": risk_profile.dict()},
            upsert=True
        )
