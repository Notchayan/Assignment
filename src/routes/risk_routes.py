from fastapi import APIRouter, HTTPException
from src.services.risk_calculator import RiskCalculatorService
from src.models.risk_profile import RiskProfileResponse

router = APIRouter()
risk_calculator = RiskCalculatorService()

@router.get("/risks/{merchant_id}", response_model=RiskProfileResponse)
async def get_risk_profile(merchant_id: str):
    try:
        risk_profile = await risk_calculator.analyze_merchant_risk(merchant_id)
        return risk_profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
