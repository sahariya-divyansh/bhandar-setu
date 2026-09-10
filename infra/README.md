# Bhandar Setu — Production Infrastructure & Deployment Guide

This directory contains production deployment configurations for:
- **Backend Service (`cloudrun/`)**: Google Cloud Run serverless container service
- **Frontend SPA (`firebase/`)**: Firebase Hosting static web application hosting

---

## 1. Backend Deployment (Google Cloud Run)

### Prerequisites
- Google Cloud SDK (`gcloud` CLI) installed and authenticated (`gcloud auth login`)
- GCP Project created (e.g., `bhandar-setu-prod`) with billing enabled
- Artifact Registry & Cloud Run APIs enabled:
  ```bash
  gcloud services enable artifactregistry.googleapis.com run.googleapis.com secretmanager.googleapis.com
  ```

### Step 1: Create Artifact Registry Repository
```bash
gcloud artifacts repositories create bhandar-setu-repo \
  --repository-format=docker \
  --location=asia-south1 \
  --description="Bhandar Setu Container Images"
```

### Step 2: Build & Push Docker Container Image
From the repository root (`bhandar-setu/`):
```bash
# Configure Docker authentication for Artifact Registry
gcloud auth configure-docker asia-south1-docker.pkg.dev

# Build multi-stage production container image
docker build -t asia-south1-docker.pkg.dev/bhandar-setu-prod/bhandar-setu-repo/backend:latest -f infra/cloudrun/Dockerfile .

# Push image to GCP Artifact Registry
docker push asia-south1-docker.pkg.dev/bhandar-setu-prod/bhandar-setu-repo/backend:latest
```

### Step 3: Configure GCP Secrets (Optional / Recommended)
```bash
# Create Gemini API Key secret
echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-

# Grant Secret Accessor role to Cloud Run service account
PROJECT_NUMBER=$(gcloud projects describe bhandar-setu-prod --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Step 4: Deploy to Cloud Run
```bash
gcloud run deploy bhandar-setu-backend \
  --image=asia-south1-docker.pkg.dev/bhandar-setu-prod/bhandar-setu-repo/backend:latest \
  --region=asia-south1 \
  --platform=managed \
  --allow-unauthenticated \
  --min-instances=0 \
  --max-instances=3 \
  --memory=512Mi \
  --set-env-vars="ENVIRONMENT=production,ALLOWED_ORIGINS=https://bhandar-setu.web.app,https://bhandar-setu.firebaseapp.app" \
  --set-secrets="GEMINI_API_KEY=gemini-api-key:latest"
```

> **Result**: Save the returned Service URL (e.g., `https://bhandar-setu-backend-xyz-el.a.run.app`). You will need this URL for the frontend configuration.

---

## 2. Frontend Deployment (Firebase Hosting)

### Prerequisites
- Node.js v18+ and Firebase CLI installed (`npm install -g firebase-tools`)

### Step 1: Firebase Login & Project Initialization
```bash
# Authenticate with Google / Firebase
firebase login

# Initialize Firebase in project (if not already configured)
cd infra/firebase
firebase init hosting
```

### Step 2: Build Frontend with Cloud Run API Target
From the repository root (`bhandar-setu/`):
```bash
cd frontend

# Set environment variable targeting deployed Cloud Run URL
export VITE_API_BASE_URL=https://bhandar-setu-backend-xyz-el.a.run.app

# Build optimized production bundle
npm run build
```

### Step 3: Deploy to Firebase Hosting
```bash
cd ../infra/firebase
firebase deploy --only hosting
```

> **Result**: Your frontend SPA will be live at `https://bhandar-setu.web.app`.
