# src/utils/exceptions.py

from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

class DatabaseConnectionError(HTTPException):
    def __init__(self, detail: str = "Failed to connect to the database."):
        super().__init__(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

class MerchantNotFoundError(HTTPException):
    def __init__(self, merchant_id: str):
        detail = f"Merchant with ID '{merchant_id}' not found."
        super().__init__(status_code=HTTP_404_NOT_FOUND, detail=detail)

class RiskProfileNotFoundError(HTTPException):
    def __init__(self, merchant_id: str):
        detail = f"Risk profile for Merchant ID '{merchant_id}' not found."
        super().__init__(status_code=HTTP_404_NOT_FOUND, detail=detail)
        
class InvalidTransactionError(HTTPException):
    def __init__(self, detail: str = "Invalid transaction data provided."):
        super().__init__(status_code=HTTP_400_BAD_REQUEST, detail=detail)
        
class GeneralAPIError(HTTPException):
    def __init__(self, detail: str = "An unexpected error occurred."):
        super().__init__(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)