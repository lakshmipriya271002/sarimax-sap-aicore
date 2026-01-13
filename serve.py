"""
SAP AI Core Inference Server for SARIMAX Time Series Forecasting
Supports daily, weekly, biweekly, and monthly predictions with exogenous variables
"""

from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import pickle
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variables for loaded models
MODELS = {}
EXOG_FEATURES = []

# Model directory
MODEL_DIR = os.environ.get('MODEL_PATH', '/app/models')


def load_models():
    """Load all saved SARIMAX models from the models directory"""
    global MODELS, EXOG_FEATURES
    
    logger.info(f"Loading models from {MODEL_DIR}")
    
    if not os.path.exists(MODEL_DIR):
        logger.error(f"Model directory not found: {MODEL_DIR}")
        return False
    
    try:
        # Load all model files
        model_files = [f for f in os.listdir(MODEL_DIR) if f.endswith('.pkl')]
        
        if not model_files:
            logger.error("No model files found in models directory")
            return False
        
        logger.info(f"Found {len(model_files)} model files")
        
        for model_file in model_files:
            model_path = os.path.join(MODEL_DIR, model_file)
            model_name = model_file.replace('.pkl', '')
            
            with open(model_path, 'rb') as f:
                MODELS[model_name] = pickle.load(f)
            
            logger.info(f"Loaded model: {model_name}")
        
        # Define exogenous features (based on your pipeline)
        EXOG_FEATURES = [
            'gcv_cal_value_lag_1', 'gcv_cal_value_lag_7', 'gcv_cal_value_lag_14', 'gcv_cal_value_lag_30',
            'gst_rcovery_rate_lag_1', 'gst_rcovery_rate_lag_7', 'gst_rcovery_rate_lag_14', 'gst_rcovery_rate_lag_30',
            'zutf_rate_lag_1', 'zutf_rate_lag_7', 'zutf_rate_lag_14', 'zutf_rate_lag_30',
            'ztu1_rate_lag_1', 'ztu1_rate_lag_7', 'ztu1_rate_lag_14', 'ztu1_rate_lag_30',
            'ztf1_rate_lag_1', 'ztf1_rate_lag_7', 'ztf1_rate_lag_14', 'ztf1_rate_lag_30',
            'exch_rate_lag_1', 'exch_rate_lag_7', 'exch_rate_lag_14', 'exch_rate_lag_30',
            'ncv_cal_value_lag_1', 'ncv_cal_value_lag_7', 'ncv_cal_value_lag_14', 'ncv_cal_value_lag_30',
            'marketing_margn_rate_lag_1', 'marketing_margn_rate_lag_7', 'marketing_margn_rate_lag_14', 'marketing_margn_rate_lag_30',
            'vat_rate_lag_1', 'vat_rate_lag_7', 'vat_rate_lag_14', 'vat_rate_lag_30',
            'gcv_to_ncv_ratio_lag_1', 'gcv_to_ncv_ratio_lag_7', 'gcv_to_ncv_ratio_lag_14', 'gcv_to_ncv_ratio_lag_30'
        ]
        
        logger.info(f"Configured {len(EXOG_FEATURES)} exogenous features")
        logger.info("All models loaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        return False


def forecast_with_sarimax(model, steps: int, exog_forecast: Optional[np.ndarray] = None) -> np.ndarray:
    """
    Generate forecast using trained SARIMAX model
    
    Parameters:
    -----------
    model : Fitted SARIMAX model
    steps : Number of steps to forecast
    exog_forecast : Exogenous variables for forecast period
    
    Returns:
    --------
    forecast : numpy array of predictions
    """
    try:
        forecast = model.forecast(steps=steps, exog=exog_forecast)
        return forecast.values if hasattr(forecast, 'values') else forecast
    except Exception as e:
        logger.error(f"Error in forecasting: {str(e)}")
        return None


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for SAP AI Core"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': len(MODELS),
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/v1/models', methods=['GET'])
def list_models():
    """List all available models"""
    model_info = []
    for model_name, model in MODELS.items():
        model_info.append({
            'name': model_name,
            'type': 'SARIMAX',
            'order': str(model.model.order),
            'seasonal_order': str(model.model.seasonal_order),
            'n_obs': int(model.nobs)
        })
    
    return jsonify({
        'models': model_info,
        'total': len(model_info)
    }), 200


@app.route('/v1/predict', methods=['POST'])
def predict():
    """
    Main prediction endpoint
    
    Expected JSON payload:
    {
        "model_name": "sarimax_initial_18months",  # Optional, uses latest if not provided
        "forecast_type": "daily",  # daily, weekly, biweekly, monthly
        "steps": 30,  # Number of steps to forecast
        "start_date": "2025-10-01",  # Start date for forecast
        "exog_data": {  # Optional exogenous variables
            "gcv_cal_value_lag_1": [values...],
            "gst_rcovery_rate_lag_1": [values...],
            ...
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Extract parameters
        model_name = data.get('model_name', None)
        forecast_type = data.get('forecast_type', 'daily')
        steps = data.get('steps', 30)
        start_date = data.get('start_date', datetime.now().strftime('%Y-%m-%d'))
        exog_data = data.get('exog_data', None)
        
        # Select model
        if model_name and model_name in MODELS:
            selected_model = MODELS[model_name]
            logger.info(f"Using specified model: {model_name}")
        else:
            # Use the latest retrained model (highest month number)
            model_names = sorted([k for k in MODELS.keys() if 'month' in k], reverse=True)
            if model_names:
                model_name = model_names[0]
                selected_model = MODELS[model_name]
                logger.info(f"Using latest model: {model_name}")
            else:
                model_name = 'sarimax_initial_18months'
                selected_model = MODELS.get(model_name)
                logger.info(f"Using initial model: {model_name}")
        
        if selected_model is None:
            return jsonify({'error': 'No model available'}), 500
        
        # Prepare exogenous variables
        exog_forecast = None
        if exog_data and len(exog_data) > 0:
            try:
                # Convert exog_data dict to DataFrame
                exog_df = pd.DataFrame(exog_data)
                
                # Ensure all required features are present
                missing_features = [f for f in EXOG_FEATURES if f not in exog_df.columns]
                if missing_features:
                    logger.warning(f"Missing exogenous features: {missing_features[:5]}... Filling with zeros")
                    for feature in missing_features:
                        exog_df[feature] = 0.0
                
                # Reorder columns to match training
                exog_df = exog_df[EXOG_FEATURES]
                
                # Take only the required number of steps
                exog_forecast = exog_df.iloc[:steps].values
                
                logger.info(f"Using exogenous variables: shape {exog_forecast.shape}")
            except Exception as e:
                logger.error(f"Error processing exogenous data: {str(e)}")
                exog_forecast = None
        
        # Generate forecast
        logger.info(f"Generating {forecast_type} forecast for {steps} steps from {start_date}")
        predictions = forecast_with_sarimax(selected_model, steps=steps, exog_forecast=exog_forecast)
        
        if predictions is None:
            return jsonify({'error': 'Forecast generation failed'}), 500
        
        # Create date range based on forecast type
        start_dt = pd.to_datetime(start_date)
        if forecast_type == 'daily':
            date_range = pd.date_range(start=start_dt, periods=steps, freq='D')
        elif forecast_type == 'weekly':
            date_range = pd.date_range(start=start_dt, periods=steps, freq='W')
        elif forecast_type == 'biweekly':
            date_range = pd.date_range(start=start_dt, periods=steps, freq='2W')
        elif forecast_type == 'monthly':
            date_range = pd.date_range(start=start_dt, periods=steps, freq='MS')
        else:
            date_range = pd.date_range(start=start_dt, periods=steps, freq='D')
        
        # Prepare response
        forecast_results = []
        for i, (date, pred) in enumerate(zip(date_range, predictions)):
            forecast_results.append({
                'date': date.strftime('%Y-%m-%d'),
                'predicted_quantity': float(pred),
                'step': i + 1
            })
        
        response = {
            'model_used': model_name,
            'forecast_type': forecast_type,
            'total_predictions': len(forecast_results),
            'start_date': start_date,
            'end_date': date_range[-1].strftime('%Y-%m-%d'),
            'predictions': forecast_results,
            'metadata': {
                'model_order': str(selected_model.model.order),
                'seasonal_order': str(selected_model.model.seasonal_order),
                'exogenous_used': exog_forecast is not None,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        logger.info(f"Successfully generated {len(forecast_results)} predictions")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/v1/predict/batch', methods=['POST'])
def predict_batch():
    """
    Batch prediction endpoint for multiple dates
    
    Expected JSON payload:
    {
        "model_name": "sarimax_initial_18months",
        "dates": ["2025-10-01", "2025-10-02", "2025-10-03"],
        "exog_data": {...}  # Same format as single prediction
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'dates' not in data:
            return jsonify({'error': 'dates field is required'}), 400
        
        dates = data['dates']
        model_name = data.get('model_name', None)
        exog_data = data.get('exog_data', None)
        
        # Predict for each date
        results = []
        for date in dates:
            pred_data = {
                'model_name': model_name,
                'forecast_type': 'daily',
                'steps': 1,
                'start_date': date,
                'exog_data': exog_data
            }
            
            # Call the predict function internally
            with app.test_request_context('/v1/predict', method='POST', json=pred_data):
                response = predict()
                if response[1] == 200:
                    pred_result = response[0].get_json()
                    if pred_result['predictions']:
                        results.append(pred_result['predictions'][0])
        
        return jsonify({
            'total_predictions': len(results),
            'predictions': results
        }), 200
        
    except Exception as e:
        logger.error(f"Error in batch prediction: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/v1/info', methods=['GET'])
def model_info():
    """Get detailed information about the service"""
    return jsonify({
        'service': 'SARIMAX Time Series Forecasting',
        'version': '1.0.0',
        'description': 'Expanding window SARIMAX forecasting for City Gas-CNG demand',
        'models_available': len(MODELS),
        'exogenous_features': len(EXOG_FEATURES),
        'supported_forecast_types': ['daily', 'weekly', 'biweekly', 'monthly'],
        'endpoints': {
            'health': '/health',
            'models': '/v1/models',
            'predict': '/v1/predict',
            'batch_predict': '/v1/predict/batch',
            'info': '/v1/info'
        }
    }), 200


if __name__ == '__main__':
    logger.info("Starting SARIMAX Inference Server...")
    
    # Load models on startup
    if load_models():
        logger.info(f"Server ready with {len(MODELS)} models")
        port = int(os.environ.get('PORT', 9001))
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        logger.error("Failed to load models. Exiting.")
        exit(1)
