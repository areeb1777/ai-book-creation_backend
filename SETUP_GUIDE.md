# External Services Setup Guide

This guide provides step-by-step instructions for setting up all required external services.

## 1. OpenAI Platform Setup

**Steps**:
1. Visit [platform.openai.com](https://platform.openai.com/)
2. Create an account or sign in
3. Go to API Keys section: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
4. Click "Create new secret key"
5. Name it "RAG Chatbot Dev"
6. **IMPORTANT**: Copy the key immediately (starts with `sk-...`) - you won't see it again
7. Set usage limit: Go to Settings → Usage limits → Set $5/month limit

**What you'll need for .env**:
```
OPENAI_API_KEY=sk-your-key-here
```

**Cost estimate**: ~$0.01 for ingestion, ~$0.001 per query

---

## 2. Qdrant Cloud Setup

**Steps**:
1. Visit [cloud.qdrant.io](https://cloud.qdrant.io/)
2. Sign up with email or GitHub
3. Create new cluster:
   - Click "Create Cluster"
   - Name: `book-chatbot-dev`
   - Region: Choose closest to you
   - Tier: **Free** (1GB storage, 100 RPM)
4. Wait for cluster provisioning (~30 seconds)
5. Get credentials:
   - Click on cluster name
   - Copy **Cluster URL**: `https://xyz-abc.cloud.qdrant.io`
   - Click "API Keys" → "Generate API Key"
   - Copy the API key

**What you'll need for .env**:
```
QDRANT_URL=https://xyz-abc.cloud.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key
QDRANT_COLLECTION_NAME=book_chunks
```

**Free tier limits**: 1GB storage (~1M vectors), 100 requests/minute

---

## 3. Neon Serverless Postgres Setup

**Steps**:
1. Visit [neon.tech](https://neon.tech/)
2. Sign up with email or GitHub
3. Create new project:
   - Click "New Project"
   - Name: `rag-chatbot-dev`
   - Region: Choose closest to you
   - Postgres version: 15 (default)
4. Get connection string:
   - Go to Dashboard → Connection Details
   - Copy **Pooled connection** string (recommended for serverless):
     ```
     postgresql://user:pass@ep-xyz.neon.tech/dbname?sslmode=require
     ```
5. Enable auto-pause:
   - Go to Settings → Compute
   - Set "Auto-pause after": 5 minutes (default)

**What you'll need for .env**:
```
DATABASE_URL=postgresql://user:pass@ep-xyz.neon.tech/dbname?sslmode=require
```

**Free tier limits**: 0.5GB storage, 100 compute hours/month (auto-pause extends this)

---

## 4. Railway Setup (for deployment)

**Steps**:
1. Visit [railway.app](https://railway.app/)
2. Sign up with GitHub (recommended for auto-deploy)
3. Click "New Project" → "Deploy from GitHub repo"
4. Authorize Railway to access your GitHub
5. Select your repository
6. Select branch: `001-rag-chatbot`
7. Railway will auto-detect Dockerfile
8. **Don't deploy yet** - we'll set environment variables first

**What you'll do later**:
- Set all environment variables in Railway dashboard
- Enable auto-deploy on git push
- Get public URL for production backend

---

## 5. Verification Checklist

Before proceeding to implementation, verify you have:

- [ ] OpenAI API key (starts with `sk-`)
- [ ] OpenAI usage limit set ($5/month recommended)
- [ ] Qdrant cluster URL and API key
- [ ] Neon database connection string (pooled connection)
- [ ] Railway account linked to GitHub

---

## 6. Next Steps

After completing external service setup:

1. Create `.env` file (see T008)
2. Run setup scripts to initialize databases (T021, T024)
3. Test service connections with health endpoint (T028-T029)

---

## Cost Estimates

**Development Phase** (1-2 months):
- OpenAI: ~$0.10-$0.50 (ingestion + testing)
- Qdrant: $0 (free tier sufficient)
- Neon: $0 (free tier sufficient)
- Railway: $0 (free tier: 500 hours/month)
- **Total**: <$1

**Production Phase** (per month, 1000 queries):
- OpenAI: ~$2 (embeddings + chat completions)
- Qdrant: $0 (free tier sufficient for single book)
- Neon: $0 (free tier sufficient with auto-pause)
- Railway: $0-$5 (depends on traffic)
- **Total**: ~$2-$7/month

---

## Troubleshooting

### OpenAI API Key Invalid
- Verify key copied correctly (no extra spaces)
- Check billing enabled: Settings → Billing
- Verify key not deleted in dashboard

### Qdrant Connection Failed
- Verify cluster is "Running" (not "Stopped")
- Test with curl:
  ```bash
  curl -X GET "YOUR_QDRANT_URL/collections" -H "api-key: YOUR_KEY"
  ```

### Neon Connection Timeout
- Verify database is not paused (Dashboard → Compute)
- Use **pooled connection** string (not direct)
- Check firewall not blocking port 5432

### Railway Deployment Issues
- Verify Dockerfile exists in rag-backend/
- Check Railway build logs for errors
- Ensure all environment variables set in Railway dashboard
