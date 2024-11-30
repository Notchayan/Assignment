import pytest
from src.services.data_processor import DataProcessorService
from src.utils.exceptions import GeneralAPIError
from unittest.mock import AsyncMock, patch
from src.models.risk_profile import RiskPattern

@pytest.fixture
def data_processor_service():
    return DataProcessorService()

@pytest.mark.asyncio
async def test_summarize_transactions_success(data_processor_service):
    merchant_id = "merchant_1234567890abcdef12345678"
    days = 30
    mock_transactions = [
        {"amount": 100.0, "timestamp": "2023-09-01T12:00:00Z"},
        {"amount": 200.0, "timestamp": "2023-09-02T12:00:00Z"}
    ]

    with patch("src.services.data_processor.db.transaction_collection.find") as mock_find:
        mock_find.return_value.to_list = AsyncMock(return_value=mock_transactions)
        summary = await data_processor_service.summarize_transactions(merchant_id, days)
        assert summary["total_transactions"] == 2
        assert summary["total_amount"] == 300.0
        assert summary["average_transaction_amount"] == 150.0
        assert summary["max_transaction_amount"] == 200.0
        assert summary["min_transaction_amount"] == 100.0
        assert summary["transaction_velocity"] == 0.06666666666666667

@pytest.mark.asyncio
async def test_summarize_transactions_no_transactions(data_processor_service):
    merchant_id = "merchant_1234567890abcdef12345678"
    days = 30

    with patch("src.services.data_processor.db.transaction_collection.find") as mock_find:
        mock_find.return_value.to_list = AsyncMock(return_value=[])
        summary = await data_processor_service.summarize_transactions(merchant_id, days)
        assert summary["total_transactions"] == 0
        assert summary["total_amount"] == 0.0
        assert summary["average_transaction_amount"] == 0.0
        assert summary["max_transaction_amount"] == 0.0
        assert summary["min_transaction_amount"] == 0.0
        assert summary["transaction_velocity"] == 0.0

@pytest.mark.asyncio
async def test_calculate_risk_metrics(data_processor_service):
    merchant_id = "merchant_1234567890abcdef12345678"
    summary = {
        "transaction_velocity": 60.0,
        "average_transaction_amount": 12000.0
    }
    detected_patterns = [
        RiskPattern(name="High Velocity Spike", details="..."),
        RiskPattern(name="Large Transaction Amounts", details="...")
    ]

    risk_score = await data_processor_service.calculate_risk_metrics(merchant_id, summary, detected_patterns)
    expected_score = 0.1 + (1.0 * 0.3) + (1.0 * 0.3) + (0.4 * 0.4)  # 0.1 + 0.3 + 0.3 + 0.16 = 0.86
    assert risk_score == expected_score

@pytest.mark.asyncio
async def test_generate_timeline_events(data_processor_service):
    merchant_id = "merchant_1234567890abcdef12345678"
    detected_patterns = [
        RiskPattern(name="High Velocity Spike", details="..."),
        RiskPattern(name="Large Transaction Amounts", details="...")
    ]

    with patch("src.services.data_processor.db.timeline_events.insert_many") as mock_insert:
        mock_insert.return_value = AsyncMock()
        events = await data_processor_service.generate_timeline_events(merchant_id, detected_patterns)
        assert len(events) == 2
        mock_insert.assert_awaited_once()
