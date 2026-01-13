# 🚀 Deployment Guide

## Prerequisites

- SAP AI Core instance with access credentials
- Docker Hub account
- GitHub account

## Step 1: Upload to GitHub

This repository is ready to be uploaded to GitHub as-is.

### Option A: Create New Repository via GitHub UI

1. Go to https://github.com/new
2. Repository name: `sarimax-sap-aicore`
3. Visibility: Public or Private
4. **Do NOT** initialize with README (we already have one)
5. Click "Create repository"
6. Follow the commands below

### Option B: Push This Directory

```bash
cd sarimax-sap-aicore
git init
git add .
git commit -m "Initial commit: SAP AI Core workflow"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/sarimax-sap-aicore.git
git push -u origin main
```

## Step 2: Create Docker Registry Secret

Your Docker image needs to be accessible by SAP AI Core.

```bash
# Use SAP AI Core SDK or API to create secret
# Secret name: docker-secret
# Registry: docker.io
# Username: priyaannamalai
# Password: <your-docker-hub-token>
```

**Python example:**
```python
import requests

# Get SAP AI Core token
token = "<your-sap-token>"
base_url = "https://api.ai.intprod-eu12.eu-central-1.aws.ml.hana.ondemand.com"

# Create Docker secret
secret_data = {
    "name": "docker-secret",
    "data": {
        ".dockerconfigjson": "<base64-encoded-docker-config>"
    }
}

response = requests.post(
    f'{base_url}/v2/admin/dockerRegistrySecrets',
    headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    },
    json=secret_data
)
```

## Step 3: Register GitHub Repository with SAP AI Core

Use SAP AI Core API or UI to register this GitHub repository.

**Via API:**
```python
# Register repository
repo_data = {
    "name": "sarimax-workflows",
    "url": "https://github.com/YOUR_USERNAME/sarimax-sap-aicore",
    "username": "YOUR_GITHUB_USERNAME",
    "password": "YOUR_GITHUB_TOKEN"
}

response = requests.post(
    f'{base_url}/v2/admin/repositories',
    headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    },
    json=repo_data
)
```

**Via SAP AI Launchpad:**
1. Navigate to ML Operations → Git Repositories
2. Click "Add Repository"
3. Enter repository details
4. Save

## Step 4: Create Application

Link the repository to an application.

```python
app_data = {
    "applicationName": "sarimax-forecasting",
    "repositoryUrl": "https://github.com/YOUR_USERNAME/sarimax-sap-aicore",
    "revision": "main",
    "path": ".github/workflows"
}

response = requests.post(
    f'{base_url}/v2/admin/applications',
    headers={
        'Authorization': f'Bearer {token}',
        'AI-Resource-Group': 'default',
        'Content-Type': 'application/json'
    },
    json=app_data
)
```

## Step 5: Wait for Sync

SAP AI Core will automatically sync the workflow. This takes 2-3 minutes.

Check sync status:
```python
response = requests.get(
    f'{base_url}/v2/lm/scenarios',
    headers={
        'Authorization': f'Bearer {token}',
        'AI-Resource-Group': 'default'
    }
)

# Look for scenario: sarimax-timeseries
```

## Step 6: Create Configuration

Once synced, create a deployment configuration.

```python
config_data = {
    "name": "sarimax-config",
    "scenarioId": "sarimax-timeseries",
    "executableId": "sarimax-server",
    "parameterBindings": [
        {
            "key": "modelName",
            "value": "sarimax_initial_18months"
        },
        {
            "key": "imageName",
            "value": "docker.io/priyaannamalai/sarimax-forecasting:v1"
        }
    ]
}

response = requests.post(
    f'{base_url}/v2/lm/configurations',
    headers={
        'Authorization': f'Bearer {token}',
        'AI-Resource-Group': 'default',
        'Content-Type': 'application/json'
    },
    json=config_data
)

config_id = response.json()['id']
```

## Step 7: Create Deployment

Deploy the model using the configuration.

```python
deployment_data = {
    "configurationId": config_id
}

response = requests.post(
    f'{base_url}/v2/lm/deployments',
    headers={
        'Authorization': f'Bearer {token}',
        'AI-Resource-Group': 'default',
        'Content-Type': 'application/json'
    },
    json=deployment_data
)

deployment_id = response.json()['id']
```

## Step 8: Monitor Deployment

Wait for deployment to be RUNNING (3-5 minutes).

```python
response = requests.get(
    f'{base_url}/v2/lm/deployments/{deployment_id}',
    headers={
        'Authorization': f'Bearer {token}',
        'AI-Resource-Group': 'default'
    }
)

status = response.json()['status']
deployment_url = response.json()['deploymentUrl']
```

## Step 9: Test Deployment

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

## 🎉 Success!

Your SARIMAX forecasting model is now deployed and ready to use!

## 📊 Monitoring

- View deployment status in SAP AI Launchpad
- Check logs for errors
- Monitor resource usage
- Track API calls

## 🔄 Updates

To update the deployment:
1. Modify the workflow file
2. Push changes to GitHub
3. SAP AI Core will auto-sync
4. Create new deployment with updated configuration

## 🆘 Troubleshooting

### Scenario not found
- Wait 2-3 minutes for sync
- Check application is linked to repository
- Verify repository path is correct

### Deployment fails
- Check Docker secret is created
- Verify image is accessible
- Review deployment logs

### Image pull errors
- Ensure docker-secret exists
- Check Docker Hub credentials
- Verify image name is correct

## 📚 Resources

- [SAP AI Core Documentation](https://help.sap.com/docs/AI_CORE)
- [SAP AI Core API](https://api.sap.com/api/AI_CORE_API/overview)
- [Tutorial: Deploy with AI Core](https://developers.sap.com/tutorials/ai-core-code.html)
