from datetime import datetime, time, timedelta
from typing import List, Dict, Optional, Callable
from collections import defaultdict, Counter
import logging
import math

from src.models.risk_profile import (
    RiskPattern, RiskPatternType, RiskProfileResponse, PatternCharacteristics,
    RiskStatus
)
from src.config.database import db

from enum import Enum, auto
from dataclasses import dataclass, field

# Setup logging
logger = logging.getLogger("RiskCalculatorService")
logging.basicConfig(level=logging.INFO)

# Define Strategy Classes

class RiskEvaluationStrategy:
    """
    A strategy-based approach to risk pattern detection.
    Allows for dynamic, pluggable risk evaluation methods.
    """
    @staticmethod
    def exponential_risk_scaling(base_score: float, intensity: float) -> float:
        """
        Create non-linear risk scaling that emphasizes high-risk signals.

        Args:
            base_score: Initial risk score.
            intensity: Measure of pattern severity.

        Returns:
            Scaled risk score with exponential growth.
        """
        return min(1.0, base_score * (1 + math.log(1 + intensity)))

    @staticmethod
    def calculate_pattern_correlation(patterns: List[RiskPattern]) -> float:
        """
        Assess risk correlation between detected patterns.

        Prevents double-counting risks while recognizing compounding effects.

        Args:
            patterns: List of detected risk patterns.

        Returns:
            Correlation coefficient representing interconnected risks.
        """
        unique_pattern_types = len(set(p.name for p in patterns))
        return min(1.0, unique_pattern_types * 0.25)


class PatternCorrelationStrategy:
    @staticmethod
    def assess_pattern_overlap(pattern1: RiskPattern, pattern2: RiskPattern) -> float:
        """
        Determine risk pattern overlap and potential systemic risk.

        Args:
            pattern1: First risk pattern.
            pattern2: Second risk pattern.

        Returns:
            Correlation coefficient.
        """
        overlap_factors = [
            # Example: Placeholder for actual overlap logic
            0.0  # Implement actual overlap logic here
        ]
        
        # Avoid division by zero
        if not overlap_factors or len(overlap_factors) == 0:
            return 0.0
        return sum(overlap_factors) / len(overlap_factors)


@dataclass
class RiskAnalysisContext:
    """
    Comprehensive context for risk analysis.
    Provides rich metadata for risk evaluation.
    """
    merchant_id: str
    analysis_window: timedelta = field(default_factory=lambda: timedelta(days=30))
    historical_risk_trends: Optional[Dict] = None
    external_risk_signals: Optional[Dict] = None


class AdvancedRiskCalculator:
    def __init__(self, context: RiskAnalysisContext):
        self.context = context
        self.pattern_correlator = PatternCorrelationStrategy()
        self.logger = logging.getLogger("AdvancedRiskCalculator")
    
    async def calculate_comprehensive_risk(self, detected_patterns: List[RiskPattern]) -> float:
        """
        Calculate a multi-dimensional risk score.

        Args:
            detected_patterns: List of detected risk patterns.

        Returns:
            Comprehensive risk score.
        """
        base_risk_scores = [
            pattern.confidence_score * self._get_pattern_weight(pattern.name)
            for pattern in detected_patterns
        ]

        # Apply non-linear scaling
        scaled_risks = [
            RiskEvaluationStrategy.exponential_risk_scaling(score, 0.5)
            for score in base_risk_scores
        ]

        # Calculate pattern correlation penalty
        correlation_penalty = self._calculate_pattern_correlation(detected_patterns)

        # Incorporate external risk signals
        external_risk_factor = self._assess_external_risk_signals()

        comprehensive_score = (
            sum(scaled_risks) * (1 - correlation_penalty) *
            (1 + external_risk_factor)
        )

        return min(comprehensive_score, 1.0)
    
    def _calculate_pattern_correlation(self, patterns: List[RiskPattern]) -> float:
        """Calculate risk pattern interdependencies."""
        if len(patterns) <= 1:
            return 0.0

        correlation_matrix = [
            self.pattern_correlator.assess_pattern_overlap(p1, p2)
            for i, p1 in enumerate(patterns)
            for j, p2 in enumerate(patterns[i+1:])
        ]

        if not correlation_matrix:
            return 0.0

        average_correlation = sum(correlation_matrix) / len(correlation_matrix)
        self.logger.info(f"Average pattern correlation: {average_correlation}")
        return average_correlation
    
    def _assess_external_risk_signals(self) -> float:
        """
        Incorporate external risk indicators.

        Could include:
        - Merchant credit score
        - Industry risk ratings
        - Historical chargeback rates
        """
        # Placeholder for more complex external risk assessment
        if self.context.external_risk_signals:
            return self.context.external_risk_signals.get("external_risk_multiplier", 0.1)
        return 0.0

    def _get_pattern_weight(self, pattern_name: str) -> float:
        """Retrieve weight for a given pattern."""
        weight_map = {
            RiskPatternType.LATE_NIGHT: 0.2,
            RiskPatternType.VELOCITY_SPIKE: 0.3,
            RiskPatternType.SPLIT_TRANSACTIONS: 0.25,
            RiskPatternType.ROUND_AMOUNT: 0.15,
            RiskPatternType.CUSTOMER_CONCENTRATION: 0.1,
        }
        return weight_map.get(pattern_name, 0.1)


