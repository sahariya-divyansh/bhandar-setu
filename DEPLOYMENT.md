# Bhandar Setu — End-to-End Production Deployment Guide

This document outlines the complete step-by-step deployment sequence for publishing Bhandar Setu to production.

---

## 📋 Deployment Sequence Overview

```
┌─────────────────────────────────┐
│ 1. Deploy Backend to Cloud Run  │ ──► Generates Cloud Run Service URL
└────────────────┬────────────────┘     (e.g., https://backend-xyz.a.run.app)
                 │
                 ▼
┌─────────────────────────────────┐
│ 2. Set VITE_API_BASE_URL        │ ──► Injects Cloud Run URL into Frontend
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ 3. Build & Deploy Frontend      │ ──► Published on Firebase Hosting
└────────────────┬────────────────┘     (e.g., https://bhandar-setu.web.app)
                 │
                 ▼
┌─────────────────────────────────┐
│ 4. Verify System Integration    │ ──► Health checks & CORS validation
└─────────────────────────────────┘
```

---

## Phase 1: Deploy Backend Service (Google Cloud Run)

### Step 1.1: Authenticate and Set GCP Project
```bash
gcloud auth login
gcloud config set project bhandar-setu-prod
gcloud services enable artifactregistry.googleapis.com run.googleapis.com secretmanager.googleapis.com
```

### Step 1.2: Build and Push Production Container Image
From the repository root (`bhandar-setu/`):
```bash
# Configure Docker credential helper
gcloud auth configure-docker asia-south1-docker.pkg.dev

# Create Artifact Registry repository if not exists
gcloud artifacts repositories create bhandar-setu-repo \
  --repository-format=docker \
  --location=asia-south1

# Build multi-stage production container
docker build -t asia-south1-docker.pkg.dev/bhandar-setu-prod/bhandar-setu-repo/backend:latest -f infra/cloudrun/Dockerfile .

# Push image to registry
docker push asia-south1-docker.pkg.dev/bhandar-setu-prod/bhandar-setu-repo/backend:latest
```

### Step 1.3: Deploy to Cloud Run
```bash
gcloud run deploy bhandar-setu-backend \
  --image=asia-south1-docker.pkg.dev/bhandar-setu-prod/bhandar-setu-repo/backend:latest \
  --region=asia-south1 \
  --platform=managed \
  --allow-unauthenticated \
  --min-instances=0 \
  --max-instances=3 \
  --memory=512Mi \
  --set-env-vars="ENVIRONMENT=production,ALLOWED_ORIGINS=https://bhandar-setu.web.app,https://bhandar-setu.firebaseapp.app"
```

> 📌 **Important**: Note down the generated Cloud Run URL:
> `https://bhandar-setu-backend-xyz-el.a.run.app`

---

## Phase 2: Deploy Frontend Web Application (Firebase Hosting)

### Step 2.1: Configure Environment & Build
From the repository root (`bhandar-setu/`):
```bash
cd frontend

# Set the deployed Cloud Run API URL
export VITE_API_BASE_URL=https://bhandar-setu-backend-xyz-el.a.run.app

# Install dependencies and build static distribution bundle
npm install
npm run build
```

### Step 2.2: Deploy to Firebase Hosting
```bash
cd ../infra/firebase

# Login to Firebase (if not already logged in)
firebase login

# Deploy static assets to Firebase CDN
firebase deploy --only hosting
```

> 📌 **Target Application URL**: `https://bhandar-setu.web.app`

---

## Phase 3: Post-Deployment Verification

### 1. Verify Backend Health Endpoint
```bash
curl https://bhandar-setu-backend-xyz-el.a.run.app/health
```
**Expected Response**:
```json
{
  "status": "healthy",
  "service": "Bhandar Setu API",
  "version": "0.1.0",
  "environment": "production"
}
```

### 2. Verify Frontend SPA Load & CORS Communication
1. Open `https://bhandar-setu.web.app` in browser.
2. Verify that monitored facilities, risk matrix table, and redistribution planner load data without CORS errors.
