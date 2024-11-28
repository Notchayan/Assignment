from typing import List, Tuple, Dict, Optional, Generator
import random
import string
from datetime import datetime, timedelta
import uuid
from faker import Faker
import numpy as np
from dataclasses import dataclass
from enum import Enum
import pandas as pd
from scipy import stats

# Initialize Faker with multiple locales for more diverse data
fake = Faker(['en_US', 'en_GB', 'en_IN'])

class FraudPattern(Enum):
    LATE_NIGHT = "late_night_trading"
    VELOCITY_SPIKE = "sudden_activity_spike"
    SPLIT_TXN = "split_transactions"
    ROUND_AMOUNT = "round_amount_pattern"
    CUSTOMER_CONCENTRATION = "customer_concentration"
    NETWORK_ANOMALY = "network_pattern"
    BEHAVIORAL_SHIFT = "behavior_change"

@dataclass
class BusinessConfig:
    """Generalized business configuration"""
    category_weights: Dict[str, float]
    revenue_ranges: Dict[str, Tuple[float, float]]
    ticket_ranges: Dict[str, Tuple[float, float]]
    operating_hours: Dict[str, List[Tuple[int, int]]]
    seasonality: Dict[str, float]
    risk_factors: Dict[str, float]

@dataclass
class TransactionConfig:
    """Generalized transaction configuration"""
    volume_ranges: Dict[str, Tuple[int, int]]
    payment_methods: Dict[str, float]
    status_weights: Dict[str, float]
    platform_weights: Dict[str, float]
    time_patterns: Dict[str, List[Tuple[int, int]]]

@dataclass
class FraudConfig:
    """Advanced ML data generation configuration for complex fraud pattern simulation"""
    
    # Temporal dynamics and seasonality
    temporal_dynamics: Dict = {
        "time_windows": {
            "intraday": [(0, 6), (6, 12), (12, 18), (18, 24)],  # Multiple daily windows
            "weekly": {"weekday": (0.6, 1.2), "weekend": (1.3, 2.5)},  # Weekly patterns
            "monthly": {"start": 1.0, "mid": 1.4, "end": 1.8},  # Monthly cycles
            "seasonal": {"q1": 0.8, "q2": 1.0, "q3": 1.2, "q4": 1.6}  # Quarterly trends
        },
        "volatility_factors": {
            "base_multiplier": (1.0, 10.0),
            "seasonal_boost": (1.2, 3.0),
            "event_boost": (1.5, 5.0),
            "crisis_multiplier": (2.0, 8.0)
        },
        "pattern_memory": {
            "lookback_periods": [7, 30, 90],  # Days of historical influence
            "decay_rate": (0.1, 0.5),  # Pattern decay over time
            "adaptation_rate": (0.2, 0.8)  # Pattern learning rate
        }
    }

    # Behavioral anomalies and pattern evolution
    behavioral_dynamics: Dict = {
        "pattern_evolution": {
            "complexity": (1, 10),  # Pattern complexity level
            "mutation_rate": (0.05, 0.3),  # Rate of pattern changes
            "adaptation_speed": (0.1, 0.9),  # Speed of pattern adaptation
            "correlation_matrix": {
                "temporal": 0.7,
                "spatial": 0.5,
                "monetary": 0.6
            }
        },
        "anomaly_characteristics": {
            "intensity_distribution": "pareto",  # Statistical distribution
            "duration_profile": "exponential",
            "clustering_tendency": (0.2, 0.8)
        },
        "feedback_mechanisms": {
            "detection_influence": (0.1, 0.9),  # Impact of detection on behavior
            "risk_tolerance": (0.2, 0.8),  # Risk-taking behavior
            "learning_rate": (0.1, 0.5)  # Adaptation to detection
        }
    }

    # Network and entity relationships
    network_dynamics: Dict = {
        "graph_properties": {
            "centrality_measures": ["degree", "betweenness", "eigenvector"],
            "community_structure": {
                "size_range": (3, 50),
                "density_range": (0.1, 0.9),
                "overlap_factor": (0.1, 0.4)
            },
            "temporal_evolution": {
                "growth_rate": (0.1, 0.5),
                "dissolution_rate": (0.05, 0.3),
                "merger_probability": 0.2
            }
        },
        "entity_interactions": {
            "connection_strength": (0.1, 1.0),
            "interaction_frequency": (1, 100),
            "relationship_types": ["direct", "indirect", "hierarchical"]
        }
    }

    # Advanced feature engineering
    feature_composition: Dict = {
        "base_features": [
            "transaction_velocity",
            "amount_distribution",
            "temporal_patterns",
            "network_metrics",
            "behavioral_indicators"
        ],
        "derived_features": {
            "windows": [1, 7, 14, 30, 90, 180],
            "aggregations": ["mean", "std", "skew", "kurt", "quantile"],
            "transformations": ["log", "sqrt", "box-cox"],
            "interactions": ["first_order", "second_order", "custom"]
        },
        "feature_importance": {
            "behavioral": 0.35,
            "network": 0.25,
            "temporal": 0.25,
            "transactional": 0.15
        }
    }

    # Model-specific configurations
    model_parameters: Dict = {
        "label_distribution": {
            "fraud_ratio": (0.001, 0.1),
            "uncertainty_range": (0.05, 0.2),
            "noise_level": (0.01, 0.1)
        },
        "data_quality": {
            "missing_value_rate": (0.01, 0.1),
            "error_rate": (0.001, 0.05),
            "inconsistency_rate": (0.01, 0.08)
        },
        "validation_metrics": [
            "precision", "recall", "f1",
            "auc_roc", "auc_pr", "ks_statistic"
        ]
    }

    # Environmental and external factors
    context_factors: Dict = {
        "market_conditions": {
            "volatility": (0.1, 0.5),
            "trend": [-1.0, 1.0],
            "seasonality": {
                "annual": (0.8, 1.2),
                "quarterly": (0.9, 1.1),
                "monthly": (0.95, 1.05)
            }
        },
        "risk_factors": {
            "geo_political": (0.1, 2.0),
            "economic": (0.5, 1.5),
            "technological": (0.8, 1.2)
        }
    }

