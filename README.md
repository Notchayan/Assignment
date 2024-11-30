# Merchant Risk Analysis API

## Overview

The Merchant Risk Analysis API is a sophisticated system designed to evaluate merchant transactions and determine risk profiles based on a variety of predefined patterns. This API is built using FastAPI, a modern, fast (high-performance) web framework for building APIs with Python 3.8+ based on standard Python type hints. It leverages MongoDB for efficient data storage and Pydantic for data validation, ensuring a robust and scalable solution for merchant risk assessment.

## Key Features

- **Real-time Transaction Risk Analysis:** The API provides immediate risk assessment for transactions, allowing businesses to make informed decisions quickly.
- **Multiple Risk Pattern Detection:** It can detect various risk patterns such as velocity spikes, late-night trading, and split transactions, which are crucial for identifying fraudulent activities.
- **Customizable Risk Scoring System:** The risk scoring system is flexible and can be tailored to meet specific business needs, providing a personalized risk assessment.
- **RESTful API Endpoints:** The API is designed with RESTful principles, ensuring easy integration and interaction with other systems.
- **Asynchronous Data Processing:** Utilizing Python's asynchronous capabilities, the API can handle multiple requests efficiently, improving performance and scalability.
- **MongoDB Integration:** The API uses MongoDB for data storage, offering a scalable and flexible database solution that can handle large volumes of transaction data.

## Architecture

### Core Components

1. **Models**
   - **Merchant Profiles:** Define the structure and attributes of merchant data.
   - **Transaction Records:** Capture details of each transaction processed by the system.
   - **Risk Patterns:** Represent the various risk patterns that the system can detect.
   - **Risk Profile Responses:** Provide a structured response format for risk assessments.

2. **Services**
   - **Risk Calculation Engine:** Analyzes transactions to calculate risk scores based on detected patterns.
   - **Transaction Processing:** Manages the processing and validation of transactions.
   - **Data Generation and Analysis:** Generates necessary data for risk analysis and performs in-depth analysis.

3. **API Endpoints**
   - **Merchant Management:** Endpoints for managing merchant data and retrieving merchant information.
   - **Risk Profile Retrieval:** Endpoints for obtaining risk profiles of merchants.
   - **Transaction Processing:** Endpoints for processing and analyzing transactions.

### Technology Stack

- **Backend Framework:** FastAPI, chosen for its speed, ease of use, and modern features.
- **Database:** MongoDB, selected for its scalability and flexibility in handling large datasets.
- **Data Validation:** Pydantic, used for its powerful data validation and settings management using Python type annotations.
- **API Documentation:** Swagger/OpenAPI, providing interactive and comprehensive API documentation.

## Getting Started

### Prerequisites

To run the Merchant Risk Analysis API, ensure you have the following installed:

- **Python 3.8+**: The API is built using Python, so a compatible version is required.
- **MongoDB**: The API uses MongoDB for data storage, so ensure it is installed and running.
- **pip**: Python's package installer, used to install the required dependencies.

### Installation

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Install the required dependencies using pip:
   ```bash
   pip install -r requirements.txt
   ```

### Running the API

To start the API server, use the following command:
```bash
uvicorn src.main:app --reload
```
This command will start the server with hot-reloading enabled, allowing you to see changes in real-time.

## API Documentation

### Detailed API Documentation

#### Risk Analysis Endpoints

##### Get Merchant Risk Profile
```http
GET /api/merchants/{merchant_id}/risk-profile
```
Retrieves comprehensive risk analysis for a merchant.

**Parameters:**
- `merchant_id` (path) - Unique identifier of the merchant
- `days` (query, optional) - Analysis window in days (default: 30)

**Response:**
```json
{
  "merchant_id": "string",
  "overall_risk_score": 75.5,
  "detected_patterns": [
    {
      "pattern_id": "string",
      "name": "LATE_NIGHT",
      "confidence_score": 0.85,
      "characteristics": {},
      "red_flags": ["string"]
    }
  ],
  "monitoring_status": "HIGH_RISK",
  "review_required": true
}
```

