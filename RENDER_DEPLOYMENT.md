# Render Deployment Guide

## Overview
This guide explains how to deploy the Megeb backend to Render.com using Docker. The frontend is deployed separately on Vercel for optimal performance.

## Prerequisites
- GitHub account with the Megeb repository
- Render.com account (free tier available)
- MongoDB Atlas account (for production database)
- Groq API key (for AI features)
- Cloudinary account (for image storage)

## Quick Deployment Steps

### 1. Push Code to GitHub
```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### 2. Deploy to Render
1. Go to [render.com](https://render.com) and sign up/login
2. Click "New +" and select "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml`
5. Review the configuration and click "Apply"

### 3. Configure Environment Variables
After deployment, add these environment variables in the Render dashboard for the `megeb-backend` service:

**Required Variables:**
- `MONGO_URL`: Your MongoDB Atlas connection string
  ```
  mongodb+srv://joshuaminase404_db_user:L6psm6qP4w7s7hBr@cluster0.at0ukfr.mongodb.net/?appName=Cluster0
  ```
- `GROQ_API_KEY`: Your Groq API key
  ```
  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
  ```
- `CLOUDINARY_CLOUD_NAME`: Your Cloudinary cloud name
  ```
  uwdynwqg
  ```
- `CLOUDINARY_API_KEY`: Your Cloudinary API key
  ```
  648132774427692
  ```
- `CLOUDINARY_API_SECRET`: Your Cloudinary API secret
  ```
  xkNMi8o-j5CxZ3QrIjUlEdw2lxw
  ```

**Auto-Generated:**
- `JWT_SECRET`: Render will auto-generate this

**Pre-Configured:**
- `CORS_ORIGINS`: Will be set to your Render URLs (update after deployment)
- `PORT`: Set to 8000
- `RENDER`: Set to true (detects Render environment)

### 4. Update CORS Origins
After deployment, update the `CORS_ORIGINS` environment variable with your actual Render URLs:
```
https://your-frontend-url.onrender.com,https://your-backend-url.onrender.com
```

## Services Created

### Backend Service (`megeb-backend`)
- **Type**: Docker Web Service
- **Build**: Uses Dockerfile to build container
- **Start**: Runs FastAPI with Uvicorn in Docker
- **Port**: 8000
- **URL**: `https://megeb-backend.onrender.com`

### Note on Frontend
The frontend is deployed separately on Vercel for optimal performance. See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for frontend deployment instructions.

## Post-Deployment Setup

### 1. Test the Deployment
- Frontend: `https://megeb-frontend.onrender.com`
- Backend Health: `https://megeb-backend.onrender.com/health`
- API Status: `https://megeb-backend.onrender.com/api`

### 2. Set Up Admin User
Connect to MongoDB Atlas and promote a user to admin:
```javascript
db.users.updateOne({ email: "your@email.com" }, { $set: { role: "admin" } })
```

### 3. Configure Custom Domain (Optional)
1. Add custom domain in Render dashboard
2. Update DNS records as instructed by Render
3. Update `CORS_ORIGINS` environment variable
4. Update `frontend/js/config.js` if needed

## Environment-Specific Configuration

The frontend automatically detects the environment and configures the API URL:

- **Local Development**: Uses `http://localhost:8000` or same-origin proxy
- **Render**: Uses `https://megeb-backend.onrender.com`
- **Custom Domain**: Uses same-origin (relative URLs)

## Troubleshooting

### Backend Fails to Start
- Check Render logs for error messages
- Verify all environment variables are set
- Ensure MongoDB Atlas connection string is correct
- Check that required services are running

### Frontend Cannot Connect to API
- Verify CORS origins are correctly configured
- Check that backend service is running
- Verify API URL configuration in `frontend/js/config.js`
- Check browser console for CORS errors

### Database Connection Issues
- Verify MongoDB Atlas connection string
- Check Atlas IP whitelist (includes Render's IP ranges)
- Ensure Atlas database user has correct permissions
- Check database is not paused in Atlas

### Free Tier Limitations
- Render free tier services spin down after inactivity
- First request may take longer (cold start)
- Consider upgrading to paid tier for better performance
- MongoDB Atlas free tier has connection limits

## Monitoring and Logs

### View Logs
- Go to Render dashboard
- Select the service (backend or frontend)
- Click "Logs" tab
- View real-time logs and historical logs

### Health Checks
- Backend health: `https://megeb-backend.onrender.com/health`
- Expected response: `{"status":"ok","db":true}`

### Metrics
- Render provides basic metrics in the dashboard
- Monitor response times, error rates, and resource usage
- Set up alerts for critical failures

## Scaling Considerations

### When to Scale Up
- High traffic volumes
- Slow response times
- Frequent timeouts
- Memory/CPU constraints

### Scaling Options
- Upgrade to paid Render plan
- Add more instances (horizontal scaling)
- Increase instance size (vertical scaling)
- Consider CDN for static assets

## Backup and Recovery

### Database Backups
- MongoDB Atlas provides automated backups
- Configure backup retention in Atlas dashboard
- Test restore procedures regularly

### Application Backups
- Code is stored in GitHub
- Environment variables in Render dashboard
- Document any manual configuration changes

## Security Best Practices

### Environment Variables
- Never commit `.env` file to Git
- Use Render's environment variable management
- Rotate secrets regularly
- Use strong JWT_SECRET

### API Security
- CORS properly configured
- Rate limiting enabled (slowapi)
- Input validation on all endpoints
- SQL injection prevention (MongoDB sanitization)

### User Data
- Passwords hashed with bcrypt
- JWT tokens for authentication
- Admin role for sensitive operations
- HTTPS enforced by Render

## Cost Optimization

### Free Tier Limitations
- 512MB RAM for web services
- 0.1 CPU hours per month
- Services spin down after inactivity
- Ephemeral filesystem

### Cost Reduction Tips
- Optimize database queries
- Implement caching where possible
- Use CDN for static assets
- Monitor and optimize resource usage

### Paid Tier Benefits
- No spin-up time
- More RAM and CPU
- Better performance
- Priority support

## Maintenance

### Regular Tasks
- Monitor logs for errors
- Update dependencies regularly
- Review security advisories
- Test backup restoration
- Review resource usage

### Updates and Deployments
- Push changes to GitHub
- Render auto-deploys on push
- Monitor deployment logs
- Test after each deployment
- Roll back if issues occur

## Support Resources

- [Render Documentation](https://render.com/docs)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Groq API Documentation](https://console.groq.com/docs)
- [Cloudinary Documentation](https://cloudinary.com/documentation)

## Summary

The Megeb platform is now configured for easy deployment to Render with:

- ✅ Automated deployment via `render.yaml`
- ✅ Environment-specific configuration
- ✅ Production-ready services
- ✅ Comprehensive documentation
- ✅ Security best practices
- ✅ Monitoring and logging setup

Deploy to Render and your Ethiopian recipe platform will be live in minutes! 🇪🇹
