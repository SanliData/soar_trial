***REMOVED*** SOAR B2B - Google Cloud Run Deployment Guide

***REMOVED******REMOVED*** Overview

Google Cloud Run is a serverless platform that automatically scales containers. This guide covers deployment to Cloud Run with pay-as-you-go pricing.

***REMOVED******REMOVED*** Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud CLI (gcloud)** installed
3. **Project created** in Google Cloud Console

***REMOVED******REMOVED*** Quick Start

***REMOVED******REMOVED******REMOVED*** 1. Install Google Cloud CLI

**Windows:**
```powershell
***REMOVED*** Download and install from:
***REMOVED*** https://cloud.google.com/sdk/docs/install-sdk

***REMOVED*** Or use Chocolatey:
choco install gcloudsdk
```

***REMOVED******REMOVED******REMOVED*** 2. Authenticate

```powershell
gcloud auth login
gcloud auth application-default login
```

***REMOVED******REMOVED******REMOVED*** 3. Set Project

```powershell
***REMOVED*** List projects
gcloud projects list

***REMOVED*** Set active project
gcloud config set project YOUR_PROJECT_ID

***REMOVED*** Or set via environment variable
$env:GCP_PROJECT_ID = "your-project-id"
```

***REMOVED******REMOVED******REMOVED*** 4. Enable Required APIs

```powershell
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

***REMOVED******REMOVED******REMOVED*** 5. Prepare .env File

Create `backend/.env` with production values:

```env
ENV=production
SOARB2B_API_KEYS=your-production-key-1,your-production-key-2,your-production-key-3
FINDEROS_CORS_ORIGINS=https://soarb2b.com,https://www.soarb2b.com
FINDEROS_CORS_ALLOW_ALL=false
```

***REMOVED******REMOVED******REMOVED*** 6. Deploy

```powershell
***REMOVED*** From project root
.\deploy_gcp.ps1
```

***REMOVED******REMOVED*** What the Script Does

1. **Builds Docker image** using Cloud Build
2. **Pushes to Artifact Registry** (gcr.io)
3. **Deploys to Cloud Run** with:
   - Unauthenticated access (public)
   - Environment variables from .env
   - 512MB memory
   - 300s timeout
   - Port 8080 (Cloud Run standard)
   - Auto-scaling (0-10 instances)

***REMOVED******REMOVED*** Manual Deployment

If you prefer manual steps:

```powershell
cd backend

***REMOVED*** Build and submit
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/soarb2b-v1

***REMOVED*** Deploy
gcloud run deploy soarb2b `
  --image gcr.io/YOUR_PROJECT_ID/soarb2b-v1 `
  --platform managed `
  --region europe-west3 `
  --allow-unauthenticated `
  --set-env-vars "ENV=production,SOARB2B_API_KEYS=key1,key2,FINDEROS_CORS_ORIGINS=https://soarb2b.com" `
  --memory 512Mi `
  --timeout 300 `
  --port 8080
```

***REMOVED******REMOVED*** Custom Domain Setup

After deployment:

***REMOVED******REMOVED******REMOVED*** Option 1: Cloud Run Domain Mapping

```powershell
***REMOVED*** Map custom domain
gcloud run domain-mappings create `
  --service soarb2b `
  --domain www.soarb2b.com `
  --region europe-west3
```

Follow DNS configuration instructions provided by gcloud.

***REMOVED******REMOVED******REMOVED*** Option 2: Cloud Load Balancer + Domain

For production with SSL:
- Use Cloud Load Balancer
- Map domain to load balancer
- SSL certificate managed by Google

***REMOVED******REMOVED*** Configuration

***REMOVED******REMOVED******REMOVED*** Environment Variables

Cloud Run environment variables can be set via:
1. `.env` file (read by deploy script)
2. `gcloud run services update` command
3. Cloud Console UI

```powershell
***REMOVED*** Update environment variables
gcloud run services update soarb2b `
  --region europe-west3 `
  --update-env-vars "SOARB2B_API_KEYS=new-key-1,new-key-2"
```

***REMOVED******REMOVED******REMOVED*** Resource Limits

