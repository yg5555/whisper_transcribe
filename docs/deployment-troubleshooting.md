# Deployment Troubleshooting Guide

## Common Issues and Solutions

### 1. Application Times Out After 10 Minutes

**Symptoms:**
- Application starts successfully (server running on port 8000)
- Logs show "Timed Out" after 10 minutes
- Health checks may be failing

**Root Cause:**
- Render's health check is failing because the health endpoint wasn't properly configured
- The application might be taking too long to respond to health checks

**Solutions:**
1. **Added root health endpoint**: Both `/health` and `/api/health` are now available
2. **Improved health check configuration**: Added `healthCheckPath: /health` to `render.yaml`
3. **Enhanced timeout settings**: Added `--timeout-keep-alive 75` to uvicorn startup
4. **Better error handling**: Improved start script with better fallback logic

### 2. Frontend Build Failures

**Symptoms:**
- "フロントエンドビルド失敗" in logs
- Application falls back to API-only mode

**Solutions:**
1. **Memory optimization**: Set `NODE_OPTIONS="--max-old-space-size=256"`
2. **Build script improvements**: Enhanced error handling in build process
3. **Graceful fallback**: Application continues to work in API-only mode

### 3. Port Configuration Issues

**Symptoms:**
- "New primary port detected" messages
- Application restarts due to port changes

**Solutions:**
1. **Dynamic port handling**: Use `${PORT:-8000}` in start script
2. **Explicit port configuration**: Set `PORT: 8000` in environment variables
3. **Host binding**: Ensure `--host 0.0.0.0` for proper binding

## Health Check Endpoints

The application now provides multiple health check endpoints:

- `/health` - Root health endpoint (for Render health checks)
- `/api/health` - API-specific health endpoint
- `/` - Root endpoint with application info

## Testing Health Checks

Use the provided health check script:

```bash
# Test local deployment
python health_check.py

# Test deployed application
python health_check.py https://your-app-name.onrender.com
```

## Environment Variables

Ensure these environment variables are set in Render:

- `PYTHON_VERSION`: 3.11.0
- `NODE_VERSION`: 18.19.0
- `PORT`: 8000
- `NODE_OPTIONS`: --max-old-space-size=256

## Deployment Checklist

Before deploying:

1. ✅ Health endpoints are properly configured
2. ✅ Port configuration is correct
3. ✅ Memory limits are set for Node.js
4. ✅ Fallback logic is in place
5. ✅ Timeout settings are optimized
6. ✅ CORS is properly configured

## Monitoring

Monitor these key indicators:

1. **Startup time**: Should be under 2 minutes
2. **Health check responses**: Should return 200 OK
3. **Memory usage**: Should stay within limits
4. **Error logs**: Check for any recurring errors

## Recent Fixes Applied

1. **Added root health endpoint** to both main.py and main_fallback.py
2. **Enhanced start script** with better error handling and port configuration
3. **Updated render.yaml** with health check path configuration
4. **Improved timeout settings** for uvicorn server
5. **Created health check script** for testing endpoints 