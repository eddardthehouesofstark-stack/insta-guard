# Render Keep-Alive Solution

## Problem
Render free tier spins down your backend after **15 minutes of inactivity**. The first request after spin-down takes **30-60 seconds** to wake up, causing "Failed to fetch" errors.

---

## Solutions Implemented

### 1. Frontend Keep-Alive (Built-in) ✅
**Location:** `frontend/js/utils.js`

- Pings backend every **5 minutes**
- Runs automatically when users are active
- Prevents spin-down during user sessions

**Pros:**
- Already implemented
- No external service needed
- Works when users are on the site

**Cons:**
- Only works when users have the site open
- Doesn't prevent overnight spin-downs

---

### 2. Retry Logic with User Feedback ✅
**Location:** `frontend/pages/image-checker.html`

- Detects when backend is sleeping
- Shows user-friendly message: "Backend is waking up, please wait 30 seconds..."
- Automatically retries after 30 seconds
- Improves user experience during cold starts

**User Experience:**
```
1. User uploads image
2. If backend is sleeping:
   → Shows: "Backend is waking up, please wait 30 seconds..."
   → Waits 30 seconds
   → Automatically retries
   → Success! ✓
```

---

### 3. UptimeRobot (Recommended External Solution) 🌟

**Setup Steps:**

1. **Sign up for free:** https://uptimerobot.com
   - 100% free forever
   - Monitor up to 50 services
   - No credit card required

2. **Create New Monitor:**
   - Click "+ Add New Monitor"
   - Monitor Type: **HTTP(s)**
   - Friendly Name: `InstaGuard Backend`
   - URL: `https://insta-guard.onrender.com/`
   - Monitoring Interval: **5 minutes** (free tier)

3. **Configure:**
   - Monitor Timeout: 30 seconds
   - Monitor Interval: Every 5 minutes
   - Alert Contacts: Your email (optional)

4. **Done!** ✅
   - UptimeRobot will ping your backend every 5 minutes
   - Backend will NEVER spin down
   - Zero cost, fully automated

**Benefits:**
- ✅ Backend stays awake 24/7
- ✅ Works even when no users are active
- ✅ Email alerts if backend goes down
- ✅ Completely free forever
- ✅ No configuration on Render needed

---

## Current Status

| Solution | Status | Effectiveness |
|----------|--------|---------------|
| Frontend Keep-Alive | ✅ Implemented | Good (during user sessions) |
| Retry Logic | ✅ Implemented | Excellent (handles cold starts gracefully) |
| UptimeRobot | ⚠️ Manual Setup | **Best** (prevents all spin-downs) |

---

## Recommended Next Step

**Set up UptimeRobot** (5 minutes setup, lifetime benefit):

1. Go to https://uptimerobot.com
2. Sign up for free
3. Add monitor for: `https://insta-guard.onrender.com/`
4. Set interval: **5 minutes**
5. Done! Your backend will stay awake 24/7

---

## Alternative Solutions

### Option A: Upgrade to Render Paid Plan
**Cost:** $7/month per service
**Benefit:** No spin-downs, better performance

### Option B: Move to Railway
**Cost:** $5/month for 500 hours
**Benefit:** No forced spin-downs

### Option C: Use Render Cron Jobs
**Limitation:** Render free tier doesn't support cron jobs

---

## Testing

### Test if Backend is Awake:
```bash
curl https://insta-guard.onrender.com/
```

**Expected Response:**
```json
{"status":"InstaGuard API running"}
```

### Test if Keep-Alive is Working:
1. Open browser console (F12)
2. Look for: `[Keep-Alive] Backend is awake ✓`
3. Should appear every 5 minutes

---

## FAQ

**Q: Why does it still fail sometimes?**  
A: If no one visits your site for 15+ minutes AND UptimeRobot isn't set up, Render will spin down. First request wakes it up (30s delay).

**Q: Will UptimeRobot cost anything?**  
A: No! 100% free forever for up to 50 monitors.

**Q: Can I use another service instead of UptimeRobot?**  
A: Yes! Alternatives:
- Cron-job.org (free)
- Better Uptime (free tier)
- Pingdom (paid)
- StatusCake (free tier)

**Q: What's the best long-term solution?**  
A: UptimeRobot (free, automated) OR upgrade to Render paid plan ($7/mo) for better reliability.

---

## Summary

✅ **Current Setup (Good):**
- Frontend keep-alive during user sessions
- Retry logic handles cold starts gracefully

🌟 **Best Setup (Recommended):**
- Current setup + UptimeRobot
- Backend stays awake 24/7
- Zero cost, zero maintenance

💰 **Professional Setup:**
- Upgrade to Render paid plan ($7/mo)
- No spin-downs, better performance
- Better for production apps

---

**Need Help?**
- UptimeRobot Docs: https://uptimerobot.com/help/
- Render Docs: https://render.com/docs/free#free-web-services

---

**Created for InstaGuard Project**  
Last Updated: June 6, 2026
