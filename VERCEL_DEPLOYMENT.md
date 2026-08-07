# Vercel Deployment Guide (Frontend)

## Overview
This guide explains how to deploy the Megeb frontend to Vercel while keeping the backend on Render. This hybrid approach provides excellent performance for the static frontend with Vercel's global CDN.

## Architecture
- **Frontend**: Vercel (static site with global CDN)
- **Backend**: Render (Python FastAPI web service)
- **Database**: MongoDB Atlas (shared between both)
- **API Proxy**: Vercel rewrites API calls to Render backend

## Prerequisites
- GitHub account with the Megeb repository
- Vercel account (free tier available)
- Backend already deployed on Render
- MongoDB Atlas configured
- Backend API URL available

## Quick Deployment Steps

### 1. Deploy Backend to Render First
```bash
# Follow the Render deployment guide first
# Ensure backend is running at: https://megeb-backend.onrender.com
```

### 2. Deploy Frontend to Vercel
1. Go to [vercel.com](https://vercel.com) and sign up/login
2. Click "Add New Project" 
3. Import your GitHub repository
4. Vercel will automatically detect the `vercel.json` configuration
5. Configure project settings:
   - **Framework Preset**: Other
   - **Build Command**: `echo 'No build required'`
   - **Output Directory**: `frontend`
   - **Root Directory**: `./`

### 3. Configure Environment Variables (Optional)
The frontend doesn't require environment variables, but you can add:
- `NEXT_PUBLIC_API_URL`: Override backend URL (if needed)
- `NEXT_PUBLIC_APP_NAME`: Custom app name

### 4. Deploy
Click "Deploy" and Vercel will:
- Build the static site
- Deploy to global CDN
- Provide a URL like `https://megeb-frontend.vercel.app`

### 5. Update Backend CORS
After Vercel deployment, update the backend CORS origins:
1. Go to Render dashboard
2. Edit `megeb-backend` service
3. Update `CORS_ORIGINS` environment variable:
   ```
   https://megeb-backend.onrender.com,https://your-vercel-app.vercel.app
   ```

## Configuration Files

### vercel.json
```json
{
  "version": 2,
  "buildCommand": "echo 'No build required'",
  "outputDirectory": "frontend",
  "cleanUrls": true,
  "trailingSlash": false,
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://megeb-backend.onrender.com/api/:path*"
    },
    {
      "source": "/auth/:path*",
      "destination": "https://megeb-backend.onrender.com/auth/:path*"
    },
    {
      "source": "/health",
      "destination": "https://megeb-backend.onrender.com/health"
    }
  ]
}
```

### API Proxy Configuration
The `vercel.json` file configures URL rewrites to proxy API calls:
- `/api/*` → `https://megeb-backend.onrender.com/api/*`
- `/auth/*` → `https://megeb-backend.onrender.com/auth/*`
- `/health` → `https://megeb-backend.onrender.com/health`

This allows the frontend to make API calls without CORS issues.

## Environment Detection

The frontend automatically detects the deployment environment in `frontend/js/config.js`:

```javascript
// Vercel deployment
else if (hostname.includes('vercel.app')) {
  API_BASE_URL = 'https://megeb-backend.onrender.com';
}
```

## Post-Deployment Setup

### 1. Test the Deployment
- Frontend: `https://your-vercel-app.vercel.app`
- Backend Health: `https://megeb-backend.onrender.com/health`
- API Test: Try signing up/logging in on the frontend

### 2. Configure Custom Domain (Optional)
1. Go to Vercel dashboard
2. Select your project
3. Click "Settings" → "Domains"
4. Add your custom domain
5. Update DNS records as instructed
6. Update backend CORS origins with new domain

### 3. Set Up Admin User
Connect to MongoDB Atlas and promote a user to admin:
```javascript
db.users.updateOne({ email: "your@email.com" }, { $set: { role: "admin" } })
```

## Performance Optimization

### Vercel Benefits
- **Global CDN**: Content served from edge locations worldwide
- **Automatic HTTPS**: SSL certificates automatically configured
- **Fast Builds**: Static site builds in seconds
- **Instant Rollbacks**: One-click rollback to previous deployments
- **Analytics**: Built-in performance analytics

### Caching Strategy
- Static files cached at edge
- API calls proxied to backend
- Vercel automatically handles cache headers
- Browser caching configured in frontend

## Troubleshooting

### Frontend Cannot Connect to Backend
- Verify backend is running on Render
- Check CORS origins are correctly configured
- Test backend health endpoint directly
- Check browser console for CORS errors
- Verify API proxy configuration in vercel.json

### API Calls Failing
- Check backend logs on Render
- Verify Vercel rewrites are correct
- Test backend endpoints directly
- Check network tab in browser for request details
- Ensure backend CORS includes Vercel domain

### Build Failures
- Check Vercel build logs
- Verify file structure is correct
- Ensure frontend directory exists
- Check for any missing files
- Verify vercel.json syntax

### Custom Domain Issues
- Verify DNS records are correct
- Check Vercel domain configuration
- Ensure SSL certificate is issued
- Update CORS origins with custom domain
- Test both www and non-www versions

## Monitoring and Analytics

### Vercel Dashboard
- **Real-time logs**: View deployment and access logs
- **Analytics**: Page views, bandwidth, performance
- **Performance**: Core Web Vitals monitoring
- **Errors**: Track JavaScript errors and failed requests

### Backend Monitoring
- Monitor Render dashboard for backend health
- Check database connection status
- Monitor API response times
- Track error rates

## Security Considerations

### Frontend Security
- **HTTPS**: Automatic SSL certificates
- **Content Security Policy**: Can be configured in vercel.json
- **API Proxy**: Backend API not directly exposed
- **Environment Variables**: Sensitive data never exposed

### Backend Security
- **CORS**: Properly configured for Vercel domain
- **Rate Limiting**: Already configured with slowapi
- **Authentication**: JWT-based auth system
- **Input Validation**: All endpoints validate input

## Cost Comparison

### Vercel Free Tier
- Unlimited projects
- 100GB bandwidth per month
- Global CDN
- Automatic HTTPS
- Build minutes: 6,000 per month

### Render Free Tier
- Free web service
- 512MB RAM
- 0.1 CPU hours
- Spin-up time for inactive services

### Total Cost
- **Development**: $0 (both free tiers)
- **Production**: Free tiers sufficient for most use cases
- **Scale up**: Paid plans available for high traffic

## Scaling Strategy

### When to Scale Up
- High frontend traffic
- Slow API response times
- Frequent timeouts
- Resource constraints

### Scaling Options
- **Vercel**: Upgrade to Pro plan for more bandwidth
- **Render**: Upgrade to paid tier for better performance
- **Database**: Upgrade MongoDB Atlas cluster
- **CDN**: Vercel automatically scales globally

## Backup and Recovery

### Frontend Backup
- Code stored in GitHub
- Vercel maintains deployment history
- One-click rollback to previous versions
- No data to backup (static site)

### Backend Backup
- Code in GitHub
- Environment variables in Render dashboard
- Database backups via MongoDB Atlas
- Regular backup testing recommended

## CI/CD Integration

### Automatic Deployments
- **Vercel**: Auto-deploys on git push
- **Render**: Auto-deploys on git push
- **GitHub**: Can add status checks
- **Branch previews**: Vercel provides preview URLs

### Manual Deployments
- **Vercel**: Deploy via dashboard or CLI
- **Render**: Manual deploy trigger available
- **Rollback**: One-click rollback on both platforms

## Advanced Configuration

### Custom Headers (vercel.json)
```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        }
      ]
    }
  ]
}
```

### Redirects (vercel.json)
```json
{
  "redirects": [
    {
      "source": "/old-path",
      "destination": "/new-path",
      "statusCode": 301
    }
  ]
}
```

## Maintenance

### Regular Tasks
- Monitor Vercel analytics
- Check backend health
- Review security advisories
- Test backup restoration
- Update dependencies

### Updates and Deployments
- Push changes to GitHub
- Auto-deploy to both platforms
- Monitor deployment logs
- Test after each deployment
- Roll back if issues occur

## Support Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Render Documentation](https://render.com/docs)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com)
- [FastAPI Documentation](https://fastapi.tiangolo.com)

## Hybrid Deployment Benefits

### Why This Architecture?
- **Performance**: Vercel's global CDN for static assets
- **Cost**: Both platforms have generous free tiers
- **Flexibility**: Easy to scale each component independently
- **Reliability**: Redundant deployment across platforms
- **Developer Experience**: Both platforms have excellent DX

### Comparison with All-in-One
- **Render-only**: No global CDN, slower static asset delivery
- **Vercel-only**: More complex backend deployment
- **Hybrid**: Best of both worlds

## Summary

The hybrid deployment approach provides:
- ✅ Vercel's global CDN for frontend performance
- ✅ Render's simple Python backend deployment
- ✅ Cost-effective free tier usage
- ✅ Easy scaling and management
- ✅ Excellent developer experience
- ✅ Built-in monitoring and analytics

Deploy your frontend to Vercel and backend to Render for optimal performance! 🚀
