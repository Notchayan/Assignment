# src/services

## Overview

The **Merchant Risk Analysis System** is a comprehensive suite of services designed to detect, analyze, and monitor risk patterns in merchant transactions. This documentation provides an in-depth overview of the system's architecture, key components, and usage guidelines.

---

## Table of Contents
1. [Overview](#overview)
2. [Risk Calculator Service](#risk-calculator-service)
   - [Purpose](#purpose)
   - [Key Components](#key-components)
   - [Configuration](#configuration)
   - [Usage Example](#usage-example)
3. [Data Generator Service](#data-generator-service)
   - [Purpose](#purpose-1)
   - [Key Features](#key-features)
   - [Configuration Parameters](#configuration-parameters)
   - [Usage Example](#usage-example-1)
4. [Transaction Processor Service](#transaction-processor-service)
   - [Purpose](#purpose-2)
   - [Key Functions](#key-functions)
   - [Integration Points](#integration-points)
5. [Error Handling and Logging](#error-handling-and-logging)

---

## Risk Calculator Service

### Purpose
The **Risk Calculator Service** is the central component for analyzing transaction patterns and calculating risk scores. It uses advanced detection algorithms to identify anomalies and assess risk efficiently.

### Key Components

#### 1. Risk Analysis Pipeline
- **Input**: Merchant ID and analysis window (in days).  
- **Output**: A `RiskProfileResponse` object containing a detailed risk assessment.  
- **Process Flow**:
  1. Fetch transaction history.
  2. Analyze risk patterns using configured detectors.
  3. Calculate a comprehensive risk score.
  4. Generate actionable timeline events.

#### 2. Pattern Detection
Sophisticated algorithms identify and quantify the following risk patterns:
- **Late Night Trading**: Flags unusual activity during off-business hours.  
- **Velocity Spikes**: Highlights abnormal transaction frequencies.  
- **Split Transactions**: Detects potential structuring of payments.  
- **Round Amount Patterns**: Flags unusually rounded transaction values.  
- **Customer Concentration**: Tracks the distribution of customer activity.  
- **Geographic Dispersion**: Detects unusual geographic distribution of transactions.  

### Configuration

```python
pattern_configs = {
    "late_night": {
        "time_window": "23:00-04:00",
        "threshold": 50
    },
    "velocity_spike": {
        "threshold": 100,
        "time_window_seconds": 3600
    },
    "split_transaction": {
        "time_window_minutes": 30,
        "amount_threshold": 10000,
        "min_transactions": 3
    },
    "round_amount": {
        "precision": 100,  # Flags amounts divisible by 100
        "threshold_percentage": 25  # Alerts if >25% of transactions are round
    },
    "customer_concentration": {
        "single_customer_threshold": 40,  # Percentage of total volume
        "time_window_days": 7,
        "min_transaction_count": 10
    },
    "geographic_dispersion": {
        "radius_km": 100,
        "unusual_location_threshold": 3,  # Standard deviations from normal
        "min_transactions": 5
    }
}
```

### Usage Example

```python
risk_calculator = RiskCalculatorService()
risk_profile = await risk_calculator.analyze_merchant_risk(
    merchant_id="merchant_123",
    days=30
)
```

---

## Data Generator Service

### Purpose
The **Data Generator Service** is used to simulate realistic transaction data for testing and development. It supports generating both normal and fraudulent transaction patterns.

### Key Features
1. **Normal Transaction Simulation**
   - Models daily/hourly transaction patterns.
   - Accounts for seasonal and weekly trends.
   - Supports merchant-specific configurations.

2. **Fraud Scenario Simulation**
   - Generates synthetic fraud cases for validation.
   - Incorporates various risk factors like amount, velocity, and customer distribution.

### Configuration Parameters
- **Base risk scores**: Determines risk levels for generated transactions.  
- **Temporal dynamics**: Captures time-based patterns (e.g., seasonality).  
- **Merchant profiles**: Customizes generation based on specific merchant traits.  

### Usage Example

```python
generator = DataGenerator()
transactions = generator.generate_normal_transactions(
    merchant=merchant_data,
    date=datetime.now()
)
```

---

## Transaction Processor Service

### Purpose
The **Transaction Processor Service** processes incoming transactions in real-time, applying risk calculations and flagging suspicious activities.

### Key Functions
1. **Transaction Validation**
   - Ensures transaction data integrity.
   - Handles missing or malformed inputs.

2. **Real-Time Risk Assessment**
   - Evaluates transactions against pre-configured risk patterns.
   - Flags anomalies for further review.

### Integration Points
- **Database Operations**: Fetch and update transaction data.  
- **Risk Calculator Service**: Leverages its analysis for real-time scoring.  
- **Event Generation**: Sends notifications for flagged activities.  

---

## Error Handling and Logging

Comprehensive error handling and logging ensure system reliability and traceability.

### Error Categories
- **Database Errors**: Connection issues or query failures.  
- **Validation Errors**: Missing or invalid input data.  
- **Processing Errors**: Failures in real-time analysis.  
- **Configuration Errors**: Incorrect or missing service configurations.  

### Logging Levels
- **INFO**: Tracks normal operations.  
- **WARNING**: Highlights potential problems.  
- **ERROR**: Logs critical failures.  
- **DEBUG**: Provides detailed diagnostic data for troubleshooting.  

---
