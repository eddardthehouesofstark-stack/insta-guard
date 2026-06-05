# InstaGuard Deployment Guide

## Prerequisites
- GitHub account
- Render account (https://render.com)
- Vercel account (https://vercel.com)

---

## Backend Deployment (Render)

### 1. Push Code to GitHub
```bash
cd instaGuard
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/instaguard.git
git push -u origin main
```

### 2. Deploy on Render
1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: instaguard-backend
   - **Root Directory**: `backend`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 3. Add Environment Variables
In Render dashboard, go to **Environment** and add:

```
SUPABASE_URL=your-supabase-url-here
SUPABASE_ANON_KEY=your-supabase-anon-key-here
SUPABASE_SERVICE_KEY=your-supabase-service-key-here
GROQ_API_KEY=your-groq-api-key-here
JWT_SECRET=your-random-secure-secret-key-here
```

**Note**: Replace with your actual keys from:
- Supabase: https://supabase.com/dashboard → Project Settings → API
- Groq: https://console.groq.com → API Keys

### 4. Deploy
- Click **"Create Web Service"**
- Wait for deployment (5-10 minutes)
- Copy your backend URL: `https://instaguard-backend.onrender.com`

---

## Frontend Deployment (Vercel)

### 1. Update API URL
Before deploying, update `frontend/js/utils.js`:

```javascript
const API = window.location.hostname === 'localhost' 
  ? 'http://localhost:8000' 
  : 'https://YOUR-BACKEND-URL.onrender.com'; // Replace with your actual backend URL
```

### 2. Deploy on Vercel
1. Go to https://vercel.com
2. Click **"Add New"** → **"Project"**
3. Import your GitHub repository
4. Configure:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Other
   - **Build Command**: (leave empty)
   - **Output Directory**: `.`

### 3. Deploy
- Click **"Deploy"**
- Wait for deployment (2-3 minutes)
- Your site will be live at: `https://instaguard.vercel.app`

---

## Update Google OAuth Redirect URLs

### 1. Google Cloud Console
1. Go to https://console.cloud.google.com
2. Select your project
3. Go to **APIs & Services** → **Credentials**
4. Edit your OAuth 2.0 Client
5. Add to **Authorized redirect URIs**:
   ```
   https://mrbmrckpghhmuwdvaoxl.supabase.co/auth/v1/callback
   ```
6. Add to **Authorized JavaScript origins**:
   ```
   https://instaguard.vercel.app
   ```

### 2. Supabase Dashboard
1. Go to https://supabase.com/dashboard
2. Select your project
3. Go to **Authentication** → **URL Configuration**
4. Update **Site URL**: `https://instaguard.vercel.app`
5. Add to **Redirect URLs**:
   ```
   https://instaguard.vercel.app/*
   ```

---

## Backend CORS Configuration

Update `backend/main.py` to allow your frontend domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://instaguard.vercel.app",  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then redeploy the backend on Render.

---

## Testing Production Deployment

1. Visit your Vercel URL: `https://instaguard.vercel.app`
2. Click "Continue with Google"
3. Sign in
4. Test image analysis
5. Verify dashboard loads

---

## Troubleshooting

### Backend not responding
- Check Render logs: Dashboard → Logs
- Verify environment variables are set
- Check if service is running

### Frontend can't connect to backend
- Verify API URL in `utils.js` is correct
- Check browser console for CORS errors
- Verify backend CORS allows frontend domain

### Google OAuth not working
- Verify redirect URLs in Google Cloud Console
- Check Supabase URL configuration
- Clear browser cache and try again

---

## Free Tier Limitations

**Render Free Tier:**
- Service spins down after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds
- 750 hours/month (enough for one service)

**Vercel Free Tier:**
- 100 GB bandwidth/month
- Unlimited deployments
- Automatic HTTPS

**Upgrade to paid plans for:**
- No cold starts
- More bandwidth
- Better performance
- Custom domains

---

## Security Notes

1. **Never commit `.env` files** - Always use environment variables
2. **Use strong JWT_SECRET** - Generate with: `openssl rand -hex 32`
3. **Enable HTTPS** - Both Render and Vercel provide free SSL
4. **Update CORS origins** - Restrict to your actual domains in production
5. **Rotate API keys** - Regularly update Groq and Supabase keys

---

## Need Help?

- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- Supabase Docs: https://supabase.com/docs

