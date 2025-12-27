#!/bin/bash

# GrandPal Deployment Script for Google Cloud Run
# Prerequisites: gcloud CLI installed and configured

set -e

# Configuration - UPDATE THESE
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-your-project-id}"
REGION="us-central1"
BACKEND_SERVICE="grandpal-api"
FRONTEND_SERVICE="grandpal-web"

echo "🚀 Deploying GrandPal to Google Cloud Run..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"

# Enable required APIs
echo "📦 Enabling required APIs..."
gcloud services enable run.googleapis.com --project=$PROJECT_ID
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID
gcloud services enable artifactregistry.googleapis.com --project=$PROJECT_ID

# Deploy Backend
echo ""
echo "🔧 Deploying Backend..."
cd backend

gcloud run deploy $BACKEND_SERVICE \
    --source . \
    --project=$PROJECT_ID \
    --region=$REGION \
    --platform=managed \
    --allow-unauthenticated \
    --set-env-vars="ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY},GEMINI_API_KEY=${GEMINI_API_KEY},ELEVENLABS_AGENT_ID=${ELEVENLABS_AGENT_ID}" \
    --memory=512Mi \
    --cpu=1 \
    --timeout=300

# Get backend URL
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --project=$PROJECT_ID --region=$REGION --format='value(status.url)')
echo "✅ Backend deployed: $BACKEND_URL"

cd ..

# Update frontend to use backend URL
echo ""
echo "🎨 Deploying Frontend..."
cd frontend

# Create production vite config with backend URL
cat > .env.production << EOF
VITE_API_URL=${BACKEND_URL}
EOF

gcloud run deploy $FRONTEND_SERVICE \
    --source . \
    --project=$PROJECT_ID \
    --region=$REGION \
    --platform=managed \
    --allow-unauthenticated \
    --set-env-vars="BACKEND_URL=${BACKEND_URL}" \
    --memory=256Mi \
    --cpu=1

FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE --project=$PROJECT_ID --region=$REGION --format='value(status.url)')
echo "✅ Frontend deployed: $FRONTEND_URL"

cd ..

echo ""
echo "=========================================="
echo "🎉 Deployment Complete!"
echo "=========================================="
echo ""
echo "Frontend URL: $FRONTEND_URL"
echo "Backend URL:  $BACKEND_URL"
echo ""
echo "Next steps:"
echo "1. Test the app at $FRONTEND_URL"
echo "2. Update ELEVENLABS agent webhook to use $BACKEND_URL"
echo "3. Record your demo video!"

