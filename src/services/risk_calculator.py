from datetime import datetime, time, timedelta
from typing import List, Dict, Optional, Callable
from collections import defaultdict, Counter
import logging
import math
import json
from functools import lru_cache
import redis
import uuid

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
    """
    RiskCalculatorService: Core service for merchant risk analysis and pattern detection.

    This service implements sophisticated risk analysis algorithms to evaluate merchant behavior
    and detect potential fraud patterns. It processes transaction data through multiple pattern
    detection algorithms and generates comprehensive risk profiles.

    Key Features:
        - Multi-pattern risk detection
        - Configurable risk thresholds
        - Timeline event generation
        - Risk score calculation and categorization

    Usage:
        calculator = RiskCalculatorService()
        risk_profile = await calculator.analyze_merchant_risk(merchant_id="merchant_123")

    Author: [Your Name]
    Last Modified: [Date]
    """
    def __init__(self, db_client):
        self.db = db_client
        self.pattern_configs = self._load_pattern_configs()
        self.redis_client = redis.Redis(
            host='localhost', 
            port=6379, 
            db=0,
            decode_responses=True
        )
        self.cache_ttl = {
            'merchant_profile': 3600,  # 1 hour
            'risk_metrics': 1800,      # 30 minutes
            'pattern_results': 900     # 15 minutes
        }
        self.pattern_weights = {
            'late_night': 0.2,
            'velocity_spike': 0.25,
            'split_transactions': 0.2,
            'round_amount': 0.15,
            'customer_concentration': 0.2
        }

    async def get_cached_pattern_results(self, merchant_id: str, pattern_type: str) -> Optional[Dict]:
        """Get cached pattern detection results."""
        cache_key = f"pattern:{merchant_id}:{pattern_type}"
        cached_result = self.redis_client.get(cache_key)
        return json.loads(cached_result) if cached_result else None

    async def cache_pattern_results(self, merchant_id: str, pattern_type: str, results: Dict):
        """Cache pattern detection results."""
        cache_key = f"pattern:{merchant_id}:{pattern_type}"
        self.redis_client.setex(
            cache_key,
            self.cache_ttl['pattern_results'],
            json.dumps(results)
        )

    async def _detect_pattern_with_cache(
        self, 
        transactions: List[Dict], 
        pattern_type: RiskPatternType, 
        config: Dict
    ) -> Optional[RiskPattern]:
        merchant_id = transactions[0]['merchant_id']
        cached_result = await self.get_cached_pattern_results(merchant_id, pattern_type.value)
        
        if cached_result:
            return RiskPattern(**cached_result)

        pattern = await self._detect_pattern(transactions, pattern_type, config)
        if pattern:
            await self.cache_pattern_results(merchant_id, pattern_type.value, pattern.dict())
        
        return pattern

    @lru_cache(maxsize=1000)
    async def get_cached_merchant_profile(self, merchant_id: str):
        """Cache merchant profiles in memory."""
        cache_key = f"merchant_profile:{merchant_id}"
        
        # Try to get from Redis first
        cached_profile = self.redis_client.get(cache_key)
        if cached_profile:
            return json.loads(cached_profile)
            
        # If not in cache, get from database
        profile = await self.db.merchants.find_one({"merchant_id": merchant_id})
        if profile:
            # Store in Redis
            self.redis_client.setex(
                cache_key,
                self.cache_ttl['merchant_profile'],
                json.dumps(profile)
            )
        return profile

    async def process_rule_based_patterns(self, transactions: List[Dict]) -> List[Dict]:
        """Process transactions through rule-based patterns."""
        events = []
        
        # Late night transaction pattern
        night_txns = [t for t in transactions if 23 <= t['timestamp'].hour or t['timestamp'].hour <= 4]
        if len(night_txns) / len(transactions) > 0.5:
            events.append({
                "type": "HIGH_RISK_PATTERN",
                "pattern": "LATE_NIGHT",
                "severity": "HIGH",
                "description": "Over 50% transactions during late night hours"
            })

        # Customer concentration pattern
        customer_counts = Counter(t['customer_id'] for t in transactions)
        max_customer_percentage = max(customer_counts.values()) / len(transactions)
        if max_customer_percentage > 0.8:
            events.append({
                "type": "HIGH_RISK_PATTERN",
                "pattern": "CUSTOMER_CONCENTRATION",
                "severity": "HIGH",
                "description": "Over 80% transactions from single customer"
            })

        return events

    async def cache_risk_metrics(self, merchant_id: str, risk_metrics: Dict):
        """Cache risk metrics in Redis."""
        cache_key = f"risk_metrics:{merchant_id}"
        self.redis_client.setex(
            cache_key,
            self.cache_ttl['risk_metrics'],
            json.dumps(risk_metrics)
        )

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
                pattern = await self._detect_pattern_with_cache(transactions, pattern_type, config)
                if pattern:
                    detected_patterns.append(pattern)
                    risk_factors.append(pattern.name)

            # Calculate comprehensive risk
            risk_score = await self.calculate_comprehensive_risk(detected_patterns)
            logger.info(f"Overall risk score for merchant {merchant_id}: {risk_score*100}")

            # Generate timeline events
            timeline_generator = TimelineGenerator()
            timeline_events = await timeline_generator.generate_events(
                merchant_id,
                {"risk_score": risk_score * 100, "risk_factors": risk_factors},
                daily_summaries
            )

            return RiskProfileResponse(
                merchant_id=merchant_id,
                overall_risk_score=risk_score * 100,  # Scaling to 0-100
                detected_patterns=detected_patterns,
                last_updated=datetime.utcnow(),
                risk_factors=risk_factors,
                monitoring_status=self.categorize_risk(risk_score),
                review_required=risk_score * 100 > 70,
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

    def categorize_risk(self, risk_score: float) -> str:
        """Categorize merchant based on risk score."""
        if risk_score > 0.7:
            return "HIGH_RISK"
        elif risk_score > 0.4:
            return "MEDIUM_RISK"
        return "LOW_RISK"

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
        """Enhanced split transaction detection with temporal clustering."""
        time_window = config.get('time_window_minutes', 30)
        amount_threshold = config.get('amount_threshold', 10000)
        min_transactions = config.get('min_transactions', 3)
        
        # Sort transactions by timestamp
        sorted_txns = sorted(transactions, key=lambda x: x['timestamp'])
        clusters = []
        current_cluster = []
        
        for txn in sorted_txns:
            if not current_cluster:
                current_cluster.append(txn)
            else:
                time_diff = (txn['timestamp'] - current_cluster[-1]['timestamp']).total_seconds() / 60
                if time_diff <= time_window:
                    current_cluster.append(txn)
                else:
                    if len(current_cluster) >= min_transactions:
                        clusters.append(current_cluster)
                    current_cluster = [txn]
        
        if len(current_cluster) >= min_transactions:
            clusters.append(current_cluster)
        
        suspicious_clusters = []
        for cluster in clusters:
            total_amount = sum(t['amount'] for t in cluster)
            if total_amount >= amount_threshold:
                suspicious_clusters.append(cluster)
        
        if suspicious_clusters:
            return RiskPattern(
                pattern_id=f"pattern_split_transactions_{uuid.uuid4().hex[:8]}",
                name=RiskPatternType.SPLIT_TRANSACTIONS.value,
                confidence_score=len(suspicious_clusters) / len(clusters),
                characteristics={
                    "cluster_count": len(suspicious_clusters),
                    "average_cluster_size": sum(len(c) for c in suspicious_clusters) / len(suspicious_clusters),
                    "total_amount": sum(sum(t['amount'] for t in c) for c in suspicious_clusters)
                },
                red_flags=[
                    f"Found {len(suspicious_clusters)} suspicious transaction clusters",
                    f"Average cluster size: {sum(len(c) for c in suspicious_clusters) / len(suspicious_clusters):.1f} transactions"
                ]
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

    async def calculate_comprehensive_risk(self, merchant_id: str, summaries: Dict) -> float:
        risk_score = 0.0
        
        # Late night risk
        late_night_risk = await self._calculate_late_night_risk(merchant_id)
        risk_score += late_night_risk * self.pattern_weights["late_night"]
        
        # Velocity spike risk
        velocity_risk = await self._calculate_velocity_risk(merchant_id)
        risk_score += velocity_risk * self.pattern_weights["velocity_spike"]
        
        # Customer concentration risk
        concentration_risk = await self._calculate_concentration_risk(merchant_id)
        risk_score += concentration_risk * self.pattern_weights["customer_concentration"]
        
        # Inconsistent trends risk
        trend_risk = self._calculate_trend_risk(summaries)
        risk_score += trend_risk * self.pattern_weights["inconsistent_trends"]
        
        return min(risk_score, 1.0)  # Normalize to 0-1 range

    def _calculate_trend_risk(self, summaries: Dict) -> float:
        """Calculate trend risk based on transaction summaries."""
        # Implement trend risk calculation logic here
        return 0.0

    async def _calculate_late_night_risk(self, merchant_id: str) -> float:
        """Calculate late-night risk based on transaction summaries."""
        # Implement late-night risk calculation logic here
        return 0.0

    async def _calculate_velocity_risk(self, merchant_id: str) -> float:
        """Calculate velocity spike risk based on transaction summaries."""
        # Implement velocity spike risk calculation logic here
        return 0.0

    async def _calculate_concentration_risk(self, merchant_id: str) -> float:
        """Calculate customer concentration risk based on transaction summaries."""
        # Implement customer concentration risk calculation logic here
        return 0.0
