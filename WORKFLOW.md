# Workflow Specification

## Overview

This workflow defines a KServe-based serving template for SAP AI Core.

## File Location

`.github/workflows/sarimax-serving.yaml`

## Workflow Structure

```yaml
apiVersion: ai.sap.com/v1alpha1
kind: ServingTemplate
metadata:
  name: sarimax-forecasting-server
  annotations:
    scenarios.ai.sap.com/description: "..."
    scenarios.ai.sap.com/name: "sarimax-timeseries"
    executables.ai.sap.com/description: "..."
    executables.ai.sap.com/name: "sarimax-server"
  labels:
    scenarios.ai.sap.com/id: "sarimax-timeseries"
    ai.sap.com/version: "1.0.0"
```

## Identifiers

### Scenario
- **ID**: `sarimax-timeseries`
- **Name**: SARIMAX Time Series Forecasting for City Gas-CNG Demand
- **Description**: Expanding window SARIMAX models for demand forecasting

### Executable
- **ID**: `sarimax-server`
- **Name**: Expanding Window SARIMAX Model with Exogenous Variables
- **Description**: Serves predictions via REST API

## Parameters

### modelName
- **Type**: string
- **Default**: `sarimax_initial_18months`
- **Description**: Which SARIMAX model to use for predictions
- **Options**:
  - `sarimax_initial_18months`
  - `sarimax_month_1_19months`
  - `sarimax_month_2_20months`
  - `sarimax_month_3_21months`
  - `sarimax_month_4_22months`
  - `sarimax_month_5_23months`

### imageName
- **Type**: string
- **Default**: `docker.io/priyaannamalai/sarimax-forecasting:v1`
- **Description**: Docker image to deploy
- **Format**: `registry/username/image:tag`

## Resource Configuration

### Scaling
- **Min Replicas**: 1
- **Max Replicas**: 3
- **Autoscaling**: Enabled based on load

### Compute Resources

**Requests:**
- Memory: 2 Gi
- CPU: 1000m (1 core)

**Limits:**
- Memory: 4 Gi
- CPU: 2000m (2 cores)

### Resource Plan
- **Plan**: `starter`
- Suitable for development and small production workloads

## Container Configuration

### Image Pull
- **Registry**: Docker Hub (`docker.io`)
- **Secret**: `docker-secret` (must be created beforehand)
- **Image**: Specified by `imageName` parameter

### Port
- **Container Port**: 9001
- **Protocol**: TCP

### Environment Variables
- `MODEL_PATH`: `/app/models`
- `PORT`: `9001`
- `MODEL_NAME`: Value from `modelName` parameter

## Health Checks

### Liveness Probe
- **Type**: HTTP GET
- **Path**: `/health`
- **Port**: 9001
- **Initial Delay**: 30 seconds
- **Period**: 30 seconds
- **Timeout**: 10 seconds

### Readiness Probe
- **Type**: HTTP GET
- **Path**: `/health`
- **Port**: 9001
- **Initial Delay**: 20 seconds
- **Period**: 10 seconds
- **Timeout**: 5 seconds

## How It Works

1. **Sync**: SAP AI Core syncs this workflow from GitHub
2. **Register**: Scenario and executable are automatically registered
3. **Configure**: User creates configuration with parameter values
4. **Deploy**: User creates deployment from configuration
5. **Scale**: System scales between 1-3 replicas based on load
6. **Serve**: Inference service handles prediction requests

## Updating the Workflow

To update:
1. Modify this YAML file
2. Commit and push to GitHub
3. SAP AI Core auto-syncs (2-3 minutes)
4. Create new configuration with updated settings
5. Deploy new version

## Validation

The workflow is automatically validated by SAP AI Core against:
- API version compatibility
- Required fields
- Resource limits
- Probe configurations

## Best Practices

1. **Versioning**: Update `ai.sap.com/version` when making changes
2. **Descriptions**: Keep annotations clear and descriptive
3. **Resources**: Request only what you need
4. **Health Checks**: Ensure your app responds to `/health`
5. **Secrets**: Never hardcode credentials in workflow

## Troubleshooting

### Workflow not syncing
- Check repository is registered
- Verify file is in `.github/workflows/` directory
- Ensure YAML syntax is valid

### Deployment fails
- Check Docker secret exists
- Verify image is accessible
- Review resource requirements

### Pods not starting
- Check liveness probe configuration
- Verify container port matches health check port
- Review pod logs in SAP AI Core

## Related Files

- [README.md](README.md) - Project overview
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment instructions
- [API.md](API.md) - API documentation