class RiskCalculatorService:
    def __init__(self, db_client):
        self.db = db_client
        self.pattern_configs = self._load_pattern_configs()
        self.risk_profile_repo = RiskProfileRepository(db_client)
        self.logger = logging.getLogger("RiskCalculatorService")

    def _load_pattern_configs(self) -> Dict:
        """Dynamically load risk pattern configurations."""
        return {
            RiskPatternType.LATE_NIGHT: {
                "time_window": "23:00-04:00",
                "volume_percentage": 70,
                "min_daily_transactions": 20,
                "pattern_duration": "2-3 weeks",
            },
            RiskPatternType.VELOCITY_SPIKE: {
                "normal_daily_txns": "10-20",
                "spike_daily_txns": "200-300",
                "spike_duration": "2-3 days",
                "pattern_frequency": "Once every 2-3 weeks",
            },
            RiskPatternType.SPLIT_TRANSACTIONS: {
                "original_amount": "50000-100000",
                "split_count": "5-10",
                "time_window": 30,  # in minutes
            },
            RiskPatternType.ROUND_AMOUNT: {
                "amount_pattern": [9999, 19999, 29999],
                "frequency_threshold": 0.70,
            },
            RiskPatternType.CUSTOMER_CONCENTRATION: {
                "customer_count": (5, 10),
                "volume_concentration": 0.80,
            },
        }

    async def analyze_merchant_risk(
        self, merchant_id: str, days: int = 30
    ) -> RiskProfileResponse:
        logger.info(f"Analyzing risk for merchant: {merchant_id}")
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            # Fetch transactions
            transactions = await self._fetch_transactions(merchant_id, start_date, end_date)
            if not transactions:
                logger.warning("No transactions found for merchant.")
                return self._create_empty_risk_profile(merchant_id)

            detected_patterns, risk_factors = [], []

            # Create RiskAnalysisContext
            context = RiskAnalysisContext(
                merchant_id=merchant_id,
                analysis_window=timedelta(days=days),
                # Add more context if needed
            )
            advanced_calculator = AdvancedRiskCalculator(context)

            # Analyze patterns
            for pattern_type, config in self.pattern_configs.items():
                logger.info(f"Detecting pattern: {pattern_type}")
                pattern = await self._detect_pattern(transactions, pattern_type, config)
                if pattern:
                    detected_patterns.append(pattern)
                    risk_factors.append(pattern.name)

            # Calculate overall score using advanced calculator
            overall_score = await advanced_calculator.calculate_comprehensive_risk(detected_patterns)
            logger.info(f"Overall risk score for merchant {merchant_id}: {overall_score*100}")

            return RiskProfileResponse(
                merchant_id=merchant_id,
                overall_risk_score=overall_score * 100,  # Scaling to 0-100
                detected_patterns=detected_patterns,
                last_updated=datetime.utcnow(),
                risk_factors=risk_factors,
                monitoring_status=self._determine_risk_status(overall_score * 100),
                review_required=overall_score * 100 > 70,
            )
        except Exception as e:
            logger.error(f"Error analyzing risk for merchant {merchant_id}: {e}", exc_info=True)
            raise

    async def _fetch_transactions(
        self, merchant_id: str, start_date: datetime, end_date: datetime
    ) -> List[Dict]:
        """Fetch transactions from the database."""
        return await db.transaction_collection.find(
            {"merchant_id": merchant_id, "timestamp": {"$gte": start_date, "$lte": end_date}}
        ).to_list(None)

    def _create_empty_risk_profile(self, merchant_id: str) -> RiskProfileResponse:
        """Create an empty risk profile for merchants with no data."""
        return RiskProfileResponse(
            merchant_id=merchant_id,
            overall_risk_score=0.0,
            detected_patterns=[],
            last_updated=datetime.utcnow(),
            risk_factors=[],
            monitoring_status="low_risk",
            review_required=False,
        )

    def _determine_risk_status(self, score: float) -> RiskStatus:
        """Determine the risk monitoring status based on the overall score."""
        if score > 70:
            return RiskStatus.HIGH
        elif score > 40:
            return RiskStatus.MEDIUM
        return RiskStatus.LOW

    async def _detect_pattern(
        self, transactions: List[Dict], pattern_type: RiskPatternType, config: Dict
    ) -> Optional[RiskPattern]:
        """Detect a specific risk pattern."""
        if not transactions:
            return None

        pattern_detectors: Dict[RiskPatternType, Callable[[List[Dict], Dict], Optional[RiskPattern]]] = {
            RiskPatternType.LATE_NIGHT: self._detect_late_night_pattern,
            RiskPatternType.VELOCITY_SPIKE: self._detect_velocity_spike,
            RiskPatternType.SPLIT_TRANSACTIONS: self._detect_split_transactions,
            RiskPatternType.ROUND_AMOUNT: self._detect_round_amount_pattern,
            RiskPatternType.CUSTOMER_CONCENTRATION: self._detect_customer_concentration,
        }

        detector = pattern_detectors.get(pattern_type)
        if detector:
            return await detector(transactions, config)
        return None

    # Example pattern detection methods
    async def _detect_late_night_pattern(self, transactions: List[Dict], config: Dict) -> Optional[RiskPattern]:
        """Detect late-night trading patterns."""
        logger.info("Detecting Late Night pattern.")
        time_window = config.get("time_window", "23:00-04:00")
        start_hour, end_hour = map(int, time_window.replace(":", "").split("-"))
        count = sum(1 for txn in transactions if start_hour <= txn['timestamp'].hour or txn['timestamp'].hour < end_hour)
        if count >= config.get("threshold", 50):
            return RiskPattern(
                pattern_id=f"pattern_{pattern_type.value}",
                name=pattern_type.value,
                confidence_score=count / config["threshold"],
                characteristics=config,
                red_flags=[f"{count} transactions during late-night hours."],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        return None

    async def _detect_velocity_spike(self, transactions: List[Dict], config: Dict) -> Optional[RiskPattern]:
        """Detect velocity spike patterns."""
        logger.info("Detecting Velocity Spike pattern.")
        threshold = config.get("threshold", 100)
        time_window_seconds = config.get("time_window_seconds", 3600)
        transaction_times = sorted(txn['timestamp'] for txn in transactions)
        spike_count = 0
        window_start = 0
        for window_end in range(len(transaction_times)):
            while (transaction_times[window_end] - transaction_times[window_start]).total_seconds() > time_window_seconds:
                window_start += 1
            window_size = window_end - window_start + 1
            if window_size >= threshold:
                spike_count += 1
        if spike_count > 0:
            return RiskPattern(
                pattern_id="pattern_velocity_spike",
                name=RiskPatternType.VELOCITY_SPIKE.value,
                confidence_score=spike_count / threshold,
                characteristics=config,
                red_flags=[f"{spike_count} velocity spikes detected."],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        return None

    async def _detect_split_transactions(self, transactions: List[Dict], config: Dict) -> Optional[RiskPattern]:
        """Detect split transactions patterns."""
        logger.info("Detecting Split Transactions pattern.")
        threshold_amount = config.get("threshold_amount", 1000)
        max_split = config.get("max_split", 5)
        split_count = sum(1 for txn in transactions if txn['amount'] > threshold_amount)
        if split_count >= max_split:
            return RiskPattern(
                pattern_id="pattern_split_transactions",
                name=RiskPatternType.SPLIT_TRANSACTIONS.value,
                confidence_score=split_count / max_split,
                characteristics=config,
                red_flags=[f"{split_count} split transactions detected."],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        return None

    async def _detect_round_amount_pattern(self, transactions: List[Dict], config: Dict) -> Optional[RiskPattern]:
        """Detect Round Amount patterns."""
        logger.info("Detecting Round Amount pattern.")
        round_factor = config.get("round_factor", 10)
        min_round_transactions = config.get("min_round_transactions", 5)
        round_transactions = [txn for txn in transactions if txn['amount'] % round_factor == 0]
        if len(round_transactions) >= min_round_transactions:
            confidence = len(round_transactions) / min_round_transactions
            return RiskPattern(
                pattern_id="pattern_round_amount",
                name=RiskPatternType.ROUND_AMOUNT.value,
                confidence_score=confidence,
                characteristics=config,
                red_flags=[f"{len(round_transactions)} transactions with amounts divisible by {round_factor}."],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        return None

    async def _detect_customer_concentration(self, transactions: List[Dict], config: Dict) -> Optional[RiskPattern]:
        """Detect Customer Concentration patterns."""
        logger.info("Detecting Customer Concentration pattern.")
        customer_threshold = config.get("customer_threshold", 50)
        customer_counts = Counter(txn['customer_id'] for txn in transactions)
        concentrated_customers = [customer for customer, count in customer_counts.items() if count >= customer_threshold]
        if concentrated_customers:
            red_flags = [
                f"Customer {customer} has {customer_counts[customer]} transactions."
                for customer in concentrated_customers
            ]
            confidence = len(concentrated_customers) / customer_threshold
            return RiskPattern(
                pattern_id="pattern_customer_concentration",
                name=RiskPatternType.CUSTOMER_CONCENTRATION.value,
                confidence_score=confidence,
                characteristics=config,
                red_flags=red_flags,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        return None