##### Submit Transaction
```http
POST /api/transactions
```
Submit a new transaction for risk assessment.

**Request Body:**
```json
{
  "merchant_id": "string",
  "amount": 1000.00,
  "timestamp": "2024-03-21T15:30:00Z",
  "customer_id": "string",
  "payment_method": "CARD",
  "location": {
    "latitude": 0,
    "longitude": 0
  }
}
```

**Response:**
```json
{
  "transaction_id": "string",
  "risk_assessment": {
    "risk_score": 25.5,
    "detected_patterns": [],
    "recommendation": "APPROVE"
  }
}
```

#### Pattern Detection Endpoints

##### Get Pattern Analysis
```http
GET /api/merchants/{merchant_id}/patterns
```
Retrieve specific pattern detection results.

**Parameters:**
- `merchant_id` (path) - Merchant identifier
- `pattern_type` (query, optional) - Specific pattern to analyze
- `start_date` (query, optional) - Analysis start date
- `end_date` (query, optional) - Analysis end date

**Response:**
```json
{
  "patterns": [
    {
      "type": "VELOCITY_SPIKE",
      "confidence_score": 0.75,
      "details": {
        "detected_spikes": 3,
        "average_intensity": 2.5
      }
    }
  ]
}
```

#### Timeline Events

##### Get Merchant Timeline
```http
GET /api/merchants/{merchant_id}/timeline
```
Retrieve chronological events and risk signals.

**Parameters:**
- `merchant_id` (path) - Merchant identifier
- `days` (query, optional) - Number of days to analyze
- `event_types` (query, optional) - Filter specific event types

**Response:**
```json
{
  "events": [
    {
      "timestamp": "2024-03-21T15:30:00Z",
      "event_type": "RISK_ALERT",
      "severity": "HIGH",
      "description": "Unusual transaction pattern detected"
    }
  ]
}
```

### Rate Limits
- Standard tier: 100 requests per minute
- Enterprise tier: 1000 requests per minute
- Burst capacity: 2x normal limit for 30 seconds

### Error Responses
All endpoints may return the following error responses:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {}
  }
}
```

Common error codes:
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Resource Not Found
- `429` - Too Many Requests
- `500` - Internal Server Error

### Authentication
All API requests require authentication using Bearer tokens:
```http
Authorization: Bearer <your_api_token>
```

Tokens can be obtained through the authentication endpoint:
```http
POST /api/auth/token
```

### Webhooks
Configure webhooks to receive real-time notifications:
```http
POST /api/webhooks/configure
```

**Request Body:**
```json
{
  "url": "https://your-domain.com/webhook",
  "events": ["RISK_ALERT", "PATTERN_DETECTED"],
  "secret": "your_webhook_secret"
}
```

The API comes with built-in documentation accessible via:

- **Swagger UI**: `http://localhost:8000/docs` - An interactive interface for exploring the API endpoints.
- **ReDoc**: `http://localhost:8000/redoc` - A more detailed and visually appealing documentation interface.

### Main Endpoints

- **`GET /api/merchants/{merchant_id}/risk-profile`**: Retrieve the risk profile of a specific merchant.
- **`POST /api/transactions`**: Submit a new transaction for processing and risk assessment.
- **`GET /api/risks/{merchant_id}`**: Obtain a detailed risk analysis for a merchant.

## Security

The API incorporates several security measures to protect data and ensure safe operations:

- **Request Validation Middleware**: Ensures that incoming requests meet the required criteria before processing.
- **MongoDB Security Best Practices**: Follows recommended practices for securing MongoDB instances.
- **Error Handling and Logging**: Comprehensive error handling and logging mechanisms are in place to track and resolve issues efficiently.

## Contributing

We welcome contributions to enhance the Merchant Risk Analysis API. To contribute:

1. Fork the repository.
2. Create a feature branch for your changes.
3. Submit a pull request with a detailed description of your changes.

## License

This project is licensed under the MIT License. See the LICENSE.md file for more details.

## Support

For support and queries, please open an issue in the repository. We are committed to providing timely assistance and addressing any concerns you may have.
