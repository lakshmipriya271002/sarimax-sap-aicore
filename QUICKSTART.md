# 🚀 QUICKSTART

## 1️⃣ Push to GitHub

```bash
cd /Users/i769086/Data\ Science/Time_series/expanding_window_SARIMAX/deployment/sarimax-sap-aicore

git init
git add .
git commit -m "Add SAP AI Core workflow"
git remote add origin https://github.com/YOUR_USERNAME/sarimax-sap-aicore.git
git push -u origin main
```

---

## 2️⃣ Deploy to SAP AI Core

```bash
cd /Users/i769086/Data\ Science/Time_series/expanding_window_SARIMAX/deployment

source ./set_credentials.sh
python3 01_create_docker_secret.py
python3 03_register_github.py
python3 04_deploy.py
```

---

## 📋 You Need

- ✅ GitHub account
- ✅ GitHub repository URL
- ✅ GitHub Personal Access Token
- ✅ Docker Hub access token
- ✅ SAP AI Core credentials (already configured)

---

## ⏱️ Time

- Push to GitHub: 2 minutes
- Deploy to SAP: 15 minutes
- **Total: ~17 minutes**

---

## 📖 More Details

- **FILES.md** - What each file does
- **UPLOAD_GUIDE.md** - Detailed upload instructions
- **DEPLOYMENT.md** - Complete deployment guide
- **API.md** - API documentation

---

**That's it! Simple and fast! 🎉**