Current settings:
- **Memory:** 512Mi (adjustable: 128Mi - 8Gi)
- **CPU:** 1 vCPU (allocated based on memory)
- **Timeout:** 300s (max: 3600s)
- **Concurrency:** 80 requests/instance (Cloud Run default)

To increase:
```powershell
gcloud run services update soarb2b `
  --region europe-west3 `
  --memory 1Gi `
  --timeout 600
```

***REMOVED******REMOVED******REMOVED*** Auto-scaling

- **Min instances:** 0 (scales to zero when idle)
- **Max instances:** 10 (auto-scales based on traffic)
- **Scale down:** After 15 minutes of inactivity

To keep instances warm:
```powershell
gcloud run services update soarb2b `
  --region europe-west3 `
  --min-instances 1
```

***REMOVED******REMOVED*** Verification

After deployment:

```powershell
***REMOVED*** Get service URL
$url = gcloud run services describe soarb2b --region europe-west3 --format="value(status.url)"

***REMOVED*** Health check
Invoke-WebRequest "$url/healthz" -UseBasicParsing

***REMOVED*** Homepage
Start-Process "$url/ui/soarb2b_home.html"
```

***REMOVED******REMOVED*** Monitoring

***REMOVED******REMOVED******REMOVED*** View Logs

```powershell
***REMOVED*** Real-time logs
gcloud run logs read soarb2b --region europe-west3 --follow

***REMOVED*** Recent logs
gcloud run logs read soarb2b --region europe-west3 --limit 50
```

***REMOVED******REMOVED******REMOVED*** Cloud Console

- **Logs:** https://console.cloud.google.com/run
- **Metrics:** https://console.cloud.google.com/run/detail/europe-west3/soarb2b/metrics

***REMOVED******REMOVED*** Cost Estimate

Cloud Run pricing (pay-as-you-go):
- **CPU:** $0.00002400 per vCPU-second
- **Memory:** $0.00000250 per GiB-second
- **Requests:** $0.40 per million requests (first 2M free)
- **Free tier:** 2 million requests/month

Estimated monthly cost for SOAR B2B:
- Light usage (10K requests): **~$0-5/month**
- Medium usage (100K requests): **~$10-20/month**
- Heavy usage (1M requests): **~$50-100/month**

***REMOVED******REMOVED*** Troubleshooting

***REMOVED******REMOVED******REMOVED*** Build Fails

```powershell
***REMOVED*** Check build logs
gcloud builds list --limit 5

***REMOVED*** View specific build
gcloud builds log BUILD_ID
```

***REMOVED******REMOVED******REMOVED*** Service Won't Start

```powershell
***REMOVED*** Check service status
gcloud run services describe soarb2b --region europe-west3

***REMOVED*** View logs
gcloud run logs read soarb2b --region europe-west3 --limit 100
```

***REMOVED******REMOVED******REMOVED*** Static Files Not Loading

- Verify `src/ui/` directory is in Docker image
- Check Cloud Run logs for 404 errors
- Ensure `/ui` mount path is correct in `app.py`

***REMOVED******REMOVED******REMOVED*** Port Issues

Cloud Run automatically sets `PORT` environment variable (usually 8080).
The Dockerfile CMD should use `${PORT:-8080}`.

***REMOVED******REMOVED*** Rollback

```powershell
***REMOVED*** List revisions
gcloud run revisions list --service soarb2b --region europe-west3

***REMOVED*** Rollback to previous revision
gcloud run services update-traffic soarb2b `
  --region europe-west3 `
  --to-revisions PREVIOUS_REVISION=100
```

***REMOVED******REMOVED*** CI/CD Integration

For automated deployments, add to GitHub Actions or GitLab CI:

```yaml
***REMOVED*** .github/workflows/deploy.yml
name: Deploy to Cloud Run
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: google-github-actions/setup-gcloud@v0
      - run: gcloud builds submit --tag gcr.io/$PROJECT_ID/soarb2b-v1
      - run: gcloud run deploy soarb2b ...
```

---

**For detailed deployment steps, see:** `DEPLOY_TO_SOARB2B_COM.md`
