***REMOVED*** Google Cloud Run - Deployment Checklist

***REMOVED******REMOVED*** Pre-Deployment

- [ ] Google Cloud account with billing enabled
- [ ] gcloud CLI installed and authenticated
- [ ] Project created in GCP Console
- [ ] Required APIs enabled (Cloud Run, Cloud Build, Artifact Registry)
- [ ] `.env` file created with production API keys

***REMOVED******REMOVED*** Deployment Steps

***REMOVED******REMOVED******REMOVED*** 1. Authentication & Project Setup

```powershell
***REMOVED*** Authenticate
gcloud auth login
gcloud auth application-default login

***REMOVED*** Set project
gcloud config set project YOUR_PROJECT_ID
***REMOVED*** Or: $env:GCP_PROJECT_ID = "your-project-id"

***REMOVED*** Enable APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

***REMOVED******REMOVED******REMOVED*** 2. Environment Variables

Create `backend/.env`:

```env
ENV=production
SOARB2B_API_KEYS=production-key-1,production-key-2,production-key-3
FINDEROS_CORS_ORIGINS=https://soarb2b.com,https://www.soarb2b.com
FINDEROS_CORS_ALLOW_ALL=false
```

***REMOVED******REMOVED******REMOVED*** 3. Deploy

```powershell
***REMOVED*** From project root
.\deploy_gcp.ps1
```

Or manually:

```powershell
cd backend
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/soarb2b-v1

gcloud run deploy soarb2b `
  --image gcr.io/YOUR_PROJECT_ID/soarb2b-v1 `
  --platform managed `
  --region europe-west3 `
  --allow-unauthenticated `
  --set-env-vars "ENV=production,SOARB2B_API_KEYS=key1,key2" `
  --memory 512Mi `
  --timeout 300 `
  --port 8080
```

***REMOVED******REMOVED*** Post-Deployment Verification

```powershell
***REMOVED*** Get service URL
$url = gcloud run services describe soarb2b --region europe-west3 --format="value(status.url)"

***REMOVED*** Health check
Invoke-WebRequest "$url/healthz" -UseBasicParsing

***REMOVED*** Homepage
Invoke-WebRequest "$url/ui/soarb2b_home.html" -UseBasicParsing

***REMOVED*** Root redirect
Invoke-WebRequest "$url/" -UseBasicParsing -MaximumRedirection 0 -ErrorAction SilentlyContinue

***REMOVED*** API test
$headers = @{"X-API-Key" = "your-production-key"}
Invoke-WebRequest -Uri "$url/api/v1/b2b/demo/hotels" -Headers $headers -UseBasicParsing
```

***REMOVED******REMOVED*** Custom Domain (Optional)

```powershell
***REMOVED*** Map domain
gcloud run domain-mappings create `
  --service soarb2b `
  --domain www.soarb2b.com `
  --region europe-west3

***REMOVED*** Follow DNS configuration instructions
```

***REMOVED******REMOVED*** Files Modified for Cloud Run

1. **backend/src/main.py** - PORT env var support (default 8080), skip port check in Cloud Run
2. **backend/dockerfile** - Slim image, PORT 8080, stateless
3. **backend/src/app.py** - Root redirect (301), static files mount with html=True
4. **deploy_gcp.ps1** - Automated deployment script

---

**Ready to deploy?** Run `.\deploy_gcp.ps1`
