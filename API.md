# API Reference

## Endpoints

### Health Check

```
GET /health
```

**Response:**
```json
{
  "status": "healthy"
}
```

---

### Model Information

```
GET /v1/info
```

**Response:**
```json
{
  "service": "SARIMAX Forecasting API",
  "version": "1.0.0",
  "models_available": 6,
  "forecast_types": ["daily", "weekly", "biweekly", "monthly"],
  "model_type": "SARIMAX (Expanding Window)"
}
```

---

### List Models

```
GET /v1/models
```

**Response:**
```json
{
  "total_models": 6,
  "models": [
    {
      "name": "sarimax_initial_18months",
      "training_months": 18,
      "description": "Initial model"
    },
    {
      "name": "sarimax_month_1_19months",
      "training_months": 19,
      "description": "Updated model (1 month)"
    }
  ]
}
```

---

### Generate Forecast

```
POST /v1/predict
```

**Request Body:**
```json
{
  "forecast_type": "daily",
  "steps": 30,
  "start_date": "2026-01-20",
  "exog_data": {
    "holiday": [0, 0, 1, 0, ...],
    "promotion": [0, 1, 0, 0, ...]
  }
}
```

**Parameters:**
- `forecast_type` (required): `"daily"`, `"weekly"`, `"biweekly"`, or `"monthly"`
- `steps` (required): Number of periods to forecast (integer)
- `start_date` (optional): Starting date in YYYY-MM-DD format
- `exog_data` (optional): Exogenous variables for future periods

**Response:**
```json
{
  "forecast_type": "daily",
  "model_used": "sarimax_initial_18months",
  "start_date": "2026-01-20",
  "total_predictions": 30,
  "predictions": [
    {
      "date": "2026-01-20",
      "predicted_quantity": 1234.56,
      "lower_bound": 1100.00,
      "upper_bound": 1369.12
    }
  ]
}
```

---

### Batch Predictions

```
POST /v1/predict/batch
```

**Request Body:**
```json
{
  "requests": [
    {
      "forecast_type": "daily",
      "steps": 7,
      "start_date": "2026-01-20"
    },
    {
      "forecast_type": "weekly",
      "steps": 4,
      "start_date": "2026-01-20"
    }
  ]
}
```

**Response:**
```json
{
  "total_requests": 2,
  "results": [
    {
      "request_index": 0,
      "status": "success",
      "forecast": { ... }
    },
    {
      "request_index": 1,
      "status": "success",
      "forecast": { ... }
    }
  ]
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid forecast_type. Must be one of: daily, weekly, biweekly, monthly"
}
```

### 404 Not Found
```json
{
  "error": "No model available for the specified forecast type"
}
```

### 500 Internal Server Error
```json
{
  "error": "Prediction failed: [error details]"
}
```

---

## cURL Examples

### Health Check
```bash
curl -X GET \
  -H "Authorization: Bearer <token>" \
  https://<deployment-url>/health
```

### Daily Forecast
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "forecast_type": "daily",
    "steps": 30,
    "start_date": "2026-01-20"
  }' \
  https://<deployment-url>/v1/predict
```

### Weekly Forecast
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "forecast_type": "weekly",
    "steps": 12,
    "start_date": "2026-01-20"
  }' \
  https://<deployment-url>/v1/predict
```

### With Exogenous Variables
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "forecast_type": "daily",
    "steps": 7,
    "start_date": "2026-01-20",
    "exog_data": {
      "holiday": [0, 0, 1, 0, 0, 0, 1],
      "promotion": [1, 1, 0, 0, 1, 1, 0]
    }
  }' \
  https://<deployment-url>/v1/predict
```

---

## Python Client Example

```python
import requests
import json

# Configuration
DEPLOYMENT_URL = "https://<your-deployment-url>"
TOKEN = "<your-sap-token>"

# Headers
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Generate forecast
payload = {
    "forecast_type": "daily",
    "steps": 30,
    "start_date": "2026-01-20"
}

response = requests.post(
    f"{DEPLOYMENT_URL}/v1/predict",
    headers=headers,
    json=payload
)

if response.status_code == 200:
    forecast = response.json()
    print(f"Total predictions: {forecast['total_predictions']}")
    for pred in forecast['predictions']:
        print(f"{pred['date']}: {pred['predicted_quantity']:.2f}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

---

## Rate Limits

- No explicit rate limits enforced
- Resource scaling based on load (1-3 replicas)
- Recommended: < 100 requests per minute per deployment

## Best Practices

1. **Cache Predictions**: Cache frequently requested forecasts
2. **Batch Requests**: Use batch endpoint for multiple forecasts
3. **Error Handling**: Always handle 4xx and 5xx errors
4. **Token Management**: Refresh OAuth tokens before expiry
5. **Date Validation**: Ensure dates are in YYYY-MM-DD format
