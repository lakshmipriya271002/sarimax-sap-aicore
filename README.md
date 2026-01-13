# SARIMAX Time Series Forecasting - SAP AI Core

This repository contains SAP AI Core workflow definitions for deploying SARIMAX time series forecasting models.

## 🚀 Quick Deploy

This repository is designed to be directly connected to SAP AI Core for automatic workflow synchronization.

## 📦 What's Inside

- **Docker Image**: `docker.io/priyaannamalai/sarimax-forecasting:v1`
- **Workflow**: `.github/workflows/sarimax-serving.yaml`
- **Models**: 6 SARIMAX models for City Gas-CNG demand forecasting

## 🎯 Workflow Details

### Scenario
- **ID**: `sarimax-timeseries`
- **Name**: SARIMAX Time Series Forecasting for City Gas-CNG Demand

### Executable
- **ID**: `sarimax-server`
- **Name**: Expanding Window SARIMAX Model with Exogenous Variables

### Parameters
- `modelName`: Which SARIMAX model to use (default: `sarimax_initial_18months`)
- `imageName`: Docker image to deploy (default: `docker.io/priyaannamalai/sarimax-forecasting:v1`)

## 📡 API Endpoints

Once deployed, the following endpoints will be available:

- `GET /health` - Health check
- `GET /v1/info` - Model information and configuration
- `GET /v1/models` - List available models
- `POST /v1/predict` - Generate forecasts
- `POST /v1/predict/batch` - Batch predictions

### Example Request

```bash
curl -X POST <deployment-url>/v1/predict \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "forecast_type": "daily",
    "steps": 30,
    "start_date": "2026-01-20"
  }'
```

### Example Response

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

## 🏗️ Model Architecture

- **Type**: SARIMAX (Seasonal ARIMA with Exogenous Variables)
- **Training**: Expanding window approach (18-23 months)
- **Forecast Types**: Daily, Weekly, Biweekly, Monthly
- **Features**: Supports exogenous variables (holidays, promotions, etc.)

### Available Models

1. `sarimax_initial_18months` - Initial model (18 months training)
2. `sarimax_month_1_19months` - Updated with 19 months
3. `sarimax_month_2_20months` - Updated with 20 months
4. `sarimax_month_3_21months` - Updated with 21 months
5. `sarimax_month_4_22months` - Updated with 22 months
6. `sarimax_month_5_23months` - Latest model (23 months training)

## 🔧 Resource Configuration

- **Min Replicas**: 1
- **Max Replicas**: 3 (auto-scaling)
- **Memory**: 2-4 Gi
- **CPU**: 1-2 cores
- **Resource Plan**: starter

## 📊 Use Cases

- City Gas and CNG demand forecasting
- Daily consumption predictions
- Weekly/Monthly planning
- Seasonal demand analysis
- Resource allocation optimization

## 🔗 Links

- [SAP AI Core Documentation](https://help.sap.com/docs/AI_CORE)
- [Docker Hub Image](https://hub.docker.com/r/priyaannamalai/sarimax-forecasting)
- [SAP AI Core Tutorial](https://developers.sap.com/tutorials/ai-core-code.html)

## 📝 Deployment Instructions

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions.

---

**Status**: ✅ Ready for SAP AI Core deployment

**Version**: 1.0.0

**Last Updated**: January 2026
