# Deployment Guide - Render

## Pre-deployment Checklist

✅ **Completed:**
- PostgreSQL database ready (Supabase)
- Requirements.txt updated with all dependencies
- Environment variables documented in .env.example
- Worker auto-starts with server (AUTO_START_WORKER=true)
- Health check endpoint available at `/health`
- PORT environment variable support added

## Render Deployment Steps

### 1. Create New Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your Git repository

### 2. Configure Service

**Basic Settings:**
- **Name**: `applix-devops-automation`
- **Environment**: `Python 3`
- **Region**: Choose closest to your database (e.g., Singapore for Supabase)
- **Branch**: `main`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `./start.sh`

**Advanced Settings:**
- **Instance Type**: Free or Starter ($7/month recommended for production)
- **Health Check Path**: `/health`

### 3. Environment Variables

Add these in Render dashboard (Settings → Environment):

```
AZURE_DEVOPS_ORG=applix-ai-dev
AZURE_DEVOPS_PROJECT=Devops-automation
AZURE_DEVOPS_PAT=your-pat-token-here

DATABASE_URL=postgresql://postgres.ycdlqesdpszcplionrfm:Mydatabase12312345@aws-1-ap-northeast-1.pooler.supabase.com:5432/postgres

ENVIRONMENT=production
DEBUG=False
AUTO_START_WORKER=true

API_TITLE=Azure DevOps Automation - Event-Driven
API_DESCRIPTION=Async user story processing with event queue
API_VERSION=1.0.0
```

### 4. Deploy

1. Click **"Create Web Service"**
2. Render will automatically build and deploy
3. Wait for deployment to complete (2-3 minutes)

### 5. Verify Deployment

Test these endpoints:
```bash
# Health check
curl https://your-app.onrender.com/health

# API documentation
https://your-app.onrender.com/docs

# Create user story (test)
curl -X POST https://your-app.onrender.com/userstory/create \
  -H "Content-Type: application/json" \
  -d '{"id": 123, "title": "Test Story", "area_path": "Devops-automation", "iteration_path": "Devops-automation"}'
```

## Azure DevOps Webhook Integration (Optional)

To automatically trigger task creation when stories are created in Azure:

### 1. Create Service Hook in Azure DevOps

1. Go to **Project Settings** → **Service Hooks**
2. Click **"+ Create subscription"**
3. Select **"Web Hooks"**
4. Configure:
   - **Trigger**: Work item created
   - **Filters**: Work Item Type = User Story
   - **URL**: `https://your-app.onrender.com/userstory/create`
   - **HTTP Headers**: `Content-Type: application/json`

### 2. Transform Payload (if needed)

Azure DevOps webhook sends different payload format. You may need to:
- Add a webhook endpoint that transforms Azure payload
- Or use Azure Logic Apps/Power Automate to transform and call your API

## Monitoring

**Render Dashboard:**
- View logs: Service → Logs
- Monitor metrics: Service → Metrics
- Check events: Service → Events

**Useful Commands:**
```bash
# View recent logs
render logs --tail

# Check service status
render services list
```

## Troubleshooting

**Service won't start:**
- Check logs in Render dashboard
- Verify DATABASE_URL is correct
- Ensure all environment variables are set

**Worker not processing:**
- Check AUTO_START_WORKER=true
- View logs for worker startup message: "✓ Worker daemon started in background"

**Database connection fails:**
- Verify DATABASE_URL format
- Check Supabase pooler is accessible from Render region
- Test connection from Render shell

**Tasks not created in Azure:**
- Verify AZURE_DEVOPS_PAT has correct permissions
- Check Azure DevOps org and project names
- View event logs in database for error messages

## Scaling

**Free Tier Limitations:**
- Sleeps after 15 minutes of inactivity
- Wakes up on request (adds ~30s delay)
- 750 hours/month free

**Upgrade to Paid:**
- Always on (no sleep)
- Better performance
- Custom domains
- More memory/CPU

## Next Steps

1. ✅ Deploy to Render
2. ⏳ Test end-to-end with real Azure DevOps stories
3. ⏳ Set up Azure webhook (optional)
4. ⏳ Monitor for 24 hours
5. ⏳ Configure alerts/notifications

## Support

- **Render Docs**: https://render.com/docs
- **Azure DevOps API**: https://learn.microsoft.com/en-us/rest/api/azure/devops/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