class DataGenerator:
    """Enhanced data generator with sophisticated fraud patterns"""
    
    def __init__(self, business_config: BusinessConfig, transaction_config: TransactionConfig):
        self.business_config = business_config
        self.transaction_config = transaction_config
        self.fraud_config = FraudConfig()
        self._merchant_cache = {}
        self._customer_cache = {}
        self._transaction_history = []
        self.rng = np.random.default_rng()
        
    def generate_dataset(
        self,
        merchant_count: int,
        days: int,
        fraud_percentage: float = 0.2,
        batch_size: int = 1000
    ) -> Generator[Tuple[List[Dict], List[Dict]], None, None]:
        """Generate dataset in batches with fraud patterns"""
        merchants = self.generate_merchant_profiles(merchant_count)
        fraud_merchants = set(random.sample(merchants, int(merchant_count * fraud_percentage)))
        
        start_date = datetime.now() - timedelta(days=days)
        current_date = start_date
        end_date = datetime.now()
        
        while current_date <= end_date:
            batch_transactions = []
            
            for merchant in merchants:
                daily_transactions = (
                    self._generate_fraud_transactions(merchant, current_date)
                    if merchant in fraud_merchants
                    else self._generate_normal_transactions(merchant, current_date)
                )
                batch_transactions.extend(daily_transactions)
                
                if len(batch_transactions) >= batch_size:
                    yield merchants, batch_transactions
                    batch_transactions = []
            
            if batch_transactions:
                yield merchants, batch_transactions
            
            current_date += timedelta(days=1)

    def _generate_normal_transactions(self, merchant: Dict, date: datetime) -> List[Dict]:
        """Generate normal transaction patterns"""
        base_volume = self._get_base_daily_volume(merchant)
        daily_pattern = self._apply_temporal_factors(merchant, date, base_volume)
        
        transactions = []
        for hour in range(24):
            hourly_volume = int(daily_pattern['hourly_distribution'][hour] * daily_pattern['volume'])
            
            for _ in range(hourly_volume):
                txn_time = date.replace(
                    hour=hour,
                    minute=random.randint(0, 59),
                    second=random.randint(0, 59)
                )
                
                amount = self._generate_transaction_amount(
                    merchant,
                    daily_pattern['amount_distribution']
                )
                
                transaction = self._create_transaction(
                    merchant,
                    txn_time,
                    amount,
                    is_fraudulent=False
                )
                transactions.append(transaction)
        
        return transactions

    def _generate_transaction_amount(self, merchant: Dict, distribution: Dict) -> float:
        """Generate realistic transaction amounts"""
        base_amount = stats.lognorm.rvs(
            s=distribution['shape'],
            scale=merchant['avg_ticket'],
            random_state=self.rng
        )
        
        # Apply seasonal and time-based factors
        amount = base_amount * self._get_seasonal_factor(datetime.now())
        
        # Round to 2 decimal places
        return round(amount, 2)

    def _create_transaction(
        self,
        merchant: Dict,
        timestamp: datetime,
        amount: float,
        is_fraudulent: bool = False,
        customer_id: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """Create a detailed transaction record"""
        if not customer_id:
            customer_id = self._get_or_create_customer()
            
        transaction = {
            "transaction_id": f"TXN-{uuid.uuid4().hex}",
            "merchant_id": merchant["merchant_id"],
            "customer_id": customer_id,
            "timestamp": timestamp.isoformat(),
            "amount": amount,
            "currency": "USD",
            "status": self._get_transaction_status(),
            "payment_method": self._get_payment_method(),
            "platform": self._get_transaction_platform(),
            "device_id": f"DEV-{uuid.uuid4().hex[:8]}",
            "ip_address": fake.ipv4(),
            "location": {
                "latitude": float(fake.latitude()),
                "longitude": float(fake.longitude())
            },
            "is_fraudulent": is_fraudulent,
            "fraud_flags": kwargs.get("fraud_flags", {}),
            "metadata": {
                "customer_age_days": self._get_customer_age(customer_id),
                "merchant_age_days": self._get_merchant_age(merchant["merchant_id"]),
                "risk_score": self._calculate_transaction_risk(
                    amount, merchant, customer_id, timestamp
                )
            }
        }
        
        self._transaction_history.append(transaction)
        return transaction

    def _calculate_transaction_risk(
        self,
        amount: float,
        merchant: Dict,
        customer_id: str,
        timestamp: datetime
    ) -> float:
        """Calculate transaction risk score"""
        base_risk = merchant.get("risk_score", 0.5)
        
        # Amount factor
        amount_factor = min(amount / merchant["avg_ticket"], 5.0) * 0.2
        
        # Time factor
        hour = timestamp.hour
        time_factor = 0.3 if hour >= 23 or hour <= 4 else 0.1
        
        # Customer history factor
        customer_history = self._get_customer_history(customer_id, days=30)
        history_factor = 0.3 if not customer_history else 0.1
        
        # Velocity factor
        recent_txns = self._get_recent_transactions(merchant["merchant_id"], minutes=60)
        velocity_factor = min(len(recent_txns) / 10, 1.0) * 0.2
        
        risk_score = base_risk + amount_factor + time_factor + history_factor + velocity_factor
        return min(max(risk_score, 0.0), 1.0)

    def _get_seasonal_factor(self, date: datetime) -> float:
        """Calculate seasonal multiplication factor"""
        month = date.month
        day_of_week = date.weekday()
        
        season_factor = self.fraud_config.temporal_dynamics["time_windows"]["seasonal"][f"q{(month-1)//3 + 1}"]
        week_factor = (
            self.fraud_config.temporal_dynamics["time_windows"]["weekly"]["weekend"]
            if day_of_week >= 5
            else self.fraud_config.temporal_dynamics["time_windows"]["weekly"]["weekday"]
        )
        
        return season_factor * week_factor

    # Add test method
    def test_generator(self, merchant_count: int = 10, days: int = 7) -> None:
        """Test the data generator and print summary statistics"""
        print("Testing Data Generator...")
        
        # Generate test dataset
        merchants = []
        transactions = []
        for batch_merchants, batch_transactions in self.generate_dataset(
            merchant_count=merchant_count,
            days=days,
            batch_size=1000
        ):
            merchants = batch_merchants
            transactions.extend(batch_transactions)
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(transactions)
        
        print("\nDataset Summary:")
        print(f"Total Merchants: {len(merchants)}")
        print(f"Total Transactions: {len(transactions)}")
        print(f"Fraudulent Transactions: {df['is_fraudulent'].sum()}")
        print(f"Fraud Percentage: {(df['is_fraudulent'].sum() / len(df)) * 100:.2f}%")
        
        print("\nAmount Statistics:")
        print(df['amount'].describe())
        
        print("\nTransactions by Platform:")
        print(df['platform'].value_counts())
        
        print("\nTransactions by Payment Method:")
        print(df['payment_method'].value_counts())
        
        print("\nHourly Transaction Distribution:")
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        print(df.groupby('hour').size())

# Example usage and test
if __name__ == "__main__":
    # Sample configurations
    business_config = BusinessConfig(
        category_weights={"retail": 0.4, "food": 0.3, "services": 0.3},
        revenue_ranges={"retail": (100000, 1000000), "food": (50000, 500000), "services": (75000, 750000)},
        ticket_ranges={"retail": (50, 500), "food": (20, 200), "services": (100, 1000)},
        operating_hours={"retail": [(9, 21)], "food": [(8, 22)], "services": [(9, 18)]},
        seasonality={"q1": 0.8, "q2": 1.0, "q3": 1.2, "q4": 1.5},
        risk_factors={"retail": 0.3, "food": 0.2, "services": 0.4}
    )
    
    transaction_config = TransactionConfig(
        volume_ranges={"retail": (50, 500), "food": (100, 1000), "services": (20, 200)},
        payment_methods={"credit": 0.4, "debit": 0.3, "wallet": 0.2, "upi": 0.1},
        status_weights={"success": 0.95, "failed": 0.05},
        platform_weights={"web": 0.4, "mobile": 0.4, "pos": 0.2},
        time_patterns={"morning": [(9, 12)], "afternoon": [(12, 17)], "evening": [(17, 21)]}
    )
    
    # Create generator and run test
    generator = DataGenerator(business_config, transaction_config)
    generator.test_generator(merchant_count=10, days=7)

