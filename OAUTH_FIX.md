# OAuth Login Loop Fix

## Problem
After clicking "Continue with Google", you get redirected back to the login page.

## Root Cause
The Supabase redirect URL configuration needs to be updated for production.

## Solution

### 1. Update Supabase Redirect URLs

Go to **Supabase Dashboard**:
1. https://supabase.com/dashboard
2. Select your project
3. Go to **Authentication** → **URL Configuration**
4. Update these settings:

**Site URL:**
```
https://insta-guard-lyart.vercel.app
```

**Redirect URLs** (add all of these):
```
http://localhost:3000/**
http://localhost:3000/pages/dashboard.html
https://insta-guard-lyart.vercel.app/**
https://insta-guard-lyart.vercel.app/pages/dashboard.html
```

5. Click **"Save"**

### 2. Verify Google OAuth Redirect URIs

Go to **Google Cloud Console**:
1. https://console.cloud.google.com
2. Go to **APIs & Services** → **Credentials**
3. Edit your OAuth 2.0 Client
4. Verify **Authorized redirect URIs** includes:
```
https://mrbmrckpghhmuwdvaoxl.supabase.co/auth/v1/callback
```

### 3. Test the Fix

1. Clear browser cache and localStorage:
   - Open DevTools (F12)
   - Application → Local Storage → Clear All
   - Application → Session Storage → Clear All

2. Close all tabs

3. Open in a new incognito window: https://insta-guard-lyart.vercel.app

4. Click "Continue with Google"

5. You should be redirected to dashboard after signing in!

### 4. If Still Having Issues

Check browser console (F12 → Console) for errors:
- CORS errors → Backend not allowing frontend origin
- 401 errors → Token issue
- Redirect loop → Supabase URL config issue

## Additional Notes

- Tokens expire after 1 hour (this is normal)
- If you see "Invalid or expired token", just log out and log back in
- The keep-alive feature will reduce backend cold starts

