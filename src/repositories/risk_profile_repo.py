from typing import Optional
from src.config.database import db
from src.models.risk_profile import RiskProfileResponse
from src.utils.exceptions import RiskProfileNotFoundError, GeneralAPIError
import logging

logger = logging.getLogger("RiskProfileRepository")

class RiskProfileRepository:
    async def get_risk_profile(self, merchant_id: str) -> Optional[RiskProfileResponse]:
        """Fetch a risk profile for a given merchant."""
        try:
            risk_profile_data = await db.risk_profiles.find_one({"merchant_id": merchant_id})
            if risk_profile_data:
                return RiskProfileResponse(**risk_profile_data)
            logger.warning(f"Risk profile not found for merchant_id: {merchant_id}")
            raise RiskProfileNotFoundError(merchant_id=merchant_id)
        except RiskProfileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error fetching risk profile for merchant_id {merchant_id}: {e}")
            raise GeneralAPIError(detail=str(e))
    
    async def save_risk_profile(self, risk_profile: RiskProfileResponse) -> None:
        """Save or update a risk profile in the database."""
        try:
            result = await db.risk_profiles.update_one(
                {"merchant_id": risk_profile.merchant_id},
                {"$set": risk_profile.dict()},
                upsert=True
            )
            if result.upserted_id:
                logger.info(f"Created new risk profile for merchant_id: {risk_profile.merchant_id}")
            else:
                logger.info(f"Updated risk profile for merchant_id: {risk_profile.merchant_id}")
        except Exception as e:
            logger.error(f"Error saving risk profile for merchant_id {risk_profile.merchant_id}: {e}")
            raise GeneralAPIError(detail=str(e))
